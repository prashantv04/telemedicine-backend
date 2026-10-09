from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from .models import Prescription
from .schemas import PrescriptionCreate, PrescriptionResponse
from .services import create_prescription


router = APIRouter(
    prefix="/prescriptions", tags=["Prescriptions"]
)


@router.post(
    "/",
    response_model=PrescriptionResponse,
    status_code=201
)
def write_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # RBAC check
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can write prescriptions"
        )

    return create_prescription(
        db=db,
        consultation_id=payload.consultation_id,
        doctor_id=current_user.id,
        notes=payload.notes,
    )


@router.get(
    "/my",
    response_model=List[PrescriptionResponse]
)
def get_my_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = db.query(Prescription)

    # -------------------------
    # RBAC
    # -------------------------

    if current_user.role == "patient":

        query = query.filter(
            Prescription.patient_id == current_user.id
        )

    elif current_user.role == "doctor":

        query = query.filter(
            Prescription.doctor_id == current_user.id
        )

    elif current_user.role == "admin":

        # Admin sees everything
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized role"
        )

    return (
        query
        .order_by(Prescription.created_at.desc())
        .all()
    )