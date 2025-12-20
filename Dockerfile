FROM gradle:8.4.0-jdk17-alpine

# 1. Устанавливаем системные зависимости
RUN apk add --no-cache wget unzip bash git

# 2. Копируем проект в контейнер
COPY . /opt/project
WORKDIR /opt/project

# 3. Устанавливаем Android SDK 
ARG ANDROID_SDK_VERSION=11076708  # Для Android SDK command-line tools
ENV ANDROID_SDK_ROOT /opt/android-sdk
ENV ANDROID_HOME /opt/android-sdk
ENV PATH ${PATH}:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools

# Скачиваем и распаковываем SDK
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip -O /tmp/tools.zip && \
    unzip -q /tmp/tools.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools && \
    mv ${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools ${ANDROID_SDK_ROOT}/cmdline-tools/latest && \
    rm /tmp/tools.zip

# 4. Принимаем лицензии и устанавливаем версии SDK
# Ваш compileSdk = 36, targetSdk = 34
RUN yes | sdkmanager --licenses --sdk_root=${ANDROID_SDK_ROOT} && \
    sdkmanager --sdk_root=${ANDROID_SDK_ROOT} \
        "platforms;android-36" \
        "platforms;android-34" \
        "build-tools;34.0.0" \
        "platform-tools" \
        "ndk;25.1.8937393"  # Для нативных зависимостей

# 5. Делаем gradlew исполняемым
RUN chmod +x gradlew

# 6. Метаданные
LABEL version="1.0" \
      maintainer="mila221" \
      description="CatHair Assistant Android Development Environment" \
      android.compileSdk="36" \
      android.targetSdk="34" \
      project.path="/opt/project" \
      build.command="./gradlew assembleDebug"

# 7. Точка входа - показываем доступные команды
CMD ["bash", "-c", "echo '=== CatHair Development Environment ===' && \
     echo 'Исходники: /opt/project' && \
     echo 'APK сборка: ./gradlew assembleDebug' && \
     echo 'Запуск тестов: ./gradlew test' && \
     echo 'Список задач: ./gradlew tasks' && \
     echo '' && \
     echo 'Пример: docker run -it --rm mila221/cathair-dev ./gradlew assembleDebug' && \
     bash"]