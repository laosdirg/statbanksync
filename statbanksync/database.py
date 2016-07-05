"""
Handle connections to database
"""

from . import config
from contextlib import contextmanager
import re
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(config.DB_URL)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False, autocommit=False))
Base = declarative_base(bind=engine)


@contextmanager
def create_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def to_identifier(identifier):
    return re.sub("[^A-Za-z0-9]", "", identifier)

def works():
    try:
        engine.execute("SELECT 1")
        return True
    except:
        return False
