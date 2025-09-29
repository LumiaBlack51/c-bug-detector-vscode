"""
标准库使用助手模块 - 检测缺失头文件、头文件拼写错误，检查常用函数参数
"""
import re
from typing import Dict, List, Set
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser


class StandardLibraryModule:
    """标准库使用助手模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 标准库函数和对应头文件的映射
        self.function_headers = {
            # stdio.h
            'printf': 'stdio.h',
            'scanf': 'stdio.h',
            'fprintf': 'stdio.h',
            'fscanf': 'stdio.h',
            'sprintf': 'stdio.h',
            'sscanf': 'stdio.h',
            'fopen': 'stdio.h',
            'fclose': 'stdio.h',
            'fread': 'stdio.h',
            'fwrite': 'stdio.h',
            'fgets': 'stdio.h',
            'fputs': 'stdio.h',
            'getchar': 'stdio.h',
            'putchar': 'stdio.h',
            'gets': 'stdio.h',
            'puts': 'stdio.h',
            'perror': 'stdio.h',
            'feof': 'stdio.h',
            'ferror': 'stdio.h',
            'clearerr': 'stdio.h',
            'rewind': 'stdio.h',
            'fseek': 'stdio.h',
            'ftell': 'stdio.h',
            'fgetpos': 'stdio.h',
            'fsetpos': 'stdio.h',
            
            # stdlib.h
            'malloc': 'stdlib.h',
            'free': 'stdlib.h',
            'calloc': 'stdlib.h',
            'realloc': 'stdlib.h',
            'exit': 'stdlib.h',
            'abort': 'stdlib.h',
            'atexit': 'stdlib.h',
            'system': 'stdlib.h',
            'getenv': 'stdlib.h',
            'putenv': 'stdlib.h',
            'rand': 'stdlib.h',
            'srand': 'stdlib.h',
            'atoi': 'stdlib.h',
            'atol': 'stdlib.h',
            'atof': 'stdlib.h',
            'strtol': 'stdlib.h',
            'strtoul': 'stdlib.h',
            'strtod': 'stdlib.h',
            'qsort': 'stdlib.h',
            'bsearch': 'stdlib.h',
            'abs': 'stdlib.h',
            'labs': 'stdlib.h',
            'div': 'stdlib.h',
            'ldiv': 'stdlib.h',
            
            # string.h
            'strlen': 'string.h',
            'strcpy': 'string.h',
            'strncpy': 'string.h',
            'strcat': 'string.h',
            'strncat': 'string.h',
            'strcmp': 'string.h',
            'strncmp': 'string.h',
            'strchr': 'string.h',
            'strrchr': 'string.h',
            'strstr': 'string.h',
            'strtok': 'string.h',
            'strspn': 'string.h',
            'strcspn': 'string.h',
            'strpbrk': 'string.h',
            'memcpy': 'string.h',
            'memmove': 'string.h',
            'memcmp': 'string.h',
            'memchr': 'string.h',
            'memset': 'string.h',
            'strerror': 'string.h',
            
            # math.h
            'sin': 'math.h',
            'cos': 'math.h',
            'tan': 'math.h',
            'asin': 'math.h',
            'acos': 'math.h',
            'atan': 'math.h',
            'atan2': 'math.h',
            'sinh': 'math.h',
            'cosh': 'math.h',
            'tanh': 'math.h',
            'exp': 'math.h',
            'log': 'math.h',
            'log10': 'math.h',
            'pow': 'math.h',
            'sqrt': 'math.h',
            'ceil': 'math.h',
            'floor': 'math.h',
            'fabs': 'math.h',
            'fmod': 'math.h',
            'frexp': 'math.h',
            'ldexp': 'math.h',
            'modf': 'math.h',
            
            # ctype.h
            'isalpha': 'ctype.h',
            'isdigit': 'ctype.h',
            'isalnum': 'ctype.h',
            'isspace': 'ctype.h',
            'isupper': 'ctype.h',
            'islower': 'ctype.h',
            'toupper': 'ctype.h',
            'tolower': 'ctype.h',
            'ispunct': 'ctype.h',
            'isprint': 'ctype.h',
            'iscntrl': 'ctype.h',
            'isgraph': 'ctype.h',
            'isxdigit': 'ctype.h',
            
            # time.h
            'time': 'time.h',
            'clock': 'time.h',
            'difftime': 'time.h',
            'mktime': 'time.h',
            'asctime': 'time.h',
            'ctime': 'time.h',
            'gmtime': 'time.h',
            'localtime': 'time.h',
            'strftime': 'time.h',
        }
        
        # 常见头文件拼写错误
        self.common_header_misspellings = {
            'stdio.h': ['studio.h', 'stdi.h', 'stdio'],
            'stdlib.h': ['stdli.h', 'stdlib'],
            'string.h': ['strng.h', 'string'],
            'math.h': ['mat.h', 'math'],
            'ctype.h': ['ctyp.h', 'ctype'],
            'time.h': ['tim.h', 'time'],
        }
        
        # 编译正则表达式模式
        self.patterns = {
            'scanf_params': re.compile(r'\bscanf\s*\([^)]*\)', re.MULTILINE),
            'printf_params': re.compile(r'\bprintf\s*\([^)]*\)', re.MULTILINE),
            'function_call': re.compile(r'\b(\w+)\s*\([^)]*\)', re.MULTILINE),
            'include': re.compile(r'#include\s*[<"]([^>"]+)[>"]', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析标准库使用问题"""
        self.error_reporter.clear_reports()
        
        # 首先扫描全局变量信息以便后续使用
        self._scan_global_variables(parsed_data)
        
        # 分析各种标准库使用问题
        self._detect_missing_headers(parsed_data)
        self._detect_header_misspellings(parsed_data)
        self._detect_function_parameter_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _scan_global_variables(self, parsed_data: Dict[str, List]):
        """扫描全局变量信息"""
        self._global_variables = {}
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 跳过注释行
            if line_content.strip().startswith('//') or line_content.strip().startswith('/*'):
                continue
            
            # 检查数组声明：int arr[10];
            array_match = re.search(r'\b(\w+)\s+(\w+)\s*\[', line_content)
            if array_match:
                var_type, var_name = array_match.groups()
                self._global_variables[var_name] = {
                    'is_array': True,
                    'is_pointer': False,
                    'type': var_type,
                    'line': line_num
                }
                continue  # 避免重复匹配
            
            # 检查指针声明：int *ptr; 或 int *ptr = &x;
            pointer_match = re.search(r'\b(\w+)\s*\*\s*(\w+)\b', line_content)
            if pointer_match:
                var_type, var_name = pointer_match.groups()
                self._global_variables[var_name] = {
                    'is_array': False,
                    'is_pointer': True,
                    'type': var_type,
                    'line': line_num
                }
                continue  # 避免重复匹配
            
            # 检查普通变量声明：int x; 或 int x = 100;
            normal_var_match = re.search(r'\b(int|char|float|double|long|short|unsigned|signed|bool)\s+(\w+)\s*[;=]', line_content)
            if normal_var_match:
                var_type, var_name = normal_var_match.groups()
                self._global_variables[var_name] = {
                    'is_array': False,
                    'is_pointer': False,
                    'type': var_type,
                    'line': line_num
                }
    
    def _detect_missing_headers(self, parsed_data: Dict[str, List]):
        """检测缺失的头文件"""
        # 获取所有包含的头文件
        included_headers = set()
        for include in parsed_data['includes']:
            included_headers.add(include['header'])
        
        # 检查函数调用
        for func_call in parsed_data['function_calls']:
            func_name = func_call['name']
            line_num = func_call['line']
            
            if func_name in self.function_headers:
                required_header = self.function_headers[func_name]
                if required_header not in included_headers:
                    self.error_reporter.add_library_error(
                        line_num,
                        f"使用函数 '{func_name}' 但未包含必要的头文件 '{required_header}'",
                        f"建议在文件开头添加：#include <{required_header}>",
                        func_call['line_content']
                    )
    
    def _detect_header_misspellings(self, parsed_data: Dict[str, List]):
        """检测头文件拼写错误"""
        for include in parsed_data['includes']:
            header = include['header']
            line_num = include['line']
            
            # 检查常见拼写错误
            for correct_header, misspellings in self.common_header_misspellings.items():
                if header in misspellings:
                    self.error_reporter.add_library_error(
                        line_num,
                        f"头文件 '{header}' 拼写错误",
                        f"建议修正为：#include <{correct_header}>",
                        include['line_content']
                    )
                    break
    
    def _detect_function_parameter_issues(self, parsed_data: Dict[str, List]):
        """检测函数参数问题"""
        # 检查scanf参数
        for scanf_call in parsed_data['scanf_calls']:
            line_content = scanf_call['line_content']
            line_num = scanf_call['line']
            
            # 检查scanf参数是否有&符号
            self._check_scanf_parameters(line_content, line_num)
        
        # 检查printf参数
        for printf_call in parsed_data['printf_calls']:
            line_content = printf_call['line_content']
            line_num = printf_call['line']
            
            # 检查printf格式字符串
            self._check_printf_parameters(line_content, line_num)
    
    def _check_scanf_parameters(self, line_content: str, line_num: int):
        """检查scanf参数 - 改进版本"""
        # 提取scanf的参数
        scanf_match = self.patterns['scanf_params'].search(line_content)
        if scanf_match:
            params = scanf_match.group(0)
            
            # 解析scanf参数：分离格式字符串和实际参数
            format_string, actual_params = self._parse_scanf_arguments(params)
            
            if format_string is None:
                return  # 解析失败，跳过检查
            
            # 检查每个实际参数
            for param in actual_params:
                param = param.strip()
                
                # 跳过空参数
                if not param:
                    continue
                
                # 检查是否是变量名（不是关键字、类型名等）
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param):
                    # 检查变量前是否有&符号
                    if not param.startswith('&'):
                        # 检查是否是数组名或指针变量（这些不需要&）
                        # 注意：这里需要用全局变量信息来判断，而不仅仅是当前行
                        if self._is_known_array_or_pointer(param):
                            continue  # 数组名和指针变量不需要&
                        
                        # 检查是否是函数参数（通常不需要&）
                        if self._is_function_parameter(param, line_content):
                            continue
                        
                        # 报告缺少&的错误
                        self.error_reporter.add_library_error(
                            line_num,
                            f"scanf中变量 '{param}' 缺少地址运算符 &",
                            f"建议修正为：scanf(\"...\", &{param});",
                            line_content
                        )
    
    def _parse_scanf_arguments(self, params_content: str):
        """解析scanf参数，返回格式字符串和参数列表"""
        params_content = params_content.strip()
        
        # 移除scanf(和)
        if params_content.startswith('scanf('):
            params_content = params_content[6:]
        if params_content.endswith(')'):
            params_content = params_content[:-1]
        
        # 查找第一个字符串字面量（格式字符串）
        string_match = re.search(r'"([^"]*)"', params_content)
        if string_match:
            format_string = string_match.group(1)
            # 获取格式字符串后的内容
            after_format = params_content[string_match.end():].strip()
            if after_format.startswith(','):
                after_format = after_format[1:].strip()
            
            # 解析剩余参数
            if after_format:
                actual_params = self._parse_comma_separated_params(after_format)
            else:
                actual_params = []
        else:
            format_string = None
            actual_params = []
        
        return format_string, actual_params
    
    def _is_array_or_pointer_variable(self, var_name: str, line_content: str) -> bool:
        """检查变量是否是数组或指针变量"""
        # 查找变量声明
        # 检查是否是数组声明：int arr[10];
        if re.search(rf'\b\w+\s+{var_name}\s*\[', line_content):
            return True
        
        # 检查是否是指针声明：int *ptr;
        if re.search(rf'\b\w+\s*\*\s*{var_name}\b', line_content):
            return True
        
        # 检查是否是函数参数中的指针：int func(int *ptr)
        if re.search(rf'\*\s*{var_name}\b', line_content):
            return True
        
        # 检查是否是赋值语句中的指针：int *xp = &x;
        if re.search(rf'\*\s*{var_name}\s*=', line_content):
            return True
        
        return False
    
    def _is_known_array_or_pointer(self, var_name: str) -> bool:
        """检查变量是否是已知的数组或指针变量"""
        # 从缓存的代码中查找变量声明信息
        # 这里可以使用全局变量状态来判断
        if hasattr(self, '_global_variables'):
            if var_name in self._global_variables:
                var_info = self._global_variables[var_name]
                return var_info.get('is_array', False) or var_info.get('is_pointer', False)
        
        # 回退到简单的命名规则判断
        # 通常数组名以arr开头，指针名以p/ptr结尾或开头
        if var_name.startswith('arr') or var_name.endswith('p') or var_name.endswith('ptr') or 'ptr' in var_name.lower():
            return True
        
        return False
    
    def _is_function_parameter(self, var_name: str, line_content: str) -> bool:
        """检查变量是否是函数参数"""
        # 查找函数定义中的参数列表
        func_match = re.search(r'\w+\s+\w+\s*\(([^)]*)\)', line_content)
        if func_match:
            params_str = func_match.group(1)
            # 检查参数列表中是否包含该变量
            if re.search(rf'\b{var_name}\b', params_str):
                return True
        
        return False
    
    def _check_printf_parameters(self, line_content: str, line_num: int):
        """检查printf参数 - 改进版本"""
        # 提取printf的参数
        printf_match = re.search(r'printf\s*\(([^)]+)\)', line_content)
        if not printf_match:
            return
            
        params_content = printf_match.group(1).strip()
        
        # 解析参数：分离格式字符串和实际参数
        format_string, actual_params = self._parse_printf_arguments(params_content)
        
        if format_string is None:
            return  # 解析失败，跳过检查
        
        # 如果格式字符串是变量名而不是字符串字面量，跳过检查
        # 注意：从双引号内提取出的格式字符串不会包含双引号
        # 只有当格式字符串是变量名时才跳过（例如 printf(fmt, x)）
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', format_string):
            return  # 格式字符串是变量，无法静态分析
            
        # 计算格式说明符数量 - 支持长度修饰符
        format_specifiers = re.findall(r'%l?l?[diouxXeEfFgGaAcspn%]', format_string)
        # 排除 %% 转义字符
        format_specifiers = [spec for spec in format_specifiers if spec != '%%']
        
        # 计算实际参数数量
        param_count = len(actual_params)
        
        # 检查匹配性
        if len(format_specifiers) != param_count:
            self.error_reporter.add_library_error(
                line_num,
                f"printf格式字符串数量({len(format_specifiers)})与参数数量({param_count})不匹配",
                "建议检查格式字符串和参数数量是否一致",
                line_content
            )
        else:
            # 检查格式说明符与参数类型的兼容性
            self._check_printf_type_compatibility(format_specifiers, actual_params, line_num, line_content)
    
    def _parse_printf_arguments(self, params_content: str):
        """解析printf参数，返回格式字符串和参数列表"""
        params_content = params_content.strip()
        
        # 处理只有格式字符串的情况：printf("string")
        if params_content.startswith('"') and params_content.endswith('"'):
            format_string = params_content[1:-1]  # 去掉引号
            return format_string, []
        
        # 处理多个参数的情况
        # 需要正确解析字符串字面量和参数
        format_string = None
        actual_params = []
        
        # 查找第一个字符串字面量（格式字符串）
        string_match = re.search(r'"([^"]*)"', params_content)
        if string_match:
            format_string = string_match.group(1)
            # 获取格式字符串后的内容
            after_format = params_content[string_match.end():].strip()
            if after_format.startswith(','):
                after_format = after_format[1:].strip()
            
            # 解析剩余参数
            if after_format:
                actual_params = self._parse_comma_separated_params(after_format)
        else:
            # 如果没有找到字符串字面量，尝试其他方法
            # 可能是printf(variable)的情况
            parts = params_content.split(',', 1)
            if len(parts) == 1:
                # 只有一个参数，可能是格式字符串变量
                format_string = parts[0].strip()
                actual_params = []
            else:
                # 多个参数，第一个是格式字符串
                format_string = parts[0].strip()
                actual_params = self._parse_comma_separated_params(parts[1])
        
        return format_string, actual_params
    
    def _parse_comma_separated_params(self, params_str: str):
        """解析逗号分隔的参数"""
        params = []
        current_param = ""
        paren_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for char in params_str:
            if escape_next:
                current_param += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_param += char
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                current_param += char
                continue
                
            if in_string:
                current_param += char
                continue
                
            if char == '(':
                paren_count += 1
                current_param += char
            elif char == ')':
                paren_count -= 1
                current_param += char
            elif char == '[':
                bracket_count += 1
                current_param += char
            elif char == ']':
                bracket_count -= 1
                current_param += char
            elif char == ',' and paren_count == 0 and bracket_count == 0:
                # 找到参数分隔符
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char
        
        # 添加最后一个参数
        if current_param.strip():
            params.append(current_param.strip())
            
        return params
    
    def _check_printf_type_compatibility(self, format_specifiers: List[str], actual_params: List[str], line_num: int, line_content: str):
        """检查printf格式说明符与参数类型的兼容性"""
        for i, (spec, param) in enumerate(zip(format_specifiers, actual_params)):
            param = param.strip()
            
            # 获取参数的可能类型信息
            param_type = self._infer_parameter_type(param)
            
            # 检查兼容性
            if not self._is_format_compatible(spec, param_type):
                expected_types = self._get_expected_types_for_format(spec)
                self.error_reporter.add_library_error(
                    line_num,
                    f"printf格式说明符 '{spec}' 与参数 '{param}' 类型不兼容",
                    f"格式 '{spec}' 期望类型: {', '.join(expected_types)}",
                    line_content
                )
    
    def _infer_parameter_type(self, param: str) -> str:
        """推断参数类型"""
        # 检查是否是已知变量
        if param in self._global_variables:
            param_type = self._global_variables[param]['type']
            return param_type
        
        # 检查是否是字面量
        if param.isdigit():
            return 'int'
        elif param.replace('.', '').replace('-', '').isdigit():
            return 'float'
        elif param.startswith('"') and param.endswith('"'):
            return 'char*'
        elif param in ['true', 'false']:
            return 'bool'
        
        return 'unknown'
    
    def _is_format_compatible(self, format_spec: str, param_type: str) -> bool:
        """检查格式说明符与参数类型是否兼容"""
        if param_type == 'unknown':
            return True  # 无法确定类型，跳过检查
        
        # 兼容性映射表
        compatibility_map = {
            '%d': ['int', 'short', 'char'],
            '%i': ['int', 'short', 'char'],
            '%u': ['unsigned int', 'unsigned', 'int'],
            '%o': ['int', 'unsigned int'],
            '%x': ['int', 'unsigned int'],
            '%X': ['int', 'unsigned int'],
            '%f': ['float', 'double'],
            '%F': ['float', 'double'],
            '%e': ['float', 'double'],
            '%E': ['float', 'double'],
            '%g': ['float', 'double'],
            '%G': ['float', 'double'],
            '%c': ['char', 'int'],
            '%s': ['char*', 'string'],
            '%p': ['pointer', 'void*', 'int*', 'char*'],
            '%ld': ['long', 'long int'],
            '%lld': ['long long', 'long long int'],
            '%lf': ['double']
        }
        
        expected_types = compatibility_map.get(format_spec, [])
        return param_type in expected_types
    
    def _get_expected_types_for_format(self, format_spec: str) -> List[str]:
        """获取格式说明符期望的类型列表"""
        type_map = {
            '%d': ['int'],
            '%i': ['int'],
            '%u': ['unsigned int'],
            '%o': ['unsigned int'],
            '%x': ['unsigned int'],
            '%X': ['unsigned int'],
            '%f': ['double'],
            '%F': ['double'],
            '%e': ['double'],
            '%E': ['double'],
            '%g': ['double'],
            '%G': ['double'],
            '%c': ['char'],
            '%s': ['char*'],
            '%p': ['pointer'],
            '%ld': ['long'],
            '%lld': ['long long'],
            '%lf': ['double']
        }
        
        return type_map.get(format_spec, ['unknown'])
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "标准库使用助手"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测缺失头文件、头文件拼写错误，检查常用函数参数"
