class FlaskJWTLoginError(Exception):
    """base class for all exceptions in this module"""
    pass


class UserLoaderNotSetException(FlaskJWTLoginError):
    """raised when callback function for loading user was not set"""
    def __init__(self, message):
        self.message = message
