# C语言Bug检测器 Docker部署指南

## 前提条件

1. **Docker Desktop已安装并运行**
   - 下载地址: https://www.docker.com/products/docker-desktop/
   - 确保Docker Desktop完全启动（系统托盘图标为绿色）

2. **Docker Hub账户**
   - 注册地址: https://hub.docker.com/
   - 用户名: lumiablack

## 部署步骤

### 步骤1: 启动Docker Desktop

```bash
# Windows
start "Docker Desktop" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 等待启动完成（约30-60秒）
# 检查状态
docker info
```

### 步骤2: 构建Docker镜像

```bash
# 构建镜像
docker build -t lumiablack/c-detector:latest .

# 标记版本
docker tag lumiablack/c-detector:latest lumiablack/c-detector:1.1.0

# 查看构建的镜像
docker images lumiablack/c-detector
```

### 步骤3: 测试镜像

```bash
# 测试运行
docker run --rm lumiablack/c-detector:latest node --version
docker run --rm lumiablack/c-detector:latest python --version

# 交互式测试
docker run -it --rm lumiablack/c-detector:latest sh
```

### 步骤4: 登录Docker Hub

```bash
# 登录Docker Hub
docker login

# 输入用户名: lumiablack
# 输入密码: [您的Docker Hub密码]
```

### 步骤5: 推送镜像

```bash
# 推送latest标签
docker push lumiablack/c-detector:latest

# 推送版本标签
docker push lumiablack/c-detector:1.1.0
```

## 自动化脚本

### Windows批处理脚本

1. **build-docker.bat** - 构建镜像
2. **push-docker.bat** - 推送镜像

使用方法:
```cmd
# 构建
build-docker.bat

# 推送
push-docker.bat
```

## 镜像信息

- **仓库**: lumiablack/c-detector
- **标签**: latest, 1.1.0
- **大小**: 约200MB
- **基础镜像**: node:18-alpine
- **架构**: linux/amd64

## 使用方法

### 拉取镜像

```bash
docker pull lumiablack/c-detector:latest
```

### 运行容器

```bash
# 基本运行
docker run -it lumiablack/c-detector:latest

# 挂载工作目录
docker run -it -v /path/to/c/files:/app/workspace lumiablack/c-detector:latest

# 后台运行
docker run -d --name c-detector lumiablack/c-detector:latest
```

### 分析C文件

```bash
# 进入容器
docker exec -it c-detector sh

# 分析文件
node vscode-extension/out/extension.js /app/workspace/test.c
python core/main.py /app/workspace/test.c
```

## 故障排除

### 常见问题

1. **Docker Desktop未运行**
   ```
   错误: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"
   解决: 启动Docker Desktop并等待完全启动
   ```

2. **构建失败**
   ```
   错误: failed to solve: failed to read dockerfile
   解决: 确保Dockerfile在当前目录
   ```

3. **推送失败**
   ```
   错误: denied: requested access to the resource is denied
   解决: 检查Docker Hub登录状态和权限
   ```

### 检查命令

```bash
# 检查Docker状态
docker --version
docker info

# 检查镜像
docker images lumiablack/c-detector

# 检查容器
docker ps -a

# 检查日志
docker logs c-detector
```

## 验证部署

### 1. 检查Docker Hub

访问: https://hub.docker.com/repository/docker/lumiablack/c-detector/general

### 2. 测试拉取

```bash
# 从其他机器测试
docker pull lumiablack/c-detector:latest
docker run --rm lumiablack/c-detector:latest echo "Hello from C Detector!"
```

### 3. 功能测试

```bash
# 创建测试文件
echo 'int main() { int x; printf("%d", x); return 0; }' > test.c

# 运行检测
docker run -it -v $(pwd):/app/workspace lumiablack/c-detector:latest \
  python core/main.py /app/workspace/test.c
```

## 维护

### 更新镜像

1. 修改代码
2. 重新构建: `docker build -t lumiablack/c-detector:latest .`
3. 推送更新: `docker push lumiablack/c-detector:latest`

### 版本管理

```bash
# 创建新版本
docker tag lumiablack/c-detector:latest lumiablack/c-detector:1.2.0
docker push lumiablack/c-detector:1.2.0
```

## 支持

- GitHub: https://github.com/LumiaBlack51/c-bug-detector-vscode
- Docker Hub: https://hub.docker.com/repository/docker/lumiablack/c-detector/general
- 问题反馈: 请在GitHub上提交Issue
