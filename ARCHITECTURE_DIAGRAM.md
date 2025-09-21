# C语言Bug检测器架构图

## 🏗️ 系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code 插件层                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Extension │  │   Backend   │  │   Results   │  │Detection│ │
│  │   (主入口)   │  │  (后端接口)  │  │  Provider   │  │  Panel  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ JSON通信
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Python 后端层                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │    Main     │  │   Memory    │  │  Variable   │  │Standard │ │
│  │  (主程序)    │  │   Safety    │  │   State     │  │Library  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Numeric   │  │   Error     │  │    Code     │              │
│  │  Control    │  │  Reporter   │  │   Parser    │              │
│  │    Flow     │  └─────────────┘  └─────────────┘              │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 数据流图

```
C文件输入
    │
    ▼
┌─────────────┐
│ Code Parser │ ──┐
└─────────────┘   │
    │             │
    ▼             │
┌─────────────┐   │
│ 检测模块1    │   │
└─────────────┘   │
    │             │
    ▼             │
┌─────────────┐   │
│ 检测模块2    │   │
└─────────────┘   │
    │             │
    ▼             │
┌─────────────┐   │
│ 检测模块3    │   │
└─────────────┘   │
    │             │
    ▼             │
┌─────────────┐   │
│ 检测模块4    │   │
└─────────────┘   │
    │             │
    ▼             │
┌─────────────┐   │
│Error Reporter│◄──┘
└─────────────┘
    │
    ▼
JSON输出
    │
    ▼
┌─────────────┐
│TypeScript   │
│Backend      │
└─────────────┘
    │
    ▼
┌─────────────┐
│Results      │
│Provider     │
└─────────────┘
    │
    ▼
┌─────────────┐  ┌─────────────┐
│Problems     │  │Detection    │
│Panel        │  │Panel        │
└─────────────┘  └─────────────┘
```

## 🔧 模块交互图

### TypeScript层交互
```
Extension.ts (主入口)
    │
    ├── Backend.ts (后端接口)
    │   ├── 调用Python子进程
    │   ├── 处理JSON数据
    │   └── 错误处理
    │
    ├── ResultsProvider.ts (结果提供者)
    │   ├── 管理检测结果
    │   ├── 更新Problems面板
    │   └── 提供树形视图
    │
    └── DetectionPanel.ts (检测面板)
        ├── Web界面
        ├── 用户交互
        └── 结果显示
```

### Python层交互
```
main.py (主程序)
    │
    ├── modules/memory_safety.py
    │   ├── 内存泄漏检测
    │   ├── 野指针检测
    │   └── 空指针检测
    │
    ├── modules/variable_state.py
    │   ├── 未初始化变量检测
    │   └── 变量作用域检测
    │
    ├── modules/standard_library.py
    │   ├── 头文件检测
    │   ├── 函数参数检测
    │   └── 拼写错误检测
    │
    ├── modules/numeric_control_flow.py
    │   ├── 类型溢出检测
    │   └── 死循环检测
    │
    └── utils/
        ├── error_reporter.py
        └── code_parser.py
```

## 🔌 接口设计

### 核心接口
```typescript
// 检测报告接口
interface BugReport {
    line_number: number;        // 行号
    error_type: string;         // 错误类型
    severity: string;           // 严重程度
    message: string;            // 错误消息
    suggestion: string;         // 修复建议
    code_snippet: string;       // 代码片段
    module_name: string;        // 模块名称
}

// 分析结果接口
interface AnalysisResult {
    file_path: string;          // 文件路径
    reports: BugReport[];       // 报告列表
    success: boolean;           // 是否成功
    error?: string;             // 错误信息
}
```

### 通信协议
```
TypeScript → Python
├── 命令行参数传递
├── 文件路径
├── 模块启用/禁用
└── 输出格式要求

Python → TypeScript
├── JSON格式输出
├── 检测结果数组
├── 错误信息
└── 状态码
```

## 🎯 可插拔架构

### 后端抽象层
```
IBugDetectorBackend (接口)
    │
    ├── PythonBackend (当前实现)
    │   ├── 子进程调用
    │   ├── JSON解析
    │   └── 错误处理
    │
    ├── NodeBackend (未来实现)
    │   ├── 直接调用
    │   ├── 内存共享
    │   └── 性能优化
    │
    └── WebBackend (未来实现)
        ├── HTTP API
        ├── 云端检测
        └── 分布式处理
```

### 配置驱动
```
VS Code配置
    │
    ├── backendType: 'python' | 'node' | 'web'
    ├── pythonPath: string
    ├── backendPath: string
    ├── enableMemorySafety: boolean
    ├── enableVariableState: boolean
    ├── enableStandardLibrary: boolean
    └── enableNumericControlFlow: boolean
```

## 📦 打包流程

### 开发流程
```
源码修改
    │
    ▼
TypeScript编译 (npm run compile)
    │
    ▼
功能测试 (F5调试)
    │
    ▼
VSIX打包 (vsce package)
    │
    ▼
插件安装测试
    │
    ▼
GitHub发布
```

### 自动化流程
```
Git Push
    │
    ▼
GitHub Actions触发
    │
    ├── 安装依赖
    ├── 编译TypeScript
    ├── 打包VSIX
    └── 创建Release
```

## 🔍 调试架构

### 调试层次
```
用户界面层
    │ (F5调试)
    ▼
VS Code插件层
    │ (console.log)
    ▼
TypeScript后端层
    │ (子进程通信)
    ▼
Python检测层
    │ (print/stderr)
    ▼
检测模块层
```

### 日志系统
```
TypeScript日志
├── 插件启动/停止
├── 命令执行
├── 配置更新
└── 错误处理

Python日志
├── 文件分析开始/结束
├── 模块检测结果
├── 错误和异常
└── 性能统计
```

## 🚀 扩展点

### 新检测模块添加
```
1. 在modules/目录创建新模块
2. 实现analyze()方法
3. 在main.py中注册模块
4. 更新package.json配置
5. 添加测试用例
```

### 新后端实现
```
1. 实现IBugDetectorBackend接口
2. 在BackendFactory中注册
3. 更新配置选项
4. 添加相应的测试
```

### 新UI组件添加
```
1. 在src/目录创建组件
2. 在extension.ts中注册
3. 更新package.json贡献点
4. 添加相应的命令和菜单
```

---

**架构图帮助理解整个系统的设计思路和组件关系！** 🏗️📊
