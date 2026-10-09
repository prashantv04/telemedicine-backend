import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin

from enum import Enum

class AvailabilityStatus(str, Enum):
    available = "available"
    booked = "booked"
    cancelled = "cancelled"


class AvailabilitySlot(Base, BaseModelMixin):
    __tablename__ = "availability_slots"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String,
        default=AvailabilityStatus.available,
        nullable=False,
        index=True
    )

    reserved_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    doctor = relationship("User")

    booking = relationship("Booking", uselist=False, overlaps="slot")

    @property
    def is_booked(self) -> bool:
        return self.status == AvailabilityStatus.booked

    __table_args__ = (
        Index("ix_doctor_start_time", "doctor_id", "start_time"),
    )