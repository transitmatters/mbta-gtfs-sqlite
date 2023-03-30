from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from models.base import Base


def create_sqlalchemy_session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


def create_sqlalchemy_session_for_file(file_path: str) -> Session:
    engine = create_engine(f"sqlite:///{file_path}")
    Base.metadata.create_all(bind=engine)
    return create_sqlalchemy_session(engine=engine)
