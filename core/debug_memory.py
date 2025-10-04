#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试内存分配识别
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.memory_safety_improved import ImprovedMemorySafetyModule
from utils.code_parser import CCodeParser

def debug_memory_allocations():
    """调试内存分配识别"""
    
    # 读取测试文件
    with open('../test_struct_pointers.c', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析代码
    parser = CCodeParser()
    parsed_data = parser.parse_file('../test_struct_pointers.c')
    
    # 创建分析器
    analyzer = ImprovedMemorySafetyModule()
    
    # 运行分析
    analyzer._identify_memory_operations(parsed_data)
    
    print("内存分配识别结果:")
    print(f"malloced_variables: {analyzer.malloced_variables}")
    print(f"memory_allocations: {analyzer.memory_allocations}")
    
    print("\n检查typedef相关行:")
    for line_num, line_content in enumerate(parsed_data['lines'], 1):
        if line_num in [49, 50, 51, 52, 53, 54, 55]:
            print(f"Line {line_num}: {line_content.strip()}")
            is_type_def = analyzer._is_type_definition(line_content)
            print(f"  -> 是类型定义: {is_type_def}")

if __name__ == '__main__':
    debug_memory_allocations()
