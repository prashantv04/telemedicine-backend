from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
    # class Config:
    #     from_attributes = True


