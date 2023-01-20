from Travlr.exceptions.api_exception import APIException


class DatabaseException(APIException):
    """
    Custom exception class will be raised if some error in database operation
    """
    description = 'Database Exception'

    def __init__(self, message, code):
        self.message = message
        self.code = code