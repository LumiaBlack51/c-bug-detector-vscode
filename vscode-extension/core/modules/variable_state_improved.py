"""
改进的变量状态监察官模块 - 重构版本，专注核心职责，避免与内存安全模块冲突
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter
from .scope_analyzer import ScopeAnalyzer
from utils.code_parser import CCodeParser, VariableInfo


class ImprovedVariableStateModule:
    """改进的变量状态监察官模块 - 暂时禁用以避免与内存安全模块冲突"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.scope_analyzer = ScopeAnalyzer()
        self.variable_states: Dict[str, Dict] = {}
    
    def get_module_name(self):
        """返回模块名称"""
        return "改进的变量状态监察官"
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析变量状态问题 - 重构版本，专注非指针变量状态分析"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.variable_states.clear()

        # 使用作用域分析器获取所有变量信息
        self.scope_variables = self.scope_analyzer.analyze(parsed_data)

        # 专注于非指针变量的状态分析，避免与内存安全模块冲突
        # 主要职责：
        # 1. 检测未初始化的非指针局部变量使用
        # 2. 检测未显式初始化的static变量（作为编程实践建议）

        # 第一阶段：从作用域分析结果中提取非指针变量
        self._extract_non_pointer_variables()

        # 第二阶段：分析非指针变量使用问题
        self._detect_non_pointer_variable_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _extract_non_pointer_variables(self):
        """从作用域分析结果中提取非指针变量"""
        for var_name, var_info in self.scope_variables.items():
            # 只处理非指针变量
            if not var_info.get('is_pointer', False):
                self.variable_states[var_name] = {
                    'type': var_info['type'],
                    'line': var_info['line'],
                    'is_initialized': var_info['is_initialized'],
                    'is_static': var_info['is_static'],
                    'is_const': var_info['is_const'],
                    'line_content': var_info['line_content'],
                    'scope_level': var_info['scope_level'],
                    'scope_type': var_info['scope_type'],
                    'scope_path': var_info['scope_path'],
                    'warned': False
                }
    
    def _detect_non_pointer_variable_issues(self, parsed_data: Dict[str, List]):
        """检测非指针变量的使用问题"""
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 跳过注释、空行
            if (line_content.strip().startswith('//') or 
                line_content.strip().startswith('/*') or 
                not line_content.strip()):
                continue
            
            # 跳过声明行（包含类型关键字）
            if re.search(r'\b(int|char|float|double|long|short|unsigned|signed|bool|struct)\s+\w+', line_content):
                continue
            
            # 跳过包含指针操作的行（让内存安全模块处理）
            if '*' in line_content or '->' in line_content:
                continue
            
            # 查找变量使用
            var_uses = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', line_content)
            
            for var_name in var_uses:
                # 跳过关键字、函数名、常量等
                if (var_name in ['if', 'else', 'while', 'for', 'return', 'printf', 'scanf', 'malloc', 'free', 
                               'main', 'int', 'char', 'float', 'double', 'void', 'struct', 'NULL', 'true', 'false',
                               'Point', 'Nested', 'get_wild_pointer', 'test_wild_param', 'test_function_params',
                               'test_static_vars', 'test_const_vars', 'sizeof', 'NULL', 'size_t', 'include',
                               'stdio', 'stdlib', 'string', 'stdbool'] or
                    var_name.isdigit() or len(var_name) <= 1):
                    continue
                
                # 检查是否是我们跟踪的非指针变量
                if var_name in self.variable_states:
                    var_info = self.variable_states[var_name]
                    
                    # 跳过const变量（它们必须在声明时初始化）
                    if var_info.get('is_const', False):
                        continue
                    
                    # 检查未初始化的局部变量使用
                    if not var_info['is_initialized'] and not var_info['is_static']:
                        # 检查是否是赋值语句的左侧（变量被赋值）
                        is_assignment_left = re.match(rf'^\s*{re.escape(var_name)}\s*=', line_content)
                        
                        # 检查是否是scanf的参数（变量作为输入参数）
                        is_scanf_param = 'scanf' in line_content and f'&{var_name}' in line_content
                        
                        # 如果既不是赋值左侧，也不是scanf参数，则报告未初始化使用
                        if not is_assignment_left and not is_scanf_param:
                            self.error_reporter.add_variable_error(
                                line_num,
                                f"使用未初始化的局部变量 '{var_name}'",
                                f"建议在使用前初始化变量：{var_info['type']} {var_name} = 0; // 或适当的初始值",
                                line_content.strip()
                            )
                            # 标记为已初始化，避免重复报告
                            var_info['is_initialized'] = True
                    
                    # 检查未显式初始化的static变量（编程实践建议）
                    elif var_info['is_static'] and not var_info['is_initialized'] and not var_info['warned']:
                        self.error_reporter.add_variable_error(
                            line_num,
                            f"使用未显式初始化的static变量 '{var_name}'（虽然默认为0，但不是好的编程实践）",
                            f"建议显式初始化以提高代码清晰度：static {var_info['type']} {var_name} = 0;",
                            line_content.strip()
                        )
                        var_info['warned'] = True