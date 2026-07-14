import re
from typing import Optional

from sqlalchemy import func, or_
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
from app.services.seat_service import get_active_allocation, get_dashboard_summary


def _find_employee(db: Session, name: Optional[str] = None, email: Optional[str] = None) -> Employee | None:
    query = db.query(Employee).options(joinedload(Employee.project))
    if email:
        return query.filter(Employee.email.ilike(email.strip())).first()
    if name:
        return query.filter(Employee.name.ilike(f"%{name.strip()}%")).first()
    return None


def _format_seat(seat: Seat) -> str:
    return f"Floor {seat.floor}, Zone {seat.zone}, Bay {seat.bay}, Seat {seat.seat_number}"


def _format_employee_seat_answer(employee: Employee, db: Session) -> str:
    allocation = get_active_allocation(db, employee.id)
    project_name = employee.project.name if employee.project else "No project assigned"
    if allocation:
        seat = db.query(Seat).filter(Seat.id == allocation.seat_id).first()
        if seat:
            pronoun = "She" if employee.name.split()[0].endswith("a") else "He"
            return (
                f"{employee.name} is seated on {_format_seat(seat)}. "
                f"{pronoun} is assigned to Project {project_name}."
            )
    if employee.status == EmploymentStatus.PENDING_ALLOCATION:
        return (
            f"{employee.name} has not been allocated a seat yet. "
            f"They are assigned to Project {project_name} and are pending seat allocation."
        )
    return f"{employee.name} does not have an active seat allocation. Project: {project_name}."


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    return match.group(0) if match else None


