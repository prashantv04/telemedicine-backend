from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# THIS LINE REGISTERS MODELS
from app.modules.users.models import User
