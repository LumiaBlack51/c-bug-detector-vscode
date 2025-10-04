"""
基于libclang的C语言静态分析器
充分利用libclang的丰富接口进行更准确的分析
"""
import sys
import os
from typing import List, Dict, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter, BugReport

try:
    import clang.cindex
    LIBCLANG_AVAILABLE = True
except ImportError:
    LIBCLANG_AVAILABLE = False
    print("警告: libclang未安装，将使用备用检测方法")


class LibClangAnalyzer:
    """基于libclang的C语言分析器 - 充分利用libclang的丰富接口"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.initialized_vars_stack: List[Set[str]] = []  # 作用域栈
        self.current_scope_vars: Set[str] = set()  # 当前作用域新声明的变量
        self.current_file: str = ""
        self.variable_definitions: Dict[str, clang.cindex.Cursor] = {}  # 变量定义位置
        self.function_definitions: Dict[str, clang.cindex.Cursor] = {}  # 函数定义位置
        self.memory_allocations: List[clang.cindex.Cursor] = []  # 内存分配调用
        self.memory_deallocations: List[clang.cindex.Cursor] = []  # 内存释放调用
        
    def get_module_name(self):
        """Return module name"""
        return "LibClang Analyzer"
        
    def analyze_file(self, file_path: str) -> List[BugReport]:
        """分析C文件并返回检测结果"""
        if not LIBCLANG_AVAILABLE:
            return []
            
        self.error_reporter.clear_reports()
        
        try:
            # 创建Clang索引
            index = clang.cindex.Index.create()
            
            # 解析C文件，启用所有相关警告
            translation_unit = index.parse(
                file_path,
                args=[
                    '-Wall',  # 启用所有警告
                    '-Wextra',  # 启用额外警告
                    '-Wformat',  # printf格式字符串检查
                    '-Wuninitialized',  # 未初始化变量检查
                    '-Wunused-variable',  # 未使用变量检查
                    '-Wunused-function',  # 未使用函数检查
                    '-Wshadow',  # 变量遮蔽检查
                    '-Wconversion',  # 类型转换检查
                    '-Wformat-security',  # 格式字符串安全检查
                    '-Wformat-nonliteral',  # 非字面量格式字符串检查
                    '-Wunused-but-set-variable',  # 设置但未使用的变量
                    '-Wunused-parameter',  # 未使用的参数
                ]
            )
            
            if not translation_unit:
                return []
            
            # 获取当前分析的文件路径
            self.current_file = translation_unit.spelling
            
            # 1. 分析编译器诊断信息（printf格式字符串等）
            self._analyze_diagnostics(translation_unit)
            
            # 2. 构建符号表和函数定义映射
            self._build_symbol_table(translation_unit.cursor)
            
            # 3. 分析AST进行未初始化变量检测
            self._analyze_ast_for_uninitialized_vars(translation_unit.cursor)
            
            # 4. 分析内存安全问题
            self._analyze_memory_safety(translation_unit.cursor)
            
            # 5. 分析printf格式字符串（更精确的方法）
            self._analyze_printf_format_strings(translation_unit.cursor)
            
            # 6. 分析变量遮蔽问题
            self._analyze_variable_shadowing(translation_unit.cursor)
            
            return self.error_reporter.get_reports()
            
        except Exception as e:
            print(f"libclang分析出错: {e}")
            return []
    
    def _analyze_diagnostics(self, translation_unit):
        """分析编译器诊断信息"""
        diagnostics = translation_unit.diagnostics
        
        for diag in diagnostics:
            # 只处理当前文件的诊断信息，忽略系统头文件
            if diag.location.file and diag.location.file.name != self.current_file:
                continue
            
            # 检查printf格式字符串问题
            if 'format' in diag.spelling.lower():
                self.error_reporter.add_library_error(
                    diag.location.line,
                    f"printf格式字符串问题: {diag.spelling}",
                    "建议检查格式字符串和参数类型是否匹配",
                    f"位置: {diag.location.file}:{diag.location.line}:{diag.location.column}"
                )
            
            # 检查未初始化变量警告
            elif 'uninitialized' in diag.spelling.lower():
                self.error_reporter.add_variable_error(
                    diag.location.line,
                    f"未初始化变量警告: {diag.spelling}",
                    "建议在使用前初始化变量",
                    f"位置: {diag.location.file}:{diag.location.line}:{diag.location.column}"
                )
            
            # 检查未使用变量
            elif 'unused' in diag.spelling.lower():
                self.error_reporter.add_variable_error(
                    diag.location.line,
                    f"未使用变量警告: {diag.spelling}",
                    "建议删除未使用的变量或添加使用",
                    f"位置: {diag.location.file}:{diag.location.line}:{diag.location.column}"
                )
            
            # 检查内存安全问题
            elif any(keyword in diag.spelling.lower() for keyword in ['leak', 'free', 'malloc', 'dereference']):
                self.error_reporter.add_memory_error(
                    diag.location.line,
                    f"内存安全问题: {diag.spelling}",
                    "建议检查内存分配和释放",
                    f"位置: {diag.location.file}:{diag.location.line}:{diag.location.column}"
                )
    
    def _build_symbol_table(self, cursor):
        """构建符号表，记录变量和函数定义"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        # 忽略宏展开的节点
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 记录变量定义 - 只记录真正的变量声明，不记录类型定义
        if cursor.kind == clang.cindex.CursorKind.VAR_DECL:
            var_name = cursor.spelling
            if var_name:
                self.variable_definitions[var_name] = cursor
        
        # 记录函数定义
        elif cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            func_name = cursor.spelling
            if func_name:
                self.function_definitions[func_name] = cursor
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._build_symbol_table(child)
    
    def _analyze_ast_for_uninitialized_vars(self, cursor):
        """分析AST检测未初始化变量"""
        # 初始化全局作用域
        if not self.initialized_vars_stack:
            self.initialized_vars_stack.append(set())
        
        self._traverse_ast(cursor)
    
    def _traverse_ast(self, cursor):
        """遍历AST节点"""
        # 只处理当前文件的节点，忽略系统头文件和宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        # 忽略宏展开的节点
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 处理变量声明 - 只处理真正的变量声明，不处理类型定义
        if cursor.kind == clang.cindex.CursorKind.VAR_DECL:
            var_name = cursor.spelling
            if var_name:  # 确保变量名不为空
                # 使用libclang的type信息检查变量类型
                var_type = cursor.type
                is_static = cursor.storage_class == clang.cindex.StorageClass.STATIC
                is_const = cursor.type.is_const_qualified()
                
                # 检查是否有初始化
                has_initializer = any(
                    child.kind.is_expression() for child in cursor.get_children()
                )
                
                # 记录当前作用域新声明的变量
                self.current_scope_vars.add(var_name)
                
                if has_initializer or is_static:
                    # 标记为已初始化
                    self.initialized_vars_stack[-1].add(var_name)
        
        # 处理赋值操作
        elif (cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR and 
              cursor.spelling == '='):
            # 获取赋值左侧
            children = list(cursor.get_children())
            if children:
                left_side = children[0]
                if left_side.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                    var_name = left_side.spelling
                    if var_name:
                        # 从当前作用域开始向上查找并标记为已初始化
                        for scope in reversed(self.initialized_vars_stack):
                            if var_name in scope:
                                scope.add(var_name)
                                break
                        # 如果是当前作用域新声明的，也加入
                        if var_name in self.current_scope_vars:
                            self.initialized_vars_stack[-1].add(var_name)
        
        # 处理变量引用（使用）
        elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            var_name = cursor.spelling
            if var_name and var_name in self.current_scope_vars:
                # 检查是否已初始化
                is_initialized = any(
                    var_name in scope for scope in reversed(self.initialized_vars_stack)
                )
                
                if not is_initialized:
                    # 获取变量类型信息
                    var_cursor = self.variable_definitions.get(var_name)
                    var_type = "int"  # 默认类型
                    if var_cursor:
                        var_type = var_cursor.type.spelling
                    
                    # 报告未初始化变量使用
                    self.error_reporter.add_variable_error(
                        cursor.location.line,
                        f"使用未初始化的变量 '{var_name}' (类型: {var_type})",
                        f"建议在使用前初始化变量: {var_name} = {{0}};",
                        f"位置: {cursor.location.file}:{cursor.location.line}:{cursor.location.column}"
                    )
                    # 避免重复报告
                    self.initialized_vars_stack[-1].add(var_name)
        
        # 处理作用域变化
        elif (cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT or 
              cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL):
            # 进入新作用域
            self.initialized_vars_stack.append(set())
            self.current_scope_vars = set()
            
            # 递归处理子节点
            for child in cursor.get_children():
                self._traverse_ast(child)
            
            # 离开作用域
            self.initialized_vars_stack.pop()
            if self.initialized_vars_stack:
                self.current_scope_vars = set()
        else:
            # 递归处理其他节点
            for child in cursor.get_children():
                self._traverse_ast(child)
    
    def _analyze_memory_safety(self, cursor):
        """分析内存安全问题"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        # 忽略宏展开的节点
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 1. 跟踪malloc/free调用
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            func_name = cursor.spelling
            if func_name == 'malloc':
                self.memory_allocations.append(cursor)
            elif func_name == 'free':
                self.memory_deallocations.append(cursor)
        
        # 2. 检查指针解引用
        elif cursor.kind == clang.cindex.CursorKind.UNARY_OPERATOR:
            # 检查是否是解引用操作 (*ptr)
            if cursor.spelling == '*':
                children = list(cursor.get_children())
                if children:
                    operand = children[0]
                    if operand.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                        ptr_name = operand.spelling
                        # 检查指针是否已分配内存
                        if ptr_name in self.variable_definitions:
                            var_cursor = self.variable_definitions[ptr_name]
                            if var_cursor.type.kind == clang.cindex.TypeKind.POINTER:
                                # 检查是否是野指针
                                if not self._is_pointer_allocated(ptr_name, cursor.location.line):
                                    self.error_reporter.add_memory_error(
                                        cursor.location.line,
                                        f"可能的野指针解引用: '{ptr_name}'",
                                        f"建议在使用前分配内存: {ptr_name} = malloc(sizeof(...));",
                                        f"位置: {cursor.location.file}:{cursor.location.line}:{cursor.location.column}"
                                    )
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._analyze_memory_safety(child)
    
    def _is_pointer_allocated(self, ptr_name: str, current_line: int) -> bool:
        """检查指针是否已分配内存"""
        # 简单的检查：在当前行之前是否有malloc调用
        for alloc in self.memory_allocations:
            if alloc.location.line < current_line:
                # 检查是否赋值给了这个指针
                # 这里需要更复杂的分析，暂时返回False
                pass
        return False
    
    def _analyze_printf_format_strings(self, cursor):
        """分析printf格式字符串（更精确的方法）"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        # 忽略宏展开的节点
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            func_name = cursor.spelling
            if func_name in ['printf', 'fprintf', 'sprintf', 'snprintf']:
                children = list(cursor.get_children())
                if len(children) >= 2:
                    # 第一个参数是格式字符串
                    format_cursor = children[0]
                    if format_cursor.kind == clang.cindex.CursorKind.STRING_LITERAL:
                        format_string = format_cursor.spelling
                        # 计算格式说明符数量
                        format_specifiers = self._count_format_specifiers(format_string)
                        # 计算实际参数数量
                        actual_args = len(children) - 1
                        
                        if format_specifiers != actual_args:
                            self.error_reporter.add_library_error(
                                cursor.location.line,
                                f"printf格式字符串参数不匹配: 格式说明符数量({format_specifiers})与参数数量({actual_args})不匹配",
                                "建议检查格式字符串和参数类型是否匹配",
                                f"位置: {cursor.location.file}:{cursor.location.line}:{cursor.location.column}"
                            )
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._analyze_printf_format_strings(child)
    
    def _count_format_specifiers(self, format_string: str) -> int:
        """计算格式字符串中的格式说明符数量"""
        import re
        # 匹配%[flags][width][.precision][length]specifier
        pattern = r'%[+-]?[0-9]*\.?[0-9]*[hlL]?[diouxXeEfFgGaAcspn]'
        matches = re.findall(pattern, format_string)
        return len(matches)
    
    def _analyze_variable_shadowing(self, cursor):
        """分析变量遮蔽问题"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        # 忽略宏展开的节点
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 检查变量遮蔽
        if cursor.kind == clang.cindex.CursorKind.VAR_DECL:
            var_name = cursor.spelling
            if var_name:
                # 检查外层作用域是否有同名变量
                for scope in self.initialized_vars_stack[:-1]:  # 排除当前作用域
                    if var_name in scope:
                        self.error_reporter.add_variable_error(
                            cursor.location.line,
                            f"变量遮蔽: '{var_name}' 遮蔽了外层作用域的同名变量",
                            f"建议使用不同的变量名或明确指定作用域",
                            f"位置: {cursor.location.file}:{cursor.location.line}:{cursor.location.column}"
                        )
                        break
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._analyze_variable_shadowing(child)


def test_libclang_analyzer():
    """测试libclang分析器"""
    if not LIBCLANG_AVAILABLE:
        print("libclang不可用，跳过测试")
        return
    
    analyzer = LibClangAnalyzer()
    
    # 创建测试文件
    test_code = """
#include <stdio.h>

int main() {
    int x;  // 未初始化
    int y = 10;  // 已初始化
    
    printf("x = %d\\n", x);  // 使用未初始化变量
    printf("y = %d\\n", y);  // 正确使用
    
    // printf格式错误
    printf("Error: %d\\n", "string");  // 类型不匹配
    
    // 变量遮蔽测试
    {
        int x = 5;  // 遮蔽外层变量
        printf("inner x = %d\\n", x);
    }
    
    return 0;
}
"""
    
    with open("test_libclang.c", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    try:
        reports = analyzer.analyze_file("test_libclang.c")
        print(f"Detected {len(reports)} issue(s):")
        for report in reports:
            print(f"  Line {report.line_number}: {report.message}")
    finally:
        # 清理测试文件
        if os.path.exists("test_libclang.c"):
            os.remove("test_libclang.c")


if __name__ == "__main__":
    test_libclang_analyzer()
