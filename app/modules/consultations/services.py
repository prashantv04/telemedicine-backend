from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from app.modules.audit.models import AuditLog
from app.modules.consultations.models import Consultation
from app.modules.users.models import User
from app.modules.bookings.models import Booking
from app.modules.availability.models import AvailabilitySlot


VALID_TRANSITIONS = {
    "scheduled": ["completed", "cancelled"],
    "completed": [],
    "cancelled": [],
}


def get_user_consultations(db: Session, user_id: UUID, role: str):
    query = db.query(Consultation)

    if role == "patient":
        query = query.filter(Consultation.patient_id == user_id)

    elif role == "doctor":
        query = query.filter(Consultation.doctor_id == user_id)

    else:
        return []

    return query.order_by(Consultation.created_at.desc()).all()


def update_consultation_status(
    db: Session,
    *,
    consultation_id: UUID,
    new_status: str,
    user_id: UUID,
    role: str
):
    # Row lock to avoid concurrent updates
    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .with_for_update()
        .first()
    )

    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # Validate transition
    allowed = VALID_TRANSITIONS.get(consultation.status, [])

    # if new_status not in allowed:
    #     raise HTTPException(status_code=400, detail="Invalid status transition")

    if consultation.status != "scheduled":
        raise HTTPException(
            status_code=400,
            detail=f"Consultation already {consultation.status} and cannot be modified"
        )

    # -------------------------
    # RBAC
    # -------------------------
    if role == "doctor":
        if consultation.doctor_id != user_id:
            raise HTTPException(status_code=403, detail="Not your consultation")

        if new_status != "completed":
            raise HTTPException(
                status_code=400,
                detail="Doctor can only complete consultation"
            )

    if role == "patient":
        if consultation.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Not your consultation")

        if new_status != "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Patient can only cancel consultation"
            )

    # -------------------------
    # Update Status
    # -------------------------
    consultation.status = new_status

    # -------------------------
    # Release Slot If Cancelled
    # -------------------------
    if new_status == "cancelled":

        booking = db.query(Booking).filter(
            Booking.id == consultation.booking_id
        ).first()

        if booking:
            slot = db.query(AvailabilitySlot).filter(
                AvailabilitySlot.id == booking.slot_id
            ).first()

            if slot:
                slot.status = "available"
                slot.reserved_until = None

    # -------------------------
    # Audit Log
    # -------------------------
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
    page: int = 1,
    limit: int = 20,
) -> List[Consultation]:

    query = (
        db.query(Consultation)
        .options(joinedload(Consultation.booking))
    )
    # -------------------------
    # RBAC
    # -------------------------
    if current_user.role == "patient":
        query = query.filter(Consultation.patient_id == current_user.id)

    elif current_user.role == "doctor":
        query = query.filter(Consultation.doctor_id == current_user.id)

    elif current_user.role == "admin":
        pass

    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    # -------------------------
    # Admin Filters
    # -------------------------
    if current_user.role == "admin":

        if doctor_id:
            query = query.filter(Consultation.doctor_id == doctor_id)

        if patient_id:
            query = query.filter(Consultation.patient_id == patient_id)

    # -------------------------
    # Optional Filters
    # -------------------------
    if status:
        query = query.filter(Consultation.status == status)

    if date_from:
        query = query.filter(Consultation.created_at >= date_from)

    if date_to:
        query = query.filter(Consultation.created_at <= date_to)


    total = query.count()
    # -------------------------
    # Ordering
    # -------------------------
    query = query.order_by(Consultation.created_at.desc())

    # -------------------------
    # Pagination
    # -------------------------

    offset = (page - 1) * limit

    items = query.offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }