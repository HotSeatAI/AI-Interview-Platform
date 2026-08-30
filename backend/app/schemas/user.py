from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    profile_completed: bool
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    institute_name: Optional[str] = None
    year_of_passout: Optional[int] = None
    job_domains: Optional[List[str]] = None
    country: Optional[str] = None
    city: Optional[str] = None
    years_of_experience: Optional[float] = None
    terms_accepted: bool
    terms_accepted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class ProfileUpdate(BaseModel):
    """Body for PUT /me/profile. Mandatory fields are required here;
    everything else stays Optional so it can be omitted or blanked."""

    full_name: str = Field(min_length=1)
    gender: str = Field(min_length=1)
    job_domains: List[str] = Field(min_length=1)
    years_of_experience: float = Field(ge=0)

    mobile_number: Optional[str] = None
    institute_name: Optional[str] = None
    year_of_passout: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None

    @field_validator("full_name", "gender")
    @classmethod
    def not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @field_validator("job_domains")
    @classmethod
    def clean_job_domains(cls, value: List[str]) -> List[str]:
        seen = set()
        cleaned = []
        for domain in value:
            stripped = domain.strip()
            if stripped and stripped.lower() not in seen:
                seen.add(stripped.lower())
                cleaned.append(stripped)
        if not cleaned:
            raise ValueError("must include at least one job domain")
        return cleaned


class GoogleLoginRequest(BaseModel):
    id_token: str
    
class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str