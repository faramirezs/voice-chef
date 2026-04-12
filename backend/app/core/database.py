import os
from sqlmodel import create_engine, Session

# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

SQL_ECHO = os.environ.get("SQL_ECHO", "false").lower() in ("1", "true", "yes")
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)

# -----------------------------------------------------------------------------
# Database Session Management
# -----------------------------------------------------------------------------

# NOTE: MP. Using with statement also ensures the session is automatically
# closed, making the `try...finally` block unnecessary and the code cleaner.
def get_session():
    with Session(engine) as session:
        yield session
