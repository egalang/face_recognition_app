from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    enrollment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    student_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    partner_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    grade_level_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    school_year: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    face_images: Mapped[list["StudentFaceImage"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class StudentFaceImage(Base):
    __tablename__ = "student_face_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("student_enrollments.enrollment_id"), index=True)
    image_type: Mapped[str] = mapped_column(String(50), default="front", nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    encoding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    student: Mapped[StudentEnrollment] = relationship(back_populates="face_images")


class RecognitionLog(Base):
    __tablename__ = "recognition_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    enrollment_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    matched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    anti_spoofing_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    attendance_logged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
