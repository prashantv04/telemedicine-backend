import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.retry import retry_with_backoff
from app.modules.consultations.models import Consultation
from app.modules.bookings.models import Booking
from app.modules.availability.models import AvailabilitySlot
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.audit.models import AuditLog
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
        Idempotent payment creation with business validation.
        """

        # --- 1. Idempotency check ---
        existing = db.query(Payment).filter(
            Payment.idempotency_key == data.idempotency_key
        ).first()

        if existing:
            return existing

        # --- 2. Lock consultation ---
        consultation = (
            db.query(Consultation)
            .filter(
                Consultation.id == data.consultation_id,
                Consultation.patient_id == patient_id
            )
            .with_for_update()
            .first()
        )

        if not consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found"
            )

        if consultation.status != "scheduled":
            raise HTTPException(
                status_code=400,
                detail="Payment only allowed for scheduled consultations"
            )

        # --- 3. Prevent duplicate successful payments ---
        already_paid = db.query(Payment).filter(
            Payment.consultation_id == consultation.id,
            Payment.status == PaymentStatus.succeeded
        ).first()

        if already_paid:
            raise HTTPException(
                status_code=400,
                detail="Consultation already paid"
            )

        # --- 4. Create payment attempt ---
        payment = Payment(
            consultation_id=consultation.id,
            patient_id=patient_id,
            amount=data.amount,
            currency=data.currency,
            status=PaymentStatus.pending,
            idempotency_key=data.idempotency_key,
            provider_reference=str(uuid.uuid4())
        )

        db.add(payment)

        try:
            db.commit()
            db.refresh(payment)
            return payment

        except IntegrityError:
            db.rollback()

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
        def _update():

            payment = (
                db.query(Payment)
                .filter(Payment.provider_reference == provider_reference)
                .with_for_update()
                .first()
            )

            if not payment:
                raise HTTPException(
                    status_code=404,
                    detail="Payment not found"
                )

            # Idempotent webhook
            if payment.status == new_status:
                return payment

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

            # --- Update slot state ---
            consultation = db.query(Consultation).filter(
                Consultation.id == payment.consultation_id
            ).first()

            if consultation:

                booking = db.query(Booking).filter(
                    Booking.id == consultation.booking_id
                ).first()

                if booking:

                    slot = db.query(AvailabilitySlot).filter(
                        AvailabilitySlot.id == booking.slot_id
                    ).first()

                    if slot:

                        if new_status == PaymentStatus.succeeded:
                            slot.status = "booked"

                        if new_status == PaymentStatus.failed:
                            slot.status = "available"
                            slot.reserved_until = None

            # --- Audit log ---
            audit = AuditLog(
                user_id=payment.patient_id,
                action="PAYMENT_STATUS_UPDATED",
                entity_type="payment",
                entity_id=str(payment.id),
                event_data=f"new_status={new_status}"
            )

            db.add(audit)

            db.commit()
            db.refresh(payment)

            return payment

        return retry_with_backoff(_update)

    @staticmethod
    def refund_payment(
        db: Session,
        *,
        payment_id: uuid.UUID,
        current_user: User
    ):
        payment = db.query(Payment).filter(
            Payment.patient_id == payment_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        if payment.status != "succeeded":
            raise HTTPException(status_code=400, detail="Only succeeded payments can be refunded")

        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admin can refund payments"
            )

        if payment.status != PaymentStatus.succeeded:
            raise HTTPException(
                status_code=400,
                detail="Only succeeded payments can be refunded"
            )

        payment.status = PaymentStatus.refunded

        audit = AuditLog(
            user_id=current_user.id,
            action="PAYMENT_REFUNDED",
            entity_type="payment",
            entity_id=str(payment.id),
            event_data="refund_processed"
        )

        db.add(audit)

        db.commit()
        db.refresh(payment)

        return payment