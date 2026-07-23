from fastapi import APIRouter,Depends

from src.ai import controller
from src.utils.db import get_db
from sqlalchemy.orm import Session
from src.product.ditos import ProductResponseSchema
from src.utils.schemas import PaginatedResponse

ai_router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@ai_router.get(
        "/search",
        response_model=PaginatedResponse[ProductResponseSchema],
        summary="AI Product Search",
        description="Performs natural language product search using AI-powered query understanding."
        )
async def ai_search(
    q: str,
    db: Session = Depends(get_db)
):
    return controller.ai_search(q,db)




