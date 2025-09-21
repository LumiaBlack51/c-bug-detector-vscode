# 安装指南

## 🎯 安装方式选择

### 方式1: VS Code插件 (推荐)
适合日常开发使用，提供图形化界面和实时检测。

### 方式2: 命令行工具
适合批量处理、CI/CD集成和脚本自动化。

## 📱 VS Code插件安装

### 步骤1: 下载插件
1. 访问 [GitHub Releases](https://github.com/your-username/c-bug-detector/releases)
2. 下载最新版本的 `c-bug-detector-*.vsix` 文件

### 步骤2: 安装插件
1. 打开VS Code
2. 按 `Ctrl+Shift+P` (Windows/Linux) 或 `Cmd+Shift+P` (macOS) 打开命令面板
3. 输入 `Extensions: Install from VSIX...`
4. 选择下载的VSIX文件
5. 点击"安装"
6. 重启VS Code

### 步骤3: 配置后端
1. 确保已安装Python 3.7+
2. 克隆或下载项目源码
3. 安装Python依赖:
   ```bash
   pip install -r requirements.txt
   ```
4. 在VS Code设置中配置后端路径:
   - 搜索 "C Bug Detector"
   - 设置 `c-bug-detector.backendPath` 为 `../main.py` 的完整路径
   - 设置 `c-bug-detector.pythonPath` 为Python解释器路径

### 步骤4: 验证安装
1. 打开一个C文件
2. 按 `Ctrl+Shift+B` 或使用命令面板 `C Bug Detector: 分析当前C文件`
3. 查看Problems面板或插件侧边栏中的检测结果

## 💻 命令行工具安装

### 步骤1: 下载源码
```bash
git clone https://github.com/your-username/c-bug-detector.git
cd c-bug-detector
```

### 步骤2: 运行安装脚本
```bash
python install.py
```

### 步骤3: 验证安装
```bash
# 查看可用模块
python main.py --list-modules

# 测试检测功能
python main.py tests/test_memory_safety.c
```

## 🔧 系统要求

### 最低要求
- **Python**: 3.7+
- **VS Code**: 1.74.0+ (仅插件版本)
- **内存**: 512MB RAM
- **磁盘**: 100MB 可用空间

### 推荐配置
- **Python**: 3.9+
- **VS Code**: 最新版本
- **内存**: 2GB+ RAM
- **磁盘**: 500MB+ 可用空间

## 🐛 故障排除

### 常见问题

#### 1. 插件安装失败
**问题**: VSIX文件无法安装
**解决方案**:
- 确保VS Code版本 >= 1.74.0
- 检查VSIX文件是否完整下载
- 尝试手动安装: `code --install-extension c-bug-detector-*.vsix`

#### 2. 后端检测器无法启动
**问题**: 检测时提示"启动检测器失败"
**解决方案**:
- 检查Python是否正确安装: `python --version`
- 检查依赖是否安装: `pip list | grep regex`
- 检查后端路径配置是否正确

#### 3. 检测结果为空
**问题**: 检测后没有显示任何问题
**解决方案**:
- 确保文件是C文件 (.c扩展名)
- 检查模块是否启用
- 尝试使用测试文件: `python main.py tests/test_memory_safety.c`

#### 4. 权限错误
**问题**: 无法写入文件或执行命令
**解决方案**:
- 确保有足够的文件系统权限
- 在Windows上以管理员身份运行
- 检查防病毒软件是否阻止了执行

### 日志调试

#### 启用调试模式
```bash
# 命令行工具调试
python main.py <file.c> --verbose

# VS Code插件调试
# 打开开发者工具 (Help > Toggle Developer Tools)
# 查看Console中的错误信息
```

#### 检查依赖
```bash
# 检查Python包
pip list | grep -E "(regex|colorama|click)"

# 检查Node.js包 (插件开发)
cd vscode-extension
npm list
```

## 🔄 更新

### 插件更新
1. 下载新版本的VSIX文件
2. 卸载旧版本插件
3. 安装新版本插件
4. 重启VS Code

### 命令行工具更新
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新运行安装脚本
python install.py
```

## 📞 获取帮助

### 支持渠道
- **GitHub Issues**: [报告问题](https://github.com/your-username/c-bug-detector/issues)
- **GitHub Discussions**: [讨论功能](https://github.com/your-username/c-bug-detector/discussions)
- **文档**: 查看项目README和Wiki

### 贡献
欢迎贡献代码、报告问题或提出建议！

---

**安装过程中遇到问题？请查看故障排除部分或提交Issue！** 🛠️
