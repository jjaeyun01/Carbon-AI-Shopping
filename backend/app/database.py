from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parent / "data" / "novera.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Incremental schema changes that SQLAlchemy create_all doesn't handle (column additions)."""
    with engine.connect() as conn:
        # Add is_verified to users table for existing DBs
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "is_verified" not in cols:
            # Default existing users to verified=1 so they aren't locked out
            conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 1"))
            conn.commit()
