from pydantic import BaseModel
from uuid import UUID


class BookingCreate(BaseModel):
    slot_id: UUID


class BookingResponse(BaseModel):
    id: UUID
    slot_id: UUID
    doctor_id: UUID
    status: str  # from Consultation

    class Config:
        from_attributes = True
