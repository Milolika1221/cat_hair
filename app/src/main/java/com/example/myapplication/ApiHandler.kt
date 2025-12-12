package com.example.myapplication

import com.google.gson.annotations.SerializedName
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import retrofit2.HttpException
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import java.io.File
import retrofit2.Response
import java.io.IOException

const val BaseUrl : String = "https://localhost:8000/api/v1";


fun File.determineMimeType(): String {
    return when (extension.lowercase()) {
        "png" -> "image/png"
        "jpg", "jpeg" -> "image/jpeg"
        "gif" -> "image/gif"
        "webp" -> "image/webp"
        else -> "application/octet-stream" // fallback
    }
}

data class CatRecommendationResponse(
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

data class CatUploadResponse(
    val sessionId: String,
    val catId: Int,
    val filename: String,
    val uploadTimestamp: Float  // милисекунды
)

data class CreateSessionResponse(
    val sessionId: String,
    val status: String,
)

interface CatApiService {
    @GET("$BaseUrl/{session_id}/{cat_id}/recommendations")
    suspend fun getRecommendations(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
    ): CatRecommendationResponse

    @Multipart
    @POST("$BaseUrl/{session_id}/{cat_id}/images")
    suspend fun uploadCatPhoto(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
        @Part("file") photo: MultipartBody.Part
    ): Response<CatUploadResponse>

    @GET("session/")
    suspend fun createSession(): CreateSessionResponse
}

public class APIHandler(private val api: CatApiService) {
    suspend fun createSession(): Result<CreateSessionResponse>
    {
        return try {
            val session = api.createSession()
            Result.success(session)
        } catch (e: HttpException) {
            Result.failure(e)
        }
    }

    suspend fun uploadImage(
        sessionId: String,
        catId: Int = 0,
        imageFile: File
    ): Result<CatUploadResponse> {
        val mimeType = imageFile.determineMimeType()
        val mediaType = mimeType.toMediaTypeOrNull() ?: "application/octet-stream".toMediaType()
        val requestBody = imageFile.asRequestBody(mediaType)
        val photoPart = MultipartBody.Part.createFormData("file", imageFile.name, requestBody)

        return try {
            val response = api.uploadCatPhoto(sessionId, catId, photoPart)

            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.success(body)
                } else {
                    Result.failure(IllegalStateException("Empty response body"))
                }
            } else {
                val errorDetail = try {
                    val errorBody = response.errorBody()?.string()!!
                    JSONObject(errorBody).optString("detail", "Unknown error")
                } catch (e: Exception) {
                    "Request failed with status ${response.code()}"
                }
                Result.failure(RuntimeException(errorDetail))
            }
        } catch (e: IOException) {
            Result.failure(RuntimeException("Network error: ${e.message}", e))
        } catch (e: Exception) {
            Result.failure(RuntimeException("Unexpected error: ${e.message}", e))
        }
    }

    suspend fun getRecommendations(
        sessionId : String,
        catId: Int,
    ): Result<CatRecommendationResponse>
    {
        return try {
            val recommendation = api.getRecommendations(sessionId, catId)
            Result.success(recommendation)
        } catch (e: HttpException){
            Result.failure(e)
        }
    }
}