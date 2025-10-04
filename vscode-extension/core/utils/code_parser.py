"""
C代码解析器 - 使用正则表达式解析C代码
"""
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VariableInfo:
    """变量信息"""
    name: str
    type: str
    line_number: int
    is_initialized: bool = False
    is_pointer: bool = False
    scope_level: int = 0


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    return_type: str
    parameters: List[str]
    line_number: int
    scope_level: int = 0


class CCodeParser:
    """C代码解析器"""
    
    def __init__(self):
        # 编译常用的正则表达式模式
        self.patterns = {
            # 变量声明
            'variable_declaration': re.compile(r'\b(int|char|float|double|long|short|unsigned|signed|void|struct\s+\w+)\s+(\w+)(?:\s*=\s*[^;]+)?\s*;', re.MULTILINE),
            
            # 指针声明
            'pointer_declaration': re.compile(r'\b(int|char|float|double|long|short|unsigned|signed|void|struct\s+\w+)\s*\*\s*(\w+)(?:\s*=\s*[^;]+)?\s*;', re.MULTILINE),
            
            # 函数定义
            'function_definition': re.compile(r'\b(int|char|float|double|long|short|unsigned|signed|void|struct\s+\w+)\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE),
            
            # 函数调用
            'function_call': re.compile(r'\b(\w+)\s*\([^)]*\)', re.MULTILINE),
            
            # 赋值语句
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            
            # 指针解引用
            'pointer_dereference': re.compile(r'\*(\w+)', re.MULTILINE),
            
            # malloc/free调用
            'malloc_call': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)', re.MULTILINE),
            'free_call': re.compile(r'\bfree\s*\([^)]+\)', re.MULTILINE),
            
            # scanf调用
            'scanf_call': re.compile(r'\bscanf\s*\([^)]+\)', re.MULTILINE),
            
            # printf调用
            'printf_call': re.compile(r'\bprintf\s*\([^)]+\)', re.MULTILINE),
            
            # 循环结构
            'while_loop': re.compile(r'\bwhile\s*\([^)]+\)\s*\{', re.MULTILINE),
            'for_loop': re.compile(r'\bfor\s*\([^)]+\)\s*\{', re.MULTILINE),
            'do_while_loop': re.compile(r'\bdo\s*\{', re.MULTILINE),
            
            # 头文件包含
            'include': re.compile(r'#include\s*[<"]([^>"]+)[>"]', re.MULTILINE),
            
            # 注释
            'single_comment': re.compile(r'//.*$', re.MULTILINE),
            'multi_comment': re.compile(r'/\*.*?\*/', re.DOTALL),
        }
    
    def parse_file(self, file_path: str) -> Dict[str, List]:
        """解析C文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_content(content)
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return {}
    
    def parse_content(self, content: str) -> Dict[str, List]:
        """解析C代码内容"""
        # 移除注释
        content = self._remove_comments(content)
        
        # 按行分割
        lines = content.split('\n')
        
        result = {
            'variables': [],
            'functions': [],
            'function_calls': [],
            'assignments': [],
            'pointer_dereferences': [],
            'malloc_calls': [],
            'free_calls': [],
            'scanf_calls': [],
            'printf_calls': [],
            'loops': [],
            'includes': [],
            'lines': lines
        }
        
        # 解析各种结构
        for line_num, line in enumerate(lines, 1):
            self._parse_line(line, line_num, result)
        
        return result
    
    def _remove_comments(self, content: str) -> str:
        """移除注释"""
        # 移除单行注释
        content = self.patterns['single_comment'].sub('', content)
        # 移除多行注释
        content = self.patterns['multi_comment'].sub('', content)
        return content
    
    def _parse_line(self, line: str, line_num: int, result: Dict[str, List]):
        """解析单行代码"""
        # 变量声明
        var_matches = self.patterns['variable_declaration'].findall(line)
        for var_type, var_name in var_matches:
            result['variables'].append(VariableInfo(
                name=var_name,
                type=var_type,
                line_number=line_num,
                is_initialized='=' in line,
                is_pointer=False
            ))
        
        # 指针声明
        ptr_matches = self.patterns['pointer_declaration'].findall(line)
        for ptr_type, ptr_name in ptr_matches:
            result['variables'].append(VariableInfo(
                name=ptr_name,
                type=ptr_type,
                line_number=line_num,
                is_initialized='=' in line,
                is_pointer=True
            ))
        
        # 函数定义
        func_matches = self.patterns['function_definition'].findall(line)
        for return_type, func_name in func_matches:
            result['functions'].append(FunctionInfo(
                name=func_name,
                return_type=return_type,
                parameters=[],  # 简化处理，不解析参数
                line_number=line_num
            ))
        
        # 函数调用
        call_matches = self.patterns['function_call'].findall(line)
        for func_name in call_matches:
            # 过滤掉关键字和类型名
            if func_name not in ['int', 'char', 'float', 'double', 'long', 'short', 'unsigned', 'signed', 'void', 'if', 'while', 'for', 'do', 'return', 'break', 'continue']:
                result['function_calls'].append({
                    'name': func_name,
                    'line': line_num,
                    'line_content': line.strip()
                })
        
        # 赋值语句
        assign_matches = self.patterns['assignment'].findall(line)
        for var_name, value in assign_matches:
            result['assignments'].append({
                'variable': var_name,
                'value': value,
                'line': line_num,
                'line_content': line.strip()
            })
        
        # 指针解引用
        deref_matches = self.patterns['pointer_dereference'].findall(line)
        for ptr_name in deref_matches:
            result['pointer_dereferences'].append({
                'pointer': ptr_name,
                'line': line_num,
                'line_content': line.strip()
            })
        
        # malloc调用
        malloc_matches = self.patterns['malloc_call'].findall(line)
        for var_name in malloc_matches:
            result['malloc_calls'].append({
                'variable': var_name,
                'line': line_num,
                'line_content': line.strip()
            })
        
        # free调用
        if self.patterns['free_call'].search(line):
            result['free_calls'].append({
                'line': line_num,
                'line_content': line.strip()
            })
        
        # scanf调用
        if self.patterns['scanf_call'].search(line):
            result['scanf_calls'].append({
                'line': line_num,
                'line_content': line.strip()
            })
        
        # printf调用
        if self.patterns['printf_call'].search(line):
            result['printf_calls'].append({
                'line': line_num,
                'line_content': line.strip()
            })
        
        # 循环结构
        if self.patterns['while_loop'].search(line):
            result['loops'].append({
                'type': 'while',
                'line': line_num,
                'line_content': line.strip()
            })
        elif self.patterns['for_loop'].search(line):
            result['loops'].append({
                'type': 'for',
                'line': line_num,
                'line_content': line.strip()
            })
        elif self.patterns['do_while_loop'].search(line):
            result['loops'].append({
                'type': 'do-while',
                'line': line_num,
                'line_content': line.strip()
            })
        
        # 头文件包含
        include_matches = self.patterns['include'].findall(line)
        for header in include_matches:
            result['includes'].append({
                'header': header,
                'line': line_num,
                'line_content': line.strip()
            })
    
    def get_variable_by_name(self, name: str, parsed_data: Dict[str, List]) -> Optional[VariableInfo]:
        """根据名称获取变量信息"""
        for var in parsed_data['variables']:
            if var.name == name:
                return var
        return None
    
    def get_function_by_name(self, name: str, parsed_data: Dict[str, List]) -> Optional[FunctionInfo]:
        """根据名称获取函数信息"""
        for func in parsed_data['functions']:
            if func.name == name:
                return func
        return None
