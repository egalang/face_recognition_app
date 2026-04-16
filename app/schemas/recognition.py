from pydantic import BaseModel


class AntiSpoofingResult(BaseModel):
    passed: bool = True
    confidence: float | None = None


class RecognitionMatch(BaseModel):
    enrollment_id: int
    student_name: str
    confidence: float


class RecognitionResponse(BaseModel):
    success: bool = True
    matched: bool
    enrollment_id: int | None = None
    student_name: str | None = None
    confidence: float | None = None
    anti_spoofing: AntiSpoofingResult
    attendance_logged: bool = False
    message: str | None = None


class PreviewResponse(BaseModel):
    success: bool = True
    matches: list[RecognitionMatch]
