from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.database import get_db, engine
from app import models, schemas

app = FastAPI()

@app.get("/")
def hello():
    return {"Hello voice-chef"}

# Create a new user (POST)
@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(username=user.username, email=user.email, firstname=user.firstname, lastname=user.lastname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# List all users (GET)
@app.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# List DB tables (GET)
@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}