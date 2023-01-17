class DataNotFoundException(Exception):
    """
    Custom exception class will be raised if the data is not found
    """
    description = 'Data Not Found'

    def __init__(self, message, code):
        self.message = message
        self.code = code