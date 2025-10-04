#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于libclang的语义分析器
专门解决结构体成员赋值的误报问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_reporter import ErrorReporter, BugReport

try:
    import clang.cindex
    LIBCLANG_AVAILABLE = True
except ImportError:
    LIBCLANG_AVAILABLE = False
    print("警告: libclang未安装，将使用备用检测方法")

class LibClangSemanticAnalyzer:
    """基于libclang的语义分析器 - 区分左值和右值"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.current_file: str = ""
        
    def get_module_name(self):
        """Return module name"""
        return "LibClang Semantic Analyzer"
    
    def analyze_file(self, file_path: str) -> List[BugReport]:
        """分析C文件中的语义问题"""
        if not LIBCLANG_AVAILABLE:
            return []
            
        self.error_reporter.clear_reports()
        
        try:
            # 创建Clang索引
            index = clang.cindex.Index.create()
            
            # 解析C文件，启用相关警告
            translation_unit = index.parse(
                file_path,
                args=[
                    '-Wall',  # 启用所有警告
                    '-Wextra',  # 启用额外警告
                    '-Wuninitialized',  # 未初始化变量检查
                    '-Wunused-variable',  # 未使用变量检查
                ]
            )
            
            if not translation_unit:
                return []
            
            # 获取当前分析的文件路径
            self.current_file = translation_unit.spelling
            
            # 分析AST进行语义分析
            self._analyze_semantic_issues(translation_unit.cursor)
            
            return self.error_reporter.get_reports()
            
        except Exception as e:
            print(f"libclang语义分析出错: {e}")
            return []
    
    def _analyze_semantic_issues(self, cursor):
        """分析AST中的语义问题"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 检查赋值操作
        if cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            if cursor.spelling == '=':
                self._analyze_assignment(cursor)
        
        # 检查变量引用（读取）
        elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            self._analyze_variable_reference(cursor)
        
        # 检查函数调用参数
        elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            self._analyze_function_call_args(cursor)
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._analyze_semantic_issues(child)
    
    def _analyze_assignment(self, assignment_cursor):
        """分析赋值操作 - 区分左值和右值"""
        children = list(assignment_cursor.get_children())
        if len(children) < 2:
            return
        
        left_side = children[0]  # 左值（被赋值）
        right_side = children[1]  # 右值（赋值源）
        
        # 分析左值 - 这是写入操作，通常是合法的
        if left_side.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
            # 结构体成员访问：point1.x = 100
            # 这是合法的写入操作，不应该报告未初始化错误
            pass
        elif left_side.kind == clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR:
            # 数组元素访问：arr[0] = value
            # 这也是合法的写入操作
            pass
        elif left_side.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            # 直接变量赋值：var = value
            # 这也是合法的写入操作
            pass
        
        # 分析右值 - 这是读取操作，需要检查是否未初始化
        self._check_uninitialized_read(right_side)
    
    def _analyze_variable_reference(self, ref_cursor):
        """分析变量引用 - 检查是否是未初始化的读取"""
        # 检查这个引用是否在赋值操作的左侧
        parent = ref_cursor.semantic_parent
        if parent and parent.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            if parent.spelling == '=':
                # 这是赋值操作的左侧，是写入操作，合法
                return
        
        # 检查是否是结构体成员访问的左侧
        if parent and parent.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
            # 这是结构体成员访问的左侧，是写入操作，合法
            return
        
        # 否则这是读取操作，需要检查是否未初始化
        self._check_uninitialized_read(ref_cursor)
    
    def _analyze_function_call_args(self, call_cursor):
        """分析函数调用参数 - 检查未初始化的参数"""
        children = list(call_cursor.get_children())
        if len(children) < 2:
            return
        
        # 跳过第一个参数（函数名），检查其他参数
        for arg in children[1:]:
            if arg.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                self._check_uninitialized_read(arg)
    
    def _check_uninitialized_read(self, cursor):
        """检查未初始化的读取操作"""
        if cursor.kind != clang.cindex.CursorKind.DECL_REF_EXPR:
            return
        
        var_name = cursor.spelling
        if not var_name:
            return
        
        # 获取变量类型
        var_type = cursor.type
        if not var_type:
            return
        
        # 跳过函数调用 - 这些不是变量
        if var_type.kind == clang.cindex.TypeKind.FUNCTIONPROTO:
            return
        
        # 跳过指针类型 - 指针解引用由内存安全模块处理
        if var_type.kind == clang.cindex.TypeKind.POINTER:
            return
        
        # 跳过数组类型 - 数组名通常不需要初始化检查
        if var_type.kind == clang.cindex.TypeKind.CONSTANTARRAY or var_type.kind == clang.cindex.TypeKind.INCOMPLETEARRAY:
            return
        
        # 检查是否是结构体类型
        if var_type.kind == clang.cindex.TypeKind.RECORD:
            # 结构体变量，检查是否是成员访问
            parent = cursor.semantic_parent
            if parent and parent.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
                # 这是结构体成员访问，检查是否是写入操作
                grandparent = parent.semantic_parent
                if grandparent and grandparent.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
                    if grandparent.spelling == '=':
                        # 这是写入操作，合法
                        return
        
        # 检查是否是静态变量或全局变量
        var_cursor = cursor.get_definition()
        if var_cursor:
            if var_cursor.storage_class == clang.cindex.StorageClass.STATIC:
                # 静态变量，不需要检查
                return
        
        # 检查是否是const变量
        if var_type.is_const_qualified():
            # const变量，不需要检查
            return
        
        # 检查是否有初始化
        if var_cursor:
            has_initializer = any(
                child.kind.is_expression() for child in var_cursor.get_children()
            )
            if has_initializer:
                # 有初始化，不需要检查
                return
        
        # 检查是否是函数参数
        if var_cursor and var_cursor.kind == clang.cindex.CursorKind.PARM_DECL:
            # 函数参数，不需要检查
            return
        
        # 这是一个未初始化的读取操作
        code_snippet = self._get_source_code_snippet(cursor)
        
        self.error_reporter.add_variable_error(
            cursor.location.line,
            f"使用未初始化的变量 '{var_name}' (类型: {var_type.spelling})",
            f"建议在使用前初始化变量: {var_name} = {{0}};",
            code_snippet,
            var_name
        )
    
    def _get_source_code_snippet(self, cursor) -> str:
        """获取AST节点对应的原始源代码片段"""
        try:
            # 获取节点的位置信息
            start_location = cursor.extent.start
            end_location = cursor.extent.end
            
            # 读取源文件
            with open(self.current_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 提取代码片段
            if start_location.line == end_location.line:
                # 单行代码
                line = lines[start_location.line - 1]
                return line[start_location.column:end_location.column].strip()
            else:
                # 多行代码
                snippet_lines = []
                for line_num in range(start_location.line - 1, end_location.line):
                    if line_num < len(lines):
                        snippet_lines.append(lines[line_num].rstrip())
                return ' '.join(snippet_lines)
                
        except Exception as e:
            return f"无法获取代码片段: {e}"

def test_semantic_analyzer():
    """测试语义分析器"""
    if not LIBCLANG_AVAILABLE:
        print("libclang不可用，跳过测试")
        return
    
    analyzer = LibClangSemanticAnalyzer()
    
    # 创建测试文件
    test_code = """
#include <stdio.h>

struct Point {
    int x;
    int y;
};

int main() {
    struct Point point1;  // 未初始化
    int x;                // 未初始化
    
    // 正确的结构体成员赋值 - 不应该报错
    point1.x = 100;       // 写入操作，合法
    point1.y = 200;       // 写入操作，合法
    
    // 错误的未初始化变量使用 - 应该报错
    printf("x = %d\\n", x);  // 读取操作，应该报错
    
    // 正确的结构体成员读取 - 应该报错（因为point1未初始化）
    printf("point1.x = %d\\n", point1.x);  // 读取操作，应该报错
    
    return 0;
}
"""
    
    with open("test_semantic.c", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    try:
        reports = analyzer.analyze_file("test_semantic.c")
        print(f"检测到 {len(reports)} 个语义问题:")
        for report in reports:
            print(f"  Line {report.line_number}: {report.message}")
            print(f"    代码: {report.code_snippet}")
    finally:
        # 清理测试文件
        import os
        if os.path.exists("test_semantic.c"):
            os.remove("test_semantic.c")

if __name__ == "__main__":
    test_semantic_analyzer()
