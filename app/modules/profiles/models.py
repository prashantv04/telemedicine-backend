import uuid
from datetime import date
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

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

    first_name: Mapped[str] = mapped_column(
        String, nullable=True
    )
    
    last_name: Mapped[str] = mapped_column(
        String, nullable=True
    )

    phone: Mapped[str] = mapped_column(
        String, nullable=True
    )

    date_of_birth: Mapped[date] = mapped_column(
        nullable=True
    )

    user = relationship("User", backref="profile", uselist=False)
