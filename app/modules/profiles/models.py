import uuid
from datetime import date
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class Profile(Base, BaseModelMixin):
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    last_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        nullable=True
    )

    user = relationship(
        "User",
        backref="profile",
        uselist=False
    )