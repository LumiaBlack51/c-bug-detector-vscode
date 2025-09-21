# C语言Bug检测器快速参考

## 🚀 快速启动

### 开发环境设置
```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 安装VS Code插件依赖
cd vscode-extension
npm install

# 3. 编译TypeScript
npm run compile

# 4. 打包插件
vsce package
```

### 调试模式
```bash
# TypeScript监听模式
npm run watch

# VS Code调试
# 按F5启动调试模式
```

## 🔧 核心接口

### TypeScript接口
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

### Python后端调用
```typescript
const process = spawn(pythonPath, [backendPath, filePath, '-f', 'json']);
process.stdout.on('data', (data) => {
    const reports: BugReport[] = JSON.parse(data.toString());
});
```

## 📦 打包命令

### VS Code插件打包
```bash
# 安装vsce
npm install -g @vscode/vsce

# 编译
npm run compile

# 打包
vsce package --allow-missing-repository
```

### 生成的文件
- `c-bug-detector-1.0.0.vsix` - VS Code插件安装包

## 🐛 常见问题

### 1. TypeScript编译错误
```typescript
// 确保实现Disposable接口
export class ResultsProvider implements vscode.TreeDataProvider<BugItem>, vscode.Disposable {
    public dispose(): void {
        this._onDidChangeTreeData.dispose();
    }
}
```

### 2. Python子进程失败
```typescript
// 检查Python路径
const pythonPath = config.get<string>('pythonPath', 'python');
const backendPath = config.get<string>('backendPath', '../main.py');
```

### 3. JSON解析错误
```typescript
try {
    const reports: BugReport[] = JSON.parse(stdout);
} catch (parseError) {
    reject(new Error(`解析结果失败: ${parseError}`));
}
```

## 🔄 更新流程

### 后端更新
1. 修改Python代码
2. 测试功能
3. 前端无需修改

### 前端更新
1. 修改TypeScript代码
2. 重新编译: `npm run compile`
3. 重新打包: `vsce package`
4. 重新安装插件

## 📁 关键文件

### 核心文件
- `vscode-extension/src/extension.ts` - 插件主入口
- `vscode-extension/src/backend.ts` - 后端接口
- `vscode-extension/src/resultsProvider.ts` - 结果提供者
- `vscode-extension/src/detectionPanel.ts` - 检测面板

### 配置文件
- `vscode-extension/package.json` - 插件配置
- `vscode-extension/tsconfig.json` - TypeScript配置
- `main.py` - Python后端主程序

### 测试文件
- `tests/test_memory_safety.c` - 内存安全测试
- `tests/test_variable_state.c` - 变量状态测试
- `tests/test_standard_library.c` - 标准库测试
- `tests/test_numeric_control_flow.c` - 数值控制流测试

## 🎯 开发技巧

### 1. 快速测试
```bash
# 测试Python后端
python main.py tests/test_memory_safety.c

# 测试VS Code插件
# 按F5启动调试，打开C文件测试
```

### 2. 配置调试
```typescript
// 在VS Code设置中配置
{
    "c-bug-detector.pythonPath": "python",
    "c-bug-detector.backendPath": "../main.py",
    "c-bug-detector.enableMemorySafety": true
}
```

### 3. 日志调试
```typescript
// TypeScript调试
console.log('调试信息:', data);

// Python调试
print(f"DEBUG: {message}", file=sys.stderr)
```

## 📋 检查清单

### 发布前检查
- [ ] TypeScript编译无错误
- [ ] Python后端测试通过
- [ ] VS Code插件功能正常
- [ ] VSIX文件生成成功
- [ ] 文档更新完整

### 开发检查
- [ ] 接口定义正确
- [ ] 错误处理完善
- [ ] 配置项完整
- [ ] 测试用例覆盖
- [ ] 代码注释清晰

---

**快速参考卡片 - 随时查阅关键信息！** 📚⚡
