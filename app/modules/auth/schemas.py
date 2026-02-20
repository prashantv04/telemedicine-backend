from pydantic import BaseModel, EmailStr
from enum import Enum

class Role(str, Enum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
