from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models.base import Base


def create_sqlalchemy_session(file_path: str) -> Session:
    engine = create_engine(f"sqlite:///{file_path}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()
