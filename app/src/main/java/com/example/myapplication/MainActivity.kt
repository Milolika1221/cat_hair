package com.example.myapplication

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.camera.view.PreviewView
import androidx.compose.ui.viewinterop.AndroidView
import com.google.accompanist.permissions.rememberPermissionState
import android.Manifest
import android.net.Uri
import android.util.Log
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.foundation.Image
import androidx.compose.ui.layout.ContentScale
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.navigation.NavType
import androidx.navigation.navArgument
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import android.graphics.Bitmap
import java.io.ByteArrayOutputStream

val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val apiService = retrofit.create(CatApiService::class.java)

val handler = APIHandler(apiService)


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            HistoryManager.initialize(this)

            CatStyleTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()

                    NavHost(
                        navController = navController,
                        startDestination = "main"
                    ) {
                        composable("main") { MainScreen(navController) }
                        composable("instructions") { InstructionsScreen(navController) }
                        composable("history") {HistoryScreen(navController)}
                        composable("photoSource") { PhotoSourceScreen(navController) }
                        composable("camera") { CameraScreen(navController) }
                        composable("gallery") { GalleryScreen(navController) }
                        composable("photoPreview") { PhotoPreviewScreen(navController) }
                        composable("analysis") { AnalysisScreen(navController) }
                        composable(
                            "recommendations/{title}/{description}/{haircutImage}",
                            arguments = listOf(
                                navArgument("title") { type = NavType.StringType },
                                navArgument("description") { type = NavType.StringType },
                                navArgument("haircutImage") {
                                    type = NavType.StringType
                                    defaultValue = ""
                                }
                            )
                        ) { backStackEntry ->
                            val title = backStackEntry.arguments?.getString("title") ?: "Unknown"
                            val description = backStackEntry.arguments?.getString("description") ?: ""
                            val haircutImageBase64 = backStackEntry.arguments?.getString("haircutImage") ?: ""

                            RecommendationsScreen(
                                navController = navController,
                                title = title,
                                description = description,
                                haircutImageBase64 = haircutImageBase64
                            )
                        }
                        composable("recognitionError") { RecognitionErrorScreen(navController) }
                    }
                }
            }
        }
    }
}

@Composable
fun CatStyleTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        content = content
    )
}

