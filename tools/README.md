# C Bug Detector Tools

这是C语言Bug检测器的工具和脚本集合。

## 📁 文件结构

```
tools/
├── install.py              # Python依赖安装脚本
├── cbug-detector.bat       # Windows批处理启动脚本
├── setup-github.ps1        # PowerShell GitHub设置脚本
└── setup-github.sh         # Bash GitHub设置脚本
```

## 🛠️ 工具说明

### 1. 安装脚本 (install.py)
**功能**: 零配置安装Python依赖和创建启动脚本

**使用方法**:
```bash
python install.py
```

**功能特性**:
- 自动检测Python环境
- 安装所有必需的依赖包
- 创建Windows批处理文件
- 创建Unix shell脚本
- 验证安装结果

**依赖包**:
- `regex`: 高级正则表达式支持
- `colorama`: 彩色终端输出
- `click`: 命令行界面增强
- `pycparser`: C代码AST解析（可选）
- `pytest`: 测试框架
- `pytest-cov`: 测试覆盖率
- `coverage`: 代码覆盖率分析

### 2. Windows启动脚本 (cbug-detector.bat)
**功能**: Windows环境下的快速启动脚本

**使用方法**:
```batch
cbug-detector.bat your_file.c
cbug-detector.bat your_directory/
```

**功能特性**:
- 自动激活Python环境
- 支持文件参数传递
- 错误处理和用户提示
- 彩色输出支持

### 3. GitHub设置脚本

#### PowerShell版本 (setup-github.ps1)
**功能**: Windows PowerShell环境下的GitHub仓库设置

**使用方法**:
```powershell
.\setup-github.ps1
```

**功能特性**:
- 初始化Git仓库
- 添加所有文件到Git
- 创建初始提交
- 设置远程仓库
- 推送到GitHub

#### Bash版本 (setup-github.sh)
**功能**: Unix/Linux/macOS环境下的GitHub仓库设置

**使用方法**:
```bash
chmod +x setup-github.sh
./setup-github.sh
```

**功能特性**:
- 跨平台兼容
- 自动权限设置
- 错误处理
- 用户确认提示

## 🚀 快速开始

### 首次安装
```bash
# 1. 安装依赖
python install.py

# 2. 设置GitHub仓库（可选）
# Windows
.\setup-github.ps1

# Unix/Linux/macOS
./setup-github.sh
```

### 日常使用
```bash
# Windows
cbug-detector.bat your_file.c

# 或直接使用Python
python ../core/main.py your_file.c
```

## 🔧 配置选项

### 安装脚本配置
```python
# install.py 中的配置
REQUIREMENTS_FILE = "requirements.txt"
BATCH_FILE = "cbug-detector.bat"
SHELL_FILE = "cbug-detector.sh"
```

### 启动脚本配置
```batch
# cbug-detector.bat 中的配置
PYTHON_CMD = "python"
MAIN_SCRIPT = "../core/main.py"
```

## 🧪 测试工具

### 验证安装
```bash
# 测试Python环境
python --version

# 测试依赖包
python -c "import regex, colorama, click; print('All packages installed successfully!')"

# 测试检测器
python ../core/main.py --list-modules
```

### 功能测试
```bash
# 测试批处理脚本
cbug-detector.bat ../tests/test_memory_safety.c

# 测试GitHub设置
.\setup-github.ps1
```

## 🔄 维护和更新

### 更新依赖
```bash
# 更新requirements.txt
pip freeze > requirements.txt

# 重新安装
python install.py
```

### 更新脚本
1. 修改脚本文件
2. 测试功能
3. 更新文档
4. 提交变更

## 📝 注意事项

### 环境要求
- **Python**: 3.7+
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **权限**: 需要写入权限创建脚本文件

### 常见问题
1. **Python未找到**: 确保Python已安装并添加到PATH
2. **权限不足**: 以管理员身份运行安装脚本
3. **网络问题**: 检查网络连接和防火墙设置

### 故障排除
```bash
# 检查Python环境
where python
python --version

# 检查pip
pip --version

# 检查网络连接
ping pypi.org
```

## 🔗 相关文档

- [核心代码文档](../core/README.md)
- [安装指南](../docs/INSTALLATION_GUIDE.md)
- [技术文档](../docs/TECHNICAL_DOCUMENTATION.md)
- [快速参考](../docs/QUICK_REFERENCE.md)

## 📄 许可证

工具脚本遵循与项目相同的 [MIT许可证](../LICENSE)。
