#!/usr/bin/env python3
"""
C语言Bug检测器演示脚本
展示各个模块的检测能力
"""
import os
import sys
from main import CBugDetector


def demo_memory_safety():
    """演示内存安全检测"""
    print("🔍 内存安全卫士模块演示")
    print("="*40)
    
    detector = CBugDetector()
    detector.disable_module('variable_state')
    detector.disable_module('standard_library')
    detector.disable_module('numeric_control_flow')
    
    reports = detector.analyze_file('tests/test_memory_safety.c')
    
    if reports:
        print(f"检测到 {len(reports)} 个内存安全问题:")
        for i, report in enumerate(reports[:5], 1):  # 只显示前5个
            print(f"{i}. 第{report.line_number}行: {report.message}")
        if len(reports) > 5:
            print(f"... 还有 {len(reports) - 5} 个问题")
    else:
        print("✅ 没有发现内存安全问题")
    print()


def demo_variable_state():
    """演示变量状态检测"""
    print("🔍 变量状态监察官模块演示")
    print("="*40)
    
    detector = CBugDetector()
    detector.disable_module('memory_safety')
    detector.disable_module('standard_library')
    detector.disable_module('numeric_control_flow')
    
    reports = detector.analyze_file('tests/test_variable_state.c')
    
    if reports:
        print(f"检测到 {len(reports)} 个变量状态问题:")
        for i, report in enumerate(reports[:5], 1):  # 只显示前5个
            print(f"{i}. 第{report.line_number}行: {report.message}")
        if len(reports) > 5:
            print(f"... 还有 {len(reports) - 5} 个问题")
    else:
        print("✅ 没有发现变量状态问题")
    print()


def demo_standard_library():
    """演示标准库使用检测"""
    print("🔍 标准库使用助手模块演示")
    print("="*40)
    
    detector = CBugDetector()
    detector.disable_module('memory_safety')
    detector.disable_module('variable_state')
    detector.disable_module('numeric_control_flow')
    
    reports = detector.analyze_file('tests/test_standard_library.c')
    
    if reports:
        print(f"检测到 {len(reports)} 个标准库使用问题:")
        for i, report in enumerate(reports[:5], 1):  # 只显示前5个
            print(f"{i}. 第{report.line_number}行: {report.message}")
        if len(reports) > 5:
            print(f"... 还有 {len(reports) - 5} 个问题")
    else:
        print("✅ 没有发现标准库使用问题")
    print()


def demo_numeric_control_flow():
    """演示数值与控制流检测"""
    print("🔍 数值与控制流分析器模块演示")
    print("="*40)
    
    detector = CBugDetector()
    detector.disable_module('memory_safety')
    detector.disable_module('variable_state')
    detector.disable_module('standard_library')
    
    reports = detector.analyze_file('tests/test_numeric_control_flow.c')
    
    if reports:
        print(f"检测到 {len(reports)} 个数值与控制流问题:")
        for i, report in enumerate(reports[:5], 1):  # 只显示前5个
            print(f"{i}. 第{report.line_number}行: {report.message}")
        if len(reports) > 5:
            print(f"... 还有 {len(reports) - 5} 个问题")
    else:
        print("✅ 没有发现数值与控制流问题")
    print()


def demo_full_analysis():
    """演示完整分析"""
    print("🔍 完整分析演示")
    print("="*40)
    
    detector = CBugDetector()
    reports = detector.analyze_file('tests/test_memory_safety.c')
    
    if reports:
        print(f"检测到 {len(reports)} 个问题:")
        
        # 按模块分组统计
        module_stats = {}
        for report in reports:
            module_name = report.module_name
            if module_name not in module_stats:
                module_stats[module_name] = 0
            module_stats[module_name] += 1
        
        print("\n📊 问题统计:")
        for module_name, count in module_stats.items():
            print(f"   {module_name}: {count} 个问题")
        
        print("\n🔍 问题详情:")
        for i, report in enumerate(reports[:10], 1):  # 只显示前10个
            print(f"{i}. [{report.module_name}] 第{report.line_number}行: {report.message}")
        if len(reports) > 10:
            print(f"... 还有 {len(reports) - 10} 个问题")
    else:
        print("✅ 没有发现任何问题")
    print()


def main():
    """主演示函数"""
    print("🎯 C语言Bug检测器功能演示")
    print("="*50)
    print()
    
    # 检查测试文件是否存在
    test_files = [
        'tests/test_memory_safety.c',
        'tests/test_variable_state.c',
        'tests/test_standard_library.c',
        'tests/test_numeric_control_flow.c'
    ]
    
    missing_files = []
    for file_path in test_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少测试文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n请确保所有测试文件都存在后再运行演示")
        return
    
    # 运行各个模块演示
    demo_memory_safety()
    demo_variable_state()
    demo_standard_library()
    demo_numeric_control_flow()
    demo_full_analysis()
    
    print("🎉 演示完成！")
    print("\n💡 提示:")
    print("   - 使用 'python main.py --list-modules' 查看所有可用模块")
    print("   - 使用 'python main.py <文件路径>' 分析您的C代码")
    print("   - 使用 'python main.py --help' 查看所有可用选项")


if __name__ == "__main__":
    main()
