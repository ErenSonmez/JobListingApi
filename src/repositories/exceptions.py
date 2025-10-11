class BaseRepositoryException(Exception):
    def __init__(self, *args):
        # Call the base class constructor with the parameters it needs
        super().__init__(*args)

class CreateClientException(BaseRepositoryException):
    def __init__(self, message):
        message = f"Could not create client: {message}"
        super().__init__(message)

class ClientInfoValidationException(BaseRepositoryException):
    def __init__(self, message):
        message = f"Could not parse client info: {message}"
        super().__init__(message)

class RepositoryNotFoundException(BaseRepositoryException):
    def __init__(self, repo_type: type):
        message = f"Repository type not found: {repo_type.__name__}"
        super().__init__(message)

class MissingIdException(BaseRepositoryException):
    def __init__(self, message):
        message = f"ID is missing: {message}"
        super.__init__(message)