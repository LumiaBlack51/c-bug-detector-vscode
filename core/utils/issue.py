#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题对象定义 - 重构版本
分析模块只负责生成问题对象，不关心最终报告格式
"""
from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum

class IssueType(Enum):
    """问题类型枚举"""
    MEMORY_SAFETY = "内存安全"
    VARIABLE_STATE = "变量状态"
    STANDARD_LIBRARY = "标准库使用"
    NUMERIC_CONTROL_FLOW = "数值与控制流"

class Severity(Enum):
    """问题严重程度"""
    ERROR = "错误"
    WARNING = "警告"
    INFO = "提示"

@dataclass
class Issue:
    """问题对象 - 包含所有结构化信息"""
    # 基本信息
    issue_type: IssueType
    severity: Severity
    description: str
    suggestion: str
    
    # 位置信息
    line_number: int
    start_column: int = 0
    end_column: int = -1
    
    # 相关变量和上下文
    variable_name: str = ""
    module_name: str = ""
    
    # 原始数据（用于代码片段提取）
    ast_node: Optional[Any] = None
    libclang_cursor: Optional[Any] = None
    
    # 元数据
    error_category: str = ""
    error_type: str = ""
    code_snippet: str = ""
    
    def get_location_info(self) -> dict:
        """获取位置信息字典"""
        return {
            'line_number': self.line_number,
            'start_column': self.start_column,
            'end_column': self.end_column,
            'variable_name': self.variable_name
        }
    
    def get_context_info(self) -> dict:
        """获取上下文信息字典"""
        return {
            'module_name': self.module_name,
            'error_category': self.error_category,
            'error_type': self.error_type,
            'ast_node': self.ast_node,
            'libclang_cursor': self.libclang_cursor
        }
