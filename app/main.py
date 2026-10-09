import json
import time
import uuid
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from app.core.context import request_context
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

    # --- 1. Extract metadata ---
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None

    user_agent = request.headers.get("user-agent")

    request_id = str(uuid.uuid4())

    # 2. Store in context (correct timing)
    request_context.set({
        "ip_address": ip_address,
        "user_agent": user_agent,
        "request_id": request_id,
    })

    # --- 3. Process request ---
    response = await call_next(request)

    # --- 4. Get user_id (optional, only for logging)
    user_id = getattr(request.state, "user_id", None)

    # --- 5. Audit log ---
    if user_id:
        db: Session = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                event_data={
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params)
                },
                ip_address=ip_address,
                user_agent=user_agent,
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




