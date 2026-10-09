from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DoctorResponse(UserResponse):
    # Extend UserResponse if you want doctor-specific fields
    specialization: str | None = None
    consultation_fee: float | None = None