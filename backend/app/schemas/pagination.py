from pydantic import BaseModel
from typing import List, Generic, TypeVar
from sqlalchemy import func
from sqlmodel import select, Session


T = TypeVar("T")

class PaginationMeta(BaseModel):
    limit: int
    offset: int
    total: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta
