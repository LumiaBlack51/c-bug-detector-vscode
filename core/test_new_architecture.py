#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的三层架构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.source_code_extractor import SourceCodeExtractor
from utils.report_generator import ReportGenerator
from utils.issue import Issue, IssueType, Severity

def test_source_code_extractor():
    """测试源代码提取器"""
    print("=== 测试源代码提取器 ===")
    
    # 创建测试文件
    test_code = """
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *ptr;  // 未初始化指针
    *ptr = 42; // BUG: 野指针解引用
    return 0;
}
"""
    
    with open("test_new_arch.c", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    # 测试源代码提取器
    extractor = SourceCodeExtractor("test_new_arch.c")
    
    # 测试简单行提取
    line_6 = extractor.get_simple_line(6)
    print(f"第6行: {line_6}")
    
    # 测试带上下文的代码片段
    snippet = extractor.get_code_snippet(6, 4, 8, context_lines=1)
    print(f"第6行代码片段:\n{snippet}")
    
    # 清理测试文件
    os.remove("test_new_arch.c")
    print("源代码提取器测试完成\n")

def test_report_generator():
    """测试报告生成器"""
    print("=== 测试报告生成器 ===")
    
    # 创建测试文件
    test_code = """
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *ptr;  // 未初始化指针
    *ptr = 42; // BUG: 野指针解引用
    return 0;
}
"""
    
    with open("test_new_arch.c", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    # 创建问题对象
    issues = [
        Issue(
            issue_type=IssueType.MEMORY_SAFETY,
            severity=Severity.ERROR,
            description="野指针解引用：未初始化指针 'ptr' 被解引用",
            suggestion="建议在使用前初始化指针：ptr = malloc(sizeof(int)); 或 ptr = NULL;",
            line_number=6,
            start_column=4,
            end_column=8,
            variable_name="ptr",
            module_name="内存安全卫士",
            error_category="memory",
            error_type="wild_pointer_dereference"
        )
    ]
    
    # 测试报告生成器
    generator = ReportGenerator("test_new_arch.c")
    
    # 生成文本报告
    text_report = generator.generate_text_report(issues)
    print("文本报告:")
    print(text_report)
    print()
    
    # 生成JSON报告
    json_report = generator.generate_json_report(issues)
    print("JSON报告:")
    print(json_report)
    print()
    
    # 生成详细报告
    detailed_report = generator.generate_detailed_report(issues)
    print("详细报告:")
    print(detailed_report)
    print()
    
    # 生成摘要
    summary = generator.generate_summary(issues)
    print("摘要:")
    print(summary)
    
    # 清理测试文件
    os.remove("test_new_arch.c")
    print("报告生成器测试完成\n")

if __name__ == "__main__":
    test_source_code_extractor()
    test_report_generator()
    print("✅ 新架构测试完成！")
