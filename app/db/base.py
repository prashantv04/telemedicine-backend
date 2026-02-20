from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# THIS LINE REGISTERS MODELS

from app.modules.users.models import User
from app.modules.availability.models import AvailabilitySlot
from app.modules.consultations.models import Consultation
import app.db.models.idempotency_key
from app.modules.bookings.models import Booking
from app.modules.audit.models import AuditLog
from app.modules.doctors.models import Doctor
from app.modules.profiles.models import Profile
from app.modules.payments.models import Payment
