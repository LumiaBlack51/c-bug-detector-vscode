# C语言Bug检测器 Docker镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers \
    git \
    curl

# 创建Python符号链接
RUN ln -sf python3 /usr/bin/python

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip3 install --break-system-packages -r core/requirements.txt

# 安装Node.js依赖
RUN cd vscode-extension && npm install

# 编译TypeScript代码
RUN cd vscode-extension && npm run compile

# 设置环境变量
ENV NODE_ENV=production
ENV PYTHONPATH=/app/core
ENV PATH="/app/tools:${PATH}"

# 创建非root用户
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# 更改文件所有权
RUN chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 暴露端口（如果需要Web服务）
EXPOSE 3000

# 设置默认命令
CMD ["node", "vscode-extension/out/extension.js"]

# 添加标签
LABEL maintainer="LumiaBlack <lumiablack@example.com>"
LABEL description="C语言Bug检测器 - 专为初学者设计的静态分析工具"
LABEL version="1.1.0"
LABEL repository="https://github.com/LumiaBlack51/c-bug-detector-vscode"
