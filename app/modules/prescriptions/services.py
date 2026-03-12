from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.modules.prescriptions.models import Prescription
from app.modules.consultations.models import Consultation


def create_prescription(
    db: Session,
    *,
    consultation_id: UUID,
    doctor_id: UUID,
    notes: str
):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    if consultation.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Prescription allowed only after consultation is completed"
        )

    if consultation.doctor_id != doctor_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to prescribe for this consultation"
        )

    prescription = Prescription(
        consultation_id=consultation.id,
        doctor_id=consultation.doctor_id,
        patient_id=consultation.patient_id,
        notes=notes
    )

    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    return prescription
