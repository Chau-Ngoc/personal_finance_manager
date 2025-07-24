from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field
from src.dependencies import session_dep
from src.models.user import User

router = APIRouter()


class BaseUser(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data["email"])


class UserOut(BaseUser):
    id: int


@router.get("/all")
async def get_all(session: session_dep) -> List[UserOut]:
    """Get all users."""
    return session.query(User).all()
