import os
from sqlmodel import create_engine, SQLModel, Session

# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

SQL_ECHO = os.environ.get("SQL_ECHO", "false").lower() in ("1", "true", "yes")
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)

# NOTE: MP. This is kept for other potential uses but get_db() will
# use sqlmodel.Session directly
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------------------------------------------------------
# Database Session Management
# -----------------------------------------------------------------------------

# NOTE: MP. Using with statement also ensures the session is automatically
# closed, making the `try...finally` block unnecessary and the code cleaner.
def get_db():
    with Session(engine) as session:
        yield session

# NOTE: MP. other Pyton synax of the same function
# def get_db():
    # db = Session()
    # try:
    #     yield db
    # finally:
    #     db.close()
