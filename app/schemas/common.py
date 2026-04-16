from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

AttendanceAction = Literal["school_in", "school_out", "class_in", "class_out"]


class MessageResponse(BaseModel):
    success: bool = True
    message: str


class Pagination(BaseModel):
    total_count: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
    next_offset: int | None
    prev_offset: int | None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class TimestampedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
