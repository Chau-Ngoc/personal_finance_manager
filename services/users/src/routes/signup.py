import argon2
from fastapi import APIRouter, HTTPException, status
from personal_finance_manager_shared.loggers.console_logger import ConsoleLogger
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from src.dependencies import session_dep
from src.models.user import User

logger = ConsoleLogger(__name__)
router = APIRouter()


class BaseUser(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data["email"])


class UserCreate(BaseUser):
    password: str = Field(min_length=20)


class UserOut(BaseUser):
    id: int


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_users(user: UserCreate, session: session_dep) -> UserOut:
    """Register a new user."""
    ph = argon2.PasswordHasher(time_cost=5)
    hashed = ph.hash(user.password)

    new_user = User(email=str(user.email), username=user.username, password=hashed)

    try:
        with session.begin():
            session.add(new_user)

        logger.info(f"User {user.username} created successfully.")
    except IntegrityError:
        logger.exception("An error occurred while creating a new user: ")
        raise HTTPException(status_code=400, detail="Email in use!")

    session.refresh(new_user)
    return new_user
