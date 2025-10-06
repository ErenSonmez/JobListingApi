from dataclasses import dataclass

@dataclass
class MongoClientCredentials:
    host: str
    port: int
    username: str
    password: str