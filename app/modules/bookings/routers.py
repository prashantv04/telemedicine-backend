from fastapi import APIRouter, Depends, Header, HTTPException, status, Response
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.bookings.service import create_booking
from app.modules.consultations.models import Consultation

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse)
def book_slot(
    payload: BookingCreate,
    response: Response,
    idempotency_key: str = Header(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book")

    booking, created = create_booking(
        db=db,
        patient_id=current_user.id,
        slot_id=payload.slot_id,
        idempotency_key=idempotency_key
    )

    # Get consultation for status
    consultation = db.query(Consultation).filter(
        Consultation.id == booking.consultation_id
    ).first()

    if created:
        response.status_code = status.HTTP_201_CREATED

    return BookingResponse(
        id=booking.id,
        slot_id=booking.slot_id,
        doctor_id=booking.doctor_id,
        status=consultation.status,
        consultation_id = consultation.id
    )