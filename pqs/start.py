"""Starts the PyQt SQLAlchemy module by defining basic variables"""
# Libraries
# # External
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Constants
Base = declarative_base()
"""
    object: Base object for all SQLAlchemy models
"""
SessionFactory = sessionmaker()
"""
    sqlalchemy.orm.session.sessionmaker: Session factory
"""
engine = None
"""
    sqlalchemy.engine.Engine: engine binded to the session factory
"""


# Methods
def bind_engine(new_engine):
    """Binds an engine to the SessionFactory

    Args:
        new_engine (sqlalchemy.engine.Engine): engine to bind to the session
    """
    global engine
    SessionFactory.configure(bind=new_engine)
    engine = new_engine


def is_engine_binded():
    """Checks if the engine has been binded"""
    return engine is not None


def get_engine():
    """Returns the binded engine"""
    return engine
