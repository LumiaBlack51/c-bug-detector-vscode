@echo off
echo ========================================
echo C语言Bug检测器 Docker推送脚本
echo ========================================

echo.
echo 检查Docker状态...
docker --version
if %errorlevel% neq 0 (
    echo 错误: Docker未安装或未正确配置
    pause
    exit /b 1
)

echo.
echo 检查Docker Desktop是否运行...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker Desktop未运行
    echo 请先启动Docker Desktop
    pause
    exit /b 1
)

echo.
echo 检查镜像是否存在...
docker images lumiablack/c-detector
if %errorlevel% neq 0 (
    echo 错误: 镜像不存在，请先运行 build-docker.bat
    pause
    exit /b 1
)

echo.
echo 登录Docker Hub...
echo 请输入您的Docker Hub用户名和密码:
docker login

if %errorlevel% neq 0 (
    echo 错误: Docker Hub登录失败
    pause
    exit /b 1
)

echo.
echo 推送镜像到Docker Hub...
echo 推送 latest 标签...
docker push lumiablack/c-detector:latest

if %errorlevel% neq 0 (
    echo 错误: 推送 latest 标签失败
    pause
    exit /b 1
)

echo.
echo 推送 1.1.0 版本标签...
docker push lumiablack/c-detector:1.1.0

if %errorlevel% neq 0 (
    echo 错误: 推送 1.1.0 标签失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 推送完成！
echo ========================================
echo.
echo 镜像已成功推送到Docker Hub:
echo - https://hub.docker.com/repository/docker/lumiablack/c-detector/general
echo.
echo 使用方法:
echo docker pull lumiablack/c-detector:latest
echo docker run -it lumiablack/c-detector:latest
echo.
pause
