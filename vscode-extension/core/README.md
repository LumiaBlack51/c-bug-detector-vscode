# C Bug Detector Core

这是C语言Bug检测器的核心Python代码部分。

## 📁 文件结构

```
core/
├── main.py                 # 主入口文件
├── demo.py                 # 演示脚本
├── requirements.txt        # Python依赖
├── modules/                # 检测模块
│   ├── __init__.py
│   ├── memory_safety.py    # 内存安全检测
│   ├── variable_state.py   # 变量状态检测
│   ├── standard_library.py # 标准库使用检测
│   └── numeric_control_flow.py # 数值和控制流检测
└── utils/                  # 工具模块
    ├── __init__.py
    ├── code_parser.py      # 代码解析器
    └── error_reporter.py    # 错误报告器
```

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行检测器
```bash
# 检测单个文件
python main.py your_file.c

# 检测目录
python main.py your_directory/

# 查看帮助
python main.py --help

# 列出可用模块
python main.py --list-modules
```

### 运行演示
```bash
python demo.py
```

## 🔧 模块说明

### 1. 内存安全模块 (memory_safety.py)
- **功能**: 检测内存泄漏、野指针、空指针解引用
- **检测内容**:
  - `malloc`/`calloc`/`realloc` 未释放
  - 使用已释放的内存
  - 空指针解引用
  - 野指针使用

### 2. 变量状态模块 (variable_state.py)
- **功能**: 检测变量未初始化和作用域问题
- **检测内容**:
  - 未初始化变量使用
  - 变量作用域错误
  - 局部变量返回指针

### 3. 标准库模块 (standard_library.py)
- **功能**: 检测头文件和库函数使用问题
- **检测内容**:
  - 缺失头文件
  - 头文件拼写错误
  - `printf`/`scanf` 参数不匹配
  - `scanf` 缺少 `&` 操作符

### 4. 数值控制流模块 (numeric_control_flow.py)
- **功能**: 检测数值溢出和死循环
- **检测内容**:
  - 类型溢出 (如 `char c = 300;`)
  - 死循环检测
  - 无限循环识别

## 🛠️ 工具模块

### 代码解析器 (code_parser.py)
- 使用正则表达式解析C代码
- 提取函数定义、变量声明、函数调用等
- 支持多行注释和字符串处理

### 错误报告器 (error_reporter.py)
- 统一错误报告格式
- 支持不同严重级别
- 提供修复建议

## 📊 输出格式

### 文本格式 (默认)
```
文件: example.c
行 5: 内存泄漏 - malloc未释放
建议: 在函数结束前调用free()释放内存
代码: int *ptr = malloc(sizeof(int));
```

### JSON格式
```json
{
  "file_path": "example.c",
  "reports": [
    {
      "line_number": 5,
      "error_type": "内存泄漏",
      "severity": "Error",
      "message": "malloc未释放",
      "suggestion": "在函数结束前调用free()释放内存",
      "code_snippet": "int *ptr = malloc(sizeof(int));",
      "module_name": "memory_safety"
    }
  ]
}
```

## 🔧 配置选项

### 命令行参数
- `input`: 输入文件或目录
- `-o, --output`: 输出文件路径
- `-f, --format`: 输出格式 (text/json)
- `--disable`: 禁用指定模块
- `--enable`: 启用指定模块
- `--list-modules`: 列出所有模块

### 示例
```bash
# 只启用内存安全检测
python main.py file.c --enable memory_safety

# 禁用数值控制流检测
python main.py file.c --disable numeric_control_flow

# 输出到JSON文件
python main.py file.c -f json -o report.json
```

## 🧪 测试

测试文件位于 `../tests/` 目录：
- `test_memory_safety.c`: 内存安全测试用例
- `test_variable_state.c`: 变量状态测试用例
- `test_standard_library.c`: 标准库测试用例
- `test_numeric_control_flow.c`: 数值控制流测试用例

## 🔄 扩展开发

### 添加新检测模块
1. 在 `modules/` 目录创建新文件
2. 继承基础检测类
3. 实现 `analyze()` 方法
4. 在 `main.py` 中注册模块

### 示例模块结构
```python
class CustomModule(BaseModule):
    def __init__(self, error_reporter):
        super().__init__(error_reporter)
        self.name = "custom_module"
    
    def analyze(self, file_path):
        # 实现检测逻辑
        pass
```

## 📝 注意事项

- 所有模块都基于正则表达式实现
- 支持C99标准语法
- 检测结果仅供参考，需要人工验证
- 建议在开发环境中使用，生产环境请谨慎

## 🔗 相关文档

- [技术文档](../docs/TECHNICAL_DOCUMENTATION.md)
- [安装指南](../docs/INSTALLATION_GUIDE.md)
- [快速参考](../docs/QUICK_REFERENCE.md)
