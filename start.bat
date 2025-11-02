@echo off
chcp 65001 > nul
echo ========================================
echo 巡河宝统计工具 - 启动开发服务器
echo ========================================
echo.

echo 正在启动Expo开发服务器...
echo.
echo 启动后：
echo 1. 在手机上打开 Expo Go 应用
echo 2. 扫描终端显示的二维码
echo 3. 等待应用加载完成
echo.
echo 按 Ctrl+C 可以停止服务器
echo.
echo ========================================
echo.

call npm start
