from pydantic import BaseModel, ConfigDict
from uuid import UUID


class BookingCreate(BaseModel):
    slot_id: UUID


class BookingResponse(BaseModel):
    id: UUID
    slot_id: UUID
    doctor_id: UUID
    status: str  # from Consultation
    consultation_id: UUID

    model_config = ConfigDict(from_attributes=True)
