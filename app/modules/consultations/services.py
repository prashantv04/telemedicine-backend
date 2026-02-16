from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from .models import Consultation
from app.modules.audit.models import AuditLog


def get_user_consultations(db: Session, user_id: UUID, role: str):
    if role == "patient":
        return db.query(Consultation).filter(
            Consultation.patient_id == user_id
        ).all()

    if role == "doctor":
        return db.query(Consultation).filter(
            Consultation.doctor_id == user_id
        ).all()

    return []


def update_consultation_status(
    db: Session,
    *,
    consultation_id: UUID,
    new_status: str,
    user_id: UUID,
    role: str
):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # RBAC rules
    if role == "doctor":
        if consultation.doctor_id != user_id:
            raise HTTPException(status_code=403, detail="Not your consultation")

        if new_status != "completed":
            raise HTTPException(status_code=400, detail="Doctor can only complete consultation")

    if role == "patient":
        if consultation.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Not your consultation")

        if new_status != "cancelled":
            raise HTTPException(status_code=400, detail="Patient can only cancel consultation")

    consultation.status = new_status

    audit = AuditLog(
        user_id=user_id,
        action="CONSULTATION_STATUS_UPDATED",
        entity_type="consultation",
        entity_id=str(consultation.id),
        event_data=f"new_status={new_status}",
    )

    db.add(audit)
    db.commit()
    db.refresh(consultation)

    return consultation
