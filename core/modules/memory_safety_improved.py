"""
改进的内存安全卫士模块 - 修复跨函数分析和状态追踪问题
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo


class ImprovedMemorySafetyModule:
    """改进的内存安全卫士模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 维护内存状态
        self.malloced_variables: Set[str] = set()
        self.freed_variables: Set[str] = set()
        self.memory_allocations: Dict[str, Dict] = {}  # 详细的内存分配信息
        self.function_returns: Dict[str, List[str]] = {}  # 函数返回的变量
        
        # 改进的正则表达式模式
        self.patterns = {
            'malloc': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)', re.MULTILINE),
            'calloc': re.compile(r'\b(\w+)\s*=\s*calloc\s*\([^)]+\)', re.MULTILINE),
            'realloc': re.compile(r'\b(\w+)\s*=\s*realloc\s*\([^)]+\)', re.MULTILINE),
            'free': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)', re.MULTILINE),
            'free_call': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)', re.MULTILINE),
            'pointer_dereference': re.compile(r'\b(\w+)\s*->\s*\w+', re.MULTILINE),
            'function_def': re.compile(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', re.MULTILINE),
            'return_statement': re.compile(r'\breturn\s+([^;]+);', re.MULTILINE),
            'function_call': re.compile(r'\b(\w+)\s*=\s*(\w+)\s*\([^)]*\)', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析内存安全问题 - 改进版本"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.malloced_variables.clear()
        self.freed_variables.clear()
        self.memory_allocations.clear()
        self.function_returns.clear()
        
        # 第一阶段：识别内存分配和释放
        self._identify_memory_operations(parsed_data)
        
        # 第二阶段：分析函数间的内存传递
        self._analyze_interprocedural_memory(parsed_data)
        
        # 第三阶段：检测内存问题
        self._detect_memory_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _identify_memory_operations(self, parsed_data: Dict[str, List]):
        """识别内存分配和释放操作"""
        
        current_function = None
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测函数定义
            func_match = self.patterns['function_def'].search(line_content)
            if func_match:
                current_function = func_match.group(1)
                self.function_returns[current_function] = []
            
            # 检测malloc分配
            malloc_matches = self.patterns['malloc'].findall(line_content)
            for var_name in malloc_matches:
                self.malloced_variables.add(var_name)
                self.memory_allocations[var_name] = {
                    'alloc_type': 'malloc',
                    'alloc_line': line_num,
                    'alloc_function': current_function,
                    'line_content': line_content.strip()
                }
            
            # 检测calloc分配
            calloc_matches = self.patterns['calloc'].findall(line_content)
            for var_name in calloc_matches:
                self.malloced_variables.add(var_name)
                self.memory_allocations[var_name] = {
                    'alloc_type': 'calloc',
                    'alloc_line': line_num,
                    'alloc_function': current_function,
                    'line_content': line_content.strip()
                }
            
            # 检测realloc
            realloc_matches = self.patterns['realloc'].findall(line_content)
            for var_name in realloc_matches:
                # realloc可能改变变量名，需要特殊处理
                if var_name in self.memory_allocations:
                    self.memory_allocations[var_name]['realloc_line'] = line_num
            
            # 检测free释放
            free_matches = self.patterns['free'].findall(line_content)
            for var_name in free_matches:
                self.freed_variables.add(var_name)
            
            # 检测return语句中的变量
            if current_function:
                return_matches = self.patterns['return_statement'].findall(line_content)
                for return_expr in return_matches:
                    # 提取返回的变量名
                    var_matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', return_expr)
                    for var_name in var_matches:
                        if var_name in self.malloced_variables:
                            self.function_returns[current_function].append(var_name)
    
    def _analyze_interprocedural_memory(self, parsed_data: Dict[str, List]):
        """分析函数间的内存传递"""
        
        # 分析函数调用中的内存传递
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            func_call_matches = self.patterns['function_call'].findall(line_content)
            for assigned_var, func_name in func_call_matches:
                if func_name in self.function_returns:
                    # 这个函数返回了分配的内存
                    returned_vars = self.function_returns[func_name]
                    for returned_var in returned_vars:
                        # 将返回的内存所有权转移给调用者
                        if assigned_var not in self.memory_allocations:
                            self.memory_allocations[assigned_var] = {
                                'alloc_type': 'returned',
                                'alloc_line': line_num,
                                'alloc_function': func_name,
                                'original_var': returned_var,
                                'line_content': line_content.strip()
                            }
        
        # 分析函数参数传递
        self._analyze_function_parameters(parsed_data)
    
    def _analyze_function_parameters(self, parsed_data: Dict[str, List]):
        """分析函数参数传递"""
        
        # 检测传递未初始化指针给函数
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 匹配函数调用：func_name(var_name)
            func_call_pattern = r'\b(\w+)\s*\([^)]*(\w+)[^)]*\)'
            matches = re.findall(func_call_pattern, line_content)
            
            for func_name, param_name in matches:
                # 跳过标准库函数和关键字
                if func_name in ['printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp', 'if', 'while', 'for']:
                    continue
                
                # 跳过数字和常量
                if param_name.isdigit() or param_name in ['NULL', 'true', 'false']:
                    continue
                
                # 跳过单字符参数（通常是函数参数）
                if len(param_name) == 1 and param_name.isalpha():
                    continue
                
                # 检查参数是否是未初始化的指针
                # 首先检查是否是已声明的指针变量
                if param_name in self.memory_allocations:
                    alloc_info = self.memory_allocations[param_name]
                    if not alloc_info.get('is_initialized', False):
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"将未初始化指针 '{param_name}' 传递给函数 '{func_name}'",
                            f"建议在使用前初始化指针：{param_name} = malloc(size); 或 {param_name} = NULL;",
                            line_content.strip()
                        )
                else:
                    # 检查是否是未声明的指针变量
                    # 查找变量声明
                    var_declared = False
                    for decl_line_num, decl_line_content in enumerate(parsed_data['lines'], 1):
                        if decl_line_num < line_num:  # 只在当前行之前查找
                            if f'{param_name}' in decl_line_content and ('*' in decl_line_content or 'struct' in decl_line_content):
                                var_declared = True
                                break
                    
                    if not var_declared:
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"将未声明的变量 '{param_name}' 传递给函数 '{func_name}'",
                            f"建议在使用前声明变量：struct Point* {param_name};",
                            line_content.strip()
                        )
    
    def _detect_memory_issues(self, parsed_data: Dict[str, List]):
        """检测内存问题"""
        
        # 检测malloc返回值检查
        self._detect_malloc_null_check(parsed_data)
        
        # 检测内存泄漏
        self._detect_memory_leaks(parsed_data)
        
        # 检测野指针
        self._detect_wild_pointers(parsed_data)
        
        # 检测未初始化指针解引用
        self._detect_uninitialized_pointer_dereference(parsed_data)
        
        # 检测循环内存泄漏
        self._detect_loop_memory_leaks(parsed_data)
        
        # 检测单函数内内存泄漏
        self._detect_single_function_memory_leaks(parsed_data)
        
        # 检测跨函数内存泄漏
        self._detect_interprocedural_memory_leaks(parsed_data)
    
    def _detect_malloc_null_check(self, parsed_data: Dict[str, List]):
        """检测malloc返回值检查"""
        
        for var_name, alloc_info in self.memory_allocations.items():
            alloc_line = alloc_info['alloc_line']
            alloc_function = alloc_info['alloc_function']
            
            # 检查分配后是否有NULL检查
            has_null_check = False
            
            # 在分配后的几行内查找NULL检查
            for i in range(alloc_line, min(alloc_line + 5, len(parsed_data['lines']))):
                if i < len(parsed_data['lines']):
                    line_content = parsed_data['lines'][i]
                    if f'{var_name}' in line_content and ('NULL' in line_content or 'null' in line_content):
                        has_null_check = True
                        break
            
            if not has_null_check:
                self.error_reporter.add_memory_error(
                    alloc_line,
                    f"变量 '{var_name}' 通过{alloc_info['alloc_type']}分配内存后未检查返回值",
                    f"建议添加NULL检查：if ({var_name} == NULL) {{ /* 处理错误 */ }}",
                    alloc_info['line_content']
                )
    
    def _detect_memory_leaks(self, parsed_data: Dict[str, List]):
        """检测内存泄漏 - 改进版本"""
        
        for var_name, alloc_info in self.memory_allocations.items():
            if var_name not in self.freed_variables:
                # 检查是否在函数结束时被返回（这种情况下不算泄漏）
                alloc_function = alloc_info['alloc_function']
                if alloc_function and var_name in self.function_returns.get(alloc_function, []):
                    continue  # 被返回的内存不算泄漏
                
                # 检查是否是跨函数的内存泄漏
                if alloc_info['alloc_type'] == 'returned':
                    # 这是从其他函数返回的内存，需要特别标记
                    self.error_reporter.add_memory_error(
                        alloc_info['alloc_line'],
                        f"变量 '{var_name}' 接收了从函数 '{alloc_info['alloc_function']}' 返回的内存但未释放，导致跨函数内存泄漏",
                        f"建议在适当位置添加 free({var_name}); 语句",
                        alloc_info['line_content']
                    )
                else:
                    # 普通的内存泄漏
                    self.error_reporter.add_memory_error(
                        alloc_info['alloc_line'],
                        f"变量 '{var_name}' 分配了内存但未释放，可能导致内存泄漏",
                        f"建议在适当位置添加 free({var_name}); 语句",
                        alloc_info['line_content']
                    )
    
    def _detect_wild_pointers(self, parsed_data: Dict[str, List]):
        """检测野指针"""
        
        # 检查free后是否还有使用
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测指针解引用
            deref_matches = self.patterns['pointer_dereference'].findall(line_content)
            for ptr_name in deref_matches:
                if ptr_name in self.freed_variables:
                    self.error_reporter.add_memory_error(
                        line_num,
                        f"指针 '{ptr_name}' 已被释放，但仍在被使用（野指针）",
                        "建议在free后设置指针为NULL：free(ptr); ptr = NULL;",
                        line_content.strip()
                    )
    
    def _detect_uninitialized_pointer_dereference(self, parsed_data: Dict[str, List]):
        """检测未初始化指针解引用"""
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测指针解引用
            deref_matches = self.patterns['pointer_dereference'].findall(line_content)
            for ptr_name in deref_matches:
                # 检查指针是否已分配内存
                if ptr_name not in self.malloced_variables and ptr_name not in self.freed_variables:
                    # 检查前面几行是否有NULL检查
                    has_null_check = False
                    for i in range(max(0, line_num - 5), line_num):
                        if i < len(parsed_data['lines']):
                            prev_line = parsed_data['lines'][i]
                            if f'{ptr_name}' in prev_line and ('NULL' in prev_line or 'null' in prev_line):
                                has_null_check = True
                                break
                    
                    if not has_null_check:
                        # 只报告内存安全问题，避免与变量状态监察官重复
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"内存安全问题：解引用未初始化指针 '{ptr_name}'",
                            f"建议在使用前初始化指针：{ptr_name} = malloc(size); 或 {ptr_name} = NULL;",
                            line_content.strip()
                        )
    
    def _detect_loop_memory_leaks(self, parsed_data: Dict[str, List]):
        """检测循环中的内存泄漏"""
        
        # 跟踪循环中的内存分配
        loop_allocations = {}  # {array_name: line_number}
        
        # 首先找到所有for循环
        for_loops = []
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            if 'for' in line_content and '{' in line_content:
                for_loops.append(line_num)
        
        # 检查每个for循环内部是否有malloc分配
        for loop_start_line in for_loops:
            # 查找循环体（简化处理，假设循环体在接下来的几行）
            for i in range(loop_start_line, min(loop_start_line + 10, len(parsed_data['lines']))):
                if i < len(parsed_data['lines']):
                    line_content = parsed_data['lines'][i]
                    
                    # 检测循环中的malloc分配
                    # 匹配 ptr_array[i] = malloc(...)
                    loop_malloc_pattern = r'\b(\w+)\s*\[[^\]]+\]\s*=\s*malloc\s*\([^)]+\)'
                    matches = re.findall(loop_malloc_pattern, line_content)
                    
                    for array_name in matches:
                        loop_allocations[array_name] = i
        
        # 检查循环分配的内存是否被释放
        for array_name, alloc_line in loop_allocations.items():
            # 检查是否有对应的释放循环
            has_free_loop = False
            for line_num, line_content in enumerate(parsed_data['lines'], 1):
                if 'for' in line_content and 'free' in line_content and array_name in line_content:
                    has_free_loop = True
                    break
            
            if not has_free_loop:
                self.error_reporter.add_memory_error(
                    alloc_line,
                    f"数组 '{array_name}' 在循环中分配的内存未被释放，导致循环内存泄漏",
                    f"建议添加释放循环：for (int i = 0; i < size; i++) {{ free({array_name}[i]); }}",
                    parsed_data['lines'][alloc_line - 1].strip()
                )
    
    def _find_loop_allocation_line(self, parsed_data: Dict[str, List], array_name: str) -> int:
        """查找循环分配的行号"""
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            if 'for' in line_content and array_name in line_content and 'malloc' in line_content:
                return line_num
        return 0
    
    def _detect_single_function_memory_leaks(self, parsed_data: Dict[str, List]):
        """检测单函数内的内存泄漏"""
        
        # 按函数分组分析内存分配和释放
        current_function = None
        function_allocations = {}  # {function_name: {var_name: alloc_info}}
        function_frees = set()     # {function_name: {var_name}}
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测函数开始
            func_match = re.search(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', line_content)
            if func_match:
                current_function = func_match.group(1)
                function_allocations[current_function] = {}
                function_frees = set()
            
            # 检测函数结束
            if line_content.strip() == '}' and current_function:
                # 检查函数内的内存泄漏
                for var_name, alloc_info in function_allocations[current_function].items():
                    if var_name not in function_frees:
                        # 报告内存泄漏
                        self.error_reporter.add_memory_error(
                            alloc_info['alloc_line'],
                            f"单函数内存泄漏：变量 '{var_name}' 分配了内存但未释放",
                            f"建议在函数结束前调用 free({var_name});",
                            alloc_info['line_content']
                        )
                current_function = None
            
            # 检测内存分配
            if current_function:
                for var_name, alloc_info in self.memory_allocations.items():
                    if alloc_info['alloc_line'] == line_num:
                        function_allocations[current_function][var_name] = alloc_info
                
                # 检测内存释放
                free_matches = self.patterns['free_call'].findall(line_content)
                for var_name in free_matches:
                    function_frees.add(var_name)
    
    def _detect_interprocedural_memory_leaks(self, parsed_data: Dict[str, List]):
        """检测跨函数内存泄漏"""
        
        # 检测函数调用中的内存传递
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 匹配 var = function_call(...) 模式
            func_call_pattern = r'\b(\w+)\s*=\s*(\w+)\s*\([^)]*\)'
            matches = re.findall(func_call_pattern, line_content)
            
            for assigned_var, func_name in matches:
                # 检查是否是返回内存的函数调用
                if func_name in self.function_returns:
                    # 这个函数返回了分配的内存
                    returned_vars = self.function_returns[func_name]
                    for returned_var in returned_vars:
                        # 将返回的内存所有权转移给调用者
                        if assigned_var not in self.memory_allocations:
                            self.memory_allocations[assigned_var] = {
                                'alloc_type': 'returned',
                                'alloc_line': line_num,
                                'alloc_function': func_name,
                                'original_var': returned_var,
                                'line_content': line_content.strip()
                            }
        
        # 检查跨函数内存泄漏
        for var_name, alloc_info in self.memory_allocations.items():
            if var_name not in self.freed_variables:
                # 检查是否是跨函数的内存泄漏
                if alloc_info['alloc_type'] == 'returned':
                    # 这是从其他函数返回的内存，需要特别标记
                    self.error_reporter.add_memory_error(
                        alloc_info['alloc_line'],
                        f"变量 '{var_name}' 接收了从函数 '{alloc_info['alloc_function']}' 返回的内存但未释放，导致跨函数内存泄漏",
                        f"建议在适当位置添加 free({var_name}); 语句",
                        alloc_info['line_content']
                    )
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "改进的内存安全卫士"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测内存泄漏、野指针、空指针解引用等内存安全问题，支持跨函数分析"
