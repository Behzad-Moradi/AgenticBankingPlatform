from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from backend.core.config import settings
from collections.abc import Generator

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session

def check_database_connection() -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return bool(result.scalar_one() == 1)
