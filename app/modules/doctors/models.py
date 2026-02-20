import uuid
from sqlalchemy import String, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    specialization: Mapped[str] = mapped_column(
        String, nullable=True
    )

    license_number: Mapped[str] = mapped_column(
        String, unique=True, nullable=True
    )

    years_of_experience: Mapped[int] = mapped_column(
        nullable=True
    )
    
    consultation_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    user = relationship("User", backref="doctor_profile", uselist=False)
