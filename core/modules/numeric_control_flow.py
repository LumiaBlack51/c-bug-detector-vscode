"""
数值与控制流分析器模块 - 检测类型溢出和死循环
"""
import re
from typing import Dict, List, Set
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser


class NumericControlFlowModule:
    """数值与控制流分析器模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 数据类型范围
        self.type_ranges = {
            'char': (-128, 127),
            'unsigned char': (0, 255),
            'short': (-32768, 32767),
            'unsigned short': (0, 65535),
            'int': (-2147483648, 2147483647),
            'unsigned int': (0, 4294967295),
            'long': (-9223372036854775808, 9223372036854775807),
            'unsigned long': (0, 18446744073709551615),
            'float': (-3.4e38, 3.4e38),
            'double': (-1.7e308, 1.7e308),
        }
        
        # 编译正则表达式模式
        self.patterns = {
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'while_loop': re.compile(r'\bwhile\s*\(([^)]+)\)\s*\{', re.MULTILINE),
            'for_loop': re.compile(r'\bfor\s*\(([^)]+)\)\s*\{', re.MULTILINE),
            'do_while_loop': re.compile(r'\bdo\s*\{', re.MULTILINE),
            'break_statement': re.compile(r'\bbreak\s*;', re.MULTILINE),
            'return_statement': re.compile(r'\breturn\s*[^;]*;', re.MULTILINE),
            'increment': re.compile(r'\b(\w+)\s*\+\+', re.MULTILINE),
            'decrement': re.compile(r'\b(\w+)\s*--', re.MULTILINE),
            'arithmetic': re.compile(r'\b(\w+)\s*[+\-*/]\s*([^;]+)', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析数值与控制流问题"""
        self.error_reporter.clear_reports()
        
        # 分析各种数值与控制流问题
        self._detect_overflow(parsed_data)
        self._detect_infinite_loops(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _detect_overflow(self, parsed_data: Dict[str, List]):
        """检测类型溢出"""
        for assignment in parsed_data['assignments']:
            var_name = assignment['variable']
            value_expr = assignment['value']
            line_num = assignment['line']
            
            # 获取变量类型
            var_info = self.parser.get_variable_by_name(var_name, parsed_data)
            if var_info:
                var_type = var_info.type
                
                # 检查是否是有范围限制的类型
                if var_type in self.type_ranges:
                    min_val, max_val = self.type_ranges[var_type]
                    
                    # 尝试解析数值
                    numeric_value = self._parse_numeric_value(value_expr)
                    if numeric_value is not None:
                        if numeric_value < min_val or numeric_value > max_val:
                            self.error_reporter.add_numeric_error(
                                line_num,
                                f"变量 '{var_name}' (类型: {var_type}) 赋值 {numeric_value} 超出范围 [{min_val}, {max_val}]",
                                f"建议使用更大的数据类型或检查赋值逻辑",
                                assignment['line_content']
                            )
    
    def _parse_numeric_value(self, expression: str) -> int:
        """解析数值表达式"""
        try:
            # 移除空格
            expression = expression.strip()
            
            # 处理简单的数值
            if expression.isdigit():
                return int(expression)
            
            # 处理负数
            if expression.startswith('-') and expression[1:].isdigit():
                return int(expression)
            
            # 处理十六进制
            if expression.startswith('0x') or expression.startswith('0X'):
                return int(expression, 16)
            
            # 处理八进制
            if expression.startswith('0') and len(expression) > 1:
                return int(expression, 8)
            
            # 处理简单的算术表达式
            if '+' in expression:
                parts = expression.split('+')
                if len(parts) == 2:
                    return self._parse_numeric_value(parts[0]) + self._parse_numeric_value(parts[1])
            
            if '-' in expression and not expression.startswith('-'):
                parts = expression.split('-')
                if len(parts) == 2:
                    return self._parse_numeric_value(parts[0]) - self._parse_numeric_value(parts[1])
            
            if '*' in expression:
                parts = expression.split('*')
                if len(parts) == 2:
                    return self._parse_numeric_value(parts[0]) * self._parse_numeric_value(parts[1])
            
            return None
        except:
            return None
    
    def _detect_infinite_loops(self, parsed_data: Dict[str, List]):
        """检测死循环"""
        for loop in parsed_data['loops']:
            loop_type = loop['type']
            line_num = loop['line']
            line_content = loop['line_content']
            
            if loop_type == 'while':
                self._check_while_loop(line_content, line_num, parsed_data)
            elif loop_type == 'for':
                self._check_for_loop(line_content, line_num, parsed_data)
            elif loop_type == 'do-while':
                self._check_do_while_loop(line_content, line_num, parsed_data)
    
    def _check_while_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List]):
        """检查while循环"""
        # 提取while条件
        while_match = self.patterns['while_loop'].search(line_content)
        if while_match:
            condition = while_match.group(1).strip()
            
            # 检查是否是恒定为真的条件
            if self._is_constant_true_condition(condition):
                # 检查循环体内是否有break或return
                has_break_or_return = self._check_loop_body_for_exit(line_num, parsed_data)
                if not has_break_or_return:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"while循环条件 '{condition}' 恒定为真且循环体内无退出语句，可能导致死循环",
                        "建议添加break语句或修改循环条件",
                        line_content
                    )
    
    def _check_for_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List]):
        """检查for循环"""
        # 提取for条件
        for_match = self.patterns['for_loop'].search(line_content)
        if for_match:
            condition = for_match.group(1).strip()
            
            # 检查是否是恒定为真的条件
            if self._is_constant_true_condition(condition):
                # 检查循环体内是否有break或return
                has_break_or_return = self._check_loop_body_for_exit(line_num, parsed_data)
                if not has_break_or_return:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"for循环条件 '{condition}' 恒定为真且循环体内无退出语句，可能导致死循环",
                        "建议添加break语句或修改循环条件",
                        line_content
                    )
    
    def _check_do_while_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List]):
        """检查do-while循环"""
        # do-while循环通常需要检查while条件
        # 这里简化处理，主要检查循环体内是否有退出语句
        has_break_or_return = self._check_loop_body_for_exit(line_num, parsed_data)
        if not has_break_or_return:
            self.error_reporter.add_numeric_error(
                line_num,
                "do-while循环体内无退出语句，可能导致死循环",
                "建议添加break语句或确保while条件能正确终止循环",
                line_content
            )
    
    def _is_constant_true_condition(self, condition: str) -> bool:
        """检查条件是否恒定为真"""
        condition = condition.strip()
        
        # 检查常见的恒定为真条件
        constant_true_conditions = [
            '1',
            'true',
            '!0',
            '!NULL',
            '!0',
            '1==1',
            '1!=0',
        ]
        
        if condition in constant_true_conditions:
            return True
        
        # 检查while(1)模式
        if condition == '1':
            return True
        
        # 检查while(true)模式
        if condition == 'true':
            return True
        
        return False
    
    def _check_loop_body_for_exit(self, loop_line: int, parsed_data: Dict[str, List]) -> bool:
        """检查循环体内是否有退出语句"""
        # 简化的检查：查找循环体中的break或return语句
        # 这里假设循环体在接下来的几行中
        for i in range(loop_line, min(loop_line + 20, len(parsed_data['lines']))):
            if i < len(parsed_data['lines']):
                line_content = parsed_data['lines'][i]
                
                # 检查break语句
                if self.patterns['break_statement'].search(line_content):
                    return True
                
                # 检查return语句
                if self.patterns['return_statement'].search(line_content):
                    return True
                
                # 如果遇到右大括号，说明循环体结束
                if '}' in line_content:
                    break
        
        return False
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "数值与控制流分析器"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测类型溢出和死循环"
