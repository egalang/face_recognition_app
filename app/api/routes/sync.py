from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.student import SyncStudentsResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def verify_admin_key(x_api_key: str | None = Header(default=None)) -> None:
    if settings.admin_api_key and x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@router.post("/students", response_model=SyncStudentsResponse, dependencies=[Depends(verify_admin_key)])
def sync_students(limit: int = 5000, offset: int = 0, db: Session = Depends(get_db)):
    synced_count, skipped_count = SyncService(db).sync_students(limit=limit, offset=offset)
    return SyncStudentsResponse(synced_count=synced_count, skipped_count=skipped_count)
