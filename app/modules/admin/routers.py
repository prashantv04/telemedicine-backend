from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.modules.users.models import User
from app.modules.consultations.models import Consultation
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.auth.dependencies import get_current_user

from app.modules.admin.schemas import AdminAnalyticsResponse


router = APIRouter(
    prefix="/admin", tags=["Admin"]
)


@router.get(
    "/analytics",
    response_model=AdminAnalyticsResponse,
    status_code=status.HTTP_200_OK
)
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin analytics dashboard.

    Returns system statistics including:
    - users
    - consultations
    - revenue
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    total_users = db.query(func.count(User.id)).scalar() or 0

    total_doctors = (
        db.query(func.count(User.id))
        .filter(User.role == "doctor")
        .scalar()
        or 0
    )

    total_patients = (
        db.query(func.count(User.id))
        .filter(User.role == "patient")
        .scalar()
        or 0
    )

    total_consultations = (
        db.query(func.count(Consultation.id)).scalar()
        or 0
    )

    completed_consultations = (
        db.query(func.count(Consultation.id))
        .filter(Consultation.status == "completed")
        .scalar()
        or 0
    )

    # Only successful payments count as revenue
    total_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.status == PaymentStatus.succeeded)
        .scalar()
        or 0
    )

    return {
        "users": total_users,
        "doctors": total_doctors,
        "patients": total_patients,
        "consultations": total_consultations,
        "completed_consultations": completed_consultations,
        "total_revenue": float(total_revenue),
    }