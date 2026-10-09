from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.payments.schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookUpdate
)
from app.modules.payments.services import PaymentService
from app.modules.users.models import User


router = APIRouter(
    prefix="/payments", tags=["Payments"]
)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=201
)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # RBAC: only patients can initiate payments
    if current_user.role != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can create payments"
        )

    return PaymentService.create_payment(
        db=db,
        patient_id=current_user.id,
        data=payload
    )


@router.post(
    "/webhook",
    response_model=PaymentResponse
)
def webhook_update(
    payload: PaymentWebhookUpdate,
    db: Session = Depends(get_db)
):
    """
    Payment provider webhook endpoint.

    NOTE:
    In production this endpoint should verify
    the payment provider signature header.
    """

    payment = PaymentService.update_status_from_webhook(
        db,
        provider_reference=payload.provider_reference,
        new_status=payload.status
    )

    return payment


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentResponse
)
def refund_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Early RBAC validation
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can refund payments"
        )

    return PaymentService.refund_payment(
        db=db,
        payment_id=payment_id,
        current_user=current_user
    )