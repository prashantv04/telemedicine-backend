import uuid
from fastapi import HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.consultations.models import Consultation
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.users.models import User


class PaymentService:

    @staticmethod
    def create_payment(
        db: Session,
        *,
        patient_id: uuid.UUID,
        data
    ):
        """
        Idempotent payment creation with proper business validation.
        """

        # Idempotency check
        existing = db.query(Payment).filter(
            Payment.idempotency_key == data.idempotency_key
        ).first()

        if existing:
            return existing

        # Validate consultation ownership
        consultation = db.query(Consultation).filter(
            Consultation.id == data.consultation_id,
            Consultation.patient_id == patient_id
        ).first()

        if not consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found"
            )

        # Check if already paid
        already_paid = db.query(Payment).filter(
            Payment.consultation_id == data.consultation_id,
            Payment.status == PaymentStatus.succeeded
        ).first()

        if already_paid:
            raise HTTPException(
                status_code=400,
                detail="Consultation already paid"
            )

        # Create new payment attempt
        payment = Payment(
            consultation_id=data.consultation_id,
            patient_id=patient_id,
            amount=data.amount,
            currency=data.currency,
            status=PaymentStatus.pending,
            idempotency_key=data.idempotency_key,
            provider_reference = str(uuid.uuid4())
        )

        db.add(payment)

        try:
            db.commit()
            db.refresh(payment)
            return payment

        except IntegrityError:
            db.rollback()

            # Handle idempotency race condition
            existing = db.query(Payment).filter(
                Payment.idempotency_key == data.idempotency_key
            ).first()

            if existing:
                return existing

            raise HTTPException(
                status_code=409,
                detail="Payment conflict occurred"
            )

    @staticmethod
    def update_status_from_webhook(
            db: Session,
            *,
            provider_reference: str,
            new_status: PaymentStatus
    ):

        payment = db.query(Payment).filter(
            Payment.provider_reference == provider_reference
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        valid_transitions = {
            PaymentStatus.pending: [
                PaymentStatus.authorized,
                PaymentStatus.failed
            ],
            PaymentStatus.authorized: [
                PaymentStatus.succeeded,
                PaymentStatus.failed
            ],
            PaymentStatus.succeeded: [
                PaymentStatus.refunded
            ]
        }

        if new_status not in valid_transitions.get(payment.status, []):
            raise HTTPException(
                status_code=400,
                detail="Invalid payment state transition"
            )

        payment.status = new_status
        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def refund_payment(
        db: Session,
        *,
        payment_id: uuid.UUID,
        current_user: User
    ):
        payment = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        # ADMIN CHECK
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admin can refund payments"
            )

        # Only succeeded payments can be refunded
        if payment.status != PaymentStatus.succeeded:
            raise HTTPException(
                status_code=400,
                detail="Only succeeded payments can be refunded"
            )

        payment.status = PaymentStatus.refunded
        db.commit()
        db.refresh(payment)

        return payment