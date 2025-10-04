#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试libclang printf检测器
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.libclang_printf_detector import LibClangPrintfDetector

def test_printf_detector():
    """测试printf检测器"""
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
            print(f"    代码: {report.code_snippet}")
    finally:
        # 清理测试文件
        if os.path.exists("test_printf_libclang.c"):
            os.remove("test_printf_libclang.c")

if __name__ == "__main__":
    test_printf_detector()
