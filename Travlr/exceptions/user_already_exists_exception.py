from Travlr.exceptions.api_exception import APIException


class UserAlreadyExistsException(APIException):
    """
    Custom exception class will be raised if the user data already exists
    """
    description = 'User Already Exists'

    def __init__(self, message, code):
        self.message = message
        self.code = code