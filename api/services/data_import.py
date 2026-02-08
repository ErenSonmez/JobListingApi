import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, Generic, get_args, get_origin

import os
import pathlib

from beanie import Document
from fastapi import UploadFile
import aiofiles

import aiocsv

import uuid

from multiprocessing import Process

from pydantic import ValidationError

from repositories.factory import RepositoryFactory
from services.base import BaseService
from services.exceptions import BadEnvironmentValueException, FileTypeNotProvidedException, UnknownFileContentTypeException, UnknownFileExtensionException
from services.schemas import ImportJob

from models.base import TModel, TModelData

from repositories.base import TRepo

# TODO: Write tests

async def _read_csv(file_path: pathlib.Path, delimiter: str = ",", line_terminator: str = "/n"):
    async with aiofiles.open(file_path, "r") as f:
        reader = aiocsv.AsyncReader(f, delimiter=delimiter, lineterminator=line_terminator)
        headers = await anext(reader)
        async for row in reader:
            yield {k:v for k,v in zip(headers, row)}


class ImportService(BaseService, Generic[TRepo, TModel, TModelData]):
    _EXTENSION_READ_METHODS: dict[str, Callable[[pathlib.Path], AsyncGenerator[dict[str, Any]]]] = {
        ".csv": _read_csv,
    }
    _CONTENT_TYPE_READ_METHODS: dict[str, Callable[[pathlib.Path], AsyncGenerator[dict[str, Any]]]] = {
        "text/csv": _read_csv,
    }
    _CONTENT_TYPE_EXTENSION_MAP: dict[str, str] = {
        "text/csv": ".csv"
    }

    ENV_IMPORT_TEMP_FOLDER_PATH_KEY: str = "IMPORT_TEMP_FOLDER"
    ENV_IMPORT_TEMP_FOLDER_PATH: pathlib.Path = None

    _IMPORT_TEMP_SAVE_CHUNK_SIZE = 1024*1024 # 1 mb

    def _read_import_temp_path_from_env(self, create_if_not_exists: bool = True):
        import_temp_path = os.getenv(self.ENV_IMPORT_TEMP_FOLDER_PATH_KEY)
        if import_temp_path is None:
            raise BadEnvironmentValueException(f"Bad temp import folder path in environment, " +
                                               f"checked key: {self.ENV_IMPORT_TEMP_FOLDER_PATH_KEY}," +
                                               f"found value: {import_temp_path}")

        import_temp_path_obj = pathlib.Path(import_temp_path)

        if create_if_not_exists and not import_temp_path_obj.exists():
            os.makedirs(import_temp_path_obj)

        return import_temp_path_obj

    def _get_import_temp_path(self):
        if not self.ENV_IMPORT_TEMP_FOLDER_PATH:
            self.ENV_IMPORT_TEMP_FOLDER_PATH = self._read_import_temp_path_from_env()

        return self.ENV_IMPORT_TEMP_FOLDER_PATH

    def _create_import_job_id(self):
        return uuid.uuid4().hex

    async def _read_file(self, file_path: pathlib.Path, content_type: str = None, file_extension: str = None, empty_str_is_none: bool = True, **kwargs):
        if not content_type:
            if not file_extension:
                raise FileTypeNotProvidedException()

            if file_extension not in self._EXTENSION_READ_METHODS:
                raise UnknownFileExtensionException(file_path.name, file_extension)

            reader_method = self._EXTENSION_READ_METHODS[file_extension]
        else:
            if content_type not in self._CONTENT_TYPE_READ_METHODS:
                raise UnknownFileContentTypeException(file_path.name, content_type)

            reader_method = self._CONTENT_TYPE_READ_METHODS[content_type]

        async for row_data in reader_method(file_path, **kwargs):
            if empty_str_is_none:
                for k,v in row_data.items():
                    if v == "":
                        row_data[k] = None
            yield row_data

    async def _create_and_run_import_job(self, job: ImportJob):
        repo = await RepositoryFactory.get_repository(job.repo_type)

        import_data = []
        last_import_coroutine: Awaitable = None

        current_batch_size = 0
        async for item in self._read_file(job.file_path,
                                          job.file_content_type,
                                          job.file_extension):
            try:
                validated_item = job.model_data_type.model_validate(item)
            except ValidationError as ex:
                continue # TODO: Return validation errors

            import_data.append(validated_item)
            current_batch_size += 1
            if current_batch_size >= job.batch_size:
                if last_import_coroutine is not None:
                    await last_import_coroutine

                last_import_coroutine = repo.create_many(import_data)

                current_batch_size = 0
                import_data = []

        # Import last batch
        await last_import_coroutine
        await repo.create_many(import_data)

    def _start_job_process(self, job):
        asyncio.run(self._create_and_run_import_job(job))

    async def import_file(self, file: UploadFile,
                          model_type: TModel, model_data_type: TModelData, repo_type: TRepo,
                          **kwargs):
        # TODO: Accept zipped file, extract extension and content type from file after opening zip
        import_job_id = self._create_import_job_id()

        content_type = file.content_type
        file_name = file.filename

        file_extension: str = None
        if content_type is not None:
            file_extension = self._CONTENT_TYPE_EXTENSION_MAP.get(content_type, None)
        if file_extension is None:
            if file_name is not None:
                file_extension = ''.join(pathlib.Path(file_name).suffixes)
            else:
                raise FileTypeNotProvidedException()

        import_temp_path = self._get_import_temp_path()
        import_file_path = import_temp_path.joinpath(f"{import_job_id}{file_extension}")

        async with aiofiles.open(import_file_path, "wb") as f:
            while chunk := await file.read(self._IMPORT_TEMP_SAVE_CHUNK_SIZE):
                await f.write(chunk)

        job = ImportJob(
            id = import_job_id,
            file_path = import_file_path,
            file_content_type = content_type,
            file_extension = file_extension,
            reader_kwargs = kwargs,

            repo_type = repo_type,
            model_type = model_type,
            model_data_type = model_data_type,
        )
        job_process = Process(target = self._start_job_process, args=(job,)) # copies self(service obj) into process
        job_process.start()

        return job