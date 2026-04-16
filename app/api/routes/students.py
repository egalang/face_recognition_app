from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.student import StudentEnrollment
from app.schemas.common import Pagination
from app.schemas.student import FaceDeleteResponse, SingleStudentResponse, StudentListResponse, StudentResponse
from app.services.face_service import FaceService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=StudentListResponse)
def list_students(limit: int = 100, offset: int = 0, search: str | None = None, db: Session = Depends(get_db)):
    query = db.query(StudentEnrollment)
    if search:
        term = f"%{search}%"
        query = query.filter(StudentEnrollment.student_name.ilike(term))

    total_count = query.count()
    rows = query.order_by(StudentEnrollment.student_name.asc()).offset(offset).limit(limit).all()
    data = [
        StudentResponse(
            **{
                "enrollment_id": row.enrollment_id,
                "student_name": row.student_name,
                "student_number": row.student_number,
                "partner_id": row.partner_id,
                "section_name": row.section_name,
                "grade_level_name": row.grade_level_name,
                "school_year": row.school_year,
                "is_active": row.is_active,
                "synced_at": row.synced_at,
                "face_image_count": len(row.face_images),
                "has_face_data": len(row.face_images) > 0,
            }
        )
        for row in rows
    ]
    return StudentListResponse(
        pagination=Pagination(
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_next=(offset + limit) < total_count,
            has_prev=offset > 0,
            next_offset=offset + limit if (offset + limit) < total_count else None,
            prev_offset=max(0, offset - limit) if offset > 0 else None,
        ),
        data=data,
    )


@router.get("/{enrollment_id}", response_model=SingleStudentResponse)
def get_student(enrollment_id: int, db: Session = Depends(get_db)):
    row = db.get(StudentEnrollment, enrollment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return SingleStudentResponse(
        data=StudentResponse(
            enrollment_id=row.enrollment_id,
            student_name=row.student_name,
            student_number=row.student_number,
            partner_id=row.partner_id,
            section_name=row.section_name,
            grade_level_name=row.grade_level_name,
            school_year=row.school_year,
            is_active=row.is_active,
            synced_at=row.synced_at,
            face_image_count=len(row.face_images),
            has_face_data=len(row.face_images) > 0,
        )
    )


@router.delete("/{enrollment_id}/faces", response_model=FaceDeleteResponse)
def delete_student_faces(enrollment_id: int, db: Session = Depends(get_db)):
    row = db.get(StudentEnrollment, enrollment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    deleted_images = FaceService(db).delete_faces(enrollment_id)
    return FaceDeleteResponse(enrollment_id=enrollment_id, deleted_images=deleted_images)
