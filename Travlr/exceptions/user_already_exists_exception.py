from Travlr.exceptions.api_exception import APIException


class UserAlreadyExistsException(Exception):
    """
    Custom exception class will be raised if the user data already exists
    """
    description = 'User Already Exists'

    def __init__(self, message, code):
        self.message = message
        self.code = code