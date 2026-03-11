from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://recipe_user:recipe_pass123@localhost:5432/recipe_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
