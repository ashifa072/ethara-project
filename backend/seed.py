"""
Seed script for Ethara Seat Allocation System.
Generates: 5000 employees, 5500+ seats, 10+ projects, 5 floors, 10+ zones.
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import (
    AllocationStatus,
    Employee,
    EmploymentStatus,
    Project,
    ProjectStatus,
    Seat,
    SeatAllocation,
    SeatStatus,
)

PROJECTS = [
    ("Indigo", "Enterprise platform development", "Rajesh Kumar"),
    ("Indreed", "Internal HR management system", "Priya Sharma"),
    ("Mydreed", "Mobile application suite", "Amit Patel"),
    ("Preed", "Predictive analytics engine", "Sneha Reddy"),
    ("Serfy", "Service management platform", "Vikram Singh"),
    ("Oreed", "Operations reporting dashboard", "Anita Desai"),
    ("bedegreed", "Background verification system", "Karan Mehta"),
    ("Opreed", "Open-source integration layer", "Deepa Nair"),
    ("Serry", "Security and compliance module", "Rahul Joshi"),
    ("Kaary", "Workflow automation tool", "Meera Iyer"),
    ("Mered", "Metrics and monitoring system", "Arjun Gupta"),
    ("Talos", "AI/ML research platform", "Neha Kapoor"),
]

DEPARTMENTS = ["Engineering", "Product", "Design", "HR", "Finance", "Operations", "Growth", "Legal"]
ROLES = {
    "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "Architect", "QA Engineer"],
    "Product": ["Product Manager", "Product Analyst", "Product Owner"],
    "Design": ["UI Designer", "UX Designer", "Design Lead"],
    "HR": ["HR Executive", "HR Manager", "Recruiter"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
    "Operations": ["Operations Executive", "Operations Manager"],
    "Growth": ["Growth Manager", "Marketing Executive", "Business Analyst"],
    "Legal": ["Legal Counsel", "Compliance Officer"],
}

FIRST_NAMES = [
    "Amit", "Priya", "Rajesh", "Sneha", "Vikram", "Anita", "Karan", "Deepa", "Rahul", "Meera",
    "Arjun", "Neha", "Sanjay", "Pooja", "Ravi", "Kavita", "Suresh", "Divya", "Manoj", "Anjali",
    "Nikhil", "Swati", "Gaurav", "Nisha", "Rohit", "Shreya", "Aditya", "Tanvi", "Varun", "Isha",
    "Harsh", "Riya", "Akash", "Simran", "Dev", "Kriti", "Yash", "Aisha", "Kunal", "Maya",
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Reddy", "Gupta", "Mehta", "Joshi", "Nair", "Iyer",
    "Desai", "Kapoor", "Verma", "Malhotra", "Chopra", "Bansal", "Agarwal", "Saxena", "Tiwari", "Mishra",
]

FLOORS = [1, 2, 3, 4, 5]
ZONES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
BAYS = ["1", "2", "3", "4", "5", "6"]


def seed_projects(db: Session) -> list[Project]:
    projects = []
    for name, desc, manager in PROJECTS:
        project = Project(
            name=name,
            description=desc,
            manager_name=manager,
            status=ProjectStatus.ACTIVE,
        )
        db.add(project)
        projects.append(project)
    db.commit()
    for p in projects:
        db.refresh(p)
    return projects


def seed_seats(db: Session, total_seats: int = 5600) -> list[Seat]:
    seats = []
    seat_counter = 0
    seats_per_floor = total_seats // len(FLOORS)

    for floor in FLOORS:
        floor_seats = seats_per_floor + (total_seats % len(FLOORS) if floor == FLOORS[-1] else 0)
        zone_index = 0
        for i in range(floor_seats):
            zone = ZONES[zone_index % len(ZONES)]
            bay = BAYS[i % len(BAYS)]
            seat_num = f"{zone}{bay}-{floor}{(i % 50) + 1:02d}"
            seat = Seat(
                floor=floor,
                zone=zone,
                bay=bay,
                seat_number=seat_num,
                status=SeatStatus.AVAILABLE,
            )
            db.add(seat)
            seats.append(seat)
            seat_counter += 1
            if (i + 1) % (floor_seats // len(ZONES)) == 0:
                zone_index += 1

    db.commit()
    for s in seats:
        db.refresh(s)
    return seats


def seed_employees(db: Session, projects: list[Project], count: int = 5000) -> list[Employee]:
    employees = []
    used_emails = set()
    used_codes = set()

    for i in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        base_email = f"{first.lower()}.{last.lower()}{i}@ethara.ai"
        email = base_email
        counter = 0
        while email in used_emails:
            counter += 1
            email = f"{first.lower()}.{last.lower()}{i}_{counter}@ethara.ai"
        used_emails.add(email)

        code = f"ETH{10000 + i}"
        while code in used_codes:
            code = f"ETH{10000 + i + random.randint(1, 9999)}"
        used_codes.add(code)

        dept = random.choice(DEPARTMENTS)
        role = random.choice(ROLES[dept])
        joining_date = date.today() - timedelta(days=random.randint(30, 2000))
        project = random.choice(projects)

        employee = Employee(
            employee_code=code,
            name=name,
            email=email,
            department=dept,
            role=role,
            joining_date=joining_date,
            status=EmploymentStatus.ACTIVE,
            project_id=project.id,
        )
        db.add(employee)
        employees.append(employee)

    db.commit()
    for e in employees:
        db.refresh(e)
    return employees


def allocate_seats(
    db: Session,
    employees: list[Employee],
    seats: list[Seat],
    pending_count: int = 50,
    reserved_count: int = 100,
    available_count: int = 500,
):
    # Mark pending employees (no seat)
    pending_employees = random.sample(employees, pending_count)
    for emp in pending_employees:
        emp.status = EmploymentStatus.PENDING_ALLOCATION

    allocatable_employees = [e for e in employees if e not in pending_employees]
    allocatable_seats = [s for s in seats if s.status == SeatStatus.AVAILABLE]

    # Reserve seats
    reserved_seats = random.sample(allocatable_seats, reserved_count)
    for seat in reserved_seats:
        seat.status = SeatStatus.RESERVED
    allocatable_seats = [s for s in allocatable_seats if s not in reserved_seats]

    # Maintenance seats (small number)
    maintenance_count = 20
    maintenance_seats = random.sample(allocatable_seats, maintenance_count)
    for seat in maintenance_seats:
        seat.status = SeatStatus.MAINTENANCE
    allocatable_seats = [s for s in allocatable_seats if s not in maintenance_seats]

    # Keep available seats
    seats_to_allocate_count = len(allocatable_employees)
    seats_needed = seats_to_allocate_count + available_count
    if len(allocatable_seats) < seats_needed:
        raise ValueError(f"Not enough seats: need {seats_needed}, have {len(allocatable_seats)}")

    seats_for_allocation = allocatable_seats[:seats_to_allocate_count]
    remaining_available = allocatable_seats[seats_to_allocate_count:seats_to_allocate_count + available_count]

    # Group employees by project for proximity allocation
    project_groups: dict[int, list[Employee]] = {}
    for emp in allocatable_employees:
        pid = emp.project_id or 0
        project_groups.setdefault(pid, []).append(emp)

    allocated_seat_ids = set()
    for project_id, group_employees in project_groups.items():
        # Prefer seats on same floor for project teams
        preferred_floor = random.choice(FLOORS)
        project_seats = [
            s for s in seats_for_allocation
            if s.id not in allocated_seat_ids and s.floor == preferred_floor
        ]
        if len(project_seats) < len(group_employees):
            project_seats = [s for s in seats_for_allocation if s.id not in allocated_seat_ids]

        random.shuffle(project_seats)
        for emp, seat in zip(group_employees, project_seats):
            allocation = SeatAllocation(
                employee_id=emp.id,
                seat_id=seat.id,
                project_id=emp.project_id,
                allocation_status=AllocationStatus.ACTIVE,
                allocation_date=emp.joining_date,
            )
            seat.status = SeatStatus.OCCUPIED
            db.add(allocation)
            allocated_seat_ids.add(seat.id)

    db.commit()
    print(f"Allocated {len(allocated_seat_ids)} seats")
    print(f"Reserved: {reserved_count}, Available target: {available_count}, Pending: {pending_count}")


def main():
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding projects...")
        projects = seed_projects(db)
        print(f"  Created {len(projects)} projects")

        print("Seeding seats...")
        seats = seed_seats(db, total_seats=5600)
        print(f"  Created {len(seats)} seats")

        print("Seeding employees...")
        employees = seed_employees(db, projects, count=5000)
        print(f"  Created {len(employees)} employees")

        print("Allocating seats...")
        allocate_seats(db, employees, seats)

        # Verify counts
        from sqlalchemy import func
        from app.models import Seat, Employee, EmploymentStatus

        total_seats = db.query(func.count(Seat.id)).scalar()
        available = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.AVAILABLE).scalar()
        occupied = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.OCCUPIED).scalar()
        reserved = db.query(func.count(Seat.id)).filter(Seat.status == SeatStatus.RESERVED).scalar()
        pending = db.query(func.count(Employee.id)).filter(Employee.status == EmploymentStatus.PENDING_ALLOCATION).scalar()

        print("\n=== Seed Summary ===")
        print(f"Projects: {len(projects)}")
        print(f"Employees: {len(employees)}")
        print(f"Total seats: {total_seats}")
        print(f"Occupied: {occupied}")
        print(f"Available: {available}")
        print(f"Reserved: {reserved}")
        print(f"Pending allocation: {pending}")
        print("\nSeed completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
