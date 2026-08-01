from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str   # <- faqat KIRISH uchun, oddiy matn holida qabul qilinadi


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    # E'TIBOR: bu yerda "password" YOKI "hashed_password" YO'Q!