class BaseError(Exception):
    """Base class for all custom errors"""
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message
    
class AlreadyExistsError(BaseError):
    """Raised when something is being added and it already exists"""
    def __init__(self, message="Object already exists.", *args):
        super().__init__(message, *args)

class DoesNotExistError(BaseError):
    """Raised when something is being deleted but does not exists"""
    def __init__(self, message="Object does not exist.", *args):
        super().__init__(message, *args)