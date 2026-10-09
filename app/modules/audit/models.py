from sqlalchemy import Column, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base
from app.db.models.base_model import BaseModelMixin


class AuditLog(Base, BaseModelMixin):
    __tablename__ = "audit_logs"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action = Column(
        String,
        nullable=False,
        index=True
    )  # LOGIN, BOOKING_CREATED, PAYMENT_REFUNDED

    entity_type = Column(
        String,
        nullable=True,
        index=True
    )

    entity_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )

    event_data = Column(
        JSONB,
        nullable=True
    )

    ip_address = Column(
        String,
        nullable=True
    )

    user_agent = Column(
        String,
        nullable=True
    )

    request_id = Column(
        String,
        nullable=True
    )

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_created_at", "created_at"),
    )