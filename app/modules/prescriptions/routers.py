from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from .models import Prescription
from .schemas import PrescriptionCreate, PrescriptionResponse
from .service import create_prescription

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post("/", response_model=PrescriptionResponse)
def write_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "doctor":
        raise Exception("Only doctors can write prescriptions")

    return create_prescription(
        db=db,
        consultation_id=payload.consultation_id,
        doctor_id=current_user.id,
        notes=payload.notes,
    )


@router.get("/my", response_model=list[PrescriptionResponse])
def get_my_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Patient → see their prescriptions
    if current_user.role == "patient":
        return db.query(Prescription).filter(
            Prescription.patient_id == current_user.id
        ).all()

    # Doctor → see prescriptions they wrote
    if current_user.role == "doctor":
        return db.query(Prescription).filter(
            Prescription.doctor_id == current_user.id
        ).all()

    return []