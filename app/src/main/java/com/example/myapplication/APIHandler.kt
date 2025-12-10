package com.example.myapplication

import android.R
import com.google.gson.annotations.SerializedName
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.HttpException
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import java.io.File
import retrofit2.Response

val BASE_URL = "https://n155wdth-8000.euw.devtunnels.ms/api/v1";

// JSON в объекты
data class CatAnalysisResponse(
    @SerializedName("cat_id")
    val catId: Int,

    @SerializedName("image")
    val imageBase64: String,

    @SerializedName("recommendation")
    val recommendation: HaircutRecommendation
)
data class HaircutRecommendation(
    @SerializedName("haircut_name")
    val name: String,

    @SerializedName("haircut_description")
    val description: String
)
// Ответ на загрузку фото
data class CatUploadResponse(
    val session_id: String,
    val cat_id: Int,
    val file_name: String,
    val upload_timestamp: Float  // милисекунды
)

// Создание сессии
data class CreateSessionResponse(
    val sessionId: String,
    val status: String,
)

interface CatApiService {
    // 1. Получение рекомендации по коту (ваш текущий)
    @GET("{session_id}/{cat_id}/images/{cat_id}/recommendations")  // ← путь эндпоинта
    suspend fun analyzeCat(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
    ): CatAnalysisResponse

    // 2. Загрузка фото кота (пример POST-запроса)
    @Multipart
    @POST("{session_id}/{cat_id}/images")
    suspend fun uploadCatPhoto(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
        @Part("file") photo: MultipartBody.Part
    ): Response<CatUploadResponse>

    // 3.
    @GET("session/")
    suspend fun createSession(): CreateSessionResponse
}

public class APIHandler(private val api: CatApiService) {
    // Функция для создания
    suspend fun createSession(): Result<CreateSessionResponse>
    {
        return try {
            val session = api.createSession()
            Result.success(session)
        } catch (e: HttpException) {
            Result.failure(e)
        }
    }

    // Функция для загрузки
    suspend fun uploadImage(sessionId: String, catId: Int = 0, imageFile: File): Result<CatUploadResponse>
    {
        val mimeType = "image/jpeg"
        val requestBody = imageFile.asRequestBody(mimeType.toMediaType())
        val photoPart = MultipartBody.Part.createFormData("file", imageFile.name, requestBody)

        return try {
            val response = api.uploadCatPhoto(sessionId, catId, photoPart)
            if (response is null)
            if (response.isSuccessful())
            Result.success(response.body())
        } catch (e: HttpException) {
            Result.failure(e)
        }
    }
}