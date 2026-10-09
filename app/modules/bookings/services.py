from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timedelta

from app.core.context import request_context
from app.core.metrics import booking_created_total
from app.modules.bookings.models import Booking
from app.modules.availability.models import AvailabilitySlot
from app.modules.consultations.models import Consultation
from app.modules.audit.models import AuditLog


RESERVATION_WINDOW_MINUTES = 5


def create_booking(
    db: Session,
    *,
    patient_id: UUID,
    slot_id: UUID,
    idempotency_key: str
):
    """
    Production-grade booking creation:
    - Idempotent
    - Concurrency safe
    - Fully atomic
    - Audit logged
    """
    ctx = request_context.get()
    try:

        # --- 1. Idempotency Check ---
        existing = (
            db.query(Booking)
            .filter(Booking.idempotency_key == idempotency_key)
            .first()
        )

        if existing:
            return existing, False

        # --- 2. Lock Slot Row ---
        slot = (
            db.query(AvailabilitySlot)
            .filter(AvailabilitySlot.id == slot_id)
            .with_for_update()
            .first()
        )

        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")

        now = datetime.utcnow()

        # --- 3. Check Slot State ---
        if slot.status == "booked":
            raise HTTPException(status_code=409, detail="Slot already booked")

        if slot.status == "reserved" and slot.reserved_until and slot.reserved_until > now:
            raise HTTPException(status_code=409, detail="Slot temporarily reserved")

        # --- 4. Reserve Slot ---
        slot.status = "reserved"
        slot.reserved_until = now + timedelta(minutes=RESERVATION_WINDOW_MINUTES)

        # --- 5. Create Booking ---
        booking = Booking(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            idempotency_key=idempotency_key
        )

        db.add(booking)
        db.flush()  # generate booking.id

        # --- 6. Create Consultation ---
        consultation = Consultation(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            booking_id=booking.id,
            status="scheduled"
        )

        db.add(consultation)
        db.flush() # generates consultation.id

        # --- 7. Mark Slot Booked ---
        slot.status = "booked"
        slot.reserved_until = None

        # --- 8. Audit Log ---
        audit = AuditLog(
            user_id=patient_id,
            action="BOOKING_CREATED",
            entity_type="consultation",
            entity_id=consultation.id,
            ip_address=ctx.get("ip_address"),
            user_agent=ctx.get("user_agent"),
            request_id=ctx.get("request_id"),
            event_data={
                "slot_id": str(slot.id),
                "booking_id": str(booking.id)
            }
        )

        db.add(audit)

        # --- 9. Commit ---
        db.commit()
        db.refresh(booking)
        print("Incrementing booking metric")
        booking_created_total.inc()
        return booking, True

    except IntegrityError:
        db.rollback()

        existing = (
            db.query(Booking)
            .filter(Booking.idempotency_key == idempotency_key)
            .first()
        )

        if existing:
            return existing, False

        raise HTTPException(status_code=409, detail="Slot already booked")

    except Exception:
        db.rollback()
        raise