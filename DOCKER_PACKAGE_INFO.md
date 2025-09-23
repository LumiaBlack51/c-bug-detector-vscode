# C语言Bug检测器 Docker部署包

## 文件清单

本部署包包含以下文件：

1. **Dockerfile** - Docker镜像构建文件
2. **.dockerignore** - Docker构建忽略文件
3. **build-docker.bat** - Windows构建脚本
4. **push-docker.bat** - Windows推送脚本
5. **DOCKER_README.md** - Docker使用说明
6. **DOCKER_DEPLOYMENT_GUIDE.md** - 详细部署指南

## 快速开始

### 1. 确保Docker Desktop运行

```bash
# 检查Docker状态
docker --version
docker info
```

如果Docker Desktop未运行，请启动它并等待完全启动。

### 2. 构建镜像

```bash
# 使用脚本构建
build-docker.bat

# 或手动构建
docker build -t lumiablack/c-detector:latest .
docker tag lumiablack/c-detector:latest lumiablack/c-detector:1.1.0
```

### 3. 推送镜像

```bash
# 使用脚本推送
push-docker.bat

# 或手动推送
docker login
docker push lumiablack/c-detector:latest
docker push lumiablack/c-detector:1.1.0
```

## 镜像特性

- **基础镜像**: node:18-alpine
- **包含组件**: Node.js + Python + TypeScript + 所有依赖
- **安全**: 非root用户运行
- **优化**: 多阶段构建，最小化镜像大小
- **功能**: 完整的C语言bug检测功能

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

# 分析C文件
docker run -it -v $(pwd):/app/workspace lumiablack/c-detector:latest \
  python core/main.py /app/workspace/test.c
```

## 检测功能

1. **内存安全卫士**
   - 内存泄漏检测
   - 空指针解引用检测
   - 野指针解引用检测

2. **变量状态监察官**
   - 未初始化变量检测
   - 变量作用域分析

3. **标准库使用助手**
   - printf/scanf使用检测
   - 头文件包含检测

4. **数值与控制流分析器**
   - 死循环检测
   - 类型溢出检测
   - 控制流分析

## 故障排除

### Docker Desktop未运行

```
错误: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"
解决: 启动Docker Desktop并等待完全启动
```

### 构建失败

```
错误: failed to solve: failed to read dockerfile
解决: 确保Dockerfile在当前目录
```

### 推送失败

```
错误: denied: requested access to the resource is denied
解决: 检查Docker Hub登录状态和权限
```

## 验证部署

访问Docker Hub查看镜像:
https://hub.docker.com/repository/docker/lumiablack/c-detector/general

## 支持

- GitHub: https://github.com/LumiaBlack51/c-bug-detector-vscode
- Docker Hub: https://hub.docker.com/repository/docker/lumiablack/c-detector/general
