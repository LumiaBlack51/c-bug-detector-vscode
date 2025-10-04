#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误报告器 - 重构版本
分析模块只负责生成问题对象，不关心最终报告格式
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from .global_error_manager import global_error_manager
from .issue import Issue, IssueType, Severity

class ErrorReporter:
    """错误报告器类 - 重构版本，只生成问题对象"""
    
    def __init__(self):
        self.issues: List[Issue] = []
    
    def add_issue(self, issue: Issue):
        """添加问题对象"""
        # 检查是否应该报告这个错误
        if self._should_report(issue):
            self.issues.append(issue)
            self._mark_reported(issue)
    
    def add_memory_error(self, line_num: int, message: str, suggestion: str, 
                        variable_name: str = "", ast_node=None, libclang_cursor=None):
        """添加内存安全错误"""
        # 确定错误类型
        error_type = "memory_leak"
        if "野指针" in message or "wild pointer" in message.lower():
            error_type = "wild_pointer_dereference"
        elif "use after free" in message.lower() or "释放后使用" in message:
            error_type = "use_after_free"
        elif "null pointer" in message.lower() or "空指针" in message:
            error_type = "null_pointer_dereference"
        elif "malloc" in message.lower() and "null" in message.lower():
            error_type = "malloc_null_check"
        
        issue = Issue(
            issue_type=IssueType.MEMORY_SAFETY,
            severity=Severity.ERROR,
            description=message,
            suggestion=suggestion,
            line_number=line_num,
            variable_name=variable_name,
            module_name="内存安全卫士",
            error_category="memory",
            error_type=error_type,
            ast_node=ast_node,
            libclang_cursor=libclang_cursor
        )
        
        self.add_issue(issue)
    
    def add_variable_error(self, line_num: int, message: str, suggestion: str, 
                          variable_name: str = "", ast_node=None, libclang_cursor=None):
        """添加变量状态错误"""
        error_type = "uninitialized_variable"
        if "unused" in message.lower() or "未使用" in message:
            error_type = "unused_variable"
        
        issue = Issue(
            issue_type=IssueType.VARIABLE_STATE,
            severity=Severity.ERROR,
            description=message,
            suggestion=suggestion,
            line_number=line_num,
            variable_name=variable_name,
            module_name="变量状态监察官",
            error_category="variable",
            error_type=error_type,
            ast_node=ast_node,
            libclang_cursor=libclang_cursor
        )
        
        self.add_issue(issue)
    
    def add_library_error(self, line_num: int, message: str, suggestion: str, 
                         variable_name: str = "", ast_node=None, libclang_cursor=None):
        """添加标准库使用错误"""
        issue = Issue(
            issue_type=IssueType.STANDARD_LIBRARY,
            severity=Severity.ERROR,
            description=message,
            suggestion=suggestion,
            line_number=line_num,
            variable_name=variable_name,
            module_name="标准库使用检查器",
            error_category="library",
            error_type="printf_format",
            ast_node=ast_node,
            libclang_cursor=libclang_cursor
        )
        
        self.add_issue(issue)
    
    def add_numeric_error(self, line_num: int, message: str, suggestion: str, 
                         variable_name: str = "", ast_node=None, libclang_cursor=None):
        """添加数值与控制流错误"""
        issue = Issue(
            issue_type=IssueType.NUMERIC_CONTROL_FLOW,
            severity=Severity.ERROR,
            description=message,
            suggestion=suggestion,
            line_number=line_num,
            variable_name=variable_name,
            module_name="数值与控制流分析器",
            error_category="numeric",
            error_type="dead_loop",
            ast_node=ast_node,
            libclang_cursor=libclang_cursor
        )
        
        self.add_issue(issue)
    
    def add_control_flow_error(self, line_num: int, message: str, suggestion: str, 
                              variable_name: str = "", ast_node=None, libclang_cursor=None):
        """添加控制流错误（别名方法）"""
        self.add_numeric_error(line_num, message, suggestion, variable_name, ast_node, libclang_cursor)
    
    def _should_report(self, issue: Issue) -> bool:
        """检查是否应该报告这个错误"""
        return global_error_manager.should_report_error(
            issue.line_number, issue.variable_name, issue.error_type, issue.error_category
        )
    
    def _mark_reported(self, issue: Issue):
        """标记错误已报告"""
        global_error_manager.mark_error_reported(
            issue.line_number, issue.variable_name, issue.error_type, issue.error_category
        )
    
    def get_issues(self) -> List[Issue]:
        """获取所有问题对象"""
        return self.issues
    
    def clear_issues(self):
        """清空问题列表"""
        self.issues.clear()
        global_error_manager.clear()
