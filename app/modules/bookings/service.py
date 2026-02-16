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
    # --- 1. Check idempotency ---
    existing = db.query(Booking).filter(
        Booking.idempotency_key == idempotency_key
    ).first()
    if existing:
        consultation = db.query(Consultation).get(existing.consultation_id)
        return {
            "id": existing.id,
            "slot_id": existing.slot_id,
            "doctor_id": existing.doctor_id,
            "status": consultation.status
        }

    try:
        # --- 2. Lock slot for booking ---
        slot = (
            db.query(AvailabilitySlot)
            .filter(AvailabilitySlot.id == slot_id)
            .with_for_update()
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

        # --- 4. Create Booking (idempotency tracker) ---
        booking = Booking(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            consultation_id=consultation.id,
            idempotency_key=idempotency_key
        )
        db.add(booking)

        # --- 5. Mark slot booked ---
        slot.is_booked = True

        # --- 6. Audit log ---
        audit = AuditLog(
            user_id=patient_id,
            action="BOOKING_CREATED",
            entity_type="consultation",
            entity_id=str(consultation.id),
            event_data=f"slot_id={slot.id}"
        )
        db.add(audit)

        db.commit()
        db.refresh(booking)

        return {
            "id": booking.id,
            "slot_id": booking.slot_id,
            "doctor_id": booking.doctor_id,
            "status": consultation.status
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate booking detected")
