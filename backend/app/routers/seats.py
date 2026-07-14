from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Seat, SeatStatus
from app.schemas import (
    PaginatedSeats,
    SeatAllocateRequest,
    SeatCreate,
    SeatReleaseRequest,
    SeatResponse,
)
from app.services.seat_service import allocate_seat, enrich_seat, release_seat

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.post("", response_model=SeatResponse, status_code=201)
def create_seat(payload: SeatCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Seat)
        .filter(
            Seat.floor == payload.floor,
            Seat.zone == payload.zone,
            Seat.seat_number == payload.seat_number,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Seat with this number already exists on the same floor and zone",
        )
    seat = Seat(**payload.model_dump())
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return enrich_seat(db, seat)


@router.get("", response_model=PaginatedSeats)
def list_seats(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    floor: int | None = None,
    zone: str | None = None,
    status: SeatStatus | None = None,
    project_id: int | None = None,
):
    query = db.query(Seat)
    if floor:
        query = query.filter(Seat.floor == floor)
    if zone:
        query = query.filter(Seat.zone.ilike(zone))
    if status:
        query = query.filter(Seat.status == status)

    total = query.count()
    seats = query.order_by(Seat.floor, Seat.zone, Seat.seat_number).offset((page - 1) * page_size).limit(page_size).all()
    items = [enrich_seat(db, s) for s in seats]

    if project_id:
        items = [i for i in items if i.get("allocated_project") and i["allocated_project"].id == project_id]
        total = len(items)

    return PaginatedSeats(total=total, page=page, page_size=page_size, items=items)


@router.get("/available", response_model=list[SeatResponse])
def list_available_seats(
    db: Session = Depends(get_db),
    floor: int | None = None,
    zone: str | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    query = db.query(Seat).filter(Seat.status == SeatStatus.AVAILABLE)
    if floor:
        query = query.filter(Seat.floor == floor)
    if zone:
        query = query.filter(Seat.zone.ilike(zone))
    seats = query.limit(limit).all()
    return [enrich_seat(db, s) for s in seats]


@router.post("/allocate")
def allocate_seat_endpoint(payload: SeatAllocateRequest, db: Session = Depends(get_db)):
    try:
        allocation = allocate_seat(db, payload.employee_id, payload.seat_id, payload.project_id)
        return {
            "message": "Seat allocated successfully",
            "allocation_id": allocation.id,
            "employee_id": allocation.employee_id,
            "seat_id": allocation.seat_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/release")
def release_seat_endpoint(payload: SeatReleaseRequest, db: Session = Depends(get_db)):
    try:
        allocation = release_seat(db, payload.employee_id)
        return {
            "message": "Seat released successfully",
            "allocation_id": allocation.id,
            "employee_id": allocation.employee_id,
            "seat_id": allocation.seat_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
