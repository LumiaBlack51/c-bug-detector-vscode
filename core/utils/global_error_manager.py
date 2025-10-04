#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局错误管理器 - 解决重复报告问题
"""
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    """错误严重程度"""
    INFO = "信息"
    WARNING = "警告" 
    ERROR = "错误"
    CRITICAL = "严重"

@dataclass
class ErrorKey:
    """错误唯一标识"""
    line_number: int
    variable_name: str
    error_type: str
    error_category: str  # 'memory', 'variable', 'library'
    
    def __hash__(self):
        return hash((self.line_number, self.variable_name, self.error_type, self.error_category))

class GlobalErrorManager:
    """全局错误管理器 - 智能去重和错误升级"""
    
    def __init__(self):
        self.reported_errors: Set[ErrorKey] = set()
        self.error_hierarchy: Dict[str, List[str]] = {
            # 更严重的错误会抑制较轻的错误
            'wild_pointer_dereference': ['uninitialized_variable', 'unused_variable', 'malloc_null_check'],
            'use_after_free': ['uninitialized_variable', 'memory_leak'],
            'null_pointer_dereference': ['uninitialized_variable'],
            'memory_leak': ['malloc_null_check'],
            'uninitialized_variable': ['unused_variable'],
        }
        
        # 错误严重程度映射
        self.error_severity = {
            'wild_pointer_dereference': 1,  # 最严重
            'use_after_free': 2,
            'null_pointer_dereference': 3,
            'memory_leak': 4,
            'uninitialized_variable': 5,
            'malloc_null_check': 6,
            'unused_variable': 7,
            'printf_format': 8,
        }
        
    def should_report_error(self, line_number: int, variable_name: str, 
                          error_type: str, error_category: str) -> bool:
        """检查是否应该报告这个错误 - 跨模块协调和智能去重"""
        error_key = ErrorKey(line_number, variable_name, error_type, error_category)
        
        # 检查是否已经报告过完全相同的错误
        if error_key in self.reported_errors:
            return False
            
        # 检查同一行同一变量的其他错误（跨模块协调）
        conflicting_errors = []
        for reported_key in self.reported_errors:
            if (reported_key.line_number == line_number and 
                reported_key.variable_name == variable_name):
                conflicting_errors.append(reported_key)
        
        # 如果有冲突错误，进行智能处理
        if conflicting_errors:
            current_severity = self.error_severity.get(error_type, 10)
            
            for reported_key in conflicting_errors:
                reported_severity = self.error_severity.get(reported_key.error_type, 10)
                
                # 如果新错误更严重，移除旧错误
                if current_severity < reported_severity:
                    self.reported_errors.remove(reported_key)
                    print(f"Error upgraded: {reported_key.error_type} -> {error_type} (line {line_number}, variable {variable_name})")
                # 如果旧错误更严重，不报告新错误
                elif reported_severity < current_severity:
                    print(f"错误抑制: {error_type} 被 {reported_key.error_type} 抑制 (行{line_number}, 变量{variable_name})")
                    return False
                # 如果严重程度相同，检查是否被抑制
                elif self._is_suppressed_by(error_type, reported_key.error_type):
                    print(f"错误抑制: {error_type} 被 {reported_key.error_type} 抑制 (行{line_number}, 变量{variable_name})")
                    return False
                    
        return True
    
    def mark_error_reported(self, line_number: int, variable_name: str,
                          error_type: str, error_category: str):
        """标记错误已报告"""
        error_key = ErrorKey(line_number, variable_name, error_type, error_category)
        self.reported_errors.add(error_key)
    
    def _is_suppressed_by(self, error_type: str, suppressor_type: str) -> bool:
        """检查error_type是否被suppressor_type抑制"""
        if suppressor_type in self.error_hierarchy:
            return error_type in self.error_hierarchy[suppressor_type]
        return False
    
    def get_error_priority(self, error_type: str) -> int:
        """获取错误优先级（数字越小优先级越高）"""
        return self.error_severity.get(error_type, 10)
    
    def clear(self):
        """清空已报告的错误"""
        self.reported_errors.clear()

# 全局错误管理器实例
global_error_manager = GlobalErrorManager()
