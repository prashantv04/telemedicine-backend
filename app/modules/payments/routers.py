from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.payments.schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookUpdate
)
from app.modules.payments.service import PaymentService
from app.modules.users.models import User


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/", response_model=PaymentResponse)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return PaymentService.create_payment(
        db,
        patient_id=current_user.id,
        data=payload
    )


@router.post("/webhook", response_model=PaymentResponse)
def webhook_update(
    payload: PaymentWebhookUpdate,
    db: Session = Depends(get_db)
):
    payment = PaymentService.update_status_from_webhook(
        db,
        provider_reference=payload.provider_reference,
        new_status=payload.status
    )
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return PaymentService.refund_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user
    )