def _extract_name(text: str) -> Optional[str]:
    patterns = [
        r"where is(?:\s+employee)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:seated|sit|sitting)",
        r"(?:find|locate)(?:\s+employee)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:seated|sit|sitting)",
        r"my name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"employee\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            if name.lower() != "employee":
                return name
    return None


def _extract_floor(text: str) -> Optional[int]:
    match = re.search(r"floor\s*(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _extract_project_name(text: str, db: Session) -> Optional[str]:
    projects = db.query(Project).all()
    text_lower = text.lower()
    for project in projects:
        if project.name.lower() in text_lower:
            return project.name
    match = re.search(r"project\s+(\w+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def process_ai_query(db: Session, query: str) -> tuple[str, str]:
    query_lower = query.lower().strip()
    email = _extract_email(query)

    # Self seat query
    if any(kw in query_lower for kw in ["where is my seat", "my seat", "where am i seated", "where do i sit"]):
        if email:
            employee = _find_employee(db, email=email)
            if employee:
                allocation = get_active_allocation(db, employee.id)
                project_name = employee.project.name if employee.project else "No project"
                if allocation:
                    seat = db.query(Seat).filter(Seat.id == allocation.seat_id).first()
                    if seat:
                        return (
                            f"You are allocated {_format_seat(seat)}. Your project is {project_name}.",
                            "my_seat",
                        )
                return (
                    f"You do not have an active seat allocation yet. Your project is {project_name}.",
                    "my_seat",
                )
        return (
            "Please provide your email in the query, e.g. 'Where is my seat? My email is amit@ethara.ai'",
            "my_seat",
        )

    # Project assignment query
    if any(kw in query_lower for kw in ["which project", "my project", "assigned to", "project am i"]):
        if email:
            employee = _find_employee(db, email=email)
            if employee:
                project_name = employee.project.name if employee.project else "No project assigned"
                return f"You are assigned to Project {project_name}.", "project_assignment"
        name = _extract_name(query)
        if name:
            employee = _find_employee(db, name=name)
            if employee:
                project_name = employee.project.name if employee.project else "No project assigned"
                return f"{employee.name} is assigned to Project {project_name}.", "project_assignment"
        return "Please provide your email or name to look up project assignment.", "project_assignment"

    # Available seats on floor
    if "available" in query_lower and "seat" in query_lower:
        floor = _extract_floor(query)
        q = db.query(Seat).filter(Seat.status == SeatStatus.AVAILABLE)
        if floor:
            q = q.filter(Seat.floor == floor)
            seats = q.limit(20).all()
            if not seats:
                return f"No available seats found on Floor {floor}.", "available_seats"
            seat_list = ", ".join(f"{s.zone}-{s.seat_number}" for s in seats[:10])
            extra = f" and {len(seats) - 10} more" if len(seats) > 10 else ""
            total = q.count()
            return (
                f"Found {total} available seats on Floor {floor}: {seat_list}{extra}.",
                "available_seats",
            )
        total = q.count()
        return f"There are {total} available seats across all floors.", "available_seats"

    # Who is sitting near me / nearby
    if any(kw in query_lower for kw in ["near me", "nearby", "sitting near", "who is near"]):
        if email:
            employee = _find_employee(db, email=email)
            if employee:
                allocation = get_active_allocation(db, employee.id)
                if allocation:
                    seat = db.query(Seat).filter(Seat.id == allocation.seat_id).first()
                    if seat:
                        nearby = (
                            db.query(SeatAllocation)
                            .join(Seat)
                            .join(Employee)
                            .filter(
                                SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
                                Seat.floor == seat.floor,
                                Seat.zone == seat.zone,
                                Seat.bay == seat.bay,
                                SeatAllocation.employee_id != employee.id,
                            )
                            .limit(10)
                            .all()
                        )
                        if nearby:
                            names = [a.employee.name for a in nearby if a.employee]
                            return f"People sitting near you in Bay {seat.bay}: {', '.join(names)}.", "nearby"
                        return f"No other employees found in your bay ({seat.bay}) on Floor {seat.floor}.", "nearby"
        return "Please provide your email to find nearby colleagues.", "nearby"

    # Project seat utilization
    if any(kw in query_lower for kw in ["how many seats", "seat utilization", "occupied for project"]):
        project_name = _extract_project_name(query, db)
        if project_name:
            project = db.query(Project).filter(Project.name.ilike(project_name)).first()
            if project:
                occupied = (
                    db.query(func.count(SeatAllocation.id))
                    .filter(
                        SeatAllocation.project_id == project.id,
                        SeatAllocation.allocation_status == AllocationStatus.ACTIVE,
                    )
                    .scalar()
                    or 0
                )
                employees = (
                    db.query(func.count(Employee.id)).filter(Employee.project_id == project.id).scalar() or 0
                )
                return (
                    f"Project {project.name} has {occupied} occupied seats and {employees} assigned employees.",
                    "project_utilization",
                )
        return "Please specify a project name, e.g. 'How many seats are occupied for Project Indigo?'", "project_utilization"

    # Employee seat lookup
    if any(kw in query_lower for kw in ["where is", "seated", "seat of", "find employee", "locate"]):
        name = _extract_name(query)
        if email:
            employee = _find_employee(db, email=email)
            if employee:
                return _format_employee_seat_answer(employee, db), "employee_seat"
        if name:
            employee = _find_employee(db, name=name)
            if employee:
                return _format_employee_seat_answer(employee, db), "employee_seat"
            return f"No employee found matching '{name}'.", "employee_seat"

    # Dashboard summary
    if any(kw in query_lower for kw in ["summary", "statistics", "stats", "overview", "dashboard"]):
        summary = get_dashboard_summary(db)
        return (
            f"Ethara has {summary['total_employees']} employees, {summary['total_seats']} total seats. "
            f"{summary['occupied_seats']} occupied, {summary['available_seats']} available, "
            f"{summary['reserved_seats']} reserved, and {summary['pending_allocation']} pending allocation.",
            "dashboard_summary",
        )

    # Pending allocation / new joiners
    if any(kw in query_lower for kw in ["pending", "new joiner", "not allocated"]):
        pending = (
            db.query(Employee)
            .filter(Employee.status == EmploymentStatus.PENDING_ALLOCATION)
            .limit(10)
            .all()
        )
        total = (
            db.query(func.count(Employee.id))
            .filter(Employee.status == EmploymentStatus.PENDING_ALLOCATION)
            .scalar()
            or 0
        )
        if pending:
            names = ", ".join(e.name for e in pending)
            extra = f" and {total - 10} more" if total > 10 else ""
            return f"{total} employees pending seat allocation: {names}{extra}.", "pending_allocation"
        return "No employees are pending seat allocation.", "pending_allocation"

    # Help / fallback
    return (
        "I can help with: seat location ('Where is employee Amit seated?'), "
        "project assignment ('Which project am I assigned to?'), "
        "available seats ('Show available seats on Floor 3'), "
        "nearby colleagues ('Who is sitting near me?'), "
        "project utilization ('How many seats for Project Indigo?'), "
        "and dashboard stats. Include an email or employee name in your query.",
        "help",
    )
