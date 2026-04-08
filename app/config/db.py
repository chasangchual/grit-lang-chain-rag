from typing import Any, Generator, Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

from app.config.config import get_config

config = get_config()
DATABASE_URL = config.database_url

engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Generator[Session, Any, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


db_session = Annotated[Session, Depends(get_session)]
