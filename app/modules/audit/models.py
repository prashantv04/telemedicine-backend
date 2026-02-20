import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True), 
        nullable=False
    ) # BOOKING_CREATED, LOGIN, etc.

    action = Column(
        String, nullable=False
    ) # booking, consultation, etc.

    entity_type = Column(
        String, nullable=True
    )  

    entity_id = Column(
        String, nullable=True
    )

    event_data = Column(
        Text, nullable=True
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
