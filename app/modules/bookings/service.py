from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID

from app.modules.bookings.models import Booking
from app.modules.availability.models import AvailabilitySlot
from app.modules.consultations.models import Consultation
from app.modules.audit.models import AuditLog


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

    try:

        # --- 1. Check idempotency ---
        existing = (
            db.query(Booking)
            .filter(Booking.idempotency_key == idempotency_key)
            .first()
        )

        if existing:
            return existing, False

        # --- 2. Lock Slot Row (CRITICAL) ---
        slot = (
            db.query(AvailabilitySlot)
            .filter(AvailabilitySlot.id == slot_id)
            .with_for_update()  # row-level lock
            .first()
        )

        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")

        if slot.is_booked:
            raise HTTPException(status_code=409, detail="Slot already booked")

        # --- 3. Create Consultation ---
        consultation = Consultation(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            status="scheduled"
        )
        db.add(consultation)
        db.flush()  # generate consultation.id

        # --- 4. Create Booking (Idempotency Tracker) ---
        booking = Booking(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            consultation_id=consultation.id,
            idempotency_key=idempotency_key
        )
        db.add(booking)

        # --- 5. Mark Slot Booked ---
        slot.is_booked = True

        # --- 6. Audit Log ---
        audit = AuditLog(
            user_id=patient_id,
            action="BOOKING_CREATED",
            entity_type="consultation",
            entity_id=str(consultation.id),
            event_data=f"slot_id={slot.id}"
        )
        db.add(audit)

        # --- 7. Commit (Single Atomic Commit) ---
        db.commit()
        db.refresh(booking)

        return booking, True

    except IntegrityError:
        db.rollback()

        # Handle race condition on idempotency key
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