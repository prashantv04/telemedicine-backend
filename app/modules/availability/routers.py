from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from .schemas import AvailabilityCreate, AvailabilityResponse
from .service import create_availability, list_availability

router = APIRouter(prefix="/availability", tags=["Availability"])


@router.post("/", response_model=AvailabilityResponse)
def create_slot(
    payload: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise Exception("Only doctors can create availability.")

    return create_availability(
        db,
        doctor_id=current_user.id,
        start_time=payload.start_time,
        end_time=payload.end_time
    )


@router.get("/doctor/{doctor_id}", response_model=list[AvailabilityResponse])
def get_doctor_availability(
    doctor_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    return list_availability(
        db,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit
    )
