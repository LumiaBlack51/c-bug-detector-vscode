#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的AST解析器 - 支持正确的行号映射
"""
import os
import sys
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# 尝试导入pycparser
try:
    from pycparser import c_parser, c_ast
    from pycparser.c_ast import *
    C_AST_AVAILABLE = True
except ImportError:
    C_AST_AVAILABLE = False
    print("警告: pycparser未安装，将使用备用解析器")

from .enhanced_lexer import EnhancedLexer, Token
from .c_preprocessor import preprocessor

@dataclass
class ASTNode:
    """AST节点 - 包含正确的位置信息"""
    node_type: str
    children: List['ASTNode']
    logical_file: str
    logical_line: int
    logical_column: int
    value: Optional[str] = None
    attributes: Dict[str, Any] = None

class EnhancedASTParser:
    """增强的AST解析器"""
    
    def __init__(self):
        self.current_file = ""
        self.lexer: Optional[EnhancedLexer] = None
        self.tokens: List[Token] = []
        self.token_index = 0
    
    def parse_file(self, file_path: str) -> Optional[ASTNode]:
        """
        解析C文件，返回带有正确行号映射的AST
        
        Args:
            file_path: C源文件路径
            
        Returns:
            AST根节点，包含正确的位置信息
        """
        self.current_file = file_path
        temp_file_path = None
        
        try:
            # 第一步：预处理并创建临时文件
            temp_file_path, line_mapping = preprocessor.create_temp_preprocessed_file(file_path)
            
            # 第二步：读取预处理后的代码
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                preprocessed_code = f.read()
            
            # 第三步：词法分析
            self.lexer = EnhancedLexer(preprocessed_code)
            self.tokens = self.lexer.tokenize()
            self.token_index = 0
            
            # 第四步：语法分析
            if C_AST_AVAILABLE:
                return self._parse_with_pycparser(preprocessed_code, file_path)
            else:
                return self._parse_with_simple_parser()
                
        except Exception as e:
            print(f"解析文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
    
    def _parse_with_pycparser(self, preprocessed_code: str, original_file: str) -> Optional[ASTNode]:
        """使用pycparser解析，但保持正确的位置信息"""
        try:
            # 使用pycparser解析预处理后的代码
            parser = c_parser.CParser()
            ast_root = parser.parse(preprocessed_code)
            
            # 将pycparser的AST转换为我们的AST，保持位置信息
            return self._convert_pycparser_ast(ast_root, original_file)
            
        except Exception as e:
            print(f"pycparser parsing failed: {e}")
            return None
    
    def _convert_pycparser_ast(self, node: Any, original_file: str) -> Optional[ASTNode]:
        """将pycparser的AST转换为我们的AST"""
        if node is None:
            return None
        
        # 获取位置信息 - 使用词法分析器的映射
        logical_file = original_file
        logical_line = 1
        logical_column = 1
        
        if hasattr(node, 'coord') and node.coord:
            # 使用词法分析器映射物理行号到逻辑行号
            logical_line, logical_column = self._map_physical_to_logical(
                node.coord.line, node.coord.column
            )
        
        # 创建我们的AST节点
        ast_node = ASTNode(
            node_type=type(node).__name__,
            children=[],
            logical_file=logical_file,
            logical_line=logical_line,
            logical_column=logical_column,
            attributes={}
        )
        
        # 递归处理子节点
        for child_name, child_node in node.children():
            if child_node is not None:
                child_ast = self._convert_pycparser_ast(child_node, original_file)
                if child_ast:
                    ast_node.children.append(child_ast)
        
        return ast_node
    
    def _parse_with_simple_parser(self) -> Optional[ASTNode]:
        """简单的解析器（备用方案）"""
        # 这里可以实现一个简单的解析器
        # 暂时返回None，表示解析失败
        return None
    
    def get_location_info(self, node: ASTNode) -> Dict[str, any]:
        """获取AST节点的位置信息"""
        return {
            'file': node.logical_file,
            'line': node.logical_line,
            'column': node.logical_column
        }
    
    def find_nodes_by_type(self, root: ASTNode, node_type: str) -> List[ASTNode]:
        """查找指定类型的AST节点"""
        result = []
        
        def traverse(node: ASTNode):
            if node.node_type == node_type:
                result.append(node)
            for child in node.children:
                traverse(child)
        
        if root:
            traverse(root)
        return result
    
    def find_nodes_by_line(self, root: ASTNode, line_number: int) -> List[ASTNode]:
        """查找指定行号的AST节点"""
        result = []
        
        def traverse(node: ASTNode):
            if node.logical_line == line_number:
                result.append(node)
            for child in node.children:
                traverse(child)
        
        if root:
            traverse(root)
        return result
    
    def _map_physical_to_logical(self, physical_line: int, physical_column: int) -> tuple:
        """将物理行号映射到逻辑行号"""
        # 查找最接近的token来获取逻辑位置
        for token in self.tokens:
            if token.physical_line == physical_line:
                return token.logical_line, token.logical_column
        
        # 如果找不到精确匹配，返回默认值
        return 1, 1

# 全局解析器实例
enhanced_parser = EnhancedASTParser()
