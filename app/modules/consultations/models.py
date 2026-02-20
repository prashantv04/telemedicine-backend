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
        nullable=False   
    ) # scheduled | completed | cancelled
   
    status = Column(
        String, default="scheduled", 
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_consultation_status", "status"),
    )
