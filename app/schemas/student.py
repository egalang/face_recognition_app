from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Pagination


class StudentBase(BaseModel):
    enrollment_id: int
    student_name: str
    student_number: str | None = None
    partner_id: int | None = None
    section_name: str | None = None
    grade_level_name: str | None = None
    school_year: str | None = None
    is_active: bool = True


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    synced_at: datetime
    face_image_count: int = 0
    has_face_data: bool = False


class StudentListResponse(BaseModel):
    success: bool = True
    pagination: Pagination
    data: list[StudentResponse]


class SingleStudentResponse(BaseModel):
    success: bool = True
    data: StudentResponse


class SyncStudentsResponse(BaseModel):
    success: bool = True
    synced_count: int
    skipped_count: int = 0


class FaceDeleteResponse(BaseModel):
    success: bool = True
    enrollment_id: int
    deleted_images: int
