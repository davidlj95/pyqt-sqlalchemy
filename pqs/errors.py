"""Defines the errors that can be raised when dealing with PQS"""


# Classes
class PQSBindersNotValidError(Exception):
    """Binders for GUI fields and model fields are not valid"""
    pass


class PQSBindersNotFoundError(Exception):
    """Binders for GUI fields and model fields can't be found"""
    pass


class PQSSessionNotValidError(Exception):
    """SQLAlchemy session is not valid"""
    pass


class PQSModelNotValidError(Exception):
    """SQLAlchemy model is not valid"""
    pass


class PQSUINotValidError(Exception):
    """UI objects must have a `setupUi` method"""


class PQSFormFieldsNotValidError(Exception):
    """Some fields of the form are not valid"""
