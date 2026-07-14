from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import DashboardSummary, FloorUtilization, ProjectUtilization
from app.services.seat_service import (
    get_dashboard_summary,
    get_floor_utilization,
    get_project_utilization,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/project-utilization", response_model=list[ProjectUtilization])
def project_utilization(db: Session = Depends(get_db)):
    return get_project_utilization(db)


@router.get("/floor-utilization", response_model=list[FloorUtilization])
def floor_utilization(db: Session = Depends(get_db)):
    return get_floor_utilization(db)
