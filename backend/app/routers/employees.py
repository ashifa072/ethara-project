from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Employee, EmploymentStatus
from app.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    PaginatedEmployees,
    SeatSuggestion,
)
from app.services.seat_service import enrich_employee, suggest_seats_for_employee

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")
    existing_code = db.query(Employee).filter(Employee.employee_code == payload.employee_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Employee code already exists")

    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    db.refresh(employee, attribute_names=["project"])
    return enrich_employee(db, employee)


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    employee_id: str | None = Query(None, alias="employee_code"),
    email: str | None = None,
    project_id: int | None = None,
    department: str | None = None,
    status: EmploymentStatus | None = None,
    floor: int | None = None,
    zone: str | None = None,
):
    query = db.query(Employee).options(joinedload(Employee.project))

    if search:
        query = query.filter(
            or_(
                Employee.name.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.employee_code.ilike(f"%{search}%"),
            )
        )
    if employee_id:
        query = query.filter(Employee.employee_code.ilike(f"%{employee_id}%"))
    if email:
        query = query.filter(Employee.email.ilike(f"%{email}%"))
    if project_id:
        query = query.filter(Employee.project_id == project_id)
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    employees = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [enrich_employee(db, e) for e in employees]

    if floor or zone:
        filtered = []
        for item in items:
            seat = item.get("active_seat")
            if not seat:
                if status == EmploymentStatus.PENDING_ALLOCATION:
                    filtered.append(item)
                continue
            if floor and seat.floor != floor:
                continue
            if zone and seat.zone.lower() != zone.lower():
                continue
            filtered.append(item)
        items = filtered
        total = len(items)

    return PaginatedEmployees(total=total, page=page, page_size=page_size, items=items)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = (
        db.query(Employee)
        .options(joinedload(Employee.project))
        .filter(Employee.id == employee_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return enrich_employee(db, employee)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing = (
            db.query(Employee)
            .filter(Employee.email == update_data["email"], Employee.id != employee_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    db.refresh(employee, attribute_names=["project"])
    return enrich_employee(db, employee)


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.status = EmploymentStatus.INACTIVE
    db.commit()
    db.refresh(employee)
    db.refresh(employee, attribute_names=["project"])
    return enrich_employee(db, employee)


@router.get("/{employee_id}/seat-suggestions", response_model=list[SeatSuggestion])
def get_seat_suggestions(employee_id: int, db: Session = Depends(get_db)):
    employee = (
        db.query(Employee)
        .options(joinedload(Employee.project))
        .filter(Employee.id == employee_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return suggest_seats_for_employee(db, employee)
