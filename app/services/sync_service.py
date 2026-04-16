from datetime import datetime

from sqlalchemy.orm import Session

from app.models.student import StudentEnrollment
from app.services.odoo import OdooClient


class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.odoo = OdooClient()

    def sync_students(self, limit: int = 5000, offset: int = 0) -> tuple[int, int]:
        payload = self.odoo.fetch_students(limit=limit, offset=offset)
        students = payload.get("data", [])
        synced_count = 0
        skipped_count = 0

        for item in students:
            enrollment_id = item.get("enrollment_id")
            student_name = item.get("student_name")
            if not enrollment_id or not student_name:
                skipped_count += 1
                continue

            record = self.db.get(StudentEnrollment, enrollment_id)
            if record is None:
                record = StudentEnrollment(enrollment_id=enrollment_id, student_name=student_name)
                self.db.add(record)

            record.student_name = student_name
            record.student_number = item.get("student_number")
            record.partner_id = item.get("partner_id")
            record.section_name = item.get("section_name")
            record.grade_level_name = item.get("grade_level_name")
            record.school_year = item.get("school_year")
            record.is_active = bool(item.get("is_active", True))
            record.synced_at = datetime.utcnow()
            synced_count += 1

        self.db.commit()
        return synced_count, skipped_count
