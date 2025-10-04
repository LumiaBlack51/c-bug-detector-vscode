#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定行的检测结果
"""
import json
import subprocess
import sys

def check_specific_lines():
    try:
        result = subprocess.run(['python', 'main.py', '../test_struct_pointers.c', '--format', 'json'], 
                               capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            print("检查typedef结构体定义行的检测结果:")
            for item in data:
                if item['line_number'] in [49, 50, 51, 52, 53, 54, 55]:
                    print(f"Line {item['line_number']}: {item['message']}")
                    print(f"  Module: {item['module_name']}")
                    print(f"  Type: {item['error_type']}")
                    print(f"  Code: {item.get('code_snippet', 'N/A')}")
                    print()
        else:
            print("检测器运行失败")
            
    except Exception as e:
        print(f"分析过程中出错: {e}")

if __name__ == '__main__':
    check_specific_lines()
