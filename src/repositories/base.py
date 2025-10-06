import os

import pymongo

from typing import Optional

from repositories.schemas import MongoClientCredentials

from repositories.exceptions import CreateClientException, ClientInfoValidationError

class BaseRepository:
    ENV_HOST_KEY="MONGO_HOST"
    ENV_PORT_KEY="MONGO_PORT"

    ENV_USERNAME_KEY="MONGO_ADMIN_USER"
    ENV_PASSWORD_KEY="MONGO_ADMIN_PASS"

    def __init__(self, client: Optional[pymongo.AsyncMongoClient] = None, client_info: Optional[MongoClientCredentials] = None):
        self._client: pymongo.AsyncMongoClient = client
        if self._client is None:
            self._client: pymongo.AsyncMongoClient = self._create_client(client_info)

        self.database: pymongo.database.Database = self._client.get_database("listing-api-db")

    def _get_client_info_from_env(self) -> MongoClientCredentials:
        host = os.getenv(self.ENV_HOST_KEY)
        port = os.getenv(self.ENV_PORT_KEY)

        try:
            port = int(port)
        except ValueError:
            raise ClientInfoValidationError(f'Could not parse port value "{port}" as integer.')

        username = os.getenv(self.ENV_USERNAME_KEY)
        password = os.getenv(self.ENV_PASSWORD_KEY)

        if not all([host, port, username, password]):
            return None

        return MongoClientCredentials(host, port, username, password)


    def _create_client(self,client_info: Optional[MongoClientCredentials]) -> pymongo.AsyncMongoClient:
        if client_info is None:
            client_info = self._get_client_info_from_env()

        if client_info is None:
            raise CreateClientException("Could not read client info from environment")

        client = pymongo.AsyncMongoClient(f'mongodb://{client_info.username}:{client_info.password}@{client_info.host}:{client_info.port}/')

        return client