from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Pathlib handles Windows backslashes and Linux slashes automatically
DB_PATH = Path("data") / "shadowgram.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False allows FastAPI & background worker threads to write safely
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import backend.models  # Ensures all table schemas register before creation
    Base.metadata.create_all(bind=engine)
    print(f"[*] Successfully initialized SQLite database at: {DB_PATH.resolve()}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()