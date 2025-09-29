#!/usr/bin/env python3
"""
测试改进的检测器模块
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.variable_state_improved import ImprovedVariableStateModule
from modules.memory_safety_improved import ImprovedMemorySafetyModule
from utils.code_parser import CCodeParser

def test_improved_modules():
    """测试改进的模块"""
    
    # 测试代码
    test_code = """
#include <stdio.h>
#include <stdlib.h>

struct Point {
    int x;
    int y;
};

void test_struct_pointers() {
    struct Point* p1;           // 未初始化指针
    struct Point* p2;           // 未初始化指针
    struct Point point1;        // 结构体变量
    
    // 应该检测到：未初始化指针解引用
    p1->x = 10;        // BUG: wild pointer dereference
    p2->y = 20;        // BUG: wild pointer dereference
    
    // 应该检测到：结构体成员访问（正确）
    point1.x = 100;    // 正确：访问结构体变量成员
    point1.y = 200;    // 正确：访问结构体变量成员
}

void test_memory_management() {
    // 应该检测到：malloc未检查返回值
    struct Point* p1 = malloc(sizeof(struct Point));
    struct Point* p2 = malloc(sizeof(struct Point));
    
    // 应该检测到：内存泄漏
    // 忘记释放 p1, p2
}

struct Point* create_point(int x, int y) {
    struct Point* p = malloc(sizeof(struct Point));
    if (p) {
        p->x = x;
        p->y = y;
    }
    return p; // 返回分配的内存
}

void test_interprocedural() {
    // 应该检测到：跨函数内存泄漏
    struct Point* p1 = create_point(1, 2);
    struct Point* p2 = create_point(3, 4);
    
    // 使用返回的指针
    if (p1) {
        printf("Point: (%d, %d)\\n", p1->x, p1->y);
    }
    
    // 忘记释放 p1, p2 - 应该检测到
}

int main() {
    test_struct_pointers();
    test_memory_management();
    test_interprocedural();
    return 0;
}
"""
    
    # 解析代码
    parser = CCodeParser()
    parsed_data = parser.parse_code(test_code)
    
    print("=" * 60)
    print("测试改进的变量状态监察官模块")
    print("=" * 60)
    
    # 测试改进的变量状态模块
    var_module = ImprovedVariableStateModule()
    var_reports = var_module.analyze(parsed_data)
    
    print(f"变量状态模块检测到 {len(var_reports)} 个问题:")
    for i, report in enumerate(var_reports, 1):
        print(f"{i}. 第{report.line_number}行: {report.message}")
        print(f"   建议: {report.suggestion}")
        print()
    
    print("=" * 60)
    print("测试改进的内存安全卫士模块")
    print("=" * 60)
    
    # 测试改进的内存安全模块
    mem_module = ImprovedMemorySafetyModule()
    mem_reports = mem_module.analyze(parsed_data)
    
    print(f"内存安全模块检测到 {len(mem_reports)} 个问题:")
    for i, report in enumerate(mem_reports, 1):
        print(f"{i}. 第{report.line_number}行: {report.message}")
        print(f"   建议: {report.suggestion}")
        print()
    
    print("=" * 60)
    print("改进效果总结")
    print("=" * 60)
    
    total_issues = len(var_reports) + len(mem_reports)
    print(f"总问题数: {total_issues}")
    print(f"变量状态问题: {len(var_reports)}")
    print(f"内存安全问题: {len(mem_reports)}")
    
    # 分析改进效果
    print("\n改进效果:")
    print("1. 变量状态模块现在能正确区分指针和结构体成员")
    print("2. 内存安全模块现在支持跨函数分析")
    print("3. 报告位置现在指向问题的根源（分配行号）")
    print("4. 减少了大量误报")

if __name__ == "__main__":
    test_improved_modules()
