from models.user import User

class BaseServiceException(Exception):
    def __init__(self, *args):
        # Call the base class constructor with the parameters it needs
        super().__init__(*args)

class BadEnvironmentValueException(BaseServiceException):
    def __init__(self, message):
        super().__init__(f"Bad environment variable: {message}")

class MissingEnvironmentVariableException(BaseServiceException):
    def __init__(self, env_key):
        super().__init__(f"Missing environment variable: {env_key}")

# AuthService
class AuthServiceException(BaseServiceException):
    def __init__(self, *args):
        super().__init__(*args)

class UserNotFoundExcepotion(AuthServiceException):
    def __init__(self, usernameOrEmail: str):
        self.usernameOrEmail = usernameOrEmail

        message = f"User with username or email not found: {usernameOrEmail}"
        super().__init__(message)

class IncorrectPasswordException(AuthServiceException):
    def __init__(self, user: User, bad_password: str):
        self.user = user
        self.bad_password = bad_password

        message = f"Invalid password used for user {user.id}"
        super().__init__(message)

class UsernameExistsException(AuthServiceException):
    def __init__(self, username: str):
        self.username = username

        message = f"Username '{username}' is taken"
        super().__init__(message)

class EmailExistsException(AuthServiceException):
    def __init__(self, email: str):
        self.email = email

        message = f"Email '{email}' is used by another user"
        super().__init__(message)

# ImportService
class ImportServiceException(BaseServiceException):
    def __init__(self, *args):
        super().__init__(*args)

class FileTypeNotProvidedException(ImportServiceException):
    def __init__(self, message = None):
        if not message:
            message = "File type info is not provided"
        super().__init__(message)

class UnknownFileExtensionException(ImportServiceException):
    def __init__(self, file_name: str, file_extension: str):
        self.file_name = file_name
        self.file_extension = file_extension

        message = f"Unknown file extension '{file_extension}', from file name '{file_name}'"
        super().__init__(message)

class UnknownFileContentTypeException(ImportServiceException):
    def __init__(self, file_name: str, content_type: str):
        self.file_name = file_name
        self.content_type = content_type

        message = f"Unknown content type '{content_type}', file name '{file_name}'"
        super().__init__(message)

