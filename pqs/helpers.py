"""Helper methods that are repeated across the library"""
# Libraries
# # Built-in
import inspect
# # Internal
from .errors import PQSModelNotValidError, PQSSessionNotValidError
from .start import Base, SessionFactory
# # External
from sqlalchemy.orm import Session
from sqlalchemy import inspect as sqlalchemy_inspect


def get_model_class(model_cls):
    """Retrieves a model class, ensuring it's a valid model class

    Detects if the passed argument is a class and a valid model class
    If no valid model class is passed, raises ValueError

    Raises:
        ValueError: if passed argument is not a valid SQLAlchemy model class
                    (subclass of Base)

    Args:
        model_cls (mixed): the SQLAlchemy model class
    """
    # Check if is class
    if inspect.isclass(model_cls):
        # Detect if class is correct
        if not issubclass(model_cls, Base):
            raise PQSModelNotValidError("Model must be a class based on " +
                                        "SQLAlchemy's Base class")
    else:
        # No valid model passed
        raise PQSModelNotValidError(
            "Model must be a subclass of SQLAlchemy's Base class")
    # Return model
    return model_cls


def get_model_object(model_cls_obj):
    """Retrieves a model object, creating one if it's a class

    Detects if the passed argument is a class or an object in order to
    create a new model from the class or use the existing model passed

    If no valid model is passed, raises ValueError

    Raises:
        ValueError: if passed argument is not either a valid SQLAlchemy
                    model object (subinstance of Base) or class
                    (subclass of Base)

    Args:
        model_cls_obj (mixed): the SQLAlchemy model class / object to inspect
            if it's an object, will return this model
            if it's a class, will create a new empty object from it
    """
    # Variables
    model = None
    # Check if is class
    if inspect.isclass(model_cls_obj):
        # Detect if class is correct
        if issubclass(model_cls_obj, Base):
            # Create object
            model = model_cls_obj()
        else:
            raise PQSModelNotValidError("Model must be a class based on " +
                                        "SQLAlchemy's base class")
    # Check if valid object
    elif isinstance(model_cls_obj, Base):
        # The passed value is a valid object
        model = model_cls_obj
    else:
        # No valid model passed
        raise PQSModelNotValidError(
            "Model must be a subclass of SQLAlchemy's base class or an " +
            "instance of a subclass of it")
    # Return model
    return model


def get_session(self, session=None):
    """Gets a session to use with one or more models

    Must be either a sqlalchemy.orm.session.Session object or None so we
    can create a new session using the session maker stored

    Raises:
        ValueError: if session passed is not valid

    Args:
        session (sqlalchemy.orm.session.Session): session to track model
            will create one if empty

    Returns:
        session (sqlalchemy.orm.session.Session): session to use
    """
    # Create a new session
    if session is None:
        session = SessionFactory()
    # Session passed is okay
    elif isinstance(session, Session):
        # The passed value is a valid object
        session = session
    else:
        # No valid session passed
        raise PQSSessionNotValidError(
            "Session must be an instance of SQLAlchemy's " +
            "`sqlalchemy.orm.session.Session` or `None` to create one " +
            "automatically")
    return session


def get_model_columns_names(model):
    """Retrieves colums names of the model

    This uses all columns of the model by looking into its attributes

    Returns:
        list(str): list of strings containing all models' columns
    """
    return [column.key for column in sqlalchemy_inspect(model).attrs]
