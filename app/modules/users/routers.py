from fastapi import APIRouter, Depends
from app.modules.users.models import User
from app.modules.auth.dependencies import get_current_user
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "mfa_enabled": current_user.mfa_enabled,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.get("/doctors")
def list_doctors(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "doctor").all()
