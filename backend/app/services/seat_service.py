from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AllocationStatus,
    Employee,
    EmploymentStatus,
    Project,
    Seat,
    SeatAllocation,
    SeatStatus,
)
from app.schemas import SeatSuggestion


def get_active_allocation(db: Session, employee_id: int) -> SeatAllocation | None:
    return (
        db.query(SeatAllocation)
        .filter(
            SeatAllocation.employee_id == employee_id,
            SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
        )
        .first()
    )


def get_seat_active_allocation(db: Session, seat_id: int) -> SeatAllocation | None:
    return (
        db.query(SeatAllocation)
        .filter(
            SeatAllocation.seat_id == seat_id,
            SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
        )
        .first()
    )


def enrich_employee(db: Session, employee: Employee) -> dict:
    allocation = get_active_allocation(db, employee.id)
    active_seat = None
    if allocation:
        seat = db.query(Seat).filter(Seat.id == allocation.seat_id).first()
        if seat:
            active_seat = seat
    return {
        **{c.name: getattr(employee, c.name) for c in employee.__table__.columns},
        "project": employee.project,
        "active_seat": active_seat,
    }


def enrich_seat(db: Session, seat: Seat) -> dict:
    allocation = get_seat_active_allocation(db, seat.id)
    allocated_employee = None
    allocated_project = None
    if allocation:
        allocated_employee = db.query(Employee).filter(Employee.id == allocation.employee_id).first()
        if allocation.project_id:
            allocated_project = db.query(Project).filter(Project.id == allocation.project_id).first()
        elif allocated_employee and allocated_employee.project_id:
            allocated_project = allocated_employee.project
    return {
        **{c.name: getattr(seat, c.name) for c in seat.__table__.columns},
        "allocated_employee": allocated_employee,
        "allocated_project": allocated_project,
    }


def suggest_seats_for_employee(db: Session, employee: Employee, limit: int = 5) -> list[SeatSuggestion]:
    suggestions: list[SeatSuggestion] = []

    available_query = db.query(Seat).filter(Seat.status == SeatStatus.AVAILABLE)

    if employee.project_id:
        project_allocations = (
            db.query(SeatAllocation)
            .join(Seat)
            .filter(
                SeatAllocation.project_id == employee.project_id,
                SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
            )
            .all()
        )
        if project_allocations:
            floors = [a.seat.floor for a in project_allocations if a.seat]
            zones = [a.seat.zone for a in project_allocations if a.seat]
            if floors and zones:
                preferred_floor = max(set(floors), key=floors.count)
                preferred_zone = max(set(zones), key=zones.count)
                preferred_seats = (
                    available_query.filter(Seat.floor == preferred_floor, Seat.zone == preferred_zone)
                    .limit(limit)
                    .all()
                )
                for seat in preferred_seats:
                    suggestions.append(
                        SeatSuggestion(
                            seat=seat,
                            reason=f"Near {employee.project.name if employee.project else 'project'} team on Floor {preferred_floor}, Zone {preferred_zone}",
                            proximity_score=1.0,
                        )
                    )

    if len(suggestions) < limit:
        existing_ids = {s.seat.id for s in suggestions}
        alternate_seats = available_query.limit(limit * 3).all()
        for seat in alternate_seats:
            if seat.id in existing_ids:
                continue
            suggestions.append(
                SeatSuggestion(
                    seat=seat,
                    reason=f"Alternate available seat on Floor {seat.floor}, Zone {seat.zone}",
                    proximity_score=0.5,
                )
            )
            if len(suggestions) >= limit:
                break

    return suggestions[:limit]


