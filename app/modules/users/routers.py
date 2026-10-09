from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, DoctorResponse
from app.modules.auth.dependencies import get_current_user
from app.api.deps import get_db


router = APIRouter(
    prefix="/users", tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile.
    """

    return current_user


@router.get(
    "/doctors",
    response_model=List[DoctorResponse],
    status_code=status.HTTP_200_OK
)
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List doctors available on the platform.
    """

    return (
        db.query(User)
        .filter(User.role == "doctor")
        .offset(skip)
        .limit(limit)
        .all()
    )