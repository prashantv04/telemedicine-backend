from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from datetime import datetime
from typing import Optional
from fastapi import Query

from app.modules.consultations.schemas import ConsultationResponse, ConsultationStatusUpdate
from app.modules.consultations.services import get_user_consultations, update_consultation_status, search_consultations

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.get("/my", response_model=list[ConsultationResponse])
def get_my_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_consultations(
        db=db,
        user_id=current_user.id,
        role=current_user.role
    )


@router.patch("/{consultation_id}/status", response_model=ConsultationResponse)
def change_status(
    consultation_id: UUID,
    payload: ConsultationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_consultation_status(
        db=db,
        consultation_id=consultation_id,
        new_status=payload.status,
        user_id=current_user.id,
        role=current_user.role
    )


@router.get("/search", response_model=list[ConsultationResponse])
def search(
    doctor_id: Optional[UUID] = None,
    patient_id: Optional[UUID] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_consultations(
        db=db,
        current_user=current_user,
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
