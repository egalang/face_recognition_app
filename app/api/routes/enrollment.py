from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.enrollment import EnrollmentImageResponse, MultiEnrollmentImageResponse
from app.services.face_service import FaceService
from app.services.storage import save_upload

router = APIRouter(prefix="/enrollment", tags=["enrollment"])


@router.post("/image", response_model=EnrollmentImageResponse)
async def enroll_face_image(
    enrollment_id: int = Form(...),
    student_name: str | None = Form(default=None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = await save_upload(image, subdir="faces")
    stored_images = FaceService(db).enroll_face(enrollment_id, student_name, file_path, image_type="front")
    return EnrollmentImageResponse(
        message="Student face enrolled successfully",
        enrollment_id=enrollment_id,
        stored_images=stored_images,
    )


@router.post("/multi-image", response_model=MultiEnrollmentImageResponse)
async def enroll_face_multi_image(
    enrollment_id: int = Form(...),
    student_name: str | None = Form(default=None),
    front_image: UploadFile = File(...),
    left_image: UploadFile = File(...),
    right_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = FaceService(db)
    stored_images = 0
    for upload, image_type in [
        (front_image, "front"),
        (left_image, "left_side"),
        (right_image, "right_side"),
    ]:
        file_path = await save_upload(upload, subdir="faces")
        stored_images = service.enroll_face(enrollment_id, student_name, file_path, image_type=image_type)

    return MultiEnrollmentImageResponse(
        message="Student face images enrolled successfully",
        enrollment_id=enrollment_id,
        stored_images=stored_images,
    )
