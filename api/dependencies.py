"""
FastAPI dependency injection helpers.

Provides a database session generator for use in route handlers
via FastAPI's Depends() mechanism.
"""

from database.connection import SessionLocal


def get_db():
    """
    Yield a SQLAlchemy session and ensure it is closed after the request.

    Usage in routers:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
