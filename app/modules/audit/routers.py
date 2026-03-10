from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.modules.audit.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/")
def list_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
