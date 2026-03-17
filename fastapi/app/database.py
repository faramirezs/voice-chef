import os
from sqlmodel import create_engine, SQLModel
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
     raise RuntimeError("DATABASE_URL environment variable is not set")

SQL_ECHO = os.environ.get("SQL_ECHO", "false").lower() in ("1", "true", "yes")
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    # Import models so that SQLModel.metadata is populated before creating tables
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


