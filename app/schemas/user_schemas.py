from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from app.utils import UserRoleEnum


class User(BaseModel):
    username: str
    api_key: Optional[str]
    rate_limit: int = 100
    active: bool
    role: UserRoleEnum = UserRoleEnum.user
    created_at: datetime = Field(default_factory=lambda : datetime.now())
    updated_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


class UserUpdate(BaseModel):
    active: Optional[bool]