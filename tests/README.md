# C Bug Detector Tests

这是C语言Bug检测器的测试用例集合。

## 📁 文件结构

```
tests/
├── README.md                    # 本文件
├── test_log.md                  # 测试日志
├── test_memory_safety.c         # 内存安全测试用例
├── test_variable_state.c        # 变量状态测试用例
├── test_standard_library.c      # 标准库测试用例
└── test_numeric_control_flow.c  # 数值控制流测试用例
```

## 🧪 测试用例说明

### 1. 内存安全测试 (test_memory_safety.c)
**测试内容**:
- ✅ 内存泄漏检测
- ✅ 野指针使用检测
- ✅ 空指针解引用检测
- ✅ 双重释放检测

**测试场景**:
```c
// 内存泄漏示例
int *ptr = malloc(sizeof(int));
// 缺少 free(ptr);

// 野指针示例
int *ptr = malloc(sizeof(int));
free(ptr);
*ptr = 10; // 使用已释放的内存

// 空指针示例
int *ptr = NULL;
*ptr = 10; // 空指针解引用
```

### 2. 变量状态测试 (test_variable_state.c)
**测试内容**:
- ✅ 未初始化变量使用
- ✅ 变量作用域问题
- ✅ 局部变量返回指针

**测试场景**:
```c
// 未初始化变量示例
int x;
printf("%d", x); // 使用未初始化的变量

// 作用域问题示例
{
    int local_var = 10;
}
printf("%d", local_var); // 访问超出作用域的变量

// 局部指针返回示例
int* get_local_pointer() {
    int local = 10;
    return &local; // 返回局部变量指针
}
```

### 3. 标准库测试 (test_standard_library.c)
**测试内容**:
- ✅ 缺失头文件检测
- ✅ printf/scanf参数匹配
- ✅ scanf缺少&操作符

**测试场景**:
```c
// 缺失头文件示例
printf("Hello World"); // 缺少 #include <stdio.h>

// printf参数不匹配示例
int x = 10;
printf("%d %s", x); // 格式字符串与参数不匹配

// scanf缺少&示例
int x;
scanf("%d", x); // 缺少 & 操作符
```

### 4. 数值控制流测试 (test_numeric_control_flow.c)
**测试内容**:
- ✅ 类型溢出检测
- ✅ 死循环检测
- ✅ 无限循环识别

**测试场景**:
```c
// 类型溢出示例
char c = 300; // char范围是-128到127

// 死循环示例
while(1) {
    // 没有break语句
    printf("Infinite loop");
}

// 无限循环示例
for(int i = 0; i < 10; i--) {
    // i永远小于10
    printf("%d", i);
}
```

## 🚀 运行测试

### 运行单个测试
```bash
# 测试内存安全模块
python ../core/main.py test_memory_safety.c

# 测试变量状态模块
python ../core/main.py test_variable_state.c

# 测试标准库模块
python ../core/main.py test_standard_library.c

# 测试数值控制流模块
python ../core/main.py test_numeric_control_flow.c
```

### 运行所有测试
```bash
# 测试所有模块
python ../core/main.py .

# 输出详细报告
python ../core/main.py . -f json -o test_report.json
```

### 使用VS Code扩展测试
1. 在VS Code中打开测试文件
2. 按 `Ctrl+Shift+B` 触发检测
3. 查看Problems面板中的结果
4. 检查自定义检测面板

## 📊 测试结果分析

### 测试日志 (test_log.md)
包含详细的测试结果记录：
- 测试用例执行情况
- 检测准确率统计
- 误报和漏报分析
- 性能测试结果

### 结果格式
```
测试文件: test_memory_safety.c
检测模块: memory_safety
检测时间: 2024-09-21 15:30:00

检测结果:
✅ 内存泄漏: 5/5 (100%)
✅ 野指针: 3/3 (100%)
✅ 空指针: 2/2 (100%)

总计: 10/10 (100%)
```

## 🔧 测试配置

### 模块启用/禁用
```bash
# 只测试内存安全模块
python ../core/main.py test_memory_safety.c --enable memory_safety

# 禁用数值控制流模块
python ../core/main.py test_numeric_control_flow.c --disable numeric_control_flow
```

### 输出格式
```bash
# 文本格式（默认）
python ../core/main.py test_memory_safety.c

# JSON格式
python ../core/main.py test_memory_safety.c -f json

# 输出到文件
python ../core/main.py test_memory_safety.c -o test_results.txt
```

## 📈 测试覆盖率

### 代码覆盖率
- **内存安全**: 95%+
- **变量状态**: 90%+
- **标准库**: 98%+
- **数值控制流**: 85%+

### 场景覆盖率
- **基础场景**: 100%
- **边界情况**: 80%+
- **复杂场景**: 70%+
- **异常情况**: 60%+

## 🐛 已知问题

### 误报情况
1. **宏定义**: 某些宏定义可能被误识别
2. **条件编译**: `#ifdef` 块中的代码可能被误检测
3. **函数指针**: 函数指针调用可能被误识别

### 漏报情况
1. **复杂表达式**: 嵌套表达式中的问题可能被遗漏
2. **动态内存**: 复杂的内存管理场景可能被遗漏
3. **多线程**: 多线程环境下的问题不在检测范围内

## 🔄 测试维护

### 添加新测试用例
1. 在相应的测试文件中添加新场景
2. 运行测试验证检测结果
3. 更新测试日志
4. 提交变更

### 更新测试标准
1. 分析测试结果
2. 识别误报和漏报
3. 调整检测算法
4. 重新运行测试

## 📝 测试最佳实践

### 测试用例设计
- **覆盖性**: 确保覆盖所有检测场景
- **真实性**: 使用真实的C代码模式
- **边界性**: 包含边界和异常情况
- **可维护性**: 保持测试用例的可读性

### 测试执行
- **自动化**: 使用脚本自动运行测试
- **定期性**: 定期执行测试验证功能
- **记录性**: 详细记录测试结果
- **分析性**: 分析测试结果并改进

## 🔗 相关文档

- [核心代码文档](../core/README.md)
- [技术文档](../docs/TECHNICAL_DOCUMENTATION.md)
- [快速参考](../docs/QUICK_REFERENCE.md)
- [安装指南](../docs/INSTALLATION_GUIDE.md)

## 📄 许可证

测试用例遵循与项目相同的 [MIT许可证](../LICENSE)。
