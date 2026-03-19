from fastapi import FastAPI, Depends, HTTPException
from app.database import get_db, engine, create_db_and_tables
from app import models
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from sqlalchemy import inspect

@asynccontextmanager
# Lifespan function to create tables on startup
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def hello():
    return {"message": "Hello voice-chef"}


# NOTE: DL - this is just a test endpoint to verify that we can fetch recipes from the database. 
# We will remove this later and implement proper endpoints for recipes.
@app.get("/recipes")
def fetch_recipes(session: Session = Depends(get_db)):
    result = session.execute(select(models.Recipe))
    recipes = result.scalars().all()
    return recipes

# Create a new user (POST)
@app.post("/users", response_model=models.UserOut)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):

    # Check if username already exists
    existing = db.exec(
        select(models.User).where(models.User.username == user.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    existing_email = db.exec(
        select(models.User).where(models.User.email == user.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = models.User(username=user.username, 
                           email=user.email, 
                           firstname=user.firstname, 
                           lastname=user.lastname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# List all users (GET)
@app.get("/users", response_model=list[models.UserOut])
def list_users(db: Session = Depends(get_db)):
    result = db.exec(select(models.User))
    return result.all()

# List DB tables (GET)
# NOTE: DL: You cannot fully replace inspect() with SQLModel's own APIs, but this is a simple 
# endpoint to verify that we can connect to the database and fetch table names. 
@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}