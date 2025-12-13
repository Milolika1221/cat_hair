package com.example.myapplication

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.snapshots.SnapshotStateList
import org.json.JSONObject
import java.io.ByteArrayOutputStream

// Класс для хранения записи истории
data class HistoryRecord(
    val catId: Int,
    val image: String,          // Base64 строка с изображением
    val title: String = "Неизвестная стрижка"    // Название стрижки (будет от нейросети)
) {
    // Сериализация в JSON строку
    fun toJsonString(): String {
        return JSONObject().apply {
            put("cat_id", catId)
            put("image", image)
            put("title", title)
        }.toString()
    }

    companion object {
        // Десериализация из JSON строки
        fun fromJsonString(jsonString: String): HistoryRecord {
            val json = JSONObject(jsonString)
            return HistoryRecord(
                catId = json.getInt("cat_id"),
                image = json.getString("image"),
                title = json.optString("title", "Неизвестная стрижка")
            )
        }
    }
}

// Объект для управления историей
object HistoryManager {
    private const val HISTORY_PREFS = "history_prefs"
    private const val HISTORY_LIST_KEY = "history_list"

    private val _historyRecords = mutableStateListOf<HistoryRecord>()
    val historyRecords: SnapshotStateList<HistoryRecord> = _historyRecords

    // Инициализация истории из SharedPreferences
    fun initialize(context: Context) {
        loadHistory(context)
    }

    // Добавление записи в историю
    fun addRecord(context: Context, record: HistoryRecord) {
        _historyRecords.add(0, record)
        saveHistory(context)
    }

    // Получение всех записей
    fun getRecords(): List<HistoryRecord> {
        return historyRecords
    }

    // Очистка истории
    fun clearHistory(context: Context) {
        _historyRecords.clear()
        saveHistory(context)
    }

    // Сохранение истории в SharedPreferences
    private fun saveHistory(context: Context) {
        val prefs = context.getSharedPreferences(HISTORY_PREFS, Context.MODE_PRIVATE)
        val editor = prefs.edit()

        val jsonSet = mutableSetOf<String>()
        historyRecords.forEach { record ->
            jsonSet.add(record.toJsonString())
        }

        editor.putStringSet(HISTORY_LIST_KEY, jsonSet)
        editor.apply()
    }

    // Загрузка истории из SharedPreferences
    private fun loadHistory(context: Context) {
        val prefs = context.getSharedPreferences(HISTORY_PREFS, Context.MODE_PRIVATE)
        val jsonSet = prefs.getStringSet(HISTORY_LIST_KEY, setOf()) ?: setOf()

        _historyRecords.clear()
        jsonSet.forEach { jsonString ->
            try {
                val record = HistoryRecord.fromJsonString(jsonString)
                _historyRecords.add(record)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    // Конвертация Bitmap в base64
    fun bitmapToBase64(bitmap: Bitmap): String {
        val byteArrayOutputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 70, byteArrayOutputStream)
        val byteArray = byteArrayOutputStream.toByteArray()
        return Base64.encodeToString(byteArray, Base64.DEFAULT)
    }

    fun Bitmap.toByteArray(): ByteArray {
        val outputStream = ByteArrayOutputStream()
        this.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
        return outputStream.toByteArray()
    }

    // Конвертация base64 в Bitmap
    fun base64ToBitmap(base64String: String): Bitmap? {
        return try {
            val decodedBytes = Base64.decode(base64String, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.size)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}