from pydantic import BaseModel, BeforeValidator, IPvAnyAddress
from typing import Annotated

IntConvertible = Annotated[int, BeforeValidator(lambda v: int(v) if isinstance(v, str) and v.isdigit() else v)]
class MongoClientCredentials(BaseModel):
    host: IPvAnyAddress
    port: IntConvertible

    username: str
    password: str

    db_name: str

class OrderByField(BaseModel):
    field_name: str
    ascending: bool