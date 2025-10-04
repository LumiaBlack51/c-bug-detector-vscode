#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析检测结果的漏报和误报情况
"""
import json
import subprocess
import sys

def analyze_detection_results():
    # 读取测试文件
    with open('../test_struct_pointers.c', 'r', encoding='utf-8') as f:
        code_lines = f.readlines()
    
    # 分析代码中的BUG注释
    expected_bugs = []
    for i, line in enumerate(code_lines, 1):
        if 'BUG:' in line:
            expected_bugs.append((i, line.strip()))
    
    print('=== 代码中标记的BUG (期望检测到的问题) ===')
    for line_num, line_content in expected_bugs:
        print(f'Line {line_num}: {line_content}')
    
    print(f'\n期望检测的BUG总数: {len(expected_bugs)}')
    
    # 运行检测器
    try:
        result = subprocess.run(['python', 'main.py', '../test_struct_pointers.c', '--format', 'json'], 
                               capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            detected_issues = json.loads(result.stdout)
            
            print(f'\n=== 实际检测到的问题 ===')
            print(f'实际检测问题总数: {len(detected_issues)}')
            
            # 按行号分组
            detected_by_line = {}
            for issue in detected_issues:
                line_num = issue['line_number']
                if line_num not in detected_by_line:
                    detected_by_line[line_num] = []
                detected_by_line[line_num].append(issue)
            
            print(f'涉及的行数: {len(detected_by_line)}')
            
            # 检查漏报
            print(f'\n=== 漏报分析 ===')
            missed_lines = []
            for line_num, _ in expected_bugs:
                if line_num not in detected_by_line:
                    missed_lines.append(line_num)
            
            if missed_lines:
                print(f'漏报的行号: {missed_lines}')
                for line_num in missed_lines:
                    print(f'  Line {line_num}: {code_lines[line_num-1].strip()}')
            else:
                print('没有发现漏报！')
            
            # 检查误报
            print(f'\n=== 误报分析 ===')
            false_positives = []
            for line_num, issues in detected_by_line.items():
                # 检查这一行是否应该有问题
                has_expected_bug = any(exp_line == line_num for exp_line, _ in expected_bugs)
                if not has_expected_bug:
                    # 检查是否是明显的误报
                    line_content = code_lines[line_num-1].strip()
                    # 排除一些合理的检测（如malloc未检查返回值、内存泄漏等）
                    if not any(keyword in line_content.lower() for keyword in 
                              ['malloc', 'calloc', 'free', 'printf', 'unused', 'uninitialized']):
                        false_positives.append((line_num, line_content, issues))
            
            if false_positives:
                print(f'可能的误报 (前10个):')
                for line_num, line_content, issues in false_positives[:10]:
                    print(f'  Line {line_num}: {line_content}')
                    for issue in issues[:2]:  # 只显示前2个问题
                        print(f'    - {issue["message"]}')
            else:
                print('没有发现明显的误报！')
            
            # 统计各类型问题
            print(f'\n=== 问题类型统计 ===')
            issue_types = {}
            for issue in detected_issues:
                error_type = issue['error_type']
                if error_type not in issue_types:
                    issue_types[error_type] = 0
                issue_types[error_type] += 1
            
            for error_type, count in issue_types.items():
                print(f'{error_type}: {count}')
                
        else:
            print('检测器运行失败')
            print(f'错误信息: {result.stderr}')
            
    except Exception as e:
        print(f'分析过程中出错: {e}')

if __name__ == '__main__':
    analyze_detection_results()
