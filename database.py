from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# postgresql url
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/SystemMonitor"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Provides database sessions to apis
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
