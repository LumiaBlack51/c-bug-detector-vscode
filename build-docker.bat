@echo off
echo ========================================
echo C语言Bug检测器 Docker构建脚本
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
    echo 警告: Docker Desktop未运行
    echo 请先启动Docker Desktop，然后重新运行此脚本
    echo.
    echo 启动Docker Desktop的方法:
    echo 1. 在开始菜单中搜索"Docker Desktop"
    echo 2. 点击启动Docker Desktop
    echo 3. 等待Docker Desktop完全启动（系统托盘图标变为绿色）
    echo 4. 重新运行此脚本
    pause
    exit /b 1
)

echo Docker Desktop正在运行，开始构建镜像...
echo.

echo 构建Docker镜像: lumiablack/c-detector:latest
docker build -t lumiablack/c-detector:latest .

if %errorlevel% neq 0 (
    echo 错误: Docker镜像构建失败
    pause
    exit /b 1
)

echo.
echo 构建成功！正在标记镜像...
docker tag lumiablack/c-detector:latest lumiablack/c-detector:1.1.0

echo.
echo 检查构建的镜像...
docker images lumiablack/c-detector

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 镜像信息:
echo - 镜像名称: lumiablack/c-detector
echo - 标签: latest, 1.1.0
echo - 大小: 请查看上面的镜像列表
echo.
echo 下一步操作:
echo 1. 登录Docker Hub: docker login
echo 2. 推送镜像: docker push lumiablack/c-detector:latest
echo 3. 推送版本标签: docker push lumiablack/c-detector:1.1.0
echo.
pause
