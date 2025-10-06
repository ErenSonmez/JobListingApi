class BaseRepositoryException(Exception):
    def __init__(self, *args):            
        # Call the base class constructor with the parameters it needs
        super().__init__(*args)

class CreateClientException(BaseRepositoryException):
    def __init__(self, message):
        self.message = f"Could not create client: {message}"
        super().__init__(message)

class ClientInfoValidationError(BaseRepositoryException):
    def __init__(self, message):
        self.message = f"Could not parse client info: {message}"

