from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Student Face Recognition API"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./data/student_face_api.db"
    storage_dir: str = "./data"

    odoo_base_url: str = "http://localhost:8069"
    odoo_access_token: str = ""
    odoo_timeout_seconds: int = 30
    odoo_student_sync_endpoint: str = "/api/students/enrollments"
    odoo_attendance_log_endpoint: str = "/api/attendance/log"

    recognition_tolerance: float = 0.48
    min_face_count: int = 1
    max_face_count: int = 1
    anti_spoofing_enabled: bool = False

    admin_api_key: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_dir)

    @property
    def face_images_path(self) -> Path:
        return self.storage_path / "faces"


settings = Settings()
