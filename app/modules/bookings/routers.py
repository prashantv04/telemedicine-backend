from fastapi import APIRouter, Depends, Header, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.bookings.services import create_booking
from app.modules.bookings.tasks import send_booking_notification
from app.modules.consultations.models import Consultation


router = APIRouter(
    prefix="/bookings", tags=["Bookings"]
)


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def book_slot(
    payload: BookingCreate,
    response: Response,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Book an availability slot.

    Features:
    - Idempotent booking
    - Slot locking
    - Background notification
    """

    # RBAC
    if current_user.role != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can book consultations"
        )

    booking, created = create_booking(
        db=db,
        patient_id=current_user.id,
        slot_id=payload.slot_id,
        idempotency_key=idempotency_key
    )

    # Fetch consultation
    consultation = db.query(Consultation).filter(
        Consultation.booking_id == booking.id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=500,
            detail="Consultation creation failed"
        )

    # Only send notification for new bookings
    if created:

        background_tasks.add_task(
            send_booking_notification,
            current_user.email,
            str(consultation.id)
        )

    return BookingResponse(
        id=booking.id,
        slot_id=booking.slot_id,
        doctor_id=booking.doctor_id,
        status=consultation.status,
        consultation_id=consultation.id
    )
