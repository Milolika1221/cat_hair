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
import androidx.compose.foundation.shape.CircleShape
import kotlinx.coroutines.delay
import kotlin.random.Random

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
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
                        composable("photoSource") { PhotoSourceScreen(navController) }
                        composable("camera") { CameraScreen(navController) }
                        composable("gallery") { GalleryScreen(navController) }
                        composable("photoPreview") { PhotoPreviewScreen(navController) }
                        composable("analysis") { AnalysisScreen(navController) }
                        composable("recommendations") { RecommendationsScreen(navController) }
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

        Spacer(modifier = Modifier.height(16.dp))

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
        Text(
            text = "Инструкция",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        InstructionItem("1. Сделайте фото кота при хорошем освещении")
        InstructionItem("2. Убедитесь, что кот виден целиком")
        InstructionItem("3. Выберите до 5 фото разных ракурсов")
        InstructionItem("4. Наш AI проанализирует тип шерсти и телосложение")
        InstructionItem("5. Получите рекомендации по стрижке")

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { navController.navigate("photoSource") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("ПОНЯТНО")
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = { navController.popBackStack() }
        ) {
            Text("НАЗАД")
        }
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

// ЭКРАН 3 - Выбор источника фото
@Composable
fun PhotoSourceScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Выбор источника фото",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(48.dp))

        Button(
            onClick = { navController.navigate("camera") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("КАМЕРА", style = MaterialTheme.typography.bodyLarge)
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate("gallery") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("ГАЛЕРЕЯ", style = MaterialTheme.typography.bodyLarge)
        }

        Spacer(modifier = Modifier.height(32.dp))

        TextButton(
            onClick = { navController.popBackStack() }
        ) {
            Text("НАЗАД", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

// ЭКРАН 4 - Камера
@Composable
fun CameraScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Сфотографируйте кота",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(32.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Text("ЗДЕСЬ БУДЕТ ВАШЕ ФОТО")
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { navController.navigate("photoPreview") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("СДЕЛАТЬ ФОТО")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(
                onClick = { /* TODO: Переснять фото */ },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.secondary
                )
            ) {
                Text("ПЕРЕСНЯТЬ")
            }

            Button(
                onClick = { navController.navigate("photoPreview") },
                modifier = Modifier.weight(1f)
            ) {
                Text("ИСПОЛЬЗОВАТЬ")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = { navController.popBackStack() }
        ) {
            Text("НАЗАД")
        }
    }
}

// ЭКРАН 5 - Галерея
@Composable
fun GalleryScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        Text(
            text = "Галерея",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Выберите до 5 фото",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(32.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp),
            contentAlignment = Alignment.Center
        ) {
            Text("Место для выбора фото", style = MaterialTheme.typography.bodyMedium)
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { navController.navigate("photoPreview") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("ПОДТВЕРДИТЬ", style = MaterialTheme.typography.bodyLarge)
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = { navController.popBackStack() },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("НАЗАД", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

// ЭКРАН 6 - Предпросмотр фото
@Composable
fun PhotoPreviewScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Предпросмотр фото",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(400.dp)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Text("ВАШЕ ФОТО")
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { navController.navigate("analysis") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("АНАЛИЗИРОВАТЬ")
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = { navController.popBackStack() }
        ) {
            Text("ВЫБРАТЬ ДРУГОЕ")
        }
    }
}

// ЭКРАН 7 - Анализ (ИСПРАВЛЕННЫЙ)
@Composable
fun AnalysisScreen(navController: NavHostController) {
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

        // Автоматический переход через 3 секунды
        LaunchedEffect(Unit) {
            delay(3000L)

            val isSuccess = listOf(true, false).random()

            if (isSuccess) {
                navController.navigate("recommendations")
            } else {
                navController.navigate("recognitionError")
            }
        }

        // Кнопка для ручного перехода
        TextButton(
            onClick = { navController.navigate("recommendations") }
        ) {
            Text("Перейти к результатам")
        }
    }
}

// ЭКРАН 8 - Ошибка распознавания (тут то же кароче должна нейронка понимать будет ошибка или нет фикс нужен и ниже ещё 9 экран)
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
            style = MaterialTheme.typography.bodyMedium,
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
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("• Кот хорошо виден", style = MaterialTheme.typography.bodySmall)
                Text("• Освещение хорошее", style = MaterialTheme.typography.bodySmall)
                Text("• Фото не размыто", style = MaterialTheme.typography.bodySmall)
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
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("ПОВТОРИТЬ")
            }

            Spacer(modifier = Modifier.height(16.dp))

            TextButton(
                onClick = {
                    navController.navigate("main") {
                        popUpTo("main") { inclusive = true }
                    }
                }
            ) {
                Text("ОТМЕНА")
            }
        }
    }
}

// ЭКРАН 9 - Рекомендации
@Composable
fun RecommendationsScreen(navController: NavHostController) {/// тут фикс кароче должна нейронка выдавать тут для примера как в прототипах!!!!!!
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Рекомендации по стрижке",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        RecommendationCard(
            title = "Стрижка \"Лев\"",
            description = "Идеально подходит для густых волос, добавляет объем и текстуру. Требует минимальной укладки и отлично смотрится на круглых и квадратных лицах."
        )

        Spacer(modifier = Modifier.height(16.dp))

        RecommendationCard(
            title = "Каре \"Боб\"",
            description = "Классический вариант для тонких и средних волос. Придает аккуратный вид и легко укладывается. Прекрасно подходит для овальных и вытянутых лиц."
        )

        Spacer(modifier = Modifier.height(16.dp))

        RecommendationCard(
            title = "Пикси \"Дерзость\"",
            description = "Смелый и стильный выбор для коротких волос. Подчеркивает черты лица, не требует сложного ухода и идеально подходит для треугольных и сердечкообразных лиц."
        )

        Spacer(modifier = Modifier.height(32.dp))

        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(
                onClick = {
                    navController.navigate("main") {
                        popUpTo("main") { inclusive = true }
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("ЗАВЕРШИТЬ")
            }

            Spacer(modifier = Modifier.height(16.dp))

            TextButton(
                onClick = {
                    navController.navigate("photoSource") {
                        popUpTo("main") { inclusive = false }
                    }
                }
            ) {
                Text("НОВЫЙ АНАЛИЗ")
            }
        }
    }
}

@Composable
fun RecommendationCard(title: String, description: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
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

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}