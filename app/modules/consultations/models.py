import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"), 
        nullable=False, 
        index=True
    )

    doctor_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False, 
        index=True
    )

    slot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("availability_slots.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # scheduled | completed | cancelled
    status = Column(
        String,
        default="scheduled",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable = False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable = False
    )

    __table_args__ = (
        Index("idx_consultation_status", "status"),
        Index("unique_active_slot_booking","slot_id", unique=True, postgresql_where=(status != "cancelled")),
    )
