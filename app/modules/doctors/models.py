import uuid
from sqlalchemy import String, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class Doctor(Base, BaseModelMixin):
    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    specialization: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    license_number: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True
    )

    years_of_experience: Mapped[int | None] = mapped_column(
        nullable=True
    )

    consultation_fee: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    user = relationship(
        "User",
        backref="doctor_profile",
        uselist=False
    )