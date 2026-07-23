from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    full_name: str
    phone: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class CustomerResponse(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)