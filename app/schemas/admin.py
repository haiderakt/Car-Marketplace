from typing import Literal

from pydantic import BaseModel, Field


class AdminPasswordUpdate(BaseModel):
    new_password: str = Field(min_length=8)


class AdminRoleUpdate(BaseModel):
    role: Literal["user", "admin"]
