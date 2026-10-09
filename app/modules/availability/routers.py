from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from .schemas import AvailabilityCreate, AvailabilityResponse
from .services import create_availability, list_availability
from app.core.logging import logger

router = APIRouter(
    prefix="/availability", tags=["Availability"]
)


@router.post(
    "/",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED
)

def create_slot(
    payload: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Doctor creates an availability slot.
    """

    # Authorization
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create availability"
        )

    # Fast validation (fail early)
    if payload.start_time >= payload.end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )

    logger.info(f"Doctor {current_user.id} creating slot")

    slot = create_availability(
        db=db,
        doctor_id=current_user.id,
        start_time=payload.start_time,
        end_time=payload.end_time
    )

    return slot


@router.get(
    "/doctor/{doctor_id}",
    response_model=List[AvailabilityResponse],
    status_code=200
)
def get_doctor_availability(
    doctor_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List availability slots for a doctor.
    """

    return list_availability(
        db=db,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit
    )