import uuid
import enum
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    authorized = "authorized"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"


class Payment(Base, BaseModelMixin):
    __tablename__ = "payments"

    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False
    )

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.pending,
        nullable=False,
        index=True,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True
    )

    consultation = relationship("Consultation")
