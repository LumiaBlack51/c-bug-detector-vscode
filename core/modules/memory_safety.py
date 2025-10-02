"""
内存安全卫士模块 - 检测内存泄漏、野指针、空指针解引用
"""
import re
from typing import Dict, List, Set
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo


class MemorySafetyModule:
    """内存安全卫士模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 维护变量状态哈希表
        self.variable_states: Dict[str, Dict] = {}
        self.malloced_variables: Set[str] = set()
        self.freed_variables: Set[str] = set()
        
        # 编译正则表达式模式
        self.patterns = {
            'malloc': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)', re.MULTILINE),
            'free': re.compile(r'\bfree\s*\([^)]*(\w+)[^)]*\)', re.MULTILINE),
            'pointer_use': re.compile(r'\*(\w+)', re.MULTILINE),
            'null_check': re.compile(r'\b(\w+)\s*==\s*NULL\b|\b(\w+)\s*!=\s*NULL\b', re.MULTILINE),
            'return_local_pointer': re.compile(r'\breturn\s+[^;]*\*[^;]*;', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析内存安全问题"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.variable_states.clear()
        self.malloced_variables.clear()
        self.freed_variables.clear()
        
        # 分析各种内存安全问题
        self._detect_memory_leaks(parsed_data)
        self._detect_wild_pointers(parsed_data)
        self._detect_null_pointer_dereference(parsed_data)
        self._detect_return_local_pointer(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _detect_memory_leaks(self, parsed_data: Dict[str, List]):
        """检测内存泄漏"""
        # 首先收集所有free调用
        freed_vars = set()
        for free_call in parsed_data['free_calls']:
            line_content = free_call['line_content']
            # 提取free中的变量名
            free_match = self.patterns['free'].search(line_content)
            if free_match:
                var_name = free_match.group(1)
                freed_vars.add(var_name)
        
        # 记录所有malloc的变量
        for malloc_call in parsed_data['malloc_calls']:
            var_name = malloc_call['variable']
            line_num = malloc_call['line']
            self.malloced_variables.add(var_name)
        
        # 检查每个malloc的变量是否都有对应的free
        for malloc_call in parsed_data['malloc_calls']:
            var_name = malloc_call['variable']
            line_num = malloc_call['line']
            
            # 只有当变量确实没有被释放时才报告内存泄漏
            if var_name not in freed_vars:
                self.error_reporter.add_memory_error(
                    line_num,
                    f"变量 '{var_name}' 分配了内存但未释放，可能导致内存泄漏",
                    "建议在适当位置添加 free({0}); 语句".format(var_name),
                    malloc_call['line_content']
                )
    
    def _detect_wild_pointers(self, parsed_data: Dict[str, List]):
        """检测野指针"""
        # 记录所有free的变量
        for free_call in parsed_data['free_calls']:
            line_content = free_call['line_content']
            line_num = free_call['line']
            
            # 提取free中的变量名
            free_match = self.patterns['free'].search(line_content)
            if free_match:
                var_name = free_match.group(1)
                self.freed_variables.add(var_name)
        
        # 检查free后是否还有使用
        for deref in parsed_data['pointer_dereferences']:
            ptr_name = deref['pointer']
            line_num = deref['line']
            
            if ptr_name in self.freed_variables:
                self.error_reporter.add_memory_error(
                    line_num,
                    f"指针 '{ptr_name}' 已被释放，但仍在被使用（野指针）",
                    "建议在free后设置指针为NULL：free(ptr); ptr = NULL;",
                    deref['line_content']
                )
        
        # 检查未初始化的指针使用
        for var in parsed_data['variables']:
            if var.is_pointer and not var.is_initialized:
                # 查找该指针的使用
                for deref in parsed_data['pointer_dereferences']:
                    if deref['pointer'] == var.name and deref['line'] > var.line_number:
                        self.error_reporter.add_memory_error(
                            deref['line'],
                            f"指针 '{var.name}' 未初始化就被解引用",
                            "建议在使用前初始化指针：ptr = NULL; 或 ptr = malloc(size);",
                            deref['line_content']
                        )
    
    def _detect_null_pointer_dereference(self, parsed_data: Dict[str, List]):
        """检测空指针解引用 - 改进版本"""
        # 检查指针解引用前是否有NULL检查
        for deref in parsed_data['pointer_dereferences']:
            ptr_name = deref['pointer']
            line_num = deref['line']
            line_content = deref['line_content']
            
            # 跳过指针初始化，只检查真正的解引用
            if self._is_pointer_initialization(line_content):
                print(f"[内存安全DEBUG] 跳过指针初始化: {line_content}")
                continue
            
            # 检查是否是真正的指针解引用
            if not self._is_real_pointer_dereference(line_content):
                print(f"[内存安全DEBUG] 跳过非解引用: {line_content}")
                continue
            
            # 跳过函数参数的解引用（减少误报）
            if self._is_function_parameter(ptr_name, parsed_data):
                print(f"[内存安全DEBUG] 跳过函数参数解引用: {ptr_name}")
                continue
            
            # 检查前面几行是否有NULL检查
            has_null_check = False
            for i in range(max(0, line_num - 5), line_num):
                if i < len(parsed_data['lines']):
                    line_content = parsed_data['lines'][i]
                    if self.patterns['null_check'].search(line_content):
                        has_null_check = True
                        break
            
            if not has_null_check:
                self.error_reporter.add_memory_error(
                    line_num,
                    f"解引用指针 '{ptr_name}' 前未进行NULL检查",
                    "建议添加NULL检查：if (ptr != NULL) { /* 使用ptr */ }",
                    line_content
                )
    
    def _is_function_parameter(self, ptr_name: str, parsed_data: Dict[str, List]) -> bool:
        """检查指针是否是函数参数"""
        # 遍历所有函数定义，检查参数列表
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 查找函数定义
            func_match = re.search(r'\w+\s+(\w+)\s*\(([^)]*)\)', line_content)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                
                # 检查参数列表中是否包含该指针
                if ptr_name in params_str:
                    # 进一步验证是否真的是参数名（而不是类型名）
                    param_pattern = rf'\b{ptr_name}\b'
                    if re.search(param_pattern, params_str):
                        return True
        
        return False
    
    def _is_pointer_initialization(self, line_content: str) -> bool:
        """检查是否是指针初始化"""
        # 检查是否是声明和初始化：int *ptr = &x;
        if re.search(r'\*\s*\w+\s*=\s*&', line_content):
            return True
        
        # 检查是否是字符串字面量初始化：const char *str = "hello";
        if re.search(r'\*\s*\w+\s*=\s*"[^"]*"', line_content):
            return True
        
        # 检查是否是malloc初始化：int *ptr = malloc(size);
        if re.search(r'\*\s*\w+\s*=\s*malloc', line_content):
            return True
        
        return False
    
    def _is_real_pointer_dereference(self, line_content: str) -> bool:
        """检查是否是真正的指针解引用"""
        # 检查是否是解引用操作：*ptr = value; 或 value = *ptr;
        if re.search(r'\*\s*\w+\s*[=<>!]', line_content) or re.search(r'[=<>!]\s*\*\s*\w+', line_content):
            return True
        
        # 检查是否是函数调用中的解引用：func(*ptr)
        if re.search(r'\(\s*\*\s*\w+\s*\)', line_content):
            return True
        
        return False
    
    def _detect_return_local_pointer(self, parsed_data: Dict[str, List]):
        """检测函数返回局部指针"""
        for func in parsed_data['functions']:
            if func.return_type and '*' in func.return_type:
                # 这是一个返回指针的函数
                func_start_line = func.line_number
                
                # 查找函数内的return语句
                for i in range(func_start_line, len(parsed_data['lines'])):
                    line_content = parsed_data['lines'][i]
                    if 'return' in line_content and '*' in line_content:
                        # 检查是否返回局部变量
                        if self.patterns['return_local_pointer'].search(line_content):
                            self.error_reporter.add_memory_error(
                                i + 1,
                                f"函数 '{func.name}' 返回局部指针，这是危险的",
                                "建议返回动态分配的内存或静态变量",
                                line_content
                            )
                        break
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "内存安全卫士"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测内存泄漏、野指针、空指针解引用等内存安全问题"
