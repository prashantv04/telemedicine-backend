from fastapi import FastAPI
import time
from app.db.base import Base
from app.db.session import engine
from sqlalchemy.exc import OperationalError

from app.modules.admin.routes import router as admin_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.routers import router as auth_router
from app.modules.users.routers import router as users_router
from app.modules.availability.routers import router as availability_router
from app.modules.bookings.routers import router as booking_router
from app.modules.consultations.routers import router as consultations_router
from app.modules.payments.routers import router as payments_router
from app.modules.prescriptions.routers import router as prescription_router


app = FastAPI(title="Telemedicine Backend")


# Create tables on startup
@app.on_event("startup")
def on_startup():
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


app.include_router(admin_router)
app.include_router(audit_router)
app.include_router(auth_router)
app.include_router(availability_router)
app.include_router(booking_router)
app.include_router(consultations_router)
app.include_router(payments_router)
app.include_router(prescription_router)
app.include_router(users_router)




