from fastapi import APIRouter,Depends

from src.ai import controller
from src.utils.db import get_db
from sqlalchemy.orm import Session

ai_router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@ai_router.get("/search")
async def ai_search(
    q: str,
    db: Session = Depends(get_db)
):
    return controller.ai_search(q,db)




