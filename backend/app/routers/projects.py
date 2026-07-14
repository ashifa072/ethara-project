from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Employee, Project
from app.schemas import EmployeeResponse, ProjectCreate, ProjectResponse
from app.services.seat_service import enrich_employee

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.name).all()


@router.get("/{project_id}/employees", response_model=list[EmployeeResponse])
def list_project_employees(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    employees = (
        db.query(Employee)
        .options(joinedload(Employee.project))
        .filter(Employee.project_id == project_id)
        .all()
    )
    return [enrich_employee(db, e) for e in employees]
