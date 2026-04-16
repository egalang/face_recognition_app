import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def ensure_storage_dirs() -> None:
    settings.face_images_path.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile, subdir: str = "faces") -> str:
    ensure_storage_dirs()
    target_dir = settings.storage_path / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "upload.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    destination = target_dir / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await file.close()
    return str(destination)
