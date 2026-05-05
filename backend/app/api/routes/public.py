from fastapi import APIRouter, Depends, Request
from app.api.routes.recipe import retrieve_recipes
from app.security import verify_api_key
from app.limiter import limiter

router = APIRouter(prefix="/public", 
                   tags=["Public"],
                   dependencies=[Depends(verify_api_key)])


@router.get("")
@limiter.limit("5/minute")
def get_recipes(request: Request):
    return retrieve_recipes()


# @router.get("/recipes/", response_model=RecipeDetailResponse)
# def get_public_recipes(db: Session = Depends(get_session)):
#     return retrieve_recipes(db=db)