from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PrescriptionCreate(BaseModel):
    consultation_id: UUID
    notes: str


class PrescriptionResponse(BaseModel):
    id: UUID
    consultation_id: UUID
    doctor_id: UUID
    patient_id: UUID
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True