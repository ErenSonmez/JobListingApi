from dataclasses import dataclass

@dataclass(frozen=True)
class MongoClientCredentials:
    # TODO: Improve validation
    host: str
    port: int

    username: str
    password: str

    db_name: str