def allocate_seat(
    db: Session,
    employee_id: int,
    seat_id: int,
    project_id: int | None = None,
) -> SeatAllocation:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")

    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        raise ValueError("Seat not found")

    if seat.status != SeatStatus.AVAILABLE:
        raise ValueError(f"Seat is not available (current status: {seat.status.value})")

    existing = get_active_allocation(db, employee_id)
    if existing:
        raise ValueError("Employee already has an active seat allocation")

    seat_allocation = get_seat_active_allocation(db, seat_id)
    if seat_allocation:
        raise ValueError("Seat is already allocated to another employee")

    effective_project_id = project_id or employee.project_id

    allocation = SeatAllocation(
        employee_id=employee_id,
        seat_id=seat_id,
        project_id=effective_project_id,
        allocation_status=AllocationStatus.ACTIVE,
        allocation_date=date.today(),
    )
    seat.status = SeatStatus.OCCUPIED
    if employee.status == EmploymentStatus.PENDING_ALLOCATION:
        employee.status = EmploymentStatus.ACTIVE

    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation


def release_seat(db: Session, employee_id: int) -> SeatAllocation:
    allocation = get_active_allocation(db, employee_id)
    if not allocation:
        raise ValueError("No active seat allocation found for employee")

    seat = db.query(Seat).filter(Seat.id == allocation.seat_id).first()
    allocation.allocation_status = AllocationStatus.RELEASED
    allocation.released_date = date.today()
    if seat:
        seat.status = SeatStatus.AVAILABLE

    db.commit()
    db.refresh(allocation)
    return allocation


def get_dashboard_summary(db: Session) -> dict:
    total_employees = db.query(func.count(Employee.id)).scalar() or 0
    total_seats = db.query(func.count(Seat.id)).scalar() or 0
    occupied_seats = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.OCCUPIED).scalar() or 0
    available_seats = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.AVAILABLE).scalar() or 0
    reserved_seats = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.RESERVED).scalar() or 0
    maintenance_seats = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.MAINTENANCE).scalar() or 0
    pending_allocation = (
        db.query(func.count(Employee.id))
        .filter(Employee.status == EmploymentStatus.PENDING_ALLOCATION)
        .scalar()
        or 0
    )
    return {
        "total_employees": total_employees,
        "total_seats": total_seats,
        "occupied_seats": occupied_seats,
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "maintenance_seats": maintenance_seats,
        "pending_allocation": pending_allocation,
    }


def get_project_utilization(db: Session) -> list[dict]:
    projects = db.query(Project).all()
    results = []
    for project in projects:
        employee_count = (
            db.query(func.count(Employee.id)).filter(Employee.project_id == project.id).scalar() or 0
        )
        occupied_seats = (
            db.query(func.count(SeatAllocation.id))
            .filter(
                SeatAllocation.project_id == project.id,
                SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
            )
            .scalar()
            or 0
        )
        results.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "employee_count": employee_count,
                "occupied_seats": occupied_seats,
            }
        )
    return results


def get_floor_utilization(db: Session) -> list[dict]:
    floors = db.query(Seat.floor).distinct().order_by(Seat.floor).all()
    results = []
    for (floor,) in floors:
        total = db.query(func.count(Seat.id)).filter(Seat.floor == floor).scalar() or 0
        occupied = (
            db.query(func.count(Seat.id))
            .filter(Seat.floor == floor, Seat.status == SeatStatus.OCCUPIED)
            .scalar()
            or 0
        )
        available = (
            db.query(func.count(Seat.id))
            .filter(Seat.floor == floor, Seat.status == SeatStatus.AVAILABLE)
            .scalar()
            or 0
        )
        reserved = (
            db.query(func.count(Seat.id))
            .filter(Seat.floor == floor, Seat.status == SeatStatus.RESERVED)
            .scalar()
            or 0
        )
        occupancy_rate = round((occupied / total * 100) if total > 0 else 0, 2)
        results.append(
            {
                "floor": floor,
                "total_seats": total,
                "occupied_seats": occupied,
                "available_seats": available,
                "reserved_seats": reserved,
                "occupancy_rate": occupancy_rate,
            }
        )
    return results
