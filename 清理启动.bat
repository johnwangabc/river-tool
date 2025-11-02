@echo off
chcp 65001 > nul
echo ========================================
echo 清理缓存并启动
echo ========================================
echo.

echo [1/2] 清理 .expo 缓存...
if exist .expo (
    rmdir /s /q .expo
    echo 缓存已清理
) else (
    echo 无缓存需要清理
)

echo.
echo [2/2] 启动 Expo...
echo.

call npx expo start -c

pause
