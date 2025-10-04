#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的源代码片段提取器 - 重构版本
提供统一的、美观的代码片段显示
"""
import os
from typing import Optional, Tuple, List

class SourceCodeExtractor:
    """统一的源代码片段提取器 - 重构版本"""
    
    def __init__(self, filepath: str):
        """初始化时一次性加载整个源代码文件"""
        self.filepath = filepath
        self.lines = []
        self._load_source_code()
    
    def _load_source_code(self):
        """加载源代码文件"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # 将源代码按行存储，方便按行号索引
                self.lines = [line.rstrip('\n') for line in f.readlines()]
        except Exception as e:
            print(f"无法加载源代码文件 {self.filepath}: {e}")
            self.lines = []
    
    def get_code_snippet(self, line_number: int, start_col: int = 0, end_col: int = -1, context_lines: int = 1) -> str:
        """获取指定行的代码片段，带上下文和高亮"""
        if not self.lines or line_number < 1 or line_number > len(self.lines):
            return f"无法获取第 {line_number} 行的代码片段"
        
        # 计算上下文范围
        context_start = max(1, line_number - context_lines)
        context_end = min(len(self.lines), line_number + context_lines)
        
        snippet_lines = []
        for i in range(context_start, context_end + 1):
            line_num_str = f"{i: >{len(str(context_end))}} | "
            line_content = self.lines[i-1]
            snippet_lines.append(line_num_str + line_content)
            
            # 为有问题的行添加高亮标记
            if i == line_number and start_col >= 0 and end_col >= 0:
                # 计算高亮标记的起始位置
                highlight_prefix = ' ' * (len(line_num_str) + start_col)
                highlight_length = max(1, end_col - start_col)
                highlight = highlight_prefix + '^' + '~' * (highlight_length - 1)
                snippet_lines.append(highlight)
                
        return "\n".join(snippet_lines)
    
    def get_ast_node_snippet(self, ast_node, context_lines: int = 1) -> str:
        """从AST节点获取代码片段"""
        try:
            # 尝试获取AST节点的位置信息
            if hasattr(ast_node, 'coord') and ast_node.coord:
                line_number = ast_node.coord.line
                column = ast_node.coord.column
                return self.get_code_snippet(line_number, column, column + 10, context_lines)
            elif hasattr(ast_node, 'logical_line'):
                # 使用增强AST的位置信息
                line_number = ast_node.logical_line
                column = ast_node.logical_column
                return self.get_code_snippet(line_number, column, column + 10, context_lines)
            else:
                return f"AST节点: {type(ast_node).__name__}"
        except Exception as e:
            return f"无法从AST节点提取代码片段: {e}"
    
    def get_libclang_snippet(self, cursor, context_lines: int = 1) -> str:
        """从libclang cursor获取代码片段"""
        try:
            # 获取cursor的位置信息
            start_location = cursor.extent.start
            end_location = cursor.extent.end
            
            # 单行代码
            if start_location.line == end_location.line:
                return self.get_code_snippet(
                    start_location.line, 
                    start_location.column, 
                    end_location.column, 
                    context_lines
                )
            else:
                # 多行代码
                snippet_lines = []
                for line_num in range(start_location.line, end_location.line + 1):
                    line_num_str = f"{line_num: >3} | "
                    line_content = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                    snippet_lines.append(line_num_str + line_content)
                return "\n".join(snippet_lines)
                
        except Exception as e:
            return f"无法从libclang cursor提取代码片段: {e}"
    
    def get_simple_line(self, line_number: int) -> str:
        """获取简单的一行代码（无上下文）"""
        if not self.lines or line_number < 1 or line_number > len(self.lines):
            return f"无法获取第 {line_number} 行"
        return self.lines[line_number - 1]
    
    def clear_cache(self):
        """清空缓存（重新加载文件）"""
        self._load_source_code()

# 全局代码提取器实例（兼容旧代码）
source_extractor = None

def get_source_extractor(filepath: str) -> SourceCodeExtractor:
    """获取源代码提取器实例"""
    global source_extractor
    if source_extractor is None or source_extractor.filepath != filepath:
        source_extractor = SourceCodeExtractor(filepath)
    return source_extractor
