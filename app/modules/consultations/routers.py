from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from app.modules.consultations.schemas import ConsultationResponse, ConsultationStatusUpdate
from app.modules.consultations.services import get_user_consultations, update_consultation_status

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
