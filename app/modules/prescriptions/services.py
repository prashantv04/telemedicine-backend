from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.modules.prescriptions.models import Prescription
from app.modules.consultations.models import Consultation
from app.modules.audit.models import AuditLog


def create_prescription(
    db: Session,
    *,
    consultation_id: UUID,
    doctor_id: UUID,
    notes: str
):
    # --- 1. Lock consultation row ---
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .with_for_update()
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    # --- 2. Ensure consultation completed ---
    if consultation.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Prescription allowed only after consultation is completed"
        )

    # --- 3. Doctor ownership check ---
    if consultation.doctor_id != doctor_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to prescribe for this consultation"
        )

    # --- 4. Prevent duplicate prescription ---
    existing = (
        db.query(Prescription)
        .filter(Prescription.consultation_id == consultation.id)
        .first()
    )

    if existing:
        return existing

    # --- 5. Create prescription ---
    prescription = Prescription(
        consultation_id=consultation.id,
        doctor_id=consultation.doctor_id,
        patient_id=consultation.patient_id,
        notes=notes
    )

    db.add(prescription)
    db.flush()

    # --- 6. Audit log ---
    audit = AuditLog(
        user_id=doctor_id,
        action="PRESCRIPTION_CREATED",
        entity_type="prescription",
        entity_id=str(prescription.id),
        event_data=f"consultation_id={consultation.id}"
    )

    db.add(audit)

    db.commit()
    db.refresh(prescription)

    return prescription