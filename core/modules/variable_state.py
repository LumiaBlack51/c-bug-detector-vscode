"""
变量状态监察官模块 - 检测变量未初始化即使用和变量作用域问题
"""
import re
from typing import Dict, List, Set
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo


class VariableStateModule:
    """变量状态监察官模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 维护变量状态哈希表
        self.variable_states: Dict[str, Dict] = {}
        self.scope_stack: List[int] = [0]  # 作用域栈
        self.current_scope: int = 0
        
        # 编译正则表达式模式
        self.patterns = {
            'variable_use': re.compile(r'\b(\w+)\b', re.MULTILINE),
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'function_call': re.compile(r'\b(\w+)\s*\([^)]*\)', re.MULTILINE),
            'array_access': re.compile(r'\b(\w+)\s*\[[^\]]+\]', re.MULTILINE),
            'pointer_arithmetic': re.compile(r'\b(\w+)\s*[+\-]\s*\d+', re.MULTILINE),
            'comparison': re.compile(r'\b(\w+)\s*[<>=!]+\s*[^;]+', re.MULTILINE),
            'arithmetic': re.compile(r'\b(\w+)\s*[+\-*/]\s*[^;]+', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析变量状态问题"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.variable_states.clear()
        self.scope_stack = [0]
        self.current_scope = 0
        
        # 分析各种变量状态问题
        self._detect_uninitialized_variables(parsed_data)
        self._detect_scope_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _detect_uninitialized_variables(self, parsed_data: Dict[str, List]):
        """检测未初始化变量使用"""
        # 首先记录所有变量声明
        for var in parsed_data['variables']:
            self.variable_states[var.name] = {
                'declared_line': var.line_number,
                'is_initialized': var.is_initialized,
                'type': var.type,
                'scope': self.current_scope,
                'last_assigned_line': var.line_number if var.is_initialized else None
            }
        
        # 检查变量使用
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            self._check_variable_usage_in_line(line_content, line_num, parsed_data)
    
    def _check_variable_usage_in_line(self, line_content: str, line_num: int, parsed_data: Dict[str, List]):
        """检查单行中的变量使用"""
        # 跳过注释和空行
        if line_content.strip().startswith('//') or line_content.strip().startswith('/*') or not line_content.strip():
            return
        
        # 跳过变量声明行
        if ';' in line_content and ('int ' in line_content or 'char ' in line_content or 
                                   'float ' in line_content or 'double ' in line_content):
            return
        
        # 检查赋值语句
        assignment_matches = self.patterns['assignment'].findall(line_content)
        for var_name, value in assignment_matches:
            if var_name in self.variable_states:
                # 更新变量状态
                self.variable_states[var_name]['is_initialized'] = True
                self.variable_states[var_name]['last_assigned_line'] = line_num
                
                # 检查赋值右侧的变量是否已初始化
                self._check_expression_variables(value, line_num)
        
        # 检查函数调用中的参数
        func_call_matches = self.patterns['function_call'].findall(line_content)
        for func_name in func_call_matches:
            if func_name not in ['printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp']:
                # 提取函数参数
                func_match = re.search(rf'\b{func_name}\s*\(([^)]+)\)', line_content)
                if func_match:
                    params = func_match.group(1)
                    self._check_expression_variables(params, line_num)
        
        # 检查其他变量使用
        self._check_general_variable_usage(line_content, line_num)
    
    def _check_expression_variables(self, expression: str, line_num: int):
        """检查表达式中的变量"""
        # 提取表达式中的变量名
        var_matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', expression)
        for var_name in var_matches:
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                if not var_state['is_initialized']:
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"变量 '{var_name}' 在初始化前被使用",
                        f"建议在使用前初始化变量：{var_name} = 初始值;",
                        ""
                    )
    
    def _check_general_variable_usage(self, line_content: str, line_num: int):
        """检查一般变量使用"""
        # 检查数组访问
        array_matches = self.patterns['array_access'].findall(line_content)
        for var_name in array_matches:
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                if not var_state['is_initialized']:
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"数组 '{var_name}' 在初始化前被访问",
                        f"建议在使用前初始化数组：{var_name}[0] = 初始值;",
                        line_content
                    )
        
        # 检查指针运算
        ptr_matches = self.patterns['pointer_arithmetic'].findall(line_content)
        for var_name in ptr_matches:
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                if not var_state['is_initialized']:
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"指针 '{var_name}' 在初始化前进行运算",
                        f"建议在使用前初始化指针：{var_name} = NULL; 或 {var_name} = malloc(size);",
                        line_content
                    )
        
        # 检查比较操作
        comparison_matches = self.patterns['comparison'].findall(line_content)
        for var_name in comparison_matches:
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                if not var_state['is_initialized']:
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"变量 '{var_name}' 在初始化前进行比较",
                        f"建议在使用前初始化变量：{var_name} = 初始值;",
                        line_content
                    )
        
        # 检查算术运算
        arithmetic_matches = self.patterns['arithmetic'].findall(line_content)
        for var_name in arithmetic_matches:
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                if not var_state['is_initialized']:
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"变量 '{var_name}' 在初始化前进行算术运算",
                        f"建议在使用前初始化变量：{var_name} = 初始值;",
                        line_content
                    )
    
    def _detect_scope_issues(self, parsed_data: Dict[str, List]):
        """检测作用域问题"""
        # 简化的作用域检测
        brace_count = 0
        current_scope = 0
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 计算大括号
            brace_count += line_content.count('{')
            brace_count -= line_content.count('}')
            
            # 检查变量声明
            if ';' in line_content and ('int ' in line_content or 'char ' in line_content or 
                                       'float ' in line_content or 'double ' in line_content):
                # 提取变量名
                var_match = re.search(r'\b(int|char|float|double|long|short|unsigned|signed|void|struct\s+\w+)\s+(\w+)', line_content)
                if var_match:
                    var_name = var_match.group(2)
                    if var_name in self.variable_states:
                        self.variable_states[var_name]['scope'] = current_scope
            
            # 更新作用域
            if brace_count > current_scope:
                current_scope = brace_count
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "变量状态监察官"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测变量未初始化即使用和变量作用域问题"
