import uuid

from sqlmodel import Field, SQLModel
from pydantic import BaseModel

from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    firstname: str = Field(nullable=False)
    lastname: str = Field(nullable=False)


class Hero(SQLModel, table=True):
    __tablename__ = "heroes"

    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    firstname: str = Field(nullable=False)
    lastname: str = Field(nullable=False)

class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, nullable=True)



class UserCreate(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    firstname: str
    lastname: str

    class Config:
        from_attributes = True
