from Travlr.exceptions.api_exception import APIException


class MustNotBeEmptyException(APIException):
    """
    Custom exception class will be raised if the field is not be empty
    """
    description = 'Must Not Be Empty'

    def __init__(self, message, code):
        self.message = message
        self.code = code