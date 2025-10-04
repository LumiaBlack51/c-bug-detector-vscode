#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试_is_type_definition方法
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.memory_safety_improved import ImprovedMemorySafetyModule

def test_type_definition_detection():
    """测试类型定义检测"""
    
    analyzer = ImprovedMemorySafetyModule()
    
    # 测试用例
    test_lines = [
        "typedef struct {",
        "    int id;",
        "    char name[50];", 
        "} Student;",
        "struct Point {",
        "    int x;",
        "    int y;",
        "};",
        "int main() {",
        "    int count;",
        "    char buffer[100];",
        "    return 0;",
        "}"
    ]
    
    print("测试_is_type_definition方法:")
    for i, line in enumerate(test_lines, 1):
        is_type_def = analyzer._is_type_definition(line)
        print(f"Line {i}: {line.strip():30} -> {'是类型定义' if is_type_def else '不是类型定义'}")

if __name__ == '__main__':
    test_type_definition_detection()
