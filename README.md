# Student Face Recognition API - Docker Compose Bundle

This is a Docker Compose package for the FastAPI-based student face recognition service.

## Included endpoints

- `POST /api/v1/sync/students`
- `GET /api/v1/students`
- `GET /api/v1/students/{enrollment_id}`
- `DELETE /api/v1/students/{enrollment_id}/faces`
- `POST /api/v1/enrollment/image`
- `POST /api/v1/enrollment/multi-image`
- `POST /api/v1/recognition/image`
- `POST /api/v1/recognition/video` placeholder
- `POST /api/v1/recognition/preview`

## Files in this bundle

- `docker-compose.yml`
- `Dockerfile`
- `.env`
- `.env.example`
- `docker-entrypoint.sh`
- `app/`
- `requirements.txt`

## Before first run

Edit `.env` and set at least:

- `ODOO_BASE_URL`
- `ODOO_ACCESS_TOKEN`
- `ADMIN_API_KEY`

If Odoo is running on your host machine, `http://host.docker.internal:8069` is usually correct on Docker Desktop for Windows.

## Start the service

```bash
docker compose up -d --build
```

## Open the service

- Swagger UI: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

## Example calls

### Sync students from Odoo

```bash
curl -X POST "http://localhost:8001/api/v1/sync/students" \
  -H "X-API-Key: change-me"
```

### List local students

```bash
curl "http://localhost:8001/api/v1/students"
```

### Enroll one face image

```bash
curl -X POST "http://localhost:8001/api/v1/enrollment/image" \
  -F "enrollment_id=10234" \
  -F "image=@/path/to/student.jpg"
```

### Recognition preview

```bash
curl -X POST "http://localhost:8001/api/v1/recognition/preview" \
  -F "image=@/path/to/unknown.jpg"
```

### Recognize and auto-log attendance

```bash
curl -X POST "http://localhost:8001/api/v1/recognition/image" \
  -F "action=school_in" \
  -F "auto_log_attendance=true" \
  -F "image=@/path/to/unknown.jpg"
```

## Notes

- The image recognition library uses `face_recognition`, which depends on `dlib`. The Dockerfile installs native build dependencies needed for a container build.
- Student sync expects your Odoo API endpoint `GET /api/students/enrollments` to exist.
- Auto-log attendance expects your Odoo API endpoint `POST /api/attendance/log` to accept `enrollment_id` and `log_type`.
- The video endpoint is currently a placeholder.

## Common issues

### Could not connect to Odoo

Check:
- `ODOO_BASE_URL`
- `ODOO_ACCESS_TOKEN`
- whether your Odoo instance is reachable from Docker

### Recognition enrollment fails with face count error

This service expects exactly one clear face per enrollment image.

### `class_in` or `class_out` fails when auto-logging

Your Odoo attendance model must accept those `log_type` values.


## Windows note
This bundle stores the SQLite database inside  to avoid bind-mount issues with single-file SQLite mounts on Windows Docker Desktop.


## Notes

- This bundle installs `face_recognition_models` during image build.
- SQLite is stored at `./data/student_face_api.db` via the bind-mounted `./data` folder.
