from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import AttendanceAction
from app.schemas.recognition import PreviewResponse, RecognitionResponse
from app.services.face_service import FaceService
from app.services.storage import save_upload

router = APIRouter(prefix="/recognition", tags=["recognition"])

@router.post("/image")
async def recognize_from_image(
    image: UploadFile = File(...),
    action: AttendanceAction = Form(...),
    auto_log_attendance: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    contents = await image.read()

    print("=== ANDROID UPLOAD DEBUG ===")
    print(f"filename={image.filename}")
    print(f"content_type={image.content_type}")
    print(f"bytes={len(contents)}")
    print(f"sha256={hashlib.sha256(contents).hexdigest()}")

    # save exact received file
    with open("/tmp/debug_upload.jpg", "wb") as f:
        f.write(contents)

    print("Saved to /tmp/debug_upload.jpg")
    print("============================")

    # continue normal flow
    from io import BytesIO
    image.file = BytesIO(contents)  # restore stream

    file_path = await save_upload(image, subdir="recognition")
    payload = FaceService(db).recognize_and_optionally_log(
        file_path, action, auto_log_attendance
    )
    return RecognitionResponse(**payload)
# @router.post("/image", response_model=RecognitionResponse)
# async def recognize_from_image(
#     image: UploadFile = File(...),
#     action: AttendanceAction = Form(...),
#     auto_log_attendance: bool = Form(default=False),
#     db: Session = Depends(get_db),
# ):
#     file_path = await save_upload(image, subdir="recognition")
#     payload = FaceService(db).recognize_and_optionally_log(file_path, action, auto_log_attendance)
#     return RecognitionResponse(**payload)


@router.post("/video")
async def recognize_from_video():
    return {
        "success": False,
        "message": "Video recognition is reserved for a later phase.",
    }


@router.post("/preview", response_model=PreviewResponse)
async def preview_matches(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = await save_upload(image, subdir="preview")
    matches = FaceService(db).get_best_matches(file_path, top_k=3)
    return PreviewResponse(matches=matches)
