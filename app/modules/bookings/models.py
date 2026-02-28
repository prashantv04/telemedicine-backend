from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    patient_id = Column(
        UUID(as_uuid=True), 
        nullable=False
    )

    doctor_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    slot_id = Column(
        UUID(as_uuid=True), 
        nullable=False
    )

    consultation_id = Column(
        UUID(as_uuid=True), 
        nullable=False
    )
    
    idempotency_key = Column(
        String, unique=True, 
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("slot_id", name="uq_booking_slot"),
    )
