#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的词法分析器 - 支持#line指令的行号映射
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Token:
    """词法单元"""
    type: str
    value: str
    logical_file: str  # 逻辑文件名（原始文件）
    logical_line: int   # 逻辑行号（原始文件中的行号）
    physical_line: int  # 物理行号（预处理文件中的行号）
    logical_column: int  # 逻辑列号（原始文件中的列号）

class EnhancedLexer:
    """增强的词法分析器 - 支持#line指令"""
    
    def __init__(self, preprocessed_code: str):
        self.code = preprocessed_code
        self.lines = preprocessed_code.split('\n')
        
        # 位置追踪状态
        self.physical_line = 1
        self.logical_file = "unknown.c"
        self.logical_line = 1
        self.logical_column = 1
        
        # 词法单元列表
        self.tokens: List[Token] = []
        
        # 正则表达式模式
        self.patterns = {
            'line_directive': re.compile(r'^\s*#\s+(\d+)\s+"([^"]+)"'),
            'line_directive_simple': re.compile(r'^\s*#\s+(\d+)'),
            'identifier': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
            'number': re.compile(r'\d+'),
            'string': re.compile(r'"[^"]*"'),
            'char': re.compile(r"'[^']*'"),
            'operator': re.compile(r'[+\-*/=<>!&|^%~]+'),
            'punctuation': re.compile(r'[{}();,\[\]]'),
            'whitespace': re.compile(r'\s+'),
            'comment': re.compile(r'//.*$|/\*.*?\*/', re.DOTALL)
        }
    
    def tokenize(self) -> List[Token]:
        """词法分析主函数"""
        self.tokens.clear()
        
        for line_num, line in enumerate(self.lines, 1):
            self.physical_line = line_num
            self.logical_column = 1
            
            # 处理#line指令
            if self._handle_line_directive(line):
                continue
            
            # 处理普通代码行
            self._tokenize_line(line)
            
            # 更新逻辑行号
            self.logical_line += 1
        
        return self.tokens
    
    def _handle_line_directive(self, line: str) -> bool:
        """处理#line指令"""
        # 尝试匹配完整的#line指令
        match = self.patterns['line_directive'].match(line)
        if match:
            self.logical_line = int(match.group(1))
            self.logical_file = match.group(2)
            return True
        
        # 尝试匹配简化的#line指令（只有行号）
        match = self.patterns['line_directive_simple'].match(line)
        if match:
            self.logical_line = int(match.group(1))
            return True
        
        return False
    
    def _tokenize_line(self, line: str):
        """对单行进行词法分析"""
        pos = 0
        while pos < len(line):
            # 跳过空白字符
            whitespace_match = self.patterns['whitespace'].match(line, pos)
            if whitespace_match:
                pos += len(whitespace_match.group())
                self.logical_column += len(whitespace_match.group())
                continue
            
            # 尝试匹配各种词法单元
            token = self._match_token(line, pos)
            if token:
                self.tokens.append(token)
                pos += len(token.value)
                self.logical_column += len(token.value)
            else:
                # 无法识别的字符，跳过
                pos += 1
                self.logical_column += 1
    
    
    def _match_token(self, line: str, pos: int) -> Optional[Token]:
        """尝试匹配词法单元"""
        # 尝试匹配标识符
        match = self.patterns['identifier'].match(line, pos)
        if match:
            return Token(
                type='IDENTIFIER',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        # 尝试匹配数字
        match = self.patterns['number'].match(line, pos)
        if match:
            return Token(
                type='NUMBER',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        # 尝试匹配字符串
        match = self.patterns['string'].match(line, pos)
        if match:
            return Token(
                type='STRING',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        # 尝试匹配字符
        match = self.patterns['char'].match(line, pos)
        if match:
            return Token(
                type='CHAR',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        # 尝试匹配操作符
        match = self.patterns['operator'].match(line, pos)
        if match:
            return Token(
                type='OPERATOR',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        # 尝试匹配标点符号
        match = self.patterns['punctuation'].match(line, pos)
        if match:
            return Token(
                type='PUNCTUATION',
                value=match.group(),
                logical_file=self.logical_file,
                logical_line=self.logical_line,
                physical_line=self.physical_line,
                logical_column=self.logical_column
            )
        
        return None
    
    def get_location_info(self, token: Token) -> Dict[str, any]:
        """获取位置信息"""
        return {
            'file': token.logical_file,
            'line': token.logical_line,
            'column': token.logical_column,
            'physical_line': token.physical_line
        }
