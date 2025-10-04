"""
改进的内存安全卫士模块 - 修复跨函数分析和状态追踪问题
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo
from .scope_analyzer import ScopeAnalyzer
from .cfg_analyzer import CFGAnalyzer


class ImprovedMemorySafetyModule:
    """改进的内存安全卫士模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        self.scope_analyzer = ScopeAnalyzer()
        self.cfg_analyzer = CFGAnalyzer()
        
        # 维护内存状态
        self.malloced_variables: Set[str] = set()
        self.freed_variables: Set[str] = set()
        self.declared_pointers: Dict[str, Dict] = {}  # 声明的指针变量信息
        self.memory_allocations: Dict[str, Dict] = {}  # 详细的内存分配信息
        self.function_returns: Dict[str, List[str]] = {}  # 函数返回的变量
        
        # 过程间分析 - 函数行为摘要
        self.function_summaries: Dict[str, Dict] = {}  # 函数行为摘要
        self.function_return_states: Dict[str, str] = {}  # 函数返回值状态
        self.tainted_variables: Dict[str, str] = {}  # 被污染的变量及其污染源
        
        # 错误聚合机制
        self.reported_pointers: Set[str] = set()  # 已报告的指针，避免重复报告
        self.pointer_usage_locations: Dict[str, List[int]] = {}  # 指针使用位置记录
        
        # 改进的正则表达式模式
        self.patterns = {
            'malloc': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)', re.MULTILINE),
            'calloc': re.compile(r'\b(\w+)\s*=\s*calloc\s*\([^)]+\)', re.MULTILINE),
            'realloc': re.compile(r'\b(\w+)\s*=\s*realloc\s*\([^)]+\)', re.MULTILINE),
            'free': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)', re.MULTILINE),
            'free_call': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)', re.MULTILINE),
            'pointer_dereference': re.compile(r'\*(\w+)|\b(\w+)\s*->\s*\w+', re.MULTILINE),
            'array_access': re.compile(r'\b(\w+)\s*\[\s*[^]]+\s*\]', re.MULTILINE),  # ptr[index]
            'double_pointer_deref': re.compile(r'\*\*(\w+)', re.MULTILINE),  # **ptr
            'pointer_declaration': re.compile(r'\b(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool|struct\s+\w+)\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
            'struct_pointer_declaration': re.compile(r'\b(struct\s+\w+\s*\*+\s*(\w+)|(\w+)\s*\*+\s*(\w+))\s*[;=]', re.MULTILINE),
            'flexible_struct_pointer': re.compile(r'\bstruct\s+\w+\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
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
        self.declared_pointers.clear()
        self.memory_allocations.clear()
        self.function_returns.clear()
        self.reported_pointers.clear()
        self.pointer_usage_locations.clear()
        self.function_summaries.clear()
        self.function_return_states.clear()
        self.tainted_variables.clear()
        
        # 第一阶段：作用域分析和变量识别
        self.scope_variables = self.scope_analyzer.analyze(parsed_data)
        self._identify_pointer_declarations(parsed_data)
        self._identify_memory_operations(parsed_data)
        
        # 第二阶段：控制流图分析
        cfg_result = self.cfg_analyzer.analyze(parsed_data)
        self.cfg = cfg_result['cfg']
        
        # 第三阶段：分析函数间的内存传递和函数行为摘要
        self._analyze_function_summaries(parsed_data)
        self._analyze_interprocedural_memory(parsed_data)
        
        # 第四阶段：检测内存问题
        self._detect_memory_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _is_function_parameter_pointer(self, ptr_name: str, current_line: int, parsed_data: Dict[str, List]) -> bool:
        """检查指针是否是函数参数"""
        # 向上查找函数定义
        for i in range(current_line - 1, -1, -1):
            if i < len(parsed_data['lines']):
                line = parsed_data['lines'][i]
                # 查找函数定义
                func_match = re.search(r'\w+\s+(\w+)\s*\(([^)]*)\)', line)
                if func_match:
                    params_str = func_match.group(2)
                    # 检查参数列表中是否包含这个指针
                    if ptr_name in params_str and '*' in params_str:
                        return True
                    break  # 找到函数定义就停止
                # 如果遇到另一个函数定义或到达文件开头，停止搜索
                if '{' in line and '}' not in line:
                    break
        return False
    
    def _is_linked_list_traversal_pattern(self, var_name: str, line_content: str, parsed_data: Dict[str, List], line_num: int) -> bool:
        """检查是否是链表遍历的标准模式，避免误报"""
        # 检查是否是标准的链表遍历模式：Edge* nx = e->next; free(e); e = nx;
        # 或者类似的模式：Node* next = current->next; free(current); current = next;
        
        # 模式1：检查当前行是否包含 ->next 访问
        if '->next' in line_content and var_name in line_content:
            # 检查前后几行是否有对应的free和赋值模式
            for offset in range(-3, 4):  # 检查前后3行
                check_line_num = line_num + offset
                if 1 <= check_line_num <= len(parsed_data['lines']):
                    check_line = parsed_data['lines'][check_line_num - 1]
                    
                    # 检查是否有 free(var_name) 模式
                    if f'free({var_name})' in check_line:
                        # 检查是否有 var_name = next_var 模式
                        for offset2 in range(-2, 3):
                            check_line_num2 = line_num + offset2
                            if 1 <= check_line_num2 <= len(parsed_data['lines']):
                                check_line2 = parsed_data['lines'][check_line_num2 - 1]
                                if f'{var_name} =' in check_line2 and 'next' in check_line2:
                                    return True
        
        # 模式2：检查是否是 while 循环中的链表遍历
        if 'while' in line_content and var_name in line_content:
            # 查找循环体中的free模式
            for i in range(line_num, min(line_num + 10, len(parsed_data['lines']))):
                if i < len(parsed_data['lines']):
                    loop_line = parsed_data['lines'][i]
                    if f'free({var_name})' in loop_line:
                        # 检查循环体中是否有赋值操作
                        for j in range(i + 1, min(i + 5, len(parsed_data['lines']))):
                            if j < len(parsed_data['lines']):
                                assign_line = parsed_data['lines'][j]
                                if f'{var_name} =' in assign_line and '->next' in assign_line:
                                    return True
        
        return False
    
    def _is_type_definition(self, line_content: str) -> bool:
        """判断是否是类型定义（typedef或结构体定义）"""
        line_content = line_content.strip()
        
        # 检查是否是typedef
        if line_content.startswith('typedef'):
            return True
        
        # 检查是否是结构体定义
        if line_content.startswith('struct ') and '{' in line_content:
            return True
        
        # 检查是否是结构体成员定义（在结构体内部）
        if ('struct' in line_content and 
            ('int' in line_content or 'char' in line_content or 'float' in line_content or 
             'double' in line_content or 'long' in line_content or 'short' in line_content) and
            ';' in line_content and '=' not in line_content):
            return True
        
        # 检查是否是typedef结构体的成员定义
        if (('int' in line_content or 'char' in line_content or 'float' in line_content or 
             'double' in line_content or 'long' in line_content or 'short' in line_content) and
            ';' in line_content and '=' not in line_content and 
            not any(keyword in line_content for keyword in ['malloc', 'calloc', 'free', 'printf'])):
            return True
        
        return False
    
    def _identify_pointer_declarations(self, parsed_data: Dict[str, List]):
        """识别指针变量声明 - 使用作用域分析结果"""
        # 使用作用域分析器已经识别的变量
        for var_name, var_info in self.scope_variables.items():
            if var_info.get('is_pointer', False):
                self.declared_pointers[var_name] = {
                    'type': var_info['type'],
                    'line': var_info['line'],
                    'is_static': var_info['is_static'],
                    'is_const': var_info['is_const'],
                    'is_initialized': var_info['is_initialized'],
                    'line_content': var_info['line_content'],
                    'scope_level': var_info['scope_level'],
                    'scope_type': var_info['scope_type'],
                    'scope_path': var_info['scope_path']
                }
    
    def _identify_memory_operations(self, parsed_data: Dict[str, List]):
        """识别内存分配和释放操作"""
        
        current_function = None
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 过滤掉typedef和结构体定义
            if self._is_type_definition(line_content):
                continue
                
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
    
    def _analyze_function_summaries(self, parsed_data: Dict[str, List]):
        """分析函数行为摘要，生成函数返回值状态信息"""
        
        current_function = None
        function_start_line = 0
        brace_count = 0
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测函数定义
            func_match = re.search(r'(\w+\s+)?(\w+)\s*\([^)]*\)\s*{', line_content)
            if func_match:
                current_function = func_match.group(2)
                function_start_line = line_num
                brace_count = 1
                
                # 初始化函数摘要
                self.function_summaries[current_function] = {
                    'start_line': line_num,
                    'end_line': 0,
                    'declared_pointers': [],
                    'uninitialized_pointers': [],
                    'return_statements': [],
                    'returns_uninitialized_pointer': False
                }
                continue
            
            if current_function and brace_count > 0:
                # 更新大括号计数
                brace_count += line_content.count('{') - line_content.count('}')
                
                # 检测指针声明
                pointer_matches = self.patterns['pointer_declaration'].findall(line_content)
                for static_qualifier, const_qualifier, var_type, var_name in pointer_matches:
                    is_initialized = '=' in line_content
                    
                    self.function_summaries[current_function]['declared_pointers'].append({
                        'name': var_name,
                        'type': var_type,
                        'line': line_num,
                        'is_initialized': is_initialized,
                        'is_static': bool(static_qualifier),
                        'is_const': bool(const_qualifier)
                    })
                    
                    # 如果未初始化，记录为潜在的未初始化指针
                    if not is_initialized and not static_qualifier:
                        self.function_summaries[current_function]['uninitialized_pointers'].append(var_name)
                
                # 检测return语句
                return_matches = self.patterns['return_statement'].findall(line_content)
                for return_expr in return_matches:
                    return_expr = return_expr.strip()
                    self.function_summaries[current_function]['return_statements'].append({
                        'line': line_num,
                        'expression': return_expr,
                        'line_content': line_content.strip()
                    })
                    
                    # 分析返回的是否是未初始化指针
                    var_matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', return_expr)
                    for var_name in var_matches:
                        if var_name in self.function_summaries[current_function]['uninitialized_pointers']:
                            self.function_summaries[current_function]['returns_uninitialized_pointer'] = True
                            self.function_return_states[current_function] = 'uninitialized_pointer'
                            break
                
                # 函数结束
                if brace_count == 0:
                    self.function_summaries[current_function]['end_line'] = line_num
                    current_function = None
    
    def _analyze_interprocedural_memory(self, parsed_data: Dict[str, List]):
        """分析函数间的内存传递"""
        
        # 分析函数调用中的内存传递和返回值污染
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            func_call_matches = self.patterns['function_call'].findall(line_content)
            for assigned_var, func_name in func_call_matches:
                # 检查函数是否返回未初始化指针
                if func_name in self.function_return_states:
                    if self.function_return_states[func_name] == 'uninitialized_pointer':
                        # 污染接收返回值的变量
                        self.tainted_variables[assigned_var] = f"函数 {func_name} 返回未初始化指针"
                        
                        # 同时将其标记为声明的指针（用于后续检测）
                        self.declared_pointers[assigned_var] = {
                            'type': 'int',  # 假设类型，实际应该从函数签名推断
                            'line': line_num,
                            'is_static': False,
                            'is_const': False,
                            'is_initialized': False,  # 关键：标记为未初始化
                            'line_content': line_content.strip(),
                            'taint_source': func_name
                        }
                
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
            for match in deref_matches:
                # 处理两种匹配模式：*ptr 或 ptr->member
                ptr_name = match[0] if match[0] else match[1]
                if not ptr_name:
                    continue
                    
                if ptr_name in self.freed_variables:
                    # 检查是否是链表遍历的标准模式
                    if not self._is_linked_list_traversal_pattern(ptr_name, line_content, parsed_data, line_num):
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"指针 '{ptr_name}' 已被释放，但仍在被使用（野指针）",
                            "建议在free后设置指针为NULL：free(ptr); ptr = NULL;",
                            line_content.strip()
                        )
    
    def _detect_uninitialized_pointer_dereference(self, parsed_data: Dict[str, List]):
        """检测未初始化指针解引用 - 增强版本支持循环和函数调用"""
        
        # 跟踪当前函数和循环上下文
        current_function = None
        in_loop = False
        loop_depth = 0
        
        # print(f"[DEBUG] 总共有 {len(parsed_data['lines'])} 行代码")
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # print(f"[DEBUG] 原始第{line_num}行: {repr(line_content)}")
            
            
            # 跳过声明行和初始化行 - 更精确的匹配
            # 匹配类似 "int *ptr;" 或 "static char *str = NULL;" 的声明
            if re.search(r'^\s*(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool|struct\s+\w+)\s*\*\s*\w+\s*[;=]', line_content):
                # print(f"[DEBUG] 跳过指针声明行: {line_num}")
                continue
            
            # 跳过结构体指针声明行 - 处理更灵活的格式
            if re.search(r'^\s*(struct\s+\w+\s*\*+\s*\w+|\w+\s*\*+\s*\w+)\s*[;=]', line_content):
                # print(f"[DEBUG] 跳过结构体指针声明行: {line_num}")
                continue
            
            # 检测函数定义
            func_match = re.search(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', line_content)
            if func_match:
                current_function = func_match.group(1)
                continue
            
            # 检测循环开始
            if re.search(r'\b(for|while|do)\s*\(', line_content):
                in_loop = True
                loop_depth += 1
                # print(f"[DEBUG] 检测到循环开始，第{line_num}行，深度: {loop_depth}")
            
            # 检测循环结束（简化版本）- 先处理内容，再检测结束
            loop_ending = False
            if in_loop and '}' in line_content:
                loop_ending = True
            
            # print(f"[DEBUG] 第{line_num}行处理: in_loop={in_loop}, 内容: {line_content.strip()}")
                
            # 检测指针解引用 (*ptr 或 ptr->member)
            deref_matches = self.patterns['pointer_dereference'].findall(line_content)
            for match in deref_matches:
                # 处理两种匹配模式：*ptr 或 ptr->member
                ptr_name = match[0] if match[0] else match[1]
                if not ptr_name:
                    continue
                
                self._check_pointer_safety(ptr_name, line_num, line_content, "解引用")
            
            # 检测数组访问 (ptr[index])
            array_matches = self.patterns['array_access'].findall(line_content)
            # if array_matches:
            #     print(f"[DEBUG] 第{line_num}行发现数组访问: {array_matches}, 内容: {line_content.strip()}")
            for ptr_name in array_matches:
                if ptr_name:
                    # print(f"[DEBUG] 检测到数组访问: {ptr_name} 在第{line_num}行，是否已声明: {ptr_name in self.declared_pointers}")
                    self._check_pointer_safety(ptr_name, line_num, line_content, "数组访问")
            
            # 检测双重指针解引用 (**ptr)
            double_matches = self.patterns['double_pointer_deref'].findall(line_content)
            for ptr_name in double_matches:
                if ptr_name:
                    self._check_pointer_safety(ptr_name, line_num, line_content, "双重指针解引用")
            
            # 检测函数调用中的野指针参数
            func_call_matches = re.findall(r'\b(\w+)\s*\(([^)]*)\)', line_content)
            for func_name, params in func_call_matches:
                if func_name not in ['printf', 'scanf', 'malloc', 'free', 'calloc', 'realloc']:
                    # 检查参数中的指针
                    param_vars = re.findall(r'\b(\w+)\b', params)
                    for param_var in param_vars:
                        if param_var in self.declared_pointers:
                            self._check_pointer_safety(param_var, line_num, line_content, f"函数调用参数传递给{func_name}")
            
            # 处理循环结束
            if loop_ending:
                loop_depth -= 1
                # print(f"[DEBUG] 检测到循环结束，第{line_num}行，深度: {loop_depth}")
                if loop_depth <= 0:
                    in_loop = False
                    loop_depth = 0
    
    def _check_pointer_safety(self, ptr_name: str, line_num: int, line_content: str, access_type: str):
        """检查指针安全性的通用方法 - 带错误聚合和污染追踪，使用作用域分析"""
        # 检查指针是否已分配内存或已初始化
        is_allocated = ptr_name in self.malloced_variables
        is_freed = ptr_name in self.freed_variables
        is_tainted = ptr_name in self.tainted_variables
        
        # 使用作用域分析器找到正确的变量定义
        var_info = self.scope_analyzer.find_variable_in_scope(ptr_name, line_num)
        is_declared_pointer = var_info is not None and var_info.get('is_pointer', False)
        
        # print(f"[DEBUG] 检查指针 {ptr_name}: allocated={is_allocated}, freed={is_freed}, declared={is_declared_pointer}, tainted={is_tainted}")
        
        # 优先检查被污染的变量（函数返回的未初始化指针）
        if is_tainted:
            # 错误聚合：记录使用位置，但只在第一次使用时报告
            if ptr_name not in self.pointer_usage_locations:
                self.pointer_usage_locations[ptr_name] = []
            self.pointer_usage_locations[ptr_name].append(line_num)
            
            # 只在第一次检测到该指针的问题时报告
            if ptr_name not in self.reported_pointers:
                self.reported_pointers.add(ptr_name)
                
                # 生成聚合的错误消息
                usage_lines = self.pointer_usage_locations[ptr_name]
                usage_info = f"（使用位置：第{', '.join(map(str, usage_lines))}行）" if len(usage_lines) > 1 else ""
                
                taint_source = self.tainted_variables[ptr_name]
                self.error_reporter.add_memory_error(
                    line_num,
                    f"野指针问题：{taint_source}，变量 '{ptr_name}' 在多处被使用{usage_info}",
                    f"建议检查函数 {self.declared_pointers.get(ptr_name, {}).get('taint_source', 'unknown')} 的实现，确保返回有效指针",
                    line_content
                )
            return
        
        if is_declared_pointer and not is_allocated and not is_freed:
            # 使用作用域分析的结果
            if var_info['is_initialized'] and not var_info['is_static']:
                return
            
            # 错误聚合：记录使用位置，但只在第一次使用时报告
            if ptr_name not in self.pointer_usage_locations:
                self.pointer_usage_locations[ptr_name] = []
            self.pointer_usage_locations[ptr_name].append(line_num)
            
            # 只在第一次检测到该指针的问题时报告
            if ptr_name not in self.reported_pointers:
                self.reported_pointers.add(ptr_name)
                
                # 生成聚合的错误消息
                usage_lines = self.pointer_usage_locations[ptr_name]
                usage_info = f"（使用位置：第{', '.join(map(str, usage_lines))}行）" if len(usage_lines) > 1 else ""
                
                # 报告野指针问题
                if var_info['is_static']:
                    self.error_reporter.add_memory_error(
                        usage_lines[0],  # 使用第一次使用的行号
                        f"野指针问题：static指针 '{ptr_name}' 默认为NULL，多处使用将导致段错误{usage_info}",
                        f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof({var_info['type']})); 或添加NULL检查",
                        line_content.strip()
                    )
                else:
                    self.error_reporter.add_memory_error(
                        usage_lines[0],  # 使用第一次使用的行号
                        f"野指针问题：未初始化指针 '{ptr_name}' 在多处被使用{usage_info}",
                        f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof({var_info['type']})); 或 {ptr_name} = NULL;",
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
