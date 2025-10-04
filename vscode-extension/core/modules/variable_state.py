"""
变量状态监察官模块 - 检测变量未初始化即使用和变量作用域问题
"""
import re
from typing import Dict, List, Set, Optional
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo

# C语言AST解析器
try:
    from pycparser import c_parser, c_ast, parse_file
    from pycparser.c_ast import *
    C_AST_AVAILABLE = True
except ImportError:
    C_AST_AVAILABLE = False
    print("警告: pycparser未安装，将使用正则表达式方法")


class VariableStateModule:
    """变量状态监察官模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 维护变量状态哈希表
        self.variable_states: Dict[str, Dict] = {}
        self.scope_stack: List[int] = [0]  # 作用域栈
        self.current_scope: int = 0
        self.function_params: Set[str] = set()  # 函数参数集合
        self.current_function: Optional[str] = None
        
        # 编译正则表达式模式
        self.patterns = {
            'variable_use': re.compile(r'\b(\w+)\b', re.MULTILINE),
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'function_call': re.compile(r'\b(\w+)\s*\([^)]*\)', re.MULTILINE),
            'array_access': re.compile(r'\b(\w+)\s*\[[^\]]+\]', re.MULTILINE),
            'pointer_arithmetic': re.compile(r'\b(\w+)\s*[+\-]\s*\d+', re.MULTILINE),
            'comparison': re.compile(r'\b(\w+)\s*[<>=!]+\s*[^;]+', re.MULTILINE),
            'arithmetic': re.compile(r'\b(\w+)\s*[+\-*/]\s*[^;]+', re.MULTILINE),
            'function_decl': re.compile(r'\w+\s+(\w+)\s*\([^)]*\)', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析变量状态问题 - 使用C语言AST"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.variable_states.clear()
        self.scope_stack = [0]
        self.current_scope = 0
        self.function_params.clear()
        self.current_function = None
        
        # 主要使用正则表达式方法，提供准确的行号和去重
        self._detect_uninitialized_variables_regex(parsed_data)
        
        # 暂时禁用AST分析以避免重复报告和行号错误
        # if C_AST_AVAILABLE:
        #     self._analyze_with_c_ast(parsed_data)
        
        # 分析各种变量状态问题
        # self._detect_uninitialized_variables(parsed_data)
        self._detect_scope_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _analyze_with_c_ast(self, parsed_data: Dict[str, List]):
        """使用C语言AST分析变量状态"""
        try:
            # 创建C语言解析器
            parser = c_parser.CParser()
            
            # 移除预处理指令，只保留C代码
            file_content = '\n'.join(parsed_data['lines'])
            cleaned_content = self._remove_preprocessor_directives(file_content)
            
            if cleaned_content.strip():
                # 添加必要的头文件声明以避免解析错误
                wrapped_content = self._wrap_c_code_for_parsing(cleaned_content)
                ast_node = parser.parse(wrapped_content)
                
                # 遍历AST节点
                self._visit_c_ast_for_variables(ast_node)
            
        except Exception as e:
            print(f"[C AST DEBUG] 变量状态AST分析异常: {e}")
            # AST解析失败时，回退到正则表达式方法
            self._fallback_to_regex_analysis(parsed_data)
    
    def _remove_preprocessor_directives(self, content: str) -> str:
        """移除预处理指令"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            # 跳过预处理指令
            if not (stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*')):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _wrap_c_code_for_parsing(self, content: str) -> str:
        """包装C代码以便AST解析"""
        # 添加必要的类型定义和函数声明
        wrapped = """
        typedef int bool;
        typedef unsigned int size_t;
        typedef struct FILE FILE;
        extern int printf(const char *format, ...);
        extern int scanf(const char *format, ...);
        extern void *malloc(size_t size);
        extern void free(void *ptr);
        extern int strlen(const char *s);
        extern char *strcpy(char *dest, const char *src);
        extern int strcmp(const char *s1, const char *s2);
        
        """ + content
        return wrapped
    
    def _fallback_to_regex_analysis(self, parsed_data: Dict[str, List]):
        """回退到正则表达式分析方法"""
        print("[C AST DEBUG] 使用正则表达式回退方法分析变量状态")
        
        # 使用正则表达式方法进行变量状态分析
        self._detect_uninitialized_variables_regex(parsed_data)
        self._detect_static_variable_warnings(parsed_data)
    
    def _visit_c_ast_for_variables(self, node, line_offset=0):
        """遍历C语言AST节点进行变量分析"""
        if node is None:
            return
            
        # 获取当前节点的行号
        current_line = getattr(node, 'coord', None)
        if current_line:
            line_num = current_line.line + line_offset
        else:
            line_num = 0
            
        # 检查函数定义
        if isinstance(node, FuncDef):
            self._analyze_function_ast(node)
        
        # 检查变量声明
        elif isinstance(node, Decl):
            self._analyze_declaration_ast(node, line_num)
        
        # 检查变量使用
        elif isinstance(node, ID):
            self._analyze_variable_use_ast(node, line_num)
        
        # 检查赋值语句
        elif isinstance(node, Assignment):
            self._analyze_assignment_ast(node, line_num)
        
        # 递归遍历子节点
        for child_name, child_node in node.children():
            self._visit_c_ast_for_variables(child_node, line_offset)
    
    def _analyze_function_ast(self, node: FuncDef):
        """分析函数定义的AST节点"""
        if isinstance(node.decl, Decl) and isinstance(node.decl.type, FuncDecl):
            func_name = node.decl.name
            self.current_function = func_name
            self.function_params.clear()
            
            # 收集函数参数
            if isinstance(node.decl.type.args, ParamList):
                for param in node.decl.type.args.params:
                    if isinstance(param, Decl) and isinstance(param.type, TypeDecl):
                        param_name = param.name
                        self.function_params.add(param_name)
                        # 函数参数被认为是已初始化的
                        self.variable_states[param_name] = {
                            'is_initialized': True,
                            'is_function_param': True,
                            'scope': self.current_scope,
                            'declared_line': 0,  # 函数参数没有具体的声明行
                            'type': str(param.type.type)
                        }
                        print(f"[C AST DEBUG] 函数参数已初始化: {param_name}")
    
    def _analyze_declaration_ast(self, node: Decl, line_num: int = 0):
        """分析变量声明的AST节点"""
        if isinstance(node.type, TypeDecl):
            var_name = node.name
            var_type = str(node.type.type)
            
            # 检查是否是static变量
            is_static = False
            storage = getattr(node, 'storage', None)
            if storage and 'static' in storage:
                is_static = True
            # 也检查类型声明中的static
            elif hasattr(node.type, 'quals') and 'static' in str(node.type.quals):
                is_static = True
            # 检查父节点是否是static声明
            elif hasattr(node, 'parent') and hasattr(node.parent, 'storage') and 'static' in node.parent.storage:
                is_static = True
            
            print(f"[C AST DEBUG] 检查static: {var_name}, storage: {storage}, quals: {getattr(node.type, 'quals', None)}, is_static: {is_static}")
            
            # 检查是否是const变量
            is_const = False
            if hasattr(node.type, 'quals') and 'const' in str(node.type.quals):
                is_const = True
            
            # 检查是否有初始化
            is_initialized = node.init is not None
            
            # static变量默认初始化为0
            if is_static and not is_initialized:
                is_initialized = True
                print(f"[C AST DEBUG] static变量默认初始化: {var_name}")
            
            # const变量必须有初始化
            if is_const and not is_initialized:
                print(f"[C AST DEBUG] const变量未初始化: {var_name}")
            
            # 检查是否是函数参数（通过检查是否已经在function_params中）
            is_function_param = var_name in self.function_params
            
            # 如果变量已经存在且是函数参数，不要覆盖
            if var_name in self.variable_states and self.variable_states[var_name].get('is_function_param', False):
                print(f"[C AST DEBUG] 保持函数参数状态: {var_name}")
                return
            
            self.variable_states[var_name] = {
                'is_initialized': is_initialized,
                'is_function_param': is_function_param,
                'is_static': is_static,
                'is_const': is_const,
                'scope': self.current_scope,
                'declared_line': line_num,
                'type': var_type
            }
            
            print(f"[C AST DEBUG] 变量声明: {var_name}, 类型: {var_type}, 初始化: {is_initialized}, static: {is_static}, const: {is_const}, 函数参数: {is_function_param}")
    
    def _analyze_variable_use_ast(self, node: ID, line_num: int = 0):
        """分析变量使用的AST节点"""
        var_name = node.name
        
        # 跳过函数名和关键字
        if var_name in ['printf', 'scanf', 'malloc', 'free', 'main', 'if', 'while', 'for', 'return', 'true', 'false']:
            return
        
        # 检查变量是否已初始化
        if var_name in self.variable_states:
            var_state = self.variable_states[var_name]
            
            # 函数参数不需要检查初始化
            if var_state.get('is_function_param', False):
                print(f"[C AST DEBUG] 跳过函数参数: {var_name}")
                return
            
            # static变量默认已初始化，但需要警告
            if var_state.get('is_static', False):
                if not var_state['is_initialized']:
                    print(f"[C AST DEBUG] static变量隐式初始化警告: {var_name}")
                    self.error_reporter.add_variable_warning(
                        line_num,
                        f"隐式依赖于静态变量 '{var_name}' 的零初始化",
                        f"建议显式初始化以提高代码清晰度：static {var_state.get('type', 'int')} {var_name} = 0;",
                        ""
                    )
                return
            
            # const变量通常已初始化
            if var_state.get('is_const', False):
                print(f"[C AST DEBUG] 跳过const变量: {var_name}")
                return
            
            # 跳过指针类型变量（可能通过malloc等函数初始化）
            var_type = var_state.get('type', '')
            if '*' in var_type or 'pointer' in var_type.lower():
                print(f"[C AST DEBUG] 跳过指针变量: {var_name} (类型: {var_type})")
                return
            
            # 检查是否未初始化
            if not var_state['is_initialized']:
                print(f"[C AST DEBUG] 检测到未初始化变量使用: {var_name}")
                self.error_reporter.add_variable_error(
                    line_num,
                    f"变量 '{var_name}' 在初始化前被使用",
                    f"建议在使用前初始化变量：{var_name} = 初始值;",
                    ""
                )
    
    def _analyze_assignment_ast(self, node: Assignment, line_num: int = 0):
        """分析赋值语句的AST节点"""
        if isinstance(node.lvalue, ID):
            var_name = node.lvalue.name
            
            # 更新变量状态为已初始化
            if var_name in self.variable_states:
                self.variable_states[var_name]['is_initialized'] = True
                print(f"[C AST DEBUG] 变量 {var_name} 通过赋值初始化")
    
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
    
    def _detect_uninitialized_variables_regex(self, parsed_data: Dict[str, List]):
        """使用正则表达式检测未初始化变量"""
        # 记录所有变量声明
        variable_declarations = {}
        function_params = set()
        reported_issues = set()  # 用于去重
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检查函数参数
            func_match = re.search(r'\w+\s+(\w+)\s*\(([^)]*)\)', line_content)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                if params_str.strip():
                    # 提取参数名
                    params = re.findall(r'\b(\w+)\b', params_str)
                    for param in params:
                        if param not in ['int', 'char', 'float', 'double', 'void', 'const', 'static']:
                            function_params.add(param)
                            variable_declarations[param] = {
                                'line': line_num,
                                'is_initialized': True,
                                'is_function_param': True,
                                'type': 'parameter'
                            }
            
            # 检查变量声明 - 按优先级排序，避免重复匹配
            decl_patterns = [
                (r'\bstatic\s+(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*=\s*([^;]+);', True, True, False),  # static带初始化
                (r'\bstatic\s+(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*;', True, False, False),  # static无初始化
                (r'\bconst\s+(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*=\s*([^;]+);', False, True, True),  # const带初始化
                (r'\b(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*=\s*([^;]+);', False, True, False),  # 带初始化
                (r'\b(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*;', False, False, False),  # 无初始化
            ]
            
            for pattern_info in decl_patterns:
                pattern, is_static, is_initialized, is_const = pattern_info
                matches = re.findall(pattern, line_content)
                
                # 如果已经匹配过，跳过后续模式
                if matches:
                    for match in matches:
                        if len(match) == 3:  # 带初始化
                            var_type, var_name, init_value = match
                            variable_declarations[var_name] = {
                                'line': line_num,
                                'is_initialized': True,
                                'is_static': is_static,
                                'is_const': is_const,
                                'type': var_type.strip()
                            }
                        elif len(match) == 2:  # 无初始化
                            var_type, var_name = match
                            variable_declarations[var_name] = {
                                'line': line_num,
                                'is_initialized': is_initialized,
                                'is_static': is_static,
                                'is_const': is_const,
                                'type': var_type.strip()
                            }
                    break  # 找到匹配后退出循环
        
        # 检查变量使用
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 跳过注释和空行
            if line_content.strip().startswith('//') or line_content.strip().startswith('/*') or not line_content.strip():
                continue
            
            # 跳过变量声明行
            if ';' in line_content and any(keyword in line_content for keyword in ['int ', 'char ', 'float ', 'double ', 'bool ']):
                continue
            
            # 检查变量使用
            var_matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', line_content)
            for var_name in var_matches:
                # 跳过关键字和函数名
                if var_name in ['printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp', 'main', 'if', 'while', 'for', 'return', 'true', 'false', 'NULL']:
                    continue
                
                if var_name in variable_declarations:
                    var_info = variable_declarations[var_name]
                    
                    # 跳过函数参数
                    if var_info.get('is_function_param', False):
                        continue
                    
                    # 跳过已初始化的变量
                    if var_info['is_initialized']:
                        continue
                    
                    # 检查是否是static变量（需要警告但不是错误）
                    if var_info.get('is_static', False):
                        issue_key = f"static_warning_{var_name}_{line_num}"
                        if issue_key not in reported_issues:
                            self.error_reporter.add_variable_warning(
                                line_num,
                                f"隐式依赖于静态变量 '{var_name}' 的零初始化",
                                f"建议显式初始化以提高代码清晰度：static {var_info['type']} {var_name} = 0;",
                                line_content
                            )
                            reported_issues.add(issue_key)
                        continue
                    
                    # 报告未初始化变量使用（去重）
                    issue_key = f"uninit_{var_name}_{line_num}"
                    if issue_key not in reported_issues:
                        self.error_reporter.add_variable_error(
                            line_num,
                            f"变量 '{var_name}' 在初始化前被使用",
                            f"建议在使用前初始化变量：{var_name} = 初始值;",
                            line_content
                        )
                        reported_issues.add(issue_key)
    
    def _detect_static_variable_warnings(self, parsed_data: Dict[str, List]):
        """检测静态变量隐式初始化的代码风格问题"""
        # 这个方法已经在_detect_uninitialized_variables_regex中实现
        pass
    
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
