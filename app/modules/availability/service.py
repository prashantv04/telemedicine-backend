from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from uuid import UUID

from .models import AvailabilitySlot


def check_overlap(
    db: Session,
    doctor_id: UUID,
    start_time,
    end_time
):
    overlapping = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.doctor_id == doctor_id,
        AvailabilitySlot.start_time < end_time,
        AvailabilitySlot.end_time > start_time
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="Availability slot overlaps with existing slot."
        )


def create_availability(
    db: Session,
    doctor_id: UUID,
    start_time,
    end_time
):
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time."
        )

    check_overlap(db, doctor_id, start_time, end_time)

    slot = AvailabilitySlot(
        doctor_id=doctor_id,
        start_time=start_time,
        end_time=end_time
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return slot


def list_availability(
    db: Session,
    doctor_id: UUID,
    skip: int = 0,
    limit: int = 20
):
    return (
        db.query(AvailabilitySlot)
        .filter(AvailabilitySlot.doctor_id == doctor_id)
        .order_by(AvailabilitySlot.start_time)
        .offset(skip)
        .limit(limit)
        .all()
    )
