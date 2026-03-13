from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = "postgresql+psycopg://recipe_user:recipe_pass123@db:5432/recipe_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


