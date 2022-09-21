from api.config import settings
from sqlmodel import create_engine, Session, SQLModel

engine = create_engine(f"sqlite:///{settings.database}")


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    try:
        with Session(engine) as session:
            yield session
    finally:
        session.close()
