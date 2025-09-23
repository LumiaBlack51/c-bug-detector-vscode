# C语言Bug检测器 Docker镜像

## 概述

这是C语言Bug检测器的Docker容器化版本，包含了完整的检测环境和所有依赖。

## 镜像信息

- **镜像名称**: `lumiablack/c-detector`
- **标签**: `latest`, `1.1.0`
- **基础镜像**: `node:18-alpine`
- **大小**: 约200MB（压缩后）

## 快速开始

### 1. 拉取镜像

```bash
docker pull lumiablack/c-detector:latest
```

### 2. 运行容器

```bash
# 交互式运行
docker run -it lumiablack/c-detector:latest

# 挂载本地目录进行分析
docker run -it -v /path/to/your/c/files:/app/workspace lumiablack/c-detector:latest

# 后台运行
docker run -d --name c-detector lumiablack/c-detector:latest
```

## 使用方法

### 分析单个C文件

```bash
# 进入容器
docker exec -it c-detector sh

# 运行检测器
node vscode-extension/out/extension.js /app/workspace/your_file.c
```

### 分析整个工作区

```bash
# 分析工作区所有C文件
node vscode-extension/out/extension.js /app/workspace/
```

### 使用Python后端

```bash
# 使用Python后端检测
python core/main.py /app/workspace/your_file.c
```

## 环境变量

- `NODE_ENV`: 设置为 `production`
- `PYTHONPATH`: 设置为 `/app/core`
- `PATH`: 包含 `/app/tools`

## 包含的组件

### Node.js/TypeScript前端
- VSCode扩展
- 检测面板
- 结果提供器

### Python后端
- 内存安全检测
- 变量状态检测
- 标准库使用检测
- 数值控制流分析

### 工具
- 安装脚本
- 设置脚本
- 批处理文件

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

## 构建说明

### 本地构建

```bash
# 构建镜像
docker build -t lumiablack/c-detector:latest .

# 标记版本
docker tag lumiablack/c-detector:latest lumiablack/c-detector:1.1.0
```

### 推送到Docker Hub

```bash
# 登录Docker Hub
docker login

# 推送镜像
docker push lumiablack/c-detector:latest
docker push lumiablack/c-detector:1.1.0
```

## 故障排除

### 常见问题

1. **Docker Desktop未运行**
   - 启动Docker Desktop
   - 等待完全启动（系统托盘图标变绿）

2. **权限问题**
   - 确保Docker有足够权限
   - 在Linux上可能需要sudo

3. **网络问题**
   - 检查Docker Hub连接
   - 配置代理（如果需要）

### 日志查看

```bash
# 查看容器日志
docker logs c-detector

# 实时查看日志
docker logs -f c-detector
```

## 贡献

欢迎提交Issue和Pull Request！

- GitHub: https://github.com/LumiaBlack51/c-bug-detector-vscode
- Docker Hub: https://hub.docker.com/repository/docker/lumiablack/c-detector/general

## 许可证

本项目采用MIT许可证。
