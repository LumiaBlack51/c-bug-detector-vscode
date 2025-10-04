#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的libclang分析器
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.libclang_analyzer import LibClangAnalyzer

def test_fixed_analyzer():
    """测试修复后的分析器"""
    
    # 创建测试文件
    test_code = """
#include <stdio.h>
#include <stdlib.h>

// 测试typedef结构体定义 - 不应该被误识别为内存分配
typedef struct {
    int id;
    char name[50];
} User;

// 测试结构体定义 - 也不应该被误识别
struct Product {
    double price;
    int quantity;
};

int main() {
    // 测试变量声明 - 这些应该被正确识别
    User user1;           // 未初始化的结构体变量
    struct Product prod1; // 未初始化的结构体变量
    int count;            // 未初始化的基本类型变量
    
    // 测试malloc调用 - 应该被正确识别为内存分配
    User* user2 = malloc(sizeof(User));
    
    // 测试未初始化变量使用 - 应该检测到
    printf("User ID: %d\\n", user1.id);     // BUG: 使用未初始化变量
    printf("Count: %d\\n", count);          // BUG: 使用未初始化变量
    
    // 测试野指针解引用 - 应该检测到
    User* wild_ptr;       // 未初始化的指针
    wild_ptr->id = 100;   // BUG: 野指针解引用
    
    // 测试printf格式字符串 - 应该检测到
    printf("Price: %d\\n", prod1.price);    // BUG: 格式字符串不匹配
    
    if (user2) {
        free(user2);
    }
    
    return 0;
}
"""
    
    # 写入测试文件
    test_file = "test_fixed_analyzer.c"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    try:
        # 运行分析器
        analyzer = LibClangAnalyzer()
        reports = analyzer.analyze_file(test_file)
        
        print("=== 修复后的检测结果 ===")
        print(f"总检测问题数: {len(reports)}")
        
        # 按类型分组
        issue_types = {}
        for report in reports:
            error_type = report.error_type
            if error_type not in issue_types:
                issue_types[error_type] = []
            issue_types[error_type].append(report)
        
        for error_type, issues in issue_types.items():
            print(f"\n{error_type} ({len(issues)}个):")
            for issue in issues:
                print(f"  Line {issue.line_number}: {issue.message}")
        
        # 分析结果
        print(f"\n=== 结果分析 ===")
        
        # 检查是否还有误报
        false_positives = []
        for report in reports:
            line_num = report.line_number
            # 检查是否是typedef或结构体定义行
            if line_num in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
                false_positives.append(report)
        
        if false_positives:
            print(f"发现 {len(false_positives)} 个可能的误报:")
            for fp in false_positives:
                print(f"  Line {fp.line_number}: {fp.message}")
        else:
            print("没有发现明显的误报！")
        
        # 检查是否检测到期望的问题
        expected_issues = [
            "使用未初始化的变量 'user1'",
            "使用未初始化的变量 'count'", 
            "可能的野指针解引用: 'wild_ptr'",
            "printf格式字符串参数不匹配"
        ]
        
        detected_expected = []
        for report in reports:
            for expected in expected_issues:
                if expected in report.message:
                    detected_expected.append(expected)
                    break
        
        print(f"\n期望检测的问题: {len(expected_issues)}")
        print(f"实际检测到: {len(detected_expected)}")
        print("检测到的问题:")
        for issue in detected_expected:
            print(f"  OK {issue}")
        
        missing = set(expected_issues) - set(detected_expected)
        if missing:
            print("未检测到的问题:")
            for issue in missing:
                print(f"  X {issue}")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == '__main__':
    test_fixed_analyzer()
