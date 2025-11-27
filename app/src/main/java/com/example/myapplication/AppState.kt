package com.example.myapplication

import android.graphics.Bitmap
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

object AppState {
    var capturedImageBitmap: Bitmap? by mutableStateOf(null)
    var imageSource: ImageSource by mutableStateOf(ImageSource.NONE)
}

enum class ImageSource {
    NONE, CAMERA, GALLERY
}