// ЭКРАН 1 - Главный
@Composable
fun MainScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "CatStyle Assistant",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Подбор стрижки для вашего кота",
            style = MaterialTheme.typography.headlineSmall,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(80.dp))

        Button(
            onClick = { navController.navigate("photoSource") },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Text(
                "ВЫБРАТЬ ФОТО",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate("history") },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.secondary
            )
        ) {
            Text(
                "ИСТОРИЯ",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate("instructions") },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.secondary
            )
        ) {
            Text(
                "ИНСТРУКЦИЯ",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

// ЭКРАН 2 - Инструкция
@Composable
fun InstructionsScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        Box(
            modifier = Modifier.fillMaxWidth()
        ) {
            IconButton(
                onClick = { navController.popBackStack() },
                modifier = Modifier.align(Alignment.CenterStart)
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }
            Text(
                text = "Инструкция",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        InstructionItem("1. Сделайте фото кота при хорошем освещении")
        InstructionItem("2. Убедитесь, что кот виден целиком")
        InstructionItem("3. Наш AI проанализирует тип шерсти и телосложение")
        InstructionItem("4. Получите рекомендации по стрижке")
    }
}

@Composable
fun InstructionItem(text: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.Top
    ) {
        Text(
            text = "• $text",
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.weight(1f)
        )
    }
}

// ЭКРАН 3 - История
@Composable
fun HistoryScreen(navController: NavHostController) {
    // Получаем записи из HistoryManager
    val historyRecords = remember { HistoryManager.historyRecords }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // Верхняя строка с кнопкой назад и заголовком
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Кнопка назад слева
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }

            // Заголовок по центру
            Text(
                text = "История",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center
            )

            // Индикатор количества записей
            Text(
                text = "(${historyRecords.size})",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        historyRecords.forEachIndexed { index, record ->
            HistoryCard(
                record = record,
                onClick = {
                    // Сохранение записи в AppState
                    AppState.currentHistoryRecord = record
                    navController.navigate("recommendations")
                }
            )
            if (index < historyRecords.size - 1) {
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun HistoryCard(
    record: HistoryRecord,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Левая часть - фото
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(
                        color = Color.Gray.copy(alpha = 0.3f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                // Пытаемся загрузить изображение из base64
                record.image?.let { base64String ->
                    val bitmap = HistoryManager.base64ToBitmap(base64String)
                    if (bitmap != null) {
                        Image(
                            bitmap = bitmap.asImageBitmap(),
                            contentDescription = "Фото из истории",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop
                        )
                    } else {
                        // Если не удалось загрузить
                        Icon(
                            painter = painterResource(id = android.R.drawable.ic_menu_camera),
                            contentDescription = "Ошибка загрузки",
                            tint = Color.Gray,
                            modifier = Modifier.size(32.dp)
                        )
                    }
                } ?: run {
                    // Если нет base64 строки
                    Icon(
                        painter = painterResource(id = android.R.drawable.ic_menu_camera),
                        contentDescription = "Нет фото",
                        tint = Color.Gray,
                        modifier = Modifier.size(32.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(16.dp))

            // Правая часть - информация
            Text(
                text = record.title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(3f)
            )
        }
    }
}

// ЭКРАН 4 - Выбор источника фото
@Composable
fun PhotoSourceScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        // Заголовок с кнопкой назад
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }

            Text(
                text = "Выбор источника фото",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(48.dp))

        // Контент
        Column(
            modifier = Modifier
                .fillMaxSize()
                .weight(1f),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Button(
                onClick = { navController.navigate("camera") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text(
                    "КАМЕРА",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { navController.navigate("gallery") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text(
                    "ГАЛЕРЕЯ",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

// ЭКРАН 5 - Камера
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraScreen(navController: NavHostController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    // Состояния для управления камерой
    var hasCameraPermission by remember { mutableStateOf(false) }
    var isCameraInitialized by remember { mutableStateOf(false) }
    var captureInProgress by remember { mutableStateOf(false) }

    // Запрос разрешения для доступа к камере
    val cameraPermissionState = rememberPermissionState(
        android.Manifest.permission.CAMERA
    )

    // Отображение камеры
    val previewView = remember { PreviewView(context) }

    // Контроллер камеры
    val cameraController = remember {
        CameraController(context, previewView, lifecycleOwner)
    }

    // Эффект для запроса разрешений
    LaunchedEffect(Unit) {
        if (!cameraPermissionState.status.isGranted) {
            cameraPermissionState.launchPermissionRequest()
        } else {
            hasCameraPermission = true
        }
    }

    // Эффект для инициализации камеры после получения разрешений
    LaunchedEffect(hasCameraPermission) {
        if (hasCameraPermission && !isCameraInitialized) {
            cameraController.startCamera()
            isCameraInitialized = true
        }
    }

    // Очистка при выходе с экрана
    DisposableEffect(Unit) {
        onDispose {
            cameraController.shutdown()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
    ) {
        // Заголовок
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }

            Text(
                text = "Сфотографируйте кота",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (!hasCameraPermission) {
            // Экран запроса разрешений
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .weight(1f),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Требуется доступ к камере",
                    style = MaterialTheme.typography.headlineMedium,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Для работы камеры необходимо предоставить разрешение",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(32.dp))

                Button(
                    onClick = { cameraPermissionState.launchPermissionRequest() }
                ) {
                    Text("ПРЕДОСТАВИТЬ РАЗРЕШЕНИЕ")
                }
            }
        } else {
            // Экран камеры
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .weight(1f),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Preview камеры
                AndroidView(
                    factory = { previewView },
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .background(Color.Black)
                )

                Spacer(modifier = Modifier.height(32.dp))

                if (captureInProgress) {
                    // Индикатор загрузки во время съемки
                    CircularProgressIndicator(
                        modifier = Modifier.size(80.dp),
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Обработка фото...",
                        style = MaterialTheme.typography.bodyMedium
                    )
                } else {
                    // Кнопка съемки
                    Button(
                        onClick = {
                            captureInProgress = true
                            cameraController.takePicture { bitmap ->
                                // Сохранение изображение и установление источника
                                AppState.capturedImageBitmap = bitmap
                                AppState.imageSource = ImageSource.CAMERA
                                captureInProgress = false

                                // Переход к предпросмотру после съемки
                                navController.navigate("photoPreview")
                            }
                        },
                        modifier = Modifier
                            .size(80.dp)
                            .clip(CircleShape),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Icon(
                            painter = painterResource(id = android.R.drawable.ic_menu_camera),
                            contentDescription = "Сделать фото",
                            modifier = Modifier.size(40.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "Нажмите для съемки",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

// ЭКРАН 6 - Галерея
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun GalleryScreen(navController: NavHostController) {
    val context = LocalContext.current


    var selectedImageBitmap by remember { mutableStateOf<Bitmap?>(null) }

    // Версия для разрешения к галерее в зависимости от версии Android
    val galleryPermission = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
        Manifest.permission.READ_MEDIA_IMAGES
    } else {
        Manifest.permission.READ_EXTERNAL_STORAGE
    }

    // Запрос разрешений для галереи
    val galleryPermissionState = rememberPermissionState(galleryPermission)

    // Отслеживаем изменение статуса разрешения
    val hasGalleryPermission by derivedStateOf {
        galleryPermissionState.status.isGranted
    }

    val imagePicker = ImagePicker()
    val imagePickerController = imagePicker.rememberImagePicker { bitmap ->
        selectedImageBitmap = bitmap
        if (bitmap != null) {
            AppState.capturedImageBitmap = bitmap
            AppState.imageSource = ImageSource.GALLERY
        }
    }

    // Эффект для автоматического запроса разрешений при открытии экрана
    LaunchedEffect(Unit) {
        if (!galleryPermissionState.status.isGranted) {
            galleryPermissionState.launchPermissionRequest()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        // Заголовок
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }
            Text(
                text = "Галерея",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Выберите фотографию кота",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(32.dp))

        if (!hasGalleryPermission) {
            // Экран запроса разрешений
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Требуется доступ к галерее",
                    style = MaterialTheme.typography.headlineSmall,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Для выбора фото необходимо предоставить разрешение",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(32.dp))

                Button(
                    onClick = {
                        galleryPermissionState.launchPermissionRequest()
                    }
                ) {
                    Text("ПРЕДОСТАВИТЬ РАЗРЕШЕНИЕ")
                }
            }
        } else {
            // Основной контент галереи
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Отображение выбранного изображения
                if (selectedImageBitmap != null) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Image(
                            bitmap = selectedImageBitmap!!.asImageBitmap(),
                            contentDescription = "Выбранное фото кота",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop
                        )
                    }
                } else {
                    // Кнопка выбора фото
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp)
                            .background(MaterialTheme.colorScheme.surfaceVariant)
                            .clickable {
                                imagePickerController.launchGallery()
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                painter = painterResource(id = android.R.drawable.ic_menu_gallery),
                                contentDescription = "Галерея",
                                modifier = Modifier.size(64.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "Нажмите чтобы выбрать фото",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Button(
                    onClick = {
                        if (selectedImageBitmap != null) {
                            navController.navigate("photoPreview")
                        } else {
                            imagePickerController.launchGallery()
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(56.dp)
                ) {
                    Text(
                        if (selectedImageBitmap != null) "ПОДТВЕРДИТЬ" else "ВЫБРАТЬ ФОТО",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                }

                if (selectedImageBitmap != null) {
                    Spacer(modifier = Modifier.height(16.dp))

                    TextButton(
                        onClick = {
                            selectedImageBitmap = null
                            AppState.capturedImageBitmap = null
                            AppState.imageSource = ImageSource.NONE
                        },
                        modifier = Modifier.fillMaxWidth().height(56.dp)
                    ) {
                        Text(
                            "ВЫБРАТЬ ДРУГОЕ ФОТО",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }
        }
    }
}

// ЭКРАН 7 - Предпросмотр фото
@Composable
fun PhotoPreviewScreen(navController: NavHostController) {
    val capturedImageBitmap = AppState.capturedImageBitmap

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = {
                    // Очищаем состояние при возврате
                    AppState.capturedImageBitmap = null
                    AppState.imageSource = ImageSource.NONE
                    navController.popBackStack()
                }
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Назад"
                )
            }
            Text(
                text = "Предпросмотр фото",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Отображаем изображение из любого источника
        if (capturedImageBitmap != null) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(400.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant)
                    .clip(RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                Image(
                    bitmap = capturedImageBitmap.asImageBitmap(),
                    contentDescription = when (AppState.imageSource) {
                        ImageSource.CAMERA -> "Сфотографированный кот"
                        ImageSource.GALLERY -> "Выбранный из галереи кот"
                        else -> "Фото кота"
                    },
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }

        } else {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(400.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("ФОТО НЕ НАЙДЕНО")
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "Вернитесь и выберите фото",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                // Переходим к анализу только если есть изображение
                if (capturedImageBitmap != null) {
                    navController.navigate("analysis")
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            enabled = capturedImageBitmap != null
        ) {
            Text(
                "АНАЛИЗИРОВАТЬ",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = {
                // Очищаем изображение при возврате к выбору фото
                AppState.capturedImageBitmap = null
                AppState.imageSource = ImageSource.NONE
                navController.popBackStack()
            }
        ) {
            Text(
                "ВЫБРАТЬ ДРУГОЕ",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

// ЭКРАН 8 - Анализ
@Composable
fun AnalysisScreen(navController: NavHostController) {
    val context = LocalContext.current

    var mySession: String by remember {mutableStateOf("")}

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Анализ изображения",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Анализируем вашего кота",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "Определяем окрас, телосложение и длину шерсти...",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Имитация загрузки
        CircularProgressIndicator()

        Spacer(modifier = Modifier.height(32.dp))

        LaunchedEffect(mySession) {
            try {
                // Создание сессии, если её нет
                val session = mySession.ifEmpty {
                    handler.createSession()
                        .onFailure {
                            navController.navigate("recognitionError")
                            return@LaunchedEffect
                        }
                        .getOrNull()?.sessionId
                        ?: run {
                            navController.navigate("recognitionError")
                            return@LaunchedEffect
                        }
                }

                // Проверка наличия bitmap
                val bitmap = AppState.capturedImageBitmap
                    ?: run {
                        Log.e("AnalysisScreen", "No captured image")
                        navController.navigate("photoPreview")
                        return@LaunchedEffect
                    }

                // Конвертация bitmap в bytes
                val imageBytes = withContext(Dispatchers.Default) {
                    ByteArrayOutputStream().use { stream ->
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream)
                        stream.toByteArray()
                    }
                }

                // Загрузка изображения
                val uploadImageResponse = handler.uploadImage(session, imageBytes)
                    .onFailure {
                        navController.navigate("recognitionError")
                        return@LaunchedEffect
                    }

                // Получение рекомендаций
                val getRecommendationResponse = handler.getRecommendations(
                    sessionId = session,
                    catId = uploadImageResponse.getOrNull()!!.catId
                ).onFailure {
                    navController.navigate("recognitionError")
                    return@LaunchedEffect
                }

                // Безопасное извлечение данных с проверкой
                val uploadResult = uploadImageResponse.getOrNull()
                    ?: run {
                        navController.navigate("recognitionError")
                        return@LaunchedEffect
                    }

                val recommendationResult = getRecommendationResponse.getOrNull()
                    ?: run {
                        navController.navigate("recognitionError")
                        return@LaunchedEffect
                    }

                // Получаем название стрижки для истории
                val haircutTitle = recommendationResult.recommendation.name

                // Добавление записи в историю с соответствующим названием стрижки
                HistoryManager.addRecord(
                    context = context,
                    HistoryRecord(
                        catId = recommendationResult.catId,
                        image = recommendationResult.imageBase64,
                        title = haircutTitle
                    )
                )

                // Кодируем параметры для навигации
                val encodedTitle = Uri.encode(recommendationResult.recommendation.name)
                val encodedDescription = Uri.encode(recommendationResult.recommendation.description)
                val encodedHaircutImage = recommendationResult.recommendation.haircutImageBase64?.let {
                    Uri.encode(it)
                } ?: ""

                // Навигация с передачей изображения стрижки
                navController.navigate(
                    "recommendations/$encodedTitle/$encodedDescription/$encodedHaircutImage"
                )

            } catch (e: Exception) {
                Log.e("AnalysisScreen", "Unexpected error", e)
                navController.navigate("recognitionError")
            }
        }


        // Кнопка для ручного перехода
        TextButton(
            onClick = { navController.navigate("recommendations") }
        ) {
            Text("Перейти к результатам",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium)
        }
    }
}

// ЭКРАН 9 - Ошибка распознавания (тут то же кароче должна нейронка понимать будет ошибка или нет фикс нужен и ниже ещё 9 экран)
@Composable
fun RecognitionErrorScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(80.dp)
                .background(
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "!",
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.onErrorContainer,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Ошибка распознавания",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Кот не распознан",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Не удалось найти кота на фото",
            style = MaterialTheme.typography.titleSmall,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Советы
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Убедитесь, что:",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("• Кот хорошо виден", style = MaterialTheme.typography.bodyLarge)
                Text("• Освещение хорошее", style = MaterialTheme.typography.bodyLarge)
                Text("• Фото не размыто", style = MaterialTheme.typography.bodyLarge)
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Кнопки
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(
                onClick = {
                    navController.navigate("photoSource") {
                        popUpTo("analysis") { inclusive = true }
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp)
            ) {
                Text("ПОВТОРИТЬ",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium)
            }

            Spacer(modifier = Modifier.height(16.dp))

            TextButton(
                onClick = {
                    navController.navigate("main") {
                        popUpTo("main") { inclusive = true }
                    }
                }
            ) {
                Text("ОТМЕНА",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium)
            }
        }
    }
}

// ЭКРАН 9 - Рекомендации
@Composable
fun RecommendationsScreen(
    navController: NavHostController,
    title: String,
    description: String,
    haircutImageBase64: String = ""
) {
    // Декодируем base64 строку
    val decodedTitle = Uri.decode(title)
    val decodedDescription = Uri.decode(description)

    // Конвертируем base64 в Bitmap
    val haircutBitmap = remember(haircutImageBase64) {
        if (haircutImageBase64.isNotEmpty()) {
            try {
                val decodedString = Uri.decode(haircutImageBase64)
                HistoryManager.base64ToBitmap(decodedString)
            } catch (e: Exception) {
                e.printStackTrace()
                null
            }
        } else {
            null
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text(
                text = "Рекомендации по стрижке",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )

        Spacer(modifier = Modifier.height(32.dp))

        RecommendationCard(
            title = decodedTitle,
            description = decodedDescription,
            haircutBitmap = haircutBitmap
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                navController.navigate("main") {
                    popUpTo("main") { inclusive = true }
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp)
        ) {
            Text("ЗАВЕРШИТЬ", style = MaterialTheme.typography.titleMedium)
        }

            Spacer(modifier = Modifier.height(16.dp))

            TextButton(
                onClick = {
                    // Очищаем состояние перед новым анализом
                    AppState.capturedImageBitmap = null
                    AppState.imageSource = ImageSource.NONE
                    navController.navigate("photoSource") {
                        popUpTo("main") { inclusive = false }
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp)
            ) {
                Text("НОВЫЙ АНАЛИЗ", style = MaterialTheme.typography.titleMedium)
            }
            }
    }
}
@Composable
fun RecommendationCard(
    title: String,
    description: String,
    haircutBitmap: Bitmap? = null
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Изображение стрижки
            haircutBitmap?.let { bitmap ->
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(MaterialTheme.colorScheme.surface)
                ) {
                    Image(
                        bitmap = bitmap.asImageBitmap(),
                        contentDescription = "Пример стрижки «$title»",
                        modifier = Modifier
                            .fillMaxSize()
                            .clip(RoundedCornerShape(12.dp)),
                        contentScale = ContentScale.Crop
                    )
                }
                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Пример стрижки:",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.height(8.dp))
            }

            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
