from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ConsultationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    slot_id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    # class Config:
    #     from_attributes = True


class ConsultationStatusUpdate(BaseModel):
    status: str  # completed | cancelled