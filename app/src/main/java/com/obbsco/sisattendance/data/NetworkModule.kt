package com.obbsco.sisattendance.data

import com.obbsco.sisattendance.BuildConfig
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

private fun String.ensureTrailingSlash(): String = if (endsWith('/')) this else "$this/"

interface AuthApi {
    @POST("api/auth/login")
    suspend fun login(@Body body: LoginRequest): LoginResponse

    @GET("api/auth/whoami")
    suspend fun whoAmI(): WhoAmIResponse
}

interface FaceApi {
    @Multipart
    @POST("api/v1/recognition/image")
    suspend fun recognize(
        @Part image: MultipartBody.Part,
        @Part action: MultipartBody.Part,
        @Part autoLogAttendance: MultipartBody.Part
    ): RecognitionResponse
}

object NetworkModule {

    fun authApi(sessionManager: SessionManager): AuthApi {
        val authInterceptor = Interceptor { chain ->
            val token = runBlocking { sessionManager.getAccessToken() }
            val request = if (!token.isNullOrBlank()) {
                chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            } else {
                chain.request()
            }
            chain.proceed(request)
        }

        val logger = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(logger)
            .build()

        return Retrofit.Builder()
            .baseUrl(BuildConfig.ODOO_BASE_URL.ensureTrailingSlash())
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AuthApi::class.java)
    }

    fun faceApi(): FaceApi {
        val apiKeyInterceptor = Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("X-API-Key", BuildConfig.FACE_API_KEY)
                .build()
            chain.proceed(request)
        }

        val logger = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(apiKeyInterceptor)
            .addInterceptor(logger)
            .build()

        return Retrofit.Builder()
            .baseUrl(BuildConfig.FACE_BASE_URL.ensureTrailingSlash())
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FaceApi::class.java)
    }
}
