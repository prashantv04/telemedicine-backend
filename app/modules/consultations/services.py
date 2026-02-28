from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from typing import Optional, List
from datetime import datetime
from app.modules.audit.models import AuditLog

from app.modules.consultations.models import Consultation
from app.modules.users.models import User


VALID_TRANSITIONS = {
    "scheduled": ["completed", "cancelled"],
    "completed": [],
    "cancelled": [],
}

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

    # Validate state transition
    allowed = VALID_TRANSITIONS.get(consultation.status, [])

    if new_status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    # RBAC
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


def search_consultations(
    db: Session,
    current_user: User,
    doctor_id: Optional[UUID] = None,
    patient_id: Optional[UUID] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> List[Consultation]:
    """
    Secure consultation search with strict RBAC.

    Role Rules:
    - patient → can ONLY see their own consultations
    - doctor  → can ONLY see their own consultations
    - admin   → can see all + apply filters
    """

    query = db.query(Consultation)

    # BASE ACCESS CONTROL (MANDATORY)
    if current_user.role == "patient":
        query = query.filter(Consultation.patient_id == current_user.id)

    elif current_user.role == "doctor":
        query = query.filter(Consultation.doctor_id == current_user.id)

    elif current_user.role == "admin":
        # Admin has full visibility
        return query.all()

    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    # OPTIONAL FILTERS (SAFE APPLICATION)

    # Only admin can filter arbitrary doctor/patient
    if current_user.role == "admin":
        if doctor_id:
            query = query.filter(Consultation.doctor_id == doctor_id)

        if patient_id:
            query = query.filter(Consultation.patient_id == patient_id)

    # Status filter (allowed for all roles)
    if status:
        query = query.filter(Consultation.status == status)

    # Date range filters
    if date_from:
        query = query.filter(Consultation.created_at >= date_from)

    if date_to:
        query = query.filter(Consultation.created_at <= date_to)

    # Optional ordering (recommended for production)
    query = query.order_by(Consultation.created_at.desc())

    return query.all()
