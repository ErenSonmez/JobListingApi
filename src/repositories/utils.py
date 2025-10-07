from repositories.schemas import MongoClientCredentials

from repositories.exceptions import ClientInfoValidationException

def validate_and_create_mongo_credentials(host: str, port: str | int, username: str, password: str, db_name: str):
    if not all([host, port, username, password, db_name]):
        raise ClientInfoValidationException("credentials contain empty or bad values")

    try:
        port = int(port)
    except ValueError:
        raise ClientInfoValidationException(f'could not parse port value "{port}" as integer.')

    return MongoClientCredentials(host, port, username, password, db_name)