from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from app.modules.consultations.schemas import (
    ConsultationResponse,
    ConsultationStatusUpdate, ConsultationSearchResponse
)

from app.modules.consultations.services import (
    get_user_consultations,
    update_consultation_status,
    search_consultations
)


router = APIRouter(
    prefix="/consultations", tags=["Consultations"]
)


@router.get(
    "/my",
    response_model=List[ConsultationResponse],
    status_code=200
)
def get_my_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get consultations for the current user.

    - Patient → their consultations
    - Doctor → consultations they conduct
    """
    return get_user_consultations(
        db=db,
        user_id=current_user.id,
        role=current_user.role
    )


@router.patch(
    "/{consultation_id}/status",
    response_model=ConsultationResponse,
    status_code=200
)
def change_status(
    consultation_id: UUID,
    payload: ConsultationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update consultation status.

    Allowed transitions:
    scheduled → completed
    scheduled → cancelled
    """

    consultation = update_consultation_status(
        db=db,
        consultation_id=consultation_id,
        new_status=payload.status,
        user_id=current_user.id,
        role=current_user.role
    )

    return ConsultationResponse.from_orm_with_slot(consultation)




@router.get(
    "/search",
    response_model=ConsultationSearchResponse,
    status_code=200
)
def search_consultations_endpoint(
    doctor_id: Optional[UUID] = None,
    patient_id: Optional[UUID] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search consultations with filters.

    RBAC rules:
    - Patient → only their consultations
    - Doctor → only their consultations
    - Admin → full search access
    """

    return search_consultations(
        db=db,
        current_user=current_user,
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )