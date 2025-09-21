# GitHub仓库设置指南

## 🚀 快速设置GitHub仓库

### 1. 创建GitHub仓库
1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 仓库名称: `c-bug-detector`
5. 描述: `A C language bug detector for beginners with modular architecture`
6. 选择 "Public" 或 "Private"
7. **不要**勾选 "Initialize this repository with a README"
8. 点击 "Create repository"

### 2. 设置本地仓库
```bash
# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/c-bug-detector.git

# 推送到GitHub
git push -u origin master
```

### 3. 使用自动化脚本
```bash
# Windows PowerShell
.\tools\setup-github.ps1

# Unix/Linux/macOS
./tools/setup-github.sh
```

## 📋 仓库信息

### 仓库名称
`c-bug-detector`

### 仓库描述
`A C language bug detector for beginners with modular architecture`

### 标签
- `c-language`
- `bug-detector`
- `static-analysis`
- `vscode-extension`
- `python`
- `typescript`
- `beginner-friendly`

### 许可证
MIT License

## 🔧 自动化设置

### PowerShell脚本 (Windows)
```powershell
# 运行设置脚本
.\tools\setup-github.ps1

# 脚本会自动：
# 1. 初始化Git仓库
# 2. 添加所有文件
# 3. 创建初始提交
# 4. 设置远程仓库
# 5. 推送到GitHub
```

### Bash脚本 (Unix/Linux/macOS)
```bash
# 给脚本执行权限
chmod +x tools/setup-github.sh

# 运行设置脚本
./tools/setup-github.sh

# 脚本会自动：
# 1. 初始化Git仓库
# 2. 添加所有文件
# 3. 创建初始提交
# 4. 设置远程仓库
# 5. 推送到GitHub
```

## 📦 发布设置

### GitHub Actions
项目已配置GitHub Actions工作流：
- 自动构建VS Code扩展
- 创建GitHub Release
- 上传VSIX文件

### 触发发布
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions会自动：
# 1. 构建VS Code扩展
# 2. 创建GitHub Release
# 3. 上传VSIX文件
```

## 🔄 日常使用

### 提交更改
```bash
# 添加更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到GitHub
git push origin master
```

### 创建分支
```bash
# 创建新分支
git checkout -b feature/new-feature

# 提交更改
git add .
git commit -m "添加新功能"

# 推送分支
git push origin feature/new-feature

# 创建Pull Request
# 在GitHub网页上创建PR
```

## 📚 仓库结构

### 主要文件夹
- `core/` - 核心Python代码
- `vscode-extension/` - VS Code扩展
- `tests/` - 测试用例
- `docs/` - 完整文档
- `tools/` - 工具和脚本
- `releases/` - 发布信息

### 重要文件
- `README.md` - 项目主文档
- `LICENSE` - MIT许可证
- `.gitignore` - Git忽略文件
- `core/requirements.txt` - Python依赖

## 🎯 仓库特性

### 功能特性
- ✅ 模块化C语言Bug检测
- ✅ VS Code扩展支持
- ✅ 命令行工具
- ✅ 完整文档系统
- ✅ 自动化CI/CD

### 技术栈
- **后端**: Python 3.7+
- **前端**: TypeScript
- **扩展**: VS Code Extension API
- **构建**: GitHub Actions
- **文档**: Markdown

## 🔗 相关链接

- [项目主页](https://github.com/YOUR_USERNAME/c-bug-detector)
- [Issues](https://github.com/YOUR_USERNAME/c-bug-detector/issues)
- [Releases](https://github.com/YOUR_USERNAME/c-bug-detector/releases)
- [Wiki](https://github.com/YOUR_USERNAME/c-bug-detector/wiki)

## 📞 支持

如果遇到问题，请：
1. 检查GitHub仓库是否存在
2. 确认你有推送权限
3. 检查网络连接
4. 查看GitHub文档

---

**设置完成后，你的C Bug Detector项目就可以在GitHub上公开访问了！** 🚀✨
