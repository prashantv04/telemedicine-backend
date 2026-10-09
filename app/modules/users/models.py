import uuid
from enum import Enum
from sqlalchemy import String, Boolean, Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class Role(str, Enum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    role: Mapped[Role] = mapped_column(
        SQLAEnum(Role, name="user_role"),
        default=Role.patient,
        nullable=False,
        index=True
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true"
    )