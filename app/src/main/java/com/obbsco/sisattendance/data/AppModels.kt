package com.obbsco.sisattendance.data

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val login: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String? = null
)

data class WhoAmIResponse(
    val id: Int? = null,
    val name: String? = null,
    val username: String? = null,
    @SerializedName("is_admin") val isAdmin: Boolean = false
)

data class RecognitionResponse(
    val success: Boolean,
    val matched: Boolean? = null,
    @SerializedName("enrollment_id") val enrollmentId: Int? = null,
    @SerializedName("student_name") val studentName: String? = null,
    val confidence: Double? = null,
    @SerializedName("attendance_logged") val attendanceLogged: Boolean? = null,
    val message: String? = null
)

enum class AttendanceAction(val apiValue: String, val label: String) {
    SCHOOL_IN("school_in", "School In"),
    SCHOOL_OUT("school_out", "School Out"),
    CLASS_IN("class_in", "Class In"),
    CLASS_OUT("class_out", "Class Out")
}
