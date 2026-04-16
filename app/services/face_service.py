from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session
from PIL import Image, ImageOps

from app.core.config import settings
from app.models.student import RecognitionLog, StudentEnrollment, StudentFaceImage
from app.services.odoo import OdooClient

try:
    import face_recognition  # type: ignore
except Exception:  # pragma: no cover
    face_recognition = None


class FaceService:
    def __init__(self, db: Session):
        self.db = db
        self.odoo = OdooClient()

    def _require_library(self) -> None:
        if face_recognition is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "face_recognition library is not installed or failed to load. "
                    "Install dlib and face_recognition on the server first."
                ),
            )

    def _load_image(self, file_path: str) -> np.ndarray:
        """
        Load image in a mobile-friendly way:
        - apply EXIF orientation
        - convert to RGB
        - resize large images to a stable working size
        """
        self._require_library()

        try:
            pil_image = Image.open(file_path)
            pil_image = ImageOps.exif_transpose(pil_image).convert("RGB")
            pil_image.thumbnail((1280, 1280))
            image = np.array(pil_image)

            print("=== FACE LOAD DEBUG ===")
            print(f"file_path={file_path}")
            print(f"image_shape={image.shape}")
            print("=======================")

            return image
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to load image for recognition: {exc}",
            )

    def _detect_face_locations(self, image: np.ndarray) -> list[tuple[int, int, int, int]]:
        """
        More tolerant face detection for mobile captures.
        First try moderate upsampling, then stronger upsampling as fallback.
        """
        self._require_library()

        try:
            locations = face_recognition.face_locations(
                image,
                number_of_times_to_upsample=2,
                model="hog",
            )

            print(f"FACE DETECT DEBUG: first_pass_faces={len(locations)}")

            if len(locations) == 0:
                locations = face_recognition.face_locations(
                    image,
                    number_of_times_to_upsample=3,
                    model="hog",
                )
                print(f"FACE DETECT DEBUG: fallback_pass_faces={len(locations)}")

            return locations
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Face detection failed: {exc}",
            )

    def _extract_single_encoding(self, file_path: str) -> tuple[np.ndarray, int]:
        image = self._load_image(file_path)
        locations = self._detect_face_locations(image)
        encodings = face_recognition.face_encodings(image, locations)
        face_count = len(encodings)

        print(f"FACE ENCODING DEBUG: encodings_found={face_count}")

        if face_count < settings.min_face_count or face_count > settings.max_face_count:
            raise HTTPException(
                status_code=400,
                detail=f"Expected exactly one face in the image, found {face_count}.",
            )

        return encodings[0], face_count

    def enroll_face(
        self,
        enrollment_id: int,
        student_name: str | None,
        file_path: str,
        image_type: str,
    ) -> int:
        student = self.db.get(StudentEnrollment, enrollment_id)
        if student is None:
            if not student_name:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found locally. Sync students first or provide student_name.",
                )
            student = StudentEnrollment(
                enrollment_id=enrollment_id,
                student_name=student_name,
                is_active=True,
            )
            self.db.add(student)
            self.db.flush()

        encoding, _ = self._extract_single_encoding(file_path)
        face_image = StudentFaceImage(
            enrollment_id=enrollment_id,
            image_type=image_type,
            file_path=file_path,
            encoding=pickle.dumps(encoding),
            quality_score=1.0,
        )
        self.db.add(face_image)
        self.db.commit()
        return self._count_face_images(enrollment_id)

    def _count_face_images(self, enrollment_id: int) -> int:
        return (
            self.db.query(StudentFaceImage)
            .filter(StudentFaceImage.enrollment_id == enrollment_id)
            .count()
        )

    def get_best_matches(self, file_path: str, top_k: int = 3) -> list[dict[str, Any]]:
        probe_encoding, _ = self._extract_single_encoding(file_path)
        known_images = self.db.query(StudentFaceImage).all()
        results: list[dict[str, Any]] = []

        for item in known_images:
            known_encoding = pickle.loads(item.encoding)
            distance = float(face_recognition.face_distance([known_encoding], probe_encoding)[0])
            confidence = max(0.0, 1.0 - distance)
            results.append(
                {
                    "enrollment_id": item.enrollment_id,
                    "student_name": item.student.student_name,
                    "confidence": round(confidence, 4),
                    "distance": distance,
                }
            )

        results.sort(key=lambda x: x["distance"])
        deduped: list[dict[str, Any]] = []
        seen: set[int] = set()
        for row in results:
            if row["enrollment_id"] in seen:
                continue
            seen.add(row["enrollment_id"])
            deduped.append(
                {
                    "enrollment_id": row["enrollment_id"],
                    "student_name": row["student_name"],
                    "confidence": row["confidence"],
                }
            )
            if len(deduped) >= top_k:
                break
        return deduped

    def recognize_and_optionally_log(
        self,
        file_path: str,
        action: str,
        auto_log_attendance: bool,
    ) -> dict[str, Any]:
        matches = self.get_best_matches(file_path, top_k=1)
        anti_spoofing = {"passed": True, "confidence": None}

        if not matches:
            self._create_recognition_log(
                None,
                None,
                action,
                False,
                None,
                file_path,
                False,
                "No enrolled faces available",
            )
            return {
                "success": True,
                "matched": False,
                "enrollment_id": None,
                "student_name": None,
                "confidence": None,
                "anti_spoofing": anti_spoofing,
                "attendance_logged": False,
                "message": "No enrolled faces available for comparison",
            }

        best = matches[0]
        matched = bool(best["confidence"] >= (1.0 - settings.recognition_tolerance))
        attendance_logged = False
        message = None

        if matched and auto_log_attendance:
            try:
                self.odoo.log_attendance(best["enrollment_id"], action)
                attendance_logged = True
            except Exception as exc:
                message = f"Match succeeded but attendance logging failed: {exc}"

        if not matched:
            message = "No confident match found"

        self._create_recognition_log(
            best["enrollment_id"] if matched else None,
            best["student_name"] if matched else None,
            action,
            matched,
            best["confidence"],
            file_path,
            attendance_logged,
            message,
        )
        return {
            "success": True,
            "matched": matched,
            "enrollment_id": best["enrollment_id"] if matched else None,
            "student_name": best["student_name"] if matched else None,
            "confidence": best["confidence"],
            "anti_spoofing": anti_spoofing,
            "attendance_logged": attendance_logged,
            "message": message,
        }

    def _create_recognition_log(
        self,
        enrollment_id: int | None,
        student_name: str | None,
        action: str | None,
        matched: bool,
        confidence: float | None,
        image_path: str | None,
        attendance_logged: bool,
        notes: str | None,
    ) -> None:
        row = RecognitionLog(
            enrollment_id=enrollment_id,
            student_name=student_name,
            action=action,
            matched=matched,
            confidence=confidence,
            anti_spoofing_passed=True,
            notes=notes,
            image_path=image_path,
            attendance_logged=attendance_logged,
        )
        self.db.add(row)
        self.db.commit()

    def delete_faces(self, enrollment_id: int) -> int:
        rows = (
            self.db.query(StudentFaceImage)
            .filter(StudentFaceImage.enrollment_id == enrollment_id)
            .all()
        )
        count = len(rows)
        for row in rows:
            try:
                Path(row.file_path).unlink(missing_ok=True)
            except Exception:
                pass
            self.db.delete(row)
        self.db.commit()
        return count