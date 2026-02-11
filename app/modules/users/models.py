from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String, nullable=False
    )

    role: Mapped[str] = mapped_column(
        String, index=True, nullable=False, default="patient"
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
