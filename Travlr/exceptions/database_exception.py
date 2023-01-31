from Travlr.exceptions.api_exception import APIException


class DatabaseException(Exception):
    """
    Custom exception class will be raised if any error in database operation
    """
    description = 'Database Exception'

    def __init__(self, message, code):
        self.message = message
        self.code = code