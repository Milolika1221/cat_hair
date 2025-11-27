package com.example.myapplication

import android.content.Context
import android.graphics.Bitmap
import android.net.Uri
import android.provider.MediaStore
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import java.io.IOException

class ImagePicker {
    @Composable
    fun rememberImagePicker(
        onImageSelected: (Bitmap?) -> Unit
    ): ImagePickerController {
        val context = LocalContext.current

        val galleryLauncher = rememberLauncherForActivityResult(
            contract = ActivityResultContracts.GetContent(),
            onResult = { uri ->
                uri?.let {
                    try {
                        val bitmap = uriToBitmap(context, it)
                        onImageSelected(bitmap)
                    } catch (e: IOException) {
                        e.printStackTrace()
                        onImageSelected(null)
                    }
                }
            }
        )

        return remember {
            ImagePickerController(
                onGalleryLaunch = {
                    galleryLauncher.launch("image/*")
                }
            )
        }
    }

    private fun uriToBitmap(context: Context, uri: Uri): Bitmap? {
        return try {
            MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
        } catch (e: IOException) {
            e.printStackTrace()
            null
        }
    }
}

class ImagePickerController(
    private val onGalleryLaunch: () -> Unit
) {
    fun launchGallery() {
        onGalleryLaunch()
    }
}