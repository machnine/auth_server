from sqlmodel import Session, SQLModel, create_engine

from api.config import settings

engine = create_engine(f"sqlite:///{settings.database}")


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    try:
        session = Session(engine)
        yield session
    finally:
        session.close()
