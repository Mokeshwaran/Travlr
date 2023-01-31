from Travlr.exceptions.api_exception import APIException


class InvalidCredentialsException(Exception):
    """
    Custom exception class will be raised if the given credentials are invalid
    """
    description = 'Invalid Credentials'

    def __init__(self, message, code):
        self.message = message
        self.code = code