from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.modules.users.models import User
from app.modules.consultations.models import Consultation
from app.modules.payments.models import Payment
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import Role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    total_users = db.query(func.count(User.id)).scalar()
    total_doctors = db.query(func.count(User.id)).filter(User.role == "doctor").scalar()
    total_patients = db.query(func.count(User.id)).filter(User.role == "patient").scalar()

    total_consultations = db.query(func.count(Consultation.id)).scalar()
    completed_consultations = (
        db.query(func.count(Consultation.id))
        .filter(Consultation.status == "completed")
        .scalar()
    )

    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0

    return {
        "users": total_users,
        "doctors": total_doctors,
        "patients": total_patients,
        "consultations": total_consultations,
        "completed_consultations": completed_consultations,
        "total_revenue": float(total_revenue),
    }