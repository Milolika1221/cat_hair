package com.example.myapplication

import com.google.gson.annotations.SerializedName
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
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

const val BASE_URL  = "http://192.168.43.19:8000/"


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
    val description: String,

    @SerializedName("haircut_image")
    val haircutImageBase64: String? = null
)

data class CatUploadResponse(
    @SerializedName("session_id")
    val sessionId: String,
    @SerializedName("cat_id")
    val catId: Int,
    @SerializedName("file_name")
    val filename: String,
    @SerializedName("upload_timestamp")
    val uploadTimestamp: Float  // милисекунды
)

data class CreateSessionResponse(
    @SerializedName("session_id")
    val sessionId: String,
    val status: String,
)

interface CatApiService {
    @GET("api/v1/{session_id}/{cat_id}/recommendations")
    suspend fun getRecommendations(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
    ): CatRecommendationResponse

    @Multipart
    @POST("api/v1/{session_id}/{cat_id}/images")
    suspend fun uploadCatPhoto(
        @Path("session_id") sessionId: String,
        @Path("cat_id") catId: Int,
        @Part file: MultipartBody.Part
    ): Response<CatUploadResponse>

    @GET("api/v1/session")
    suspend fun createSession(): CreateSessionResponse
}

class APIHandler(private val api: CatApiService) {
    suspend fun createSession(): Result<CreateSessionResponse> {
        return try {
            val session = api.createSession()
            Result.success(session)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun uploadImage(
        sessionId: String,
        imageBytes: ByteArray,
        catId: Int = 0,
        fileName: String = "some_cat.jpg",
        mimeType: String = "image/jpeg",
    ): Result<CatUploadResponse> {
        val mediaType = mimeType.toMediaTypeOrNull() ?: "image/jpeg".toMediaType()
        val requestBody = imageBytes.toRequestBody(mediaType)
        val photoPart = MultipartBody.Part.createFormData("file", fileName, requestBody)

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