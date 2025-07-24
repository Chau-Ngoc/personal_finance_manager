from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import engine


def get_session():
    with Session(engine) as session:
        yield session


session_dep = Annotated[Session, Depends(get_session)]
