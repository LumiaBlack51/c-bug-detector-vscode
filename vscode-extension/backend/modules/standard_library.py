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
        
        # 分析各种标准库使用问题
        self._detect_missing_headers(parsed_data)
        self._detect_header_misspellings(parsed_data)
        self._detect_function_parameter_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
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
        """检查scanf参数"""
        # 提取scanf的参数
        scanf_match = self.patterns['scanf_params'].search(line_content)
        if scanf_match:
            params = scanf_match.group(0)
            
            # 检查参数中是否有&符号
            # 简单的启发式检查：如果参数包含变量名但没有&，可能是错误
            var_matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', params)
            for var_name in var_matches:
                if var_name not in ['scanf', 'printf', 'int', 'char', 'float', 'double', 'long', 'short', 'unsigned', 'signed']:
                    # 检查变量前是否有&
                    var_pattern = rf'\b{var_name}\b'
                    if re.search(var_pattern, params) and '&' + var_name not in params:
                        self.error_reporter.add_library_error(
                            line_num,
                            f"scanf中变量 '{var_name}' 缺少地址运算符 &",
                            f"建议修正为：scanf(\"...\", &{var_name});",
                            line_content
                        )
    
    def _check_printf_parameters(self, line_content: str, line_num: int):
        """检查printf参数"""
        # 提取printf的参数
        printf_match = self.patterns['printf_params'].search(line_content)
        if printf_match:
            params = printf_match.group(0)
            
            # 检查格式字符串和参数数量是否匹配
            # 这是一个简化的检查，实际实现会更复杂
            format_strings = re.findall(r'%[diouxXeEfFgGaAcspn%]', params)
            
            # 提取参数部分（括号内的内容）
            param_match = re.search(r'printf\s*\(([^)]+)\)', params)
            if param_match:
                param_content = param_match.group(1)
                # 计算参数数量（排除格式字符串）
                # 简单计算：逗号分隔的参数数量
                if format_strings:
                    # 有格式字符串，计算逗号数量
                    comma_count = param_content.count(',')
                    param_count = comma_count
                else:
                    # 没有格式字符串，检查是否有参数
                    param_count = 1 if param_content.strip() and param_content.strip() != '""' else 0
                
                if len(format_strings) != param_count:
                    self.error_reporter.add_library_error(
                        line_num,
                        f"printf格式字符串数量({len(format_strings)})与参数数量({param_count})不匹配",
                        "建议检查格式字符串和参数数量是否一致",
                        line_content
                    )
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "标准库使用助手"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测缺失头文件、头文件拼写错误，检查常用函数参数"
