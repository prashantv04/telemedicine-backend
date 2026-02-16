from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class AvailabilityCreate(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilityResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    is_booked: bool

    class Config:
        from_attributes = True
