from pydantic import BaseModel


class EnrollmentImageResponse(BaseModel):
    success: bool = True
    message: str
    enrollment_id: int
    stored_images: int


class MultiEnrollmentImageResponse(BaseModel):
    success: bool = True
    message: str
    enrollment_id: int
    stored_images: int
