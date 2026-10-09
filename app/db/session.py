from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Increase the connection pool to handle high concurrency load tests
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=50,       # Keep 50 connections open in the pool
    max_overflow=100,   # Allow up to 100 extra connections during traffic spikes
    pool_timeout=30     # Maximum time (seconds) a request waits for an available connection
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)