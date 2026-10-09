from typing import List

from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.modules.bookings.schemas import BookingMiniResponse


class ConsultationResponse(BaseModel):
    id: UUID
    booking_id: UUID
    patient_id: UUID
    doctor_id: UUID
    status: str
    # slot_id: UUID | None = None
    booking: BookingMiniResponse

    model_config = ConfigDict(from_attributes=True)


class ConsultationStatusUpdate(BaseModel):
    status: str  # completed | cancelled


class ConsultationSearchResponse(BaseModel):
    items: List[ConsultationResponse]
    total: int
    page: int
    limit: int


@classmethod
def from_orm_with_slot(cls, consultation):
    return cls(
        id=consultation.id,
        booking_id=consultation.booking_id,
        patient_id=consultation.patient_id,
        doctor_id=consultation.doctor_id,
        status=consultation.status,
        slot_id=consultation.booking.slot_id if consultation.booking else None,
    )