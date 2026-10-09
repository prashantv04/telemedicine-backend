from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.exc import UnknownHashError

from app.core.rate_limiter import limiter
from app.api.deps import get_db

from app.modules.users.models import User
from app.modules.auth.schemas import SignupRequest, TokenResponse, LoginRequest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth", tags=["Auth"]
)


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/minute")
def signup(
    request: Request,
    data: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user and return access token.
    """

    email = data.email.lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=email,
        password_hash=get_password_hash(data.password),
        role=data.role,
        mfa_enabled=False,
        is_active=True
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {"access_token": token}


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """

    email = payload.email.lower()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    try:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

    except UnknownHashError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {"access_token": token}