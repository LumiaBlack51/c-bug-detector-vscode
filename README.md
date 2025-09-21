# C语言Bug检测器

一个专为初学者设计的C语言bug检测器，采用启发式与正则表达式方法，具备模块化架构。

## 🎯 项目特色

### 专为初学者设计
- **易懂的错误报告**: 使用初学者友好的语言，避免专业术语
- **具体的修复建议**: 每个错误都提供具体的代码行号和修复建议
- **模块化架构**: 可以单独启用或禁用任何检测模块

### 启发式与正则表达式双重保障
- **正则表达式优先**: 使用高效的正则表达式进行代码分析
- **启发式规则**: 当正则表达式无法处理时，使用启发式规则作为"最终防线"
- **永不崩溃**: 确保工具始终为用户提供基础可用性

## 🔧 功能特性

### 模块化设计
- **🔒 内存安全卫士**: 检测内存泄漏、野指针、空指针解引用
- **📊 变量状态监察官**: 检测变量未初始化即使用和变量作用域问题
- **📚 标准库使用助手**: 检测缺失头文件、头文件拼写错误，检查常用函数参数
- **🔢 数值与控制流分析器**: 检测类型溢出和死循环

### 检测能力
- ✅ 内存泄漏检测
- ✅ 野指针和空指针解引用检测
- ✅ 未初始化变量使用检测
- ✅ 头文件缺失和拼写错误检测
- ✅ scanf参数缺少&符号检测
- ✅ printf格式字符串与参数不匹配检测
- ✅ 数据类型溢出检测
- ✅ 死循环检测
- ✅ 函数返回局部指针检测

## 🚀 快速开始

### 安装
```bash
# 克隆项目
git clone https://github.com/your-username/c-bug-detector.git
cd c-bug-detector

# 运行安装脚本
python install.py
```

### 基本使用
```bash
# 分析单个文件
python main.py <source_file.c>

# 批量分析目录
python main.py --batch <directory>

# 指定输出格式
python main.py <file.c> -f json -o report.json

# 启用/禁用特定模块
python main.py <file.c> --enable memory_safety
python main.py <file.c> --disable standard_library

# 查看所有可用模块
python main.py --list-modules
```

### 演示
```bash
# 运行功能演示
python demo.py
```

## 📁 项目结构
```
├── modules/                    # 检测模块
│   ├── memory_safety.py       # 内存安全卫士
│   ├── variable_state.py      # 变量状态监察官
│   ├── standard_library.py    # 标准库使用助手
│   └── numeric_control_flow.py # 数值与控制流分析器
├── tests/                     # 测试用例
│   ├── test_memory_safety.c   # 内存安全测试
│   ├── test_variable_state.c  # 变量状态测试
│   ├── test_standard_library.c # 标准库测试
│   ├── test_numeric_control_flow.c # 数值控制流测试
│   └── test_log.md           # 测试日志
├── utils/                     # 工具函数
│   ├── error_reporter.py     # 错误报告器
│   └── code_parser.py        # 代码解析器
├── main.py                   # 主程序
├── demo.py                   # 演示脚本
├── install.py               # 安装脚本
├── requirements.txt         # 依赖包
└── README.md               # 项目说明
```

## 📊 测试结果

### 检测能力统计
- **内存安全卫士**: 检测到21个内存安全问题
- **变量状态监察官**: 检测到4个变量状态问题
- **标准库使用助手**: 检测到19个标准库使用问题
- **数值与控制流分析器**: 检测到12个数值与控制流问题

### 测试用例
每个模块都包含约200行的测试代码，涵盖：
- 错误示例和正确示例
- 标准答案用于验证检测准确性
- 支持后续添加新的测试用例

## 🛠️ 技术实现

### 核心技术
- **Python 3.7+**: 主要开发语言
- **正则表达式**: 高效的代码解析
- **模块化设计**: 易于扩展和维护
- **启发式规则**: 处理复杂情况

### 依赖包
- `regex`: 高级正则表达式支持
- `colorama`: 彩色终端输出
- `click`: 命令行界面
- `pycparser`: 可选的AST解析支持

## 🔮 未来计划

### 短期目标
- [x] ✅ 完成所有核心模块
- [x] ✅ 实现命令行工具
- [x] ✅ 创建测试用例
- [ ] 🔄 优化检测准确性
- [ ] 🔄 减少误报率

### 长期目标
- [ ] 📱 VS Code插件开发
- [ ] 🌐 Web界面
- [ ] 📊 更详细的代码分析
- [ ] 🔧 自动修复建议
- [ ] 📈 性能优化

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和测试用户！

---

**让C语言学习更简单，让bug无处藏身！** 🐛✨
