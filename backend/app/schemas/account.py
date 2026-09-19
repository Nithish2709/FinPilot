import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    name: str
    account_type: Optional[str] = None
    currency: str = "INR"


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
