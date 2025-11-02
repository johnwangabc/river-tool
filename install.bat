@echo off
chcp 65001 > nul
echo ========================================
echo 巡河宝统计工具 - React Native移动端
echo 自动安装脚本
echo ========================================
echo.

echo [1/4] 检查Node.js环境...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Node.js
    echo 请访问 https://nodejs.org/ 下载并安装Node.js LTS版本
    pause
    exit /b 1
) else (
    echo ✅ Node.js已安装
    node --version
)
echo.

echo [2/4] 检查npm环境...
npm --version > nul 2>&1
if errorlevel 1 (
    echo ❌ npm未正确安装
    pause
    exit /b 1
) else (
    echo ✅ npm已安装
    npm --version
)
echo.

echo [3/4] 安装项目依赖...
echo 这可能需要几分钟时间，请耐心等待...
call npm install
if errorlevel 1 (
    echo ❌ 依赖安装失败
    echo 请检查网络连接后重试
    pause
    exit /b 1
) else (
    echo ✅ 依赖安装成功
)
echo.

echo [4/4] 检查Expo CLI...
call npx expo --version > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Expo CLI未全局安装，将使用npx运行
) else (
    echo ✅ Expo CLI可用
)
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 接下来你可以：
echo.
echo 1. 运行 start.bat 启动开发服务器
echo 2. 在手机上安装 Expo Go 应用
echo 3. 扫描二维码在手机上查看应用
echo.
echo 详细文档请查看：
echo - README.md (完整文档)
echo - 快速开始.md (快速入门)
echo - 项目说明.md (项目介绍)
echo.
pause
