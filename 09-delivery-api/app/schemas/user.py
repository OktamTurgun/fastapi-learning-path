from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class UserRole(str, Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    ADMIN = "admin"


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
    roles: List[RoleRead] = []

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str  # Oddiy parol, hash service/repository qatlamida qilinadi
    role: UserRole = UserRole.CUSTOMER
    admin_secret: Optional[str] = None


class RoleAssignRequest(BaseModel):
    user_id: UUID
    role: UserRole