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


# Methods
def bind_engine(engine):
    """Binds an engine to the SessionFactory

    Args:
        engine (sqlalchemy.engine.Engine): engine to bind to the session
    """
    SessionFactory.configure(bind=engine)
