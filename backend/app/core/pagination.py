from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import select, Session


class PaginationParams(BaseModel):
    limit: int
    offset: int


def pagination_params(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def paginate(query, session: Session, pagination: PaginationParams):
    total = session.exec(
        select(func.count()).select_from(query.subquery())).one()

    items = session.exec(query.offset(pagination.offset).limit(pagination.limit)).all()

    return {
        "items": items,
        "meta": {
            "limit": pagination.limit,
            "offset": pagination.offset,
            "total": total,
        },
    }