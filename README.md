# OBBServer SIS Attendance Android App

Android Studio project scaffold for facial-recognition attendance integration with:
- Odoo SIS API for login and admin validation
- FastAPI face recognition server for image recognition and attendance logging

## What is included
- Jetpack Compose UI
- Retrofit + OkHttp API layer
- CameraX front-camera capture
- Multipart upload to FastAPI
- Session token storage with DataStore
- Admin gating using `/api/auth/whoami`

## Before opening in Android Studio
1. Copy `local.properties.example` to `local.properties`.
2. Set your Android SDK path.
3. Update:
   - `odoo.baseUrl`
   - `face.baseUrl`
   - `face.adminApiKey`

## Open the project
- Open the unzipped folder in Android Studio.
- Let Gradle sync.
- Run on an emulator or Android device.

## Notes
- This package includes the standard project layout and Gradle files.
- The Gradle wrapper JAR is not bundled in this generated scaffold. Android Studio can still import and sync the project normally, or you can generate the wrapper locally with `gradle wrapper` if you have Gradle installed.
- Cleartext HTTP is enabled because your current Odoo and FastAPI examples use `http://` endpoints.

## Expected flow
1. Admin logs in through Odoo.
2. App validates admin access using `/api/auth/whoami`.
3. User selects attendance action.
4. App captures image from front camera.
5. App uploads image to FastAPI `/api/v1/recognition/image`.
6. FastAPI recognizes face and auto-logs attendance.
7. App shows match result, confidence, and attendance status.
