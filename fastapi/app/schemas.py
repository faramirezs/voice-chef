from pydantic import BaseModel

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
