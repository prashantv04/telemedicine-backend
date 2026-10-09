import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class Booking(Base, BaseModelMixin):
    __tablename__ = "bookings"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("availability_slots.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    consultation = relationship(
        "Consultation",
        back_populates="booking",
        uselist=False,
    )

    slot = relationship("AvailabilitySlot")

    __table_args__ = (
        UniqueConstraint("slot_id", name="uq_booking_slot"),
    )