"""
数值与控制流分析器模块 - 检测类型溢出和死循环
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser

# C语言AST解析器
try:
    from pycparser import c_parser, c_ast, parse_file
    from pycparser.c_ast import *
    C_AST_AVAILABLE = True
except ImportError:
    C_AST_AVAILABLE = False
    print("警告: pycparser未安装，将使用正则表达式方法")


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
        
        # 编译正则表达式模式 - 改进版本
        self.patterns = {
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'while_loop': re.compile(r'\bwhile\s*\(([^)]+)\)\s*\{', re.MULTILINE),
            'for_loop': re.compile(r'\bfor\s*\(([^)]+)\)\s*\{', re.MULTILINE),
            'for_infinite': re.compile(r'\bfor\s*\(\s*;\s*;\s*\)\s*\{', re.MULTILINE),  # for(;;)
            'do_while_loop': re.compile(r'\bdo\s*\{', re.MULTILINE),
            'break_statement': re.compile(r'\bbreak\s*;', re.MULTILINE),
            'return_statement': re.compile(r'\breturn\s*[^;]*;', re.MULTILINE),
            'increment': re.compile(r'\b(\w+)\s*\+\+', re.MULTILINE),
            'decrement': re.compile(r'\b(\w+)\s*--', re.MULTILINE),
            'arithmetic': re.compile(r'\b(\w+)\s*[+\-*/]\s*([^;]+)', re.MULTILINE),
            'float_loop': re.compile(r'\bfor\s*\(\s*(float|double)\s+(\w+)\s*=\s*([^;]+);\s*([^;]+);\s*([^)]+)\)', re.MULTILINE),
            'ineffective_assignment': re.compile(r'\b(\w+)\s*=\s*\1\b', re.MULTILINE),  # i = i
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
        """检测死循环 - 改进版本"""
        # 使用去重机制避免重复报告
        reported_issues = set()
        
        # 首先检查所有行中的死循环模式
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            self._check_line_for_dead_loops(line_content, line_num, parsed_data, reported_issues)
        
        # 然后检查解析出的循环结构
        for loop in parsed_data['loops']:
            loop_type = loop['type']
            line_num = loop['line']
            line_content = loop['line_content']
            
            if loop_type == 'while':
                self._check_while_loop(line_content, line_num, parsed_data, reported_issues)
            elif loop_type == 'for':
                self._check_for_loop(line_content, line_num, parsed_data, reported_issues)
            elif loop_type == 'do-while':
                self._check_do_while_loop(line_content, line_num, parsed_data, reported_issues)
    
    def _check_line_for_dead_loops(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
        """检查单行中的死循环模式 - 优先使用C语言AST分析"""
        # 优先使用C语言AST分析
        ast_analyzed = False
        if C_AST_AVAILABLE:
            ast_analyzed = self._analyze_with_c_ast(line_content, line_num, parsed_data, reported_issues)
        
        # 如果AST分析失败或未检测到问题，使用正则表达式作为补充
        if not ast_analyzed:
            self._check_line_with_regex(line_content, line_num, parsed_data, reported_issues)
        
        # 检查浮点数循环精度问题（独立检测）
        self._check_float_precision_issues(line_content, line_num, reported_issues)
        
        # 检查无效赋值导致的死循环（独立检测）
        self._check_ineffective_assignment(line_content, line_num, parsed_data, reported_issues)
        
        # 数据流分析检测复杂死循环
        self._check_dataflow_dead_loops(line_content, line_num, parsed_data, reported_issues)
    
    def _analyze_with_c_ast(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set) -> bool:
        """使用C语言AST分析代码结构，返回是否成功分析了问题"""
        try:
            # 创建C语言解析器
            parser = c_parser.CParser()
            
            # 尝试解析单行代码（需要包装成完整的C代码）
            wrapped_code = self._wrap_c_code(line_content)
            
            if wrapped_code:
                # print(f"[C AST DEBUG] 第{line_num}行: 原始='{line_content.strip()}'")  # 禁用调试输出
                # print(f"[C AST DEBUG] 包装后: {wrapped_code}")  # 禁用调试输出
                
                # 解析为C语言AST
                ast_node = parser.parse(wrapped_code)
                
                # 遍历AST节点，返回是否检测到问题
                return self._visit_c_ast_nodes(ast_node, line_num, line_content, parsed_data, reported_issues)
                
        except Exception as e:
            # print(f"[C AST DEBUG] C AST解析异常: {e}")  # 禁用调试输出
            pass
        
        return False
    
    def _wrap_c_code(self, line_content: str) -> Optional[str]:
        """将单行C代码包装成完整的C代码"""
        line_content = line_content.strip()
        
        # 检查是否是循环语句
        if re.match(r'\s*(while|for|do)\s*', line_content):
            # 包装循环语句
            return f"""
            void test_function() {{
                {line_content}
                    printf("test");
                }}
            }}
            """
        
        # 检查是否是赋值语句
        if '=' in line_content and ';' in line_content:
            return f"""
            void test_function() {{
                {line_content}
            }}
            """
        
        return None
    
    def _visit_c_ast_nodes(self, node, line_num: int, line_content: str, parsed_data: Dict[str, List], reported_issues: set) -> bool:
        """遍历C语言AST节点，返回是否检测到问题"""
        if node is None:
            return False
            
        detected_issue = False
        
        # 检查while循环
        if isinstance(node, While):
            # print(f"[C AST DEBUG] 发现while循环节点")  # 禁用调试输出
            detected_issue = self._analyze_c_while_ast(node, line_num, line_content, reported_issues) or detected_issue
        
        # 检查for循环
        elif isinstance(node, For):
            # print(f"[C AST DEBUG] 发现for循环节点")  # 禁用调试输出
            detected_issue = self._analyze_c_for_ast(node, line_num, line_content, reported_issues, parsed_data) or detected_issue
        
        # 检查赋值语句
        elif isinstance(node, Assignment):
            # print(f"[C AST DEBUG] 发现赋值节点")  # 禁用调试输出
            detected_issue = self._analyze_c_assignment_ast(node, line_num, line_content, parsed_data, reported_issues) or detected_issue
        
        # 递归遍历子节点
        for child_name, child_node in node.children():
            child_detected = self._visit_c_ast_nodes(child_node, line_num, line_content, parsed_data, reported_issues)
            detected_issue = child_detected or detected_issue
        
        return detected_issue
    
    def _analyze_c_while_ast(self, node: While, line_num: int, line_content: str, reported_issues: set) -> bool:
        """分析C语言while循环的AST节点，返回是否检测到问题"""
        # 检查条件是否为常量
        if isinstance(node.cond, Constant):
            if node.cond.value == '1' or node.cond.value == 1:
                issue_key = f"while_constant_{line_num}"
                if issue_key not in reported_issues:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"C AST分析：检测到while循环使用常量条件 {node.cond.value}",
                        "建议添加break语句或修改循环条件",
                        line_content
                    )
                    reported_issues.add(issue_key)
                    return True
        return False
    
    def _analyze_c_for_ast(self, node: For, line_num: int, line_content: str, reported_issues: set, parsed_data: Dict[str, List]) -> bool:
        """分析C语言for循环的AST节点，返回是否检测到问题"""
        # 检查是否是无限循环 for(;;)
        if node.init is None and node.cond is None and node.next is None:
            # 检查循环体内是否有退出语句
            if not self._has_exit_statements_in_loop(line_num, parsed_data):
                issue_key = f"for_infinite_ast_{line_num}"
                if issue_key not in reported_issues:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        "C AST分析：检测到for(;;)无限循环",
                        "建议添加break语句或return语句",
                        line_content
                    )
                    reported_issues.add(issue_key)
                    return True
        return False
    
    def _analyze_c_assignment_ast(self, node: Assignment, line_num: int, line_content: str, parsed_data: Dict[str, List], reported_issues: set) -> bool:
        """分析C语言赋值语句的AST节点，返回是否检测到问题"""
        # 检查自赋值：i = i
        if isinstance(node.lvalue, ID) and isinstance(node.rvalue, ID):
            if node.lvalue.name == node.rvalue.name:
                if self._is_in_loop_context(line_num, parsed_data):
                    issue_key = f"self_assignment_{line_num}"
                    if issue_key not in reported_issues:
                        self.error_reporter.add_numeric_error(
                            line_num,
                            f"C AST分析：检测到自赋值 '{node.lvalue.name} = {node.rvalue.name}'",
                            "建议修改赋值操作或添加break语句",
                            line_content
                        )
                        reported_issues.add(issue_key)
                        return True
        return False
    
    def _check_line_with_regex(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
        """使用正则表达式检查死循环模式"""
        # 检查 for(;;) 死循环
        if self.patterns['for_infinite'].search(line_content):
            has_exit = self._check_loop_body_for_exit(line_num, parsed_data)
            if not has_exit:
                issue_key = f"for_infinite_regex_{line_num}"
                if issue_key not in reported_issues:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        "检测到for(;;)死循环",
                        "建议添加break语句或return语句",
                        line_content
                    )
                    reported_issues.add(issue_key)
    
    def _check_dataflow_dead_loops(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
        """数据流分析检测复杂死循环"""
        # 检查while循环中的变量是否在循环体内被修改
        while_match = self.patterns['while_loop'].search(line_content)
        if while_match:
            condition = while_match.group(1).strip()
            
            # 提取条件中的变量
            condition_vars = self._extract_variables_from_condition(condition)
            
            for var_name in condition_vars:
                # 检查变量是否在循环体内被修改
                if not self._is_variable_modified_in_loop(var_name, line_num, parsed_data):
                    # 检查变量是否是常量或外部变量
                    if not self._is_constant_or_external_var(var_name, parsed_data):
                        # 检查循环体内是否有break或return等退出语句
                        if not self._has_exit_statements_in_loop(line_num, parsed_data):
                            issue_key = f"dataflow_deadloop_{var_name}_{line_num}"
                            if issue_key not in reported_issues:
                                self.error_reporter.add_numeric_error(
                                    line_num,
                                    f"数据流分析：变量 '{var_name}' 在循环条件中使用但循环体内未被修改，可能导致死循环",
                                    f"建议在循环体内修改 '{var_name}' 或添加break语句",
                                    line_content
                                )
                                reported_issues.add(issue_key)
    
    def _extract_variables_from_condition(self, condition: str) -> List[str]:
        """从循环条件中提取变量名"""
        # 移除操作符和常量，提取变量名
        import re
        # 匹配变量名（字母开头，包含字母数字下划线）
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(var_pattern, condition)
        
        # 过滤掉关键字和常量
        keywords = {'true', 'false', 'NULL', 'null', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
        variables = [var for var in matches if var not in keywords and not var.isdigit()]
        
        return variables
    
    def _is_variable_modified_in_loop(self, var_name: str, loop_line: int, parsed_data: Dict[str, List]) -> bool:
        """检查变量是否在循环体内被修改"""
        # 查找循环体的结束行
        loop_end_line = self._find_loop_end_line(loop_line, parsed_data)
        if loop_end_line == -1:
            return False
        
        # 检查循环体内是否有对该变量的赋值
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            if loop_line < line_num <= loop_end_line:
                # 检查是否有赋值操作
                assignment_pattern = rf'\b{var_name}\s*='
                if re.search(assignment_pattern, line_content):
                    return True
                
                # 检查是否有递增递减操作
                increment_pattern = rf'\b{var_name}\s*\+\+|\b{var_name}\s*--|\+\+\s*{var_name}|--\s*{var_name}'
                if re.search(increment_pattern, line_content):
                    return True
        
        return False
    
    def _find_loop_end_line(self, loop_line: int, parsed_data: Dict[str, List]) -> int:
        """查找循环体的结束行"""
        # 简化的循环体结束检测
        brace_count = 0
        found_opening = False
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            if line_num < loop_line:
                continue
            
            if '{' in line_content:
                brace_count += line_content.count('{')
                found_opening = True
            
            if '}' in line_content:
                brace_count -= line_content.count('}')
                if found_opening and brace_count == 0:
                    return line_num
        
        return -1
    
    def _is_constant_or_external_var(self, var_name: str, parsed_data: Dict[str, List]) -> bool:
        """检查变量是否是常量或外部变量"""
        # 检查是否是函数参数
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 查找函数定义
            func_match = re.search(r'\w+\s+(\w+)\s*\(([^)]*)\)', line_content)
            if func_match:
                params_str = func_match.group(2)
                if var_name in params_str:
                    return True
        
        # 检查是否是全局变量或静态变量
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检查全局变量声明
            if re.search(rf'\b(static|extern|const)\s+.*\b{var_name}\b', line_content):
                return True
        
        return False
    
    def _has_exit_statements_in_loop(self, loop_line: int, parsed_data: Dict[str, List]) -> bool:
        """检查循环体内是否有退出语句"""
        # 查找循环体的结束行
        loop_end_line = self._find_loop_end_line(loop_line, parsed_data)
        if loop_end_line == -1:
            return False
        
        # 检查循环体内是否有退出语句
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            if loop_line < line_num <= loop_end_line:
                # 检查break语句
                if re.search(r'\bbreak\s*;', line_content):
                    return True
                
                # 检查return语句
                if re.search(r'\breturn\s*[^;]*;', line_content):
                    return True
                
                # 检查exit函数调用
                if re.search(r'\bexit\s*\(', line_content):
                    return True
                
                # 检查goto语句
                if re.search(r'\bgoto\s+\w+', line_content):
                    return True
        
        return False
    
    def _check_while_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
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
                    # 使用与AST分析相同的key，避免重复报告
                    issue_key = f"while_constant_{line_num}"
                    if issue_key not in reported_issues:
                        self.error_reporter.add_numeric_error(
                            line_num,
                            f"while循环条件 '{condition}' 恒定为真且循环体内无退出语句，可能导致死循环",
                            "建议添加break语句或修改循环条件",
                            line_content
                        )
                        reported_issues.add(issue_key)
            
            # 检查变量在循环中是否会被修改
            self._check_while_variable_modification(condition, line_num, line_content, parsed_data)
    
    def _check_for_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
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
            
            # 检查for循环的初始化、条件和递增部分
            self._analyze_for_loop_parts(condition, line_num, line_content)
    
    def _check_do_while_loop(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
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
    
    def _analyze_for_loop_parts(self, condition: str, line_num: int, line_content: str):
        """分析for循环的各个部分"""
        # 解析for循环的三个部分：初始化; 条件; 递增
        parts = condition.split(';')
        if len(parts) >= 3:
            init_part = parts[0].strip()
            cond_part = parts[1].strip()
            incr_part = parts[2].strip()
            
            # 检查条件部分
            if cond_part:
                # 检查循环变量永远不会满足退出条件的情况
                self._check_loop_variable_logic(init_part, cond_part, incr_part, line_num, line_content)
    
    def _check_loop_variable_logic(self, init_part: str, cond_part: str, incr_part: str, line_num: int, line_content: str):
        """检查循环变量逻辑"""
        # 提取循环变量名
        var_name = self._extract_variable_name(init_part)
        if not var_name:
            return
        
        # 检查各种死循环模式
        self._check_never_exit_condition(var_name, init_part, cond_part, incr_part, line_num, line_content)
        self._check_wrong_increment(var_name, init_part, cond_part, incr_part, line_num, line_content)
        self._check_step_size_issues(var_name, init_part, cond_part, incr_part, line_num, line_content)
    
    def _extract_variable_name(self, init_part: str) -> str:
        """提取变量名"""
        # 匹配 int i = 10 或 i = 10 模式
        match = re.search(r'\b(\w+)\s*=\s*([^;]+)', init_part)
        if match:
            return match.group(1)
        return None
    
    def _check_never_exit_condition(self, var_name: str, init_part: str, cond_part: str, incr_part: str, line_num: int, line_content: str):
        """检查永远不会满足退出条件的情况"""
        # 检查 i >= 10; i++ 模式
        if '>=' in cond_part and var_name in cond_part and '++' in incr_part:
            # 如果初始值已经满足条件，且递增，则永远不会退出
            init_match = re.search(rf'{var_name}\s*=\s*(\d+)', init_part)
            cond_match = re.search(rf'{var_name}\s*>=\s*(\d+)', cond_part)
            if init_match and cond_match:
                init_val = int(init_match.group(1))
                cond_val = int(cond_match.group(1))
                if init_val >= cond_val:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"循环变量 '{var_name}' 从 {init_val} 开始，条件是 {cond_part}，但递增操作永远不会让条件为假",
                        "建议修改循环条件或初始值",
                        line_content
                    )
    
    def _check_wrong_increment(self, var_name: str, init_part: str, cond_part: str, incr_part: str, line_num: int, line_content: str):
        """检查错误的递增/递减操作"""
        # 检查 i < 10; i-- 模式
        if '<' in cond_part and var_name in cond_part and '--' in incr_part:
            init_match = re.search(rf'{var_name}\s*=\s*(\d+)', init_part)
            cond_match = re.search(rf'{var_name}\s*<\s*(\d+)', cond_part)
            if init_match and cond_match:
                init_val = int(init_match.group(1))
                cond_val = int(cond_match.group(1))
                if init_val < cond_val:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"循环变量 '{var_name}' 从 {init_val} 开始，条件是 {cond_part}，但递减操作会让变量越来越小",
                        "建议修改递增操作或循环条件",
                        line_content
                    )
    
    def _check_step_size_issues(self, var_name: str, init_part: str, cond_part: str, incr_part: str, line_num: int, line_content: str):
        """检查步长问题"""
        # 检查 i == 10; i += 3 模式
        if '==' in cond_part and var_name in cond_part and '+=' in incr_part:
            init_match = re.search(rf'{var_name}\s*=\s*(\d+)', init_part)
            cond_match = re.search(rf'{var_name}\s*==\s*(\d+)', cond_part)
            incr_match = re.search(rf'{var_name}\s*\+=\s*(\d+)', incr_part)
            if init_match and cond_match and incr_match:
                init_val = int(init_match.group(1))
                cond_val = int(cond_match.group(1))
                incr_val = int(incr_match.group(1))
                
                # 检查是否会跳过目标值
                if (cond_val - init_val) % incr_val != 0:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"循环变量 '{var_name}' 从 {init_val} 开始，每次增加 {incr_val}，但条件是等于 {cond_val}，会跳过目标值",
                        "建议修改步长或循环条件",
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
    
    def _check_while_variable_modification(self, condition: str, line_num: int, line_content: str, parsed_data: Dict[str, List]):
        """检查while循环中的变量是否会被修改"""
        # 提取条件中的变量
        var_match = re.search(r'\b(\w+)\s*([><=!]+)', condition)
        if var_match:
            var_name = var_match.group(1)
            operator = var_match.group(2)
            
            # 检查循环体内是否有对该变量的修改
            has_modification = self._check_variable_modification_in_loop(var_name, line_num, parsed_data)
            if not has_modification:
                # 检查是否是简单的变量比较
                if operator in ['>', '<', '>=', '<=', '==', '!=']:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"while循环条件中的变量 '{var_name}' 在循环体内未被修改，可能导致死循环",
                        "建议在循环体内修改该变量或添加break语句",
                        line_content
                    )
    
    def _check_variable_modification_in_loop(self, var_name: str, loop_line: int, parsed_data: Dict[str, List]) -> bool:
        """检查循环体内是否有对变量的有效修改 - 改进版本"""
        # 查找循环体中的变量修改
        for i in range(loop_line, min(loop_line + 20, len(parsed_data['lines']))):
            if i < len(parsed_data['lines']):
                line_content = parsed_data['lines'][i]
                
                # 检查无效赋值：i = i
                if re.search(rf'\b{var_name}\s*=\s*{var_name}\b', line_content):
                    continue  # 无效赋值，不算修改
                
                # 检查有效赋值：i = something_else
                if re.search(rf'\b{var_name}\s*=\s*[^{var_name}]', line_content):
                    return True
                
                # 检查变量递增/递减
                if re.search(rf'\b{var_name}\s*[+\-]', line_content):
                    return True
                
                # 检查复合赋值：i +=, i -=, i *=, i /=
                if re.search(rf'\b{var_name}\s*[+\-*/]=', line_content):
                    return True
                
                # 如果遇到右大括号，说明循环体结束
                if '}' in line_content:
                    break
        
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
    
    def _check_float_precision_issues(self, line_content: str, line_num: int, reported_issues: set):
        """检查浮点数精度问题"""
        # 检查浮点数循环中的精度问题
        float_match = self.patterns['float_loop'].search(line_content)
        if float_match:
            var_type = float_match.group(1)
            var_name = float_match.group(2)
            condition = float_match.group(4)
            
            # 检查是否使用 != 比较
            if '!=' in condition:
                issue_key = f"float_precision_neq_{line_num}"
                if issue_key not in reported_issues:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"浮点数循环变量 '{var_name}' 使用 != 比较可能导致精度问题",
                        "建议使用 < 或 > 比较，或使用整数循环",
                        line_content
                    )
                    reported_issues.add(issue_key)
            
            # 检查是否使用 < 或 > 比较且步长可能导致精度问题
            elif '<' in condition or '>' in condition:
                # 检查步长是否可能导致精度累积误差
                step_match = re.search(rf'{var_name}\s*\+=\s*([0-9.]+)', line_content)
                if step_match:
                    step_value = float(step_match.group(1))
                    # 检查步长是否可能导致精度问题（如0.1, 0.2等）
                    if step_value < 1.0 and step_value > 0.0:
                        issue_key = f"float_precision_step_{line_num}"
                        if issue_key not in reported_issues:
                            self.error_reporter.add_numeric_error(
                                line_num,
                                f"浮点数循环变量 '{var_name}' 使用步长 {step_value} 可能导致精度累积误差",
                                "建议使用整数循环或调整步长以避免精度问题",
                                line_content
                            )
                            reported_issues.add(issue_key)
    
    def _check_ineffective_assignment(self, line_content: str, line_num: int, parsed_data: Dict[str, List], reported_issues: set):
        """检查无效赋值导致的死循环"""
        # 检查 i = i 这种无效赋值
        ineffective_match = self.patterns['ineffective_assignment'].search(line_content)
        if ineffective_match:
            var_name = ineffective_match.group(1)
            
            # 检查这个赋值是否在循环体内
            if self._is_in_loop_context(line_num, parsed_data):
                # 使用与AST分析相同的key，避免重复报告
                issue_key = f"self_assignment_{line_num}"
                if issue_key not in reported_issues:
                    self.error_reporter.add_numeric_error(
                        line_num,
                        f"检测到无效赋值 '{var_name} = {var_name}'，可能导致死循环",
                        "建议修改赋值操作或添加break语句",
                        line_content
                    )
                    reported_issues.add(issue_key)
    
    def _is_in_loop_context(self, line_num: int, parsed_data: Dict[str, List]) -> bool:
        """检查指定行是否在循环上下文中"""
        # 查找最近的循环开始行
        for loop in parsed_data['loops']:
            loop_start = loop['line']
            if loop_start < line_num:
                # 检查是否在循环体内（简化检查）
                for i in range(loop_start, min(loop_start + 20, len(parsed_data['lines']))):
                    if i == line_num:
                        return True
                    if i < len(parsed_data['lines']) and '}' in parsed_data['lines'][i]:
                        break
        return False
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "数值与控制流分析器"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测类型溢出和死循环"
