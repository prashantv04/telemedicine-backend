from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ConsultationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    slot_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConsultationStatusUpdate(BaseModel):
    status: str  # completed | cancelled