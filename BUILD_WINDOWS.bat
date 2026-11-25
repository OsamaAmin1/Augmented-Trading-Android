@echo off
where gradle >nul 2>nul || (echo Install Gradle 8.11.1 and Android SDK first.& pause & exit /b 1)
gradle --no-daemon :app:assembleDebug
if errorlevel 1 (echo Build failed. Review diagnostics.& pause & exit /b 1)
echo APK: app\build\outputs\apk\debug\app-debug.apk
pause
