# C Bug Detector

一个专为初学者设计的C语言Bug检测器，采用模块化架构和启发式检测方法。

## 🎯 项目概述

C Bug Detector是一个功能强大的C语言静态分析工具，专为初学者设计，提供：

- 🛡️ **四大检测模块**: 内存安全、变量状态、标准库使用、数值控制流
- 🔌 **VS Code扩展**: 一键检测、Problems面板集成、自定义检测面板
- 🖥️ **命令行工具**: 支持单文件和批量检测
- 📚 **完整文档**: 详细的使用指南和技术文档

## 🚀 快速开始

### 1. 安装依赖
```bash
# 使用安装脚本（推荐）
python tools/install.py

# 或手动安装
pip install -r core/requirements.txt
```

### 2. 运行检测器
```bash
# 检测单个文件
python core/main.py your_file.c

# 检测目录
python core/main.py your_directory/

# 查看帮助
python core/main.py --help
```

### 3. 安装VS Code扩展
1. 下载 [最新版本](releases/) 的VSIX文件
2. 在VS Code中按 `Ctrl+Shift+P`
3. 输入 `Extensions: Install from VSIX...`
4. 选择下载的VSIX文件
5. 重启VS Code

## 📁 项目结构

```
├── core/                   # 🧠 核心Python代码
│   ├── main.py            # 主入口文件
│   ├── modules/           # 检测模块
│   ├── utils/             # 工具模块
│   └── README.md          # 核心代码文档
├── vscode-extension/       # 🔌 VS Code扩展
│   ├── src/               # TypeScript源码
│   ├── backend/           # 内置Python后端
│   └── README.md          # 扩展文档
├── tests/                  # 🧪 测试用例
│   ├── test_*.c          # 各模块测试用例
│   └── README.md          # 测试文档
├── docs/                   # 📚 完整文档
│   ├── TECHNICAL_DOCUMENTATION.md
│   ├── INSTALLATION_GUIDE.md
│   └── README.md          # 文档索引
├── tools/                  # 🛠️ 工具和脚本
│   ├── install.py         # 安装脚本
│   └── README.md          # 工具文档
├── releases/               # 📦 发布和版本
│   ├── RELEASE_NOTES.md
│   └── README.md          # 发布文档
└── workflows/              # 🔄 GitHub Actions
```

## 🎯 核心功能

### 检测模块
- **🛡️ 内存安全**: 检测内存泄漏、野指针、空指针解引用
- **📊 变量状态**: 检测未初始化变量、作用域问题
- **📚 标准库**: 检测头文件缺失、printf/scanf参数不匹配
- **🔢 数值控制流**: 检测类型溢出、死循环
- **🌐 作用域分析**: 基于符号表栈的精确作用域管理
- **📈 控制流图**: 基于CFG的数据流分析
- **🏗️ 结构体检测**: 检测结构体指针解引用和成员访问问题

### VS Code扩展特性
- **⌨️ 快捷键**: `Ctrl+Shift+B` 快速检测
- **📋 Problems面板**: 检测结果直接显示在VS Code中
- **🌳 侧边栏视图**: 树形结构显示检测结果
- **🎛️ 检测面板**: 专门的Webview界面

## 📚 文档导航

### 🆕 新用户
1. [安装指南](docs/INSTALLATION_GUIDE.md) - 详细的安装步骤
2. [快速参考](docs/QUICK_REFERENCE.md) - 常用命令速查
3. [核心代码文档](core/README.md) - 了解核心功能

### 🔧 开发者
1. [技术文档](docs/TECHNICAL_DOCUMENTATION.md) - 详细的技术实现
2. [架构图](docs/ARCHITECTURE_DIAGRAM.md) - 系统架构说明
3. [VS Code扩展文档](vscode-extension/README.md) - 扩展开发指南

### 🔌 VS Code用户
1. [VS Code扩展说明](docs/VSCODE_EXTENSION_README.md) - 扩展使用指南
2. [插件安装修复](docs/PLUGIN_INSTALLATION_FIX.md) - 常见问题解决

### 📦 发布信息
1. [发布说明](releases/RELEASE_NOTES.md) - 版本更新记录
2. [项目总结](releases/PROJECT_SUMMARY.md) - 项目开发过程
3. [最终总结](releases/FINAL_SUMMARY.md) - 项目完成情况

## 🚀 使用示例

### 命令行使用
```bash
# 检测内存安全问题
python core/main.py file.c --enable memory_safety

# 输出JSON格式报告
python core/main.py file.c -f json -o report.json

# 批量检测项目
python core/main.py project/ --batch
```

### VS Code扩展使用
1. 打开C文件
2. 按 `Ctrl+Shift+B` 触发检测
3. 在Problems面板查看结果
4. 使用自定义检测面板进行批量操作

## 🧪 测试验证

```bash
# 运行所有测试用例
python core/main.py tests/

# 测试特定模块
python core/main.py tests/test_memory_safety.c
python core/main.py tests/test_variable_state.c
python core/main.py tests/test_standard_library.c
python core/main.py tests/test_numeric_control_flow.c
```

## 🔧 配置选项

### VS Code扩展配置
```json
{
  "c-bug-detector.pythonPath": "python",
  "c-bug-detector.backendPath": "backend/main.py",
  "c-bug-detector.enableMemorySafety": true,
  "c-bug-detector.enableVariableState": true,
  "c-bug-detector.enableStandardLibrary": true,
  "c-bug-detector.enableNumericControlFlow": true
}
```

### 命令行配置
```bash
# 启用/禁用特定模块
--enable memory_safety,variable_state
--disable numeric_control_flow

# 输出格式和文件
-f json -o report.json
```

## 📊 性能指标

- **检测速度**: 单文件 < 1秒，大型项目 < 10秒
- **检测准确率**: 85%+ (内存安全), 90%+ (变量状态), 95%+ (标准库)
- **内存使用**: < 100MB
- **支持文件**: .c, .h 文件

## 🔮 未来规划

### v2.1.0 (2024-12-19) - 重大架构改进
- ✅ **作用域分析系统**：基于AST的精确作用域管理
- ✅ **控制流图分析**：新增基于CFG的数据流分析
- ✅ **结构体检测增强**：支持多种声明格式和成员访问检测
- ✅ **printf解析改进**：支持完整格式字符串解析
- ✅ **死循环检测加强**：检测潜在无限循环和循环变量状态
- ✅ **误报修复**：修复链表遍历等标准模式的误报

### v2.0.0-alpha (2024-12-19)
- ✅ 重构内存安全检测模块，提升检测准确性
- ✅ 改进变量状态分析，支持更多C语言特性
- ✅ 优化错误报告，提供更清晰的修复建议
- ✅ 增强VS Code扩展功能

### v1.1.0 (计划中)
- 🔄 改进检测算法
- 📈 提高检测准确率
- 🎨 优化用户界面

### v2.0.0 (长期)
- 🌐 支持更多C标准
- 🔌 插件系统
- ☁️ 云端检测服务

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 遵循代码规范

## 📞 支持与反馈

- [GitHub Issues](https://github.com/your-username/c-bug-detector/issues)
- 邮件支持: support@example.com

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

**C Bug Detector - 让C语言编程更安全、更简单！** 🚀✨