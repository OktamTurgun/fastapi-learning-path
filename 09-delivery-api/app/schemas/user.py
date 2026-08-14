from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime
    roles: List[RoleRead]  # User bilan bog'liq rollar ro'yxati

    class Config:
        from_attributes = True  # SQLAlchemy obyektidan to'g'ridan-to'g'ri o'qish uchun

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str  # Oddiy parol, hash service/repository qatlamida qilinadi