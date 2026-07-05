from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dashboard.controller import get_dashboard
from src.dashboard.ditos import DashboardResponseSchema
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import get_current_admin

dashboard_routes = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@dashboard_routes.get(
    "",
    response_model=DashboardResponseSchema,
    summary="Admin Dashboard",
)
async def dashboard(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return get_dashboard(
        db=db,
        current_user=current_user,
    )