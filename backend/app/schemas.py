from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AllocationStatus, EmploymentStatus, ProjectStatus, SeatStatus


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    manager_name: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmployeeBase(BaseModel):
    employee_code: str
    name: str
    email: EmailStr
    department: str
    role: str
    joining_date: date
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    project_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = None
    joining_date: Optional[date] = None
    status: Optional[EmploymentStatus] = None
    project_id: Optional[int] = None


class ProjectBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SeatBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    floor: int
    zone: str
    bay: str
    seat_number: str
    status: SeatStatus


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectBrief] = None
    active_seat: Optional[SeatBrief] = None


class SeatBase(BaseModel):
    floor: int = Field(ge=1)
    zone: str
    bay: str
    seat_number: str
    status: SeatStatus = SeatStatus.AVAILABLE


class SeatCreate(SeatBase):
    pass


class SeatResponse(SeatBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    allocated_employee: Optional["EmployeeBrief"] = None
    allocated_project: Optional[ProjectBrief] = None


class EmployeeBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    name: str
    email: str


class SeatAllocateRequest(BaseModel):
    employee_id: int
    seat_id: int
    project_id: Optional[int] = None


class SeatReleaseRequest(BaseModel):
    employee_id: int


class SeatSuggestion(BaseModel):
    seat: SeatBrief
    reason: str
    proximity_score: float


class DashboardSummary(BaseModel):
    total_employees: int
    total_seats: int
    occupied_seats: int
    available_seats: int
    reserved_seats: int
    maintenance_seats: int
    pending_allocation: int


class ProjectUtilization(BaseModel):
    project_id: int
    project_name: str
    employee_count: int
    occupied_seats: int


class FloorUtilization(BaseModel):
    floor: int
    total_seats: int
    occupied_seats: int
    available_seats: int
    reserved_seats: int
    occupancy_rate: float


class AIQueryRequest(BaseModel):
    query: str


class AIQueryResponse(BaseModel):
    answer: str
    intent: Optional[str] = None


class PaginatedEmployees(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EmployeeResponse]


class PaginatedSeats(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SeatResponse]
