# C语言Bug检测器 VS Code插件

## 🎯 插件特色

### 专为初学者设计
- **图形化界面**: 直观的检测面板，一键检测C代码
- **实时问题显示**: 检测结果同时显示在Problems面板和插件窗口中
- **快捷键支持**: Ctrl+Shift+B 快速分析当前C文件
- **可插拔后端**: 后端检测器可独立更新，前端界面无需修改

### 功能特性
- 🔒 **内存安全卫士**: 检测内存泄漏、野指针、空指针解引用
- 📊 **变量状态监察官**: 检测变量未初始化即使用和变量作用域问题
- 📚 **标准库使用助手**: 检测缺失头文件、头文件拼写错误，检查常用函数参数
- 🔢 **数值与控制流分析器**: 检测类型溢出和死循环

## 🚀 安装方法

### 方法1: 从VSIX文件安装
1. 下载 `c-bug-detector-1.0.0.vsix` 文件
2. 在VS Code中按 `Ctrl+Shift+P` 打开命令面板
3. 输入 `Extensions: Install from VSIX...`
4. 选择下载的VSIX文件
5. 重启VS Code

### 方法2: 从源码安装
1. 克隆项目到本地
2. 安装后端依赖: `pip install -r requirements.txt`
3. 进入插件目录: `cd vscode-extension`
4. 安装插件依赖: `npm install`
5. 编译插件: `npm run compile`
6. 打包插件: `vsce package`
7. 安装生成的VSIX文件

## 📖 使用方法

### 基本操作
1. **分析当前文件**: 
   - 打开一个C文件
   - 按 `Ctrl+Shift+B` 或使用命令面板 `C Bug Detector: 分析当前C文件`

2. **分析工作区**:
   - 使用命令面板 `C Bug Detector: 分析工作区所有C文件`

3. **查看检测面板**:
   - 使用命令面板 `C Bug Detector: 显示检测面板`
   - 或在侧边栏点击C Bug Detector图标

4. **清除结果**:
   - 使用命令面板 `C Bug Detector: 清除检测结果`

### 配置选项
在VS Code设置中搜索 "C Bug Detector" 可以配置：

- `c-bug-detector.enableMemorySafety`: 启用内存安全卫士模块
- `c-bug-detector.enableVariableState`: 启用变量状态监察官模块
- `c-bug-detector.enableStandardLibrary`: 启用标准库使用助手模块
- `c-bug-detector.enableNumericControlFlow`: 启用数值与控制流分析器模块
- `c-bug-detector.pythonPath`: Python解释器路径
- `c-bug-detector.backendPath`: 后端检测器路径

## 🔧 后端架构

### 可插拔设计
插件采用可插拔的后端架构，具有以下优势：

1. **独立更新**: 后端检测器可以独立更新，无需修改前端代码
2. **灵活配置**: 可以轻松切换不同的检测引擎
3. **易于扩展**: 添加新的检测模块只需要更新后端

### 后端接口
```typescript
interface BugReport {
    line_number: number;
    error_type: string;
    severity: string;
    message: string;
    suggestion: string;
    code_snippet: string;
    module_name: string;
}

interface AnalysisResult {
    file_path: string;
    reports: BugReport[];
    success: boolean;
    error?: string;
}
```

### 后端通信
- 使用Python子进程调用后端检测器
- JSON格式的数据交换
- 支持模块启用/禁用参数传递

## 🎨 界面说明

### 检测面板
- **分析按钮**: 一键分析当前文件或整个工作区
- **结果展示**: 按文件分组显示检测结果
- **问题详情**: 显示问题类型、位置、描述和修复建议
- **模块标识**: 清楚标识问题来源模块

### Problems面板集成
- 检测结果自动显示在VS Code的Problems面板中
- 支持点击跳转到问题位置
- 提供详细的错误信息和修复建议

### 侧边栏视图
- 专门的C Bug Detector侧边栏
- 树形结构展示检测结果
- 支持展开/折叠文件视图

## 🛠️ 开发说明

### 项目结构
```
vscode-extension/
├── src/
│   ├── extension.ts          # 插件主入口
│   ├── backend.ts            # 后端接口
│   ├── resultsProvider.ts    # 结果提供者
│   └── detectionPanel.ts     # 检测面板
├── media/
│   └── icon.svg              # 插件图标
├── package.json              # 插件配置
└── tsconfig.json             # TypeScript配置
```

### 开发命令
```bash
# 安装依赖
npm install

# 编译插件
npm run compile

# 监听模式编译
npm run watch

# 打包插件
vsce package
```

## 🔮 未来计划

### 短期目标
- [ ] 优化检测准确性
- [ ] 添加更多检测规则
- [ ] 支持自定义检测规则

### 长期目标
- [ ] 支持实时检测
- [ ] 添加自动修复功能
- [ ] 支持更多编程语言

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

---

**让C语言学习更简单，让bug无处藏身！** 🐛✨
