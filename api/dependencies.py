"""
FastAPI dependency injection helpers.

Provides a database session generator for use in route handlers
via FastAPI's Depends() mechanism. This ensures each API request
gets its own database session that is properly closed afterward.
"""

# Import the session factory from our database module
from database.connection import SessionLocal


def get_db():
    """
    Generator function that yields a SQLAlchemy database session.

    This is used as a FastAPI dependency — FastAPI calls this function
    for each request that uses Depends(get_db), providing the route
    handler with a 'db' session parameter.

    The try/finally pattern ensures the session is ALWAYS closed,
    even if the route handler raises an exception.

    Usage in routers:
        @router.get("/")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    # Create a new database session from the session factory
    db = SessionLocal()

    try:
        # Yield the session to the route handler
        # Code execution pauses here until the route handler finishes
        yield db
    finally:
        # After the route handler completes (success or error), close the session
        # This releases the database connection back to the pool
        db.close()
