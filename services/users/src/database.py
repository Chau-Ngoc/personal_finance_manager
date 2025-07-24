import os

from personal_finance_manager_shared.loggers.console_logger import ConsoleLogger
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class Base(DeclarativeBase):
    pass


logger = ConsoleLogger(__name__)

db_user = os.environ.get("POSTGRES_DB_USER")
db_password = os.environ.get("POSTGRES_DB_PASSWORD")
if os.environ.get("PROD"):
    db_url = os.environ.get("PROD_DB_URL")
else:
    db_url = os.environ.get("DEV_DB_URL")
engine = create_engine(db_url, echo=True, pool_pre_ping=True, connect_args={"connect_timeout": 10})


@retry(
    stop=stop_after_attempt(5),
    reraise=True,
    wait=wait_fixed(2),
    retry=retry_if_exception_type(OperationalError),
    before_sleep=lambda retry_state: logger.warning(
        f"Database connection attempt {retry_state.attempt_number} failed: "
        f"{retry_state.outcome.exception()}. Retrying in {retry_state.next_action.sleep} seconds..."
    ),
)
def create_db_and_tables():
    logger.info("Creating database and tables...")
    Base.metadata.create_all(engine)
    logger.info("Database and tables created successfully.")
