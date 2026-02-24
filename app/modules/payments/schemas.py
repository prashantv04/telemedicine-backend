import uuid
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional
from app.modules.payments.models import PaymentStatus


class PaymentCreate(BaseModel):
    consultation_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    idempotency_key: str


class PaymentResponse(BaseModel):
    id: uuid.UUID
    consultation_id: uuid.UUID
    patient_id: uuid.UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider_reference: Optional[str]

    class Config:
        from_attributes = True


class PaymentWebhookUpdate(BaseModel):
    provider_reference: str
    status: PaymentStatus


class RefundRequest(BaseModel):
    reason: Optional[str] = None