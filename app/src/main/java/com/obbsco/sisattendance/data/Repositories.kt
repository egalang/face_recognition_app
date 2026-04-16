package com.obbsco.sisattendance.data

import android.util.Log
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.HttpException
import java.io.File

class AuthRepository(
    private val authApi: AuthApi,
    private val sessionManager: SessionManager
) {
    suspend fun loginAndValidate(username: String, password: String): Result<WhoAmIResponse> {
        return try {
            val login = authApi.login(LoginRequest(login = username, password = password))
            sessionManager.saveAccessToken(login.accessToken)

            val whoami = authApi.whoAmI()
            if (!whoami.isAdmin) {
                sessionManager.clear()
                Result.failure(IllegalStateException("Admin access required. This account is not an admin."))
            } else {
                Result.success(whoami)
            }
        } catch (e: Exception) {
            sessionManager.clear()
            Result.failure(e)
        }
    }

    suspend fun validateSession(): Boolean {
        return try {
            val token = sessionManager.getAccessToken()
            if (token.isNullOrBlank()) return false
            val whoami = authApi.whoAmI()
            if (!whoami.isAdmin) {
                sessionManager.clear()
                false
            } else {
                true
            }
        } catch (_: Exception) {
            sessionManager.clear()
            false
        }
    }

    suspend fun logout() {
        sessionManager.clear()
    }
}

class FaceRepository(private val faceApi: FaceApi) {
    suspend fun recognize(file: File, action: AttendanceAction): RecognitionResponse {
        try {
            val bytes = file.readBytes()

            Log.d(
                "SCAN_UPLOAD",
                "Uploading file=${file.absolutePath}, name=${file.name}, size=${bytes.size}"
            )

            val imageBody = bytes.toRequestBody("image/jpeg".toMediaType())
            val imagePart = MultipartBody.Part.createFormData(
                "image",
                file.name,
                imageBody
            )

            val actionPart = MultipartBody.Part.createFormData(
                "action",
                action.apiValue
            )

            val autoLogPart = MultipartBody.Part.createFormData(
                "auto_log_attendance",
                "true"
            )

            return faceApi.recognize(
                image = imagePart,
                action = actionPart,
                autoLogAttendance = autoLogPart
            )
        } catch (e: HttpException) {
            val errorBody = e.response()?.errorBody()?.string()
            throw IllegalStateException(
                buildString {
                    append("FastAPI scan failed: HTTP ${e.code()}")
                    if (!errorBody.isNullOrBlank()) {
                        append("\n")
                        append(errorBody)
                    }
                }
            )
        } catch (e: Exception) {
            throw IllegalStateException("FastAPI scan failed: ${e.message}", e)
        }
    }
}