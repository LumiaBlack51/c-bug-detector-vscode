# C Bug Detector VS Code Extension

这是C语言Bug检测器的VS Code扩展插件。

## 📁 文件结构

```
vscode-extension/
├── README.md              # 本文件
├── package.json           # 扩展配置和元数据
├── tsconfig.json          # TypeScript配置
├── src/                   # TypeScript源代码
│   ├── extension.ts       # 扩展主入口
│   ├── backend.ts         # Python后端接口
│   ├── resultsProvider.ts # 结果提供器
│   └── detectionPanel.ts  # 检测面板
├── out/                   # 编译后的JavaScript
├── backend/                # 内置Python后端
│   ├── main.py
│   ├── requirements.txt
│   ├── modules/
│   └── utils/
├── media/                  # 扩展资源
│   └── icon.svg
├── scripts/                # 构建脚本
│   └── copy-backend.js
└── c-bug-detector-1.0.0.vsix # 打包后的扩展文件
```

## 🚀 快速开始

### 安装扩展
1. **下载VSIX文件**
   - 从 [Releases](../../releases/) 下载最新版本
   - 或从项目根目录获取 `c-bug-detector-1.0.0.vsix`

2. **安装到VS Code**
   - 在VS Code中按 `Ctrl+Shift+P` 打开命令面板
   - 输入 `Extensions: Install from VSIX...`
   - 选择下载的VSIX文件
   - 重启VS Code

3. **验证安装**
   - 打开一个C文件
   - 按 `Ctrl+Shift+B` 测试检测功能
   - 检查Problems面板中的结果

### 使用扩展
- **一键检测**: 按 `Ctrl+Shift+B` 检测当前C文件
- **工作区检测**: 使用命令面板检测所有C文件
- **自定义面板**: 打开专门的检测面板
- **问题查看**: 在Problems面板中查看检测结果

## 🎯 功能特性

### 核心功能
- ✅ **实时检测**: 支持C文件的实时Bug检测
- ✅ **多模块支持**: 内存安全、变量状态、标准库、数值控制流
- ✅ **智能提示**: 提供详细的错误信息和修复建议
- ✅ **一键修复**: 支持某些问题的自动修复

### 用户界面
- 🖥️ **Problems面板**: 在VS Code的Problems面板中显示检测结果
- 🌳 **侧边栏视图**: 自定义的树形视图显示检测结果
- 🎛️ **检测面板**: 专门的Webview面板进行检测操作
- ⌨️ **快捷键支持**: `Ctrl+Shift+B` 快速检测

### 配置选项
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

## 🔧 开发指南

### 环境要求
- **Node.js**: 16.x+
- **TypeScript**: 4.9+
- **VS Code**: 1.74+
- **Python**: 3.7+ (用于后端)

### 开发设置
```bash
# 安装依赖
npm install

# 编译TypeScript
npm run compile

# 复制Python后端文件
npm run copy-backend

# 打包扩展
vsce package
```

### 调试扩展
1. 在VS Code中按 `F5` 启动调试
2. 在新窗口中测试扩展功能
3. 使用开发者工具查看日志

## 🏗️ 架构设计

### 前端 (TypeScript)
- **extension.ts**: 扩展主入口，注册命令和视图
- **backend.ts**: Python后端接口，处理进程通信
- **resultsProvider.ts**: 结果提供器，管理检测结果显示
- **detectionPanel.ts**: 检测面板，提供Webview界面

### 后端 (Python)
- **main.py**: 主检测器，协调各模块工作
- **modules/**: 检测模块集合
- **utils/**: 工具模块集合

### 通信机制
- 使用 `child_process.spawn` 启动Python进程
- 通过标准输入/输出进行数据交换
- JSON格式传输检测结果

## 📊 检测模块

### 1. 内存安全模块
- **功能**: 检测内存泄漏、野指针、空指针解引用
- **检测内容**: `malloc`/`free` 不匹配、使用已释放内存、空指针操作

### 2. 变量状态模块
- **功能**: 检测变量未初始化和作用域问题
- **检测内容**: 未初始化变量使用、作用域错误、局部指针返回

### 3. 标准库模块
- **功能**: 检测头文件和库函数使用问题
- **检测内容**: 缺失头文件、`printf`/`scanf` 参数不匹配、`scanf` 缺少 `&`

### 4. 数值控制流模块
- **功能**: 检测数值溢出和死循环
- **检测内容**: 类型溢出、死循环、无限循环

## 🎨 用户界面

### Problems面板集成
- 检测结果直接显示在VS Code的Problems面板中
- 支持错误、警告、信息等不同严重级别
- 点击问题可跳转到对应代码行

### 自定义侧边栏视图
- 树形结构显示检测结果
- 按文件分组显示问题
- 支持展开/折叠查看详情

### 检测面板
- Webview界面提供更丰富的交互
- 支持批量检测操作
- 实时显示检测进度

## 🔄 更新和维护

### 更新Python后端
1. 修改 `core/` 目录中的Python代码
2. 运行 `npm run copy-backend` 复制文件
3. 重新编译和打包扩展
4. 发布新版本

### 更新TypeScript前端
1. 修改 `src/` 目录中的TypeScript代码
2. 运行 `npm run compile` 编译
3. 测试功能
4. 打包和发布

## 🐛 故障排除

### 常见问题
1. **后端检测器不存在**: 检查Python路径配置
2. **检测失败**: 检查Python环境和依赖
3. **扩展无法启动**: 检查VS Code版本兼容性

### 解决方案
- 查看 [插件安装修复文档](../../docs/PLUGIN_INSTALLATION_FIX.md)
- 检查VS Code开发者工具中的错误信息
- 验证Python环境和依赖安装

## 📈 性能优化

### 检测速度
- 单文件检测: < 1秒
- 大型项目: < 10秒
- 内存使用: < 100MB

### 优化策略
- 增量检测: 只检测修改的文件
- 缓存机制: 缓存检测结果
- 异步处理: 非阻塞的检测过程

## 🔮 未来规划

### 短期目标
- 🎨 改进用户界面
- 📈 提高检测准确率
- 🔧 优化性能

### 长期目标
- 🌐 支持更多C标准
- 🔌 插件系统
- ☁️ 云端检测服务

## 📞 支持与反馈

### 问题报告
- [GitHub Issues](https://github.com/your-username/c-bug-detector/issues)
- 邮件支持: support@example.com

### 功能请求
- 通过GitHub Issues提交
- 详细描述需求和使用场景

## 📄 许可证

扩展遵循与项目相同的 [MIT许可证](../../LICENSE)。

## 🙏 致谢

感谢VS Code团队提供的优秀扩展平台和丰富的API支持。

---

**C Bug Detector VS Code Extension - 让C语言编程更安全、更简单！** 🚀✨
