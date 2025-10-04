#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的内存安全模块 - 使用正确的行号映射
"""
import sys
import os
import re
from typing import List, Dict, Set, Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_ast_parser import enhanced_parser, ASTNode
from utils.error_reporter import ErrorReporter, BugReport
from utils.issue import Issue, IssueType, Severity
from utils.source_code_extractor import SourceCodeExtractor

class EnhancedMemorySafetyModule:
    """增强的内存安全模块 - 使用正确的行号映射"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.malloced_variables: Set[str] = set()
        self.freed_variables: Set[str] = set()
        self.memory_allocations: Dict[str, Dict] = {}
        self.current_file = ""
        
        # 正则表达式模式
        self.patterns = {
            'malloc': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)'),
            'calloc': re.compile(r'\b(\w+)\s*=\s*calloc\s*\([^)]+\)'),
            'realloc': re.compile(r'\b(\w+)\s*=\s*realloc\s*\([^)]+\)'),
            'free': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)'),
            'pointer_dereference': re.compile(r'\*(\w+)|\b(\w+)\s*->\s*\w+'),
        }
    
    def get_module_name(self):
        return "增强内存安全卫士"
    
    def analyze(self, parsed_data):
        """兼容性方法 - 调用analyze_file"""
        if not hasattr(self, 'current_file') or not self.current_file:
            return []
        return self.analyze_file(self.current_file)
    
    def analyze_file(self, file_path: str) -> List[Issue]:
        """分析文件，使用正确的行号映射"""
        self.error_reporter.clear_reports()
        self.current_file = file_path
        self.malloced_variables.clear()
        self.freed_variables.clear()
        self.memory_allocations.clear()
        
        try:
            # 使用增强的AST解析器
            ast_root = enhanced_parser.parse_file(file_path)
            if not ast_root:
                return []
            
            # 分析AST
            self._analyze_ast(ast_root)
            
            # 检查内存泄漏
            self._check_memory_leaks()
            
            # 将BugReport转换为Issue对象
            issues = []
            for report in self.error_reporter.get_reports():
                issue = Issue(
                    issue_type=IssueType.MEMORY_SAFETY,
                    severity=Severity(report.severity),
                    description=report.message,
                    suggestion=report.suggestion,
                    line_number=report.line_number,
                    variable_name=report.variable_name,
                    module_name=self.get_module_name(),
                    error_category=report.error_category,
                    code_snippet=report.code_snippet
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            print(f"增强内存安全分析失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _analyze_ast(self, node: ASTNode):
        """分析AST节点"""
        if not node:
            return
        
        # 处理不同类型的节点
        if node.node_type == 'FuncDef':
            self._handle_function_definition(node)
        elif node.node_type == 'Decl':
            self._handle_declaration(node)
        elif node.node_type == 'Assignment':
            self._handle_assignment(node)
        elif node.node_type == 'FuncCall':
            self._handle_function_call(node)
        
        # 递归处理子节点
        for child in node.children:
            self._analyze_ast(child)
    
    def _handle_function_definition(self, node: ASTNode):
        """处理函数定义"""
        # 函数开始时重置状态
        self.malloced_variables.clear()
        self.freed_variables.clear()
        self.memory_allocations.clear()
    
    def _handle_declaration(self, node: ASTNode):
        """处理变量声明"""
        # 检查是否有初始化
        for child in node.children:
            if child.node_type == 'InitList' or child.node_type == 'FuncCall':
                self._handle_initialization(node, child)
    
    def _handle_assignment(self, node: ASTNode):
        """处理赋值语句"""
        # 查找左值和右值
        left_var = None
        right_call = None
        
        for child in node.children:
            if child.node_type == 'ID':
                left_var = child.value
            elif child.node_type == 'FuncCall':
                right_call = child
        
        if left_var and right_call:
            self._handle_memory_allocation(left_var, right_call, node)
    
    def _handle_function_call(self, node: ASTNode):
        """处理函数调用"""
        # 获取函数名
        func_name = None
        for child in node.children:
            if child.node_type == 'ID':
                func_name = child.value
                break
        
        if func_name == 'free':
            self._handle_memory_deallocation(node)
    
    def _handle_initialization(self, decl_node: ASTNode, init_node: ASTNode):
        """处理变量初始化"""
        # 获取变量名
        var_name = None
        for child in decl_node.children:
            if child.node_type == 'ID':
                var_name = child.value
                break
        
        if var_name and init_node.node_type == 'FuncCall':
            self._handle_memory_allocation(var_name, init_node, decl_node)
    
    def _handle_memory_allocation(self, var_name: str, call_node: ASTNode, location_node: ASTNode):
        """处理内存分配"""
        # 获取函数名
        func_name = None
        for child in call_node.children:
            if child.node_type == 'ID':
                func_name = child.value
                break
        
        if func_name in ['malloc', 'calloc', 'realloc']:
            self.malloced_variables.add(var_name)
            self.memory_allocations[var_name] = {
                'alloc_type': func_name,
                'alloc_line': location_node.logical_line,
                'alloc_file': location_node.logical_file,
                'alloc_column': location_node.logical_column
            }
    
    def _handle_memory_deallocation(self, node: ASTNode):
        """处理内存释放"""
        # 获取要释放的变量名
        var_name = None
        for child in node.children:
            if child.node_type == 'ID':
                var_name = child.value
                break
        
        if var_name:
            self.freed_variables.add(var_name)
    
    def _check_memory_leaks(self):
        """检查内存泄漏"""
        for var_name, alloc_info in self.memory_allocations.items():
            if var_name not in self.freed_variables:
                # 创建源代码提取器
                source_extractor = SourceCodeExtractor(alloc_info['alloc_file'])
                code_snippet = source_extractor.get_code_snippet(alloc_info['alloc_line'])
                
                self.error_reporter.add_memory_error(
                    alloc_info['alloc_line'],
                    f"变量 '{var_name}' 分配了内存但未释放，可能导致内存泄漏",
                    f"建议在适当位置添加 free({var_name}); 语句",
                    code_snippet,
                    var_name,
                    alloc_info['alloc_file']
                )
    
    def get_description(self):
        return "增强的内存安全检测，使用正确的行号映射"
