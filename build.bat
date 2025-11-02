@echo off
chcp 65001 > nul
echo ========================================
echo 巡河宝统计工具 - EAS云打包
echo ========================================
echo.

echo 检查EAS CLI...
call eas --version > nul 2>&1
if errorlevel 1 (
    echo ❌ EAS CLI未安装
    echo 正在安装 EAS CLI...
    call npm install -g eas-cli
    if errorlevel 1 (
        echo ❌ EAS CLI安装失败
        pause
        exit /b 1
    )
)

echo ✅ EAS CLI已就绪
echo.

echo 选择构建类型：
echo.
echo 1. Preview构建 (生成APK，用于测试)
echo 2. Production构建 (生成AAB，用于发布)
echo 3. 取消
echo.
set /p choice="请选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 开始Preview构建...
    echo 这将生成一个APK文件，可以直接安装在Android设备上
    echo.
    call eas build --platform android --profile preview
) else if "%choice%"=="2" (
    echo.
    echo 开始Production构建...
    echo 这将生成一个AAB文件，用于上传到Google Play
    echo.
    call eas build --platform android --profile production
) else (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo ========================================
echo 构建已提交！
echo ========================================
echo.
echo 你可以：
echo 1. 访问显示的链接查看构建进度
echo 2. 登录 https://expo.dev/ 查看所有构建
echo 3. 构建完成后会收到邮件通知
echo.
pause
