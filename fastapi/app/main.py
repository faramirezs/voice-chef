from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.database import get_db, engine

app = FastAPI()

@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}

@app.get("/")
def tmp():
    return {"Hello voice-chef"}