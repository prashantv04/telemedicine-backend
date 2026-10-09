import uuid
from sqlalchemy import Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class Prescription(Base, BaseModelMixin):
    __tablename__ = "prescriptions"

    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id"),
        nullable=False,
        unique=True
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("consultation_id", name="uq_prescription_consultation"),
    )