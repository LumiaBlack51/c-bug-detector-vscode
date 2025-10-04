#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于libclang的printf格式字符串检测器
专门解决printf参数数量不匹配的误报问题
"""
import re
from typing import List, Dict, Set, Optional, Tuple
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

class LibClangPrintfDetector:
    """基于libclang的printf格式字符串检测器"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.current_file: str = ""
        
    def get_module_name(self):
        """Return module name"""
        return "LibClang Printf Detector"
    
    def analyze_file(self, file_path: str) -> List[BugReport]:
        """分析C文件中的printf格式字符串问题"""
        if not LIBCLANG_AVAILABLE:
            return []
            
        self.error_reporter.clear_reports()
        
        try:
            # 创建Clang索引
            index = clang.cindex.Index.create()
            
            # 解析C文件，启用printf相关警告
            translation_unit = index.parse(
                file_path,
                args=[
                    '-Wall',  # 启用所有警告
                    '-Wextra',  # 启用额外警告
                    '-Wformat',  # printf格式字符串检查
                    '-Wformat-security',  # 格式字符串安全检查
                    '-Wformat-nonliteral',  # 非字面量格式字符串检查
                    '-Wformat-y2k',  # Y2K格式字符串检查
                    '-Wformat-extra-args',  # 额外参数检查
                    '-Wformat-zero-length',  # 零长度格式字符串检查
                    '-Wformat-invalid-specifier',  # 无效格式说明符检查
                    '-Wformat-insufficient-args',  # 参数不足检查
                ]
            )
            
            if not translation_unit:
                return []
            
            # 获取当前分析的文件路径
            self.current_file = translation_unit.spelling
            
            # 分析编译器诊断信息
            self._analyze_printf_diagnostics(translation_unit)
            
            # 分析AST中的printf调用
            self._analyze_printf_calls(translation_unit.cursor)
            
            return self.error_reporter.get_reports()
            
        except Exception as e:
            print(f"libclang printf分析出错: {e}")
            return []
    
    def _analyze_printf_diagnostics(self, translation_unit):
        """分析编译器诊断信息中的printf问题"""
        diagnostics = translation_unit.diagnostics
        
        for diag in diagnostics:
            # 只处理当前文件的诊断信息，忽略系统头文件
            if diag.location.file and diag.location.file.name != self.current_file:
                continue
            
            # 检查printf格式字符串问题
            if 'format' in diag.spelling.lower():
                # 提取变量名（如果有）
                variable_name = ""
                if 'argument' in diag.spelling.lower():
                    # 尝试从诊断信息中提取变量名
                    match = re.search(r"argument (\d+)", diag.spelling)
                    if match:
                        variable_name = f"arg{match.group(1)}"
                
                self.error_reporter.add_library_error(
                    diag.location.line,
                    f"printf格式字符串问题: {diag.spelling}",
                    "建议检查格式字符串和参数类型是否匹配",
                    f"位置: {diag.location.file}:{diag.location.line}:{diag.location.column}",
                    variable_name
                )
    
    def _analyze_printf_calls(self, cursor):
        """分析AST中的printf调用"""
        # 只处理当前文件的节点，忽略宏展开
        if (cursor.location.file and 
            cursor.location.file.name != self.current_file):
            return
        
        if hasattr(cursor.location, 'is_from_macro') and cursor.location.is_from_macro():
            return
        
        # 检查printf函数调用
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            func_name = cursor.spelling
            if func_name in ['printf', 'fprintf', 'sprintf', 'snprintf', 'dprintf', 'vprintf', 'vfprintf', 'vsprintf', 'vsnprintf']:
                self._analyze_single_printf_call(cursor)
        
        # 递归处理子节点
        for child in cursor.get_children():
            self._analyze_printf_calls(child)
    
    def _analyze_single_printf_call(self, call_cursor):
        """分析单个printf调用"""
        children = list(call_cursor.get_children())
        if len(children) < 2:
            return
        
        # 第一个参数是格式字符串
        format_cursor = children[0]
        
        # 检查格式字符串类型
        if format_cursor.kind == clang.cindex.CursorKind.STRING_LITERAL:
            # 字面量字符串
            format_string = format_cursor.spelling
            actual_args_count = len(children) - 1
            
            # 计算格式说明符数量
            format_specifiers_count = self._count_format_specifiers(format_string)
            
            if format_specifiers_count != actual_args_count:
                # 获取原始代码片段
                code_snippet = self._get_source_code_snippet(call_cursor)
                
                self.error_reporter.add_library_error(
                    call_cursor.location.line,
                    f"printf格式字符串参数不匹配: 格式说明符数量({format_specifiers_count})与参数数量({actual_args_count})不匹配",
                    "建议检查格式字符串和参数类型是否匹配",
                    code_snippet,
                    f"printf_call_line_{call_cursor.location.line}"
                )
        
        elif format_cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            # 格式字符串是变量
            format_var_name = format_cursor.spelling
            actual_args_count = len(children) - 1
            
            # 对于变量格式字符串，我们无法静态分析，但可以给出警告
            code_snippet = self._get_source_code_snippet(call_cursor)
            
            self.error_reporter.add_library_error(
                call_cursor.location.line,
                f"printf使用变量格式字符串 '{format_var_name}'，无法静态验证参数匹配",
                "建议使用字面量格式字符串或添加运行时检查",
                code_snippet,
                format_var_name
            )
    
    def _count_format_specifiers(self, format_string: str) -> int:
        """计算格式字符串中的格式说明符数量"""
        # 移除转义字符
        format_string = format_string.replace('\\n', '').replace('\\t', '').replace('\\\\', '')
        
        # 匹配%[flags][width][.precision][length]specifier
        # 支持所有标准printf格式说明符
        pattern = r'%[+-]?[0-9]*\.?[0-9]*[hlL]?[diouxXeEfFgGaAcspn%]'
        matches = re.findall(pattern, format_string)
        
        # 过滤掉%%（转义的%）
        actual_specifiers = [match for match in matches if match != '%%']
        
        return len(actual_specifiers)
    
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

def test_libclang_printf_detector():
    """测试libclang printf检测器"""
    if not LIBCLANG_AVAILABLE:
        print("libclang不可用，跳过测试")
        return
    
    detector = LibClangPrintfDetector()
    
    # 创建测试文件
    test_code = """
#include <stdio.h>

int main() {
    int x = 10;
    int y = 20;
    
    // 正确的printf调用
    printf("x = %d\\n", x);
    printf("x = %d, y = %d\\n", x, y);
    
    // 错误的printf调用 - 参数不足
    printf("x = %d, y = %d\\n", x);  // 缺少y参数
    
    // 错误的printf调用 - 参数过多
    printf("x = %d\\n", x, y);  // 多余的y参数
    
    // 复杂的格式字符串
    printf("Point: (%d, %d)\\n", x, y);  // 正确
    printf("Point: (%d, %d)\\n", x);     // 错误：缺少y参数
    
    return 0;
}
"""
    
    with open("test_printf_libclang.c", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    try:
        reports = detector.analyze_file("test_printf_libclang.c")
        print(f"检测到 {len(reports)} 个printf问题:")
        for report in reports:
            print(f"  Line {report.line_number}: {report.message}")
    finally:
        # 清理测试文件
        import os
        if os.path.exists("test_printf_libclang.c"):
            os.remove("test_printf_libclang.c")

if __name__ == "__main__":
    test_libclang_printf_detector()
