import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_ALLOCATION = "pending_allocation"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class AllocationStatus(str, enum.Enum):
    ACTIVE = "active"
    RELEASED = "released"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    manager_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employees: Mapped[list["Employee"]] = relationship(back_populates="project")
    allocations: Mapped[list["SeatAllocation"]] = relationship(back_populates="project")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project | None] = relationship(back_populates="employees")
    allocations: Mapped[list["SeatAllocation"]] = relationship(back_populates="employee")


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("floor", "zone", "seat_number", name="uq_seat_floor_zone_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    bay: Mapped[str] = mapped_column(String(20), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[SeatStatus] = mapped_column(
        Enum(SeatStatus), default=SeatStatus.AVAILABLE, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    allocations: Mapped[list["SeatAllocation"]] = relationship(back_populates="seat")


class SeatAllocation(Base):
    __tablename__ = "seat_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), nullable=False, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    allocation_status: Mapped[AllocationStatus] = mapped_column(
        Enum(AllocationStatus), default=AllocationStatus.ACTIVE, index=True
    )
    allocation_date: Mapped[date] = mapped_column(Date, nullable=False)
    released_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    employee: Mapped[Employee] = relationship(back_populates="allocations")
    seat: Mapped[Seat] = relationship(back_populates="allocations")
    project: Mapped[Project | None] = relationship(back_populates="allocations")
