#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证VS Code插件中的Python后端路径
"""

import os
import sys

def test_backend_path():
    """测试后端路径是否正确"""
    print("=== VS Code插件后端路径测试 ===")
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"当前脚本目录: {current_dir}")
    
    # 检查main.py是否存在
    main_py_path = os.path.join(current_dir, "main.py")
    print(f"main.py路径: {main_py_path}")
    print(f"main.py存在: {os.path.exists(main_py_path)}")
    
    # 检查modules目录
    modules_dir = os.path.join(current_dir, "modules")
    print(f"modules目录: {modules_dir}")
    print(f"modules目录存在: {os.path.exists(modules_dir)}")
    
    if os.path.exists(modules_dir):
        modules_files = os.listdir(modules_dir)
        print(f"modules文件数量: {len(modules_files)}")
        for f in modules_files:
            if f.endswith('.py'):
                print(f"  - {f}")
    
    # 检查utils目录
    utils_dir = os.path.join(current_dir, "utils")
    print(f"utils目录: {utils_dir}")
    print(f"utils目录存在: {os.path.exists(utils_dir)}")
    
    if os.path.exists(utils_dir):
        utils_files = os.listdir(utils_dir)
        print(f"utils文件数量: {len(utils_files)}")
        for f in utils_files:
            if f.endswith('.py'):
                print(f"  - {f}")
    
    # 测试导入
    try:
        sys.path.insert(0, current_dir)
        from modules.memory_safety_improved import ImprovedMemorySafetyModule
        print("成功导入ImprovedMemorySafetyModule")
    except Exception as e:
        print(f"导入失败: {e}")
    
    try:
        from modules.variable_state_improved import ImprovedVariableStateModule
        print("成功导入ImprovedVariableStateModule")
    except Exception as e:
        print(f"导入失败: {e}")
    
    try:
        from modules.standard_library import StandardLibraryModule
        print("成功导入StandardLibraryModule")
    except Exception as e:
        print(f"导入失败: {e}")
    
    try:
        from modules.numeric_control_flow import NumericControlFlowModule
        print("成功导入NumericControlFlowModule")
    except Exception as e:
        print(f"导入失败: {e}")

if __name__ == "__main__":
    test_backend_path()
