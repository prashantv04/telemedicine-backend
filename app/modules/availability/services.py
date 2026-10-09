from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone

from .models import AvailabilitySlot, AvailabilityStatus


def check_overlap(db, doctor_id, start_time, end_time):
    overlap_exists = db.query(
        db.query(AvailabilitySlot)
        .filter(
            AvailabilitySlot.doctor_id == doctor_id,
            AvailabilitySlot.start_time < end_time,
            AvailabilitySlot.end_time > start_time,
            AvailabilitySlot.status != AvailabilityStatus.cancelled,
        )
        .exists()
    ).scalar()

    if overlap_exists:
        raise HTTPException(
            status_code=400,
            detail="Availability slot overlaps with existing slot."
        )


def create_availability(db, doctor_id, start_time, end_time):
    if start_time >= end_time:
        raise HTTPException(400, "Start time must be before end time.")

    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise HTTPException(400, "Datetime must be timezone-aware.")

    # Normalize to UTC
    start_time = start_time.astimezone(timezone.utc)
    end_time = end_time.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)

    if start_time < now:
        raise HTTPException(400, "Cannot create slot in the past.")

    check_overlap(db, doctor_id, start_time, end_time)

    slot = AvailabilitySlot(
        doctor_id=doctor_id,
        start_time=start_time,
        end_time=end_time,
        status=AvailabilityStatus.available,
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot

def list_availability(
    db: Session,
    doctor_id: UUID,
    skip: int = 0,
    limit: int = 20,
):
    return (
        db.query(AvailabilitySlot)
        .filter(
            AvailabilitySlot.doctor_id == doctor_id,
            AvailabilitySlot.status != "cancelled",
        )
        .order_by(AvailabilitySlot.start_time)
        .offset(skip)
        .limit(limit)
        .all()
    )