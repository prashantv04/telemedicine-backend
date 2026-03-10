import json
import time
import uuid
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine
from sqlalchemy.exc import OperationalError

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.modules.audit.models import AuditLog

from app.core.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from prometheus_fastapi_instrumentator import Instrumentator

from app.modules.admin.routers import router as admin_router
from app.modules.audit.routers import router as audit_router
from app.modules.auth.routers import router as auth_router
from app.modules.users.routers import router as users_router
from app.modules.availability.routers import router as availability_router
from app.modules.bookings.routers import router as booking_router
from app.modules.consultations.routers import router as consultations_router
from app.modules.payments.routers import router as payments_router
from app.modules.prescriptions.routers import router as prescription_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -----------------------------
    # Startup logic
    # -----------------------------
    retries = 10

    while retries > 0:
        try:
            print("Waiting for database...")
            Base.metadata.create_all(bind=engine)
            print("Database ready!")
            break
        except OperationalError:
            retries -= 1
            time.sleep(2)

    if retries == 0:
        raise Exception("Database not available")

    yield  # Application runs here

    # -----------------------------
    # Shutdown logic (optional)
    # -----------------------------
    print("Shutting down application...")

app = FastAPI(
    title="Telemedicine Backend",
    lifespan=lifespan
)

# -----------------------------
# Prometheus metrics
# -----------------------------
Instrumentator().instrument(app).expose(app, include_in_schema=False)

# -----------------------------
# Rate limiter
# -----------------------------

# attach limiter
app.state.limiter = limiter

# rate limit handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# middleware
app.add_middleware(SlowAPIMiddleware)

# -----------------------------
# AUDIT LOGGING MIDDLEWARE
# -----------------------------

@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    response = await call_next(request)

    db: Session = SessionLocal()
    try:
        user_id = getattr(request.state, "user_id", None)  # set in JWT auth

        log = AuditLog(
            user_id=user_id or uuid.UUID(int=0),  # if unknown, use null UUID
            action=request.method + " " + request.url.path,  # e.g., "GET /consultations/search"
            entity_type=None,       # optionally fill based on endpoint
            entity_id=None,         # optionally fill based on request body or URL
            event_data=json.dumps({
                "status_code": response.status_code,
                "query_params": dict(request.query_params)
            })
        )

        db.add(log)
        db.commit()
    finally:
        db.close()

    return response

# -----------------------------
# Routers
# -----------------------------
app.include_router(admin_router)
app.include_router(audit_router)
app.include_router(auth_router)
app.include_router(availability_router)
app.include_router(booking_router)
app.include_router(consultations_router)
app.include_router(payments_router)
app.include_router(prescription_router)
app.include_router(users_router)




