"""
改进的变量状态监察官模块 - 修复误报和错误诊断问题
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter
from utils.code_parser import CCodeParser, VariableInfo


class ImprovedVariableStateModule:
    """改进的变量状态监察官模块"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.parser = CCodeParser()
        
        # 维护变量状态
        self.variable_states: Dict[str, Dict] = {}
        self.pointer_variables: Set[str] = set()  # 指针变量集合
        self.struct_members: Set[str] = set()    # 结构体成员集合
        self.function_params: Set[str] = set()    # 函数参数集合
        
        # 改进的正则表达式模式
        self.patterns = {
            'pointer_declaration': re.compile(r'\b(struct\s+\w+\s*\*|\w+\s*\*)\s+(\w+)', re.MULTILINE),
            'struct_member_access': re.compile(r'\b(\w+)\s*->\s*(\w+)', re.MULTILINE),  # ptr->member
            'struct_dot_access': re.compile(r'\b(\w+)\s*\.\s*(\w+)', re.MULTILINE),      # obj.member
            'assignment': re.compile(r'\b(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'malloc_assignment': re.compile(r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)', re.MULTILINE),
            'calloc_assignment': re.compile(r'\b(\w+)\s*=\s*calloc\s*\([^)]+\)', re.MULTILINE),
            'function_call': re.compile(r'\b(\w+)\s*\([^)]*\)', re.MULTILINE),
            'variable_use': re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析变量状态问题 - 改进版本"""
        self.error_reporter.clear_reports()
        
        # 重置状态
        self.variable_states.clear()
        self.pointer_variables.clear()
        self.struct_members.clear()
        self.function_params.clear()
        
        # 第一阶段：识别变量类型和状态
        self._identify_variable_types(parsed_data)
        
        # 第二阶段：追踪变量状态变化
        self._track_variable_states(parsed_data)
        
        # 第三阶段：检测真正的问题
        self._detect_real_issues(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _identify_variable_types(self, parsed_data: Dict[str, List]):
        """识别变量类型：指针、结构体成员、函数参数等"""
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 识别指针变量声明 - 改进版本
            # 匹配 struct Point* p1; 或 int* p1; 等模式
            pointer_patterns = [
                r'\bstruct\s+\w+\s*\*\s*(\w+)\s*;',  # struct Point* p1;
                r'\b(int|char|float|double|long|short|unsigned|signed|void|bool)\s*\*\s*(\w+)\s*;',  # int* p1;
                r'\b(\w+)\s*\*\s*(\w+)\s*;',  # 通用指针模式
            ]
            
            for i, pattern in enumerate(pointer_patterns):
                matches = re.findall(pattern, line_content)
                for match in matches:
                    if i == 0:  # struct Point* p1;
                        var_name = match
                    elif i == 1:  # int* p1;
                        var_name = match[1]
                    else:  # 通用指针模式
                        var_name = match[1]
                    
                    # 过滤掉明显不是变量的匹配
                    if var_name.isdigit() or len(var_name) == 1:
                        continue
                    
                    # print(f"[DEBUG] 识别到指针变量: {var_name} 在第{line_num}行")
                    self.pointer_variables.add(var_name)
                    self.variable_states[var_name] = {
                        'type': 'pointer',
                        'declared_line': line_num,
                        'is_initialized': False,
                        'is_function_param': False,
                        'points_to_struct': 'struct' in pattern
                    }
            
            # 识别函数参数
            func_match = re.search(r'\w+\s+(\w+)\s*\(([^)]*)\)', line_content)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                if params_str.strip():
                    # 提取参数名（跳过类型名）
                    params = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', params_str)
                    for param in params:
                        if param not in ['int', 'char', 'float', 'double', 'void', 'const', 'static', 'struct']:
                            self.function_params.add(param)
                            self.variable_states[param] = {
                                'type': 'parameter',
                                'declared_line': line_num,
                                'is_initialized': True,  # 函数参数被认为是已初始化的
                                'is_function_param': True
                            }
            
            # 识别普通变量声明
            var_decl_patterns = [
                (r'\b(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*=\s*([^;]+);', True),
                (r'\b(int|char|float|double|long|short|unsigned|signed|void|bool)\s+(\w+)\s*;', False),
            ]
            
            for pattern, is_initialized in var_decl_patterns:
                matches = re.findall(pattern, line_content)
                for match in matches:
                    if len(match) == 3:  # 带初始化
                        var_type, var_name, init_value = match
                    elif len(match) == 2:  # 无初始化
                        var_type, var_name = match
                    
                    if var_name not in self.variable_states:
                        self.variable_states[var_name] = {
                            'type': 'variable',
                            'declared_line': line_num,
                            'is_initialized': is_initialized,
                            'is_function_param': False,
                            'c_type': var_type.strip()
                        }
    
    def _track_variable_states(self, parsed_data: Dict[str, List]):
        """追踪变量状态变化"""
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 追踪赋值操作
            assignment_matches = self.patterns['assignment'].findall(line_content)
            for var_name, value in assignment_matches:
                if var_name in self.variable_states:
                    self.variable_states[var_name]['is_initialized'] = True
                    self.variable_states[var_name]['last_assigned_line'] = line_num
            
            # 追踪malloc/calloc赋值
            malloc_matches = self.patterns['malloc_assignment'].findall(line_content)
            for var_name in malloc_matches:
                if var_name in self.variable_states:
                    self.variable_states[var_name]['is_initialized'] = True
                    self.variable_states[var_name]['last_assigned_line'] = line_num
                    self.variable_states[var_name]['allocated_by'] = 'malloc'
                    self.variable_states[var_name]['has_allocated_memory'] = True
            
            calloc_matches = self.patterns['calloc_assignment'].findall(line_content)
            for var_name in calloc_matches:
                if var_name in self.variable_states:
                    self.variable_states[var_name]['is_initialized'] = True
                    self.variable_states[var_name]['last_assigned_line'] = line_num
                    self.variable_states[var_name]['allocated_by'] = 'calloc'
                    self.variable_states[var_name]['has_allocated_memory'] = True
            
            # 追踪声明中的malloc/calloc初始化
            # 匹配 struct Point* p1 = malloc(...); 模式
            decl_malloc_pattern = r'\b(\w+)\s*=\s*malloc\s*\([^)]+\)'
            decl_malloc_matches = re.findall(decl_malloc_pattern, line_content)
            for var_name in decl_malloc_matches:
                if var_name in self.variable_states:
                    self.variable_states[var_name]['is_initialized'] = True
                    self.variable_states[var_name]['has_allocated_memory'] = True
                    self.variable_states[var_name]['allocated_by'] = 'malloc'
            
            decl_calloc_pattern = r'\b(\w+)\s*=\s*calloc\s*\([^)]+\)'
            decl_calloc_matches = re.findall(decl_calloc_pattern, line_content)
            for var_name in decl_calloc_matches:
                if var_name in self.variable_states:
                    self.variable_states[var_name]['is_initialized'] = True
                    self.variable_states[var_name]['has_allocated_memory'] = True
                    self.variable_states[var_name]['allocated_by'] = 'calloc'
    
    def _detect_real_issues(self, parsed_data: Dict[str, List]):
        """检测真正的问题 - 避免误报"""
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 跳过注释和空行
            if line_content.strip().startswith('//') or line_content.strip().startswith('/*') or not line_content.strip():
                continue
            
            # 跳过变量声明行
            if ';' in line_content and any(keyword in line_content for keyword in ['int ', 'char ', 'float ', 'double ', 'bool ']):
                continue
            
            # 检测未初始化指针解引用
            self._detect_uninitialized_pointer_dereference(line_content, line_num)
            
            # 检测未初始化变量使用（排除结构体成员）
            self._detect_uninitialized_variable_use(line_content, line_num)
            
            # 检测基础野指针解引用（第57-60行类型的问题）
            self._detect_basic_wild_pointer_dereference(line_content, line_num)
    
    def _detect_uninitialized_pointer_dereference(self, line_content: str, line_num: int):
        """检测未初始化指针解引用 - 避免与内存安全卫士重复"""
        
        # 检测 ptr->member 模式
        struct_member_matches = self.patterns['struct_member_access'].findall(line_content)
        for ptr_name, member_name in struct_member_matches:
            if ptr_name in self.variable_states:
                var_state = self.variable_states[ptr_name]
                
                # 跳过函数参数
                if var_state.get('is_function_param', False):
                    continue
                
                # 跳过已通过malloc/calloc初始化的指针 - 这些由内存安全卫士处理
                if var_state.get('has_allocated_memory', False):
                    continue
                
                # 跳过已通过malloc/calloc初始化的指针（通过检查allocated_by字段）
                if var_state.get('allocated_by') in ['malloc', 'calloc']:
                    continue
                
                # 只报告变量状态相关的问题，避免与内存安全卫士重复
                # 检查指针是否未初始化
                if not var_state.get('is_initialized', False):
                    # 只报告变量状态问题，不报告内存安全问题
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"变量状态问题：未初始化指针 '{ptr_name}' 被解引用访问成员 '{member_name}'",
                        f"建议在使用前初始化指针：{ptr_name} = malloc(size); 或 {ptr_name} = NULL;",
                        line_content
                    )
            else:
                # 如果指针变量不在状态表中，检查是否在指针变量集合中
                if ptr_name in self.pointer_variables:
                    # 指针已声明但未初始化 - 这是变量状态问题
                    self.error_reporter.add_variable_error(
                        line_num,
                        f"变量状态问题：未初始化指针 '{ptr_name}' 被解引用访问成员 '{member_name}'",
                        f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof(struct Point)); 或 {ptr_name} = NULL;",
                        line_content
                    )
                else:
                    # 检查是否是已声明的指针（通过查找声明）
                    is_declared = self._is_pointer_declared(ptr_name, line_num)
                    if is_declared:
                        self.error_reporter.add_variable_error(
                            line_num,
                            f"变量状态问题：未初始化指针 '{ptr_name}' 被解引用访问成员 '{member_name}'",
                            f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof(struct Point)); 或 {ptr_name} = NULL;",
                            line_content
                        )
                    else:
                        self.error_reporter.add_variable_error(
                            line_num,
                            f"变量状态问题：未声明指针 '{ptr_name}' 被解引用",
                            f"建议在使用前声明并初始化指针：struct Point* {ptr_name} = malloc(sizeof(struct Point));",
                            line_content
                        )
    
    def _is_pointer_declared(self, var_name: str, current_line: int) -> bool:
        """检查变量是否在当前行之前被声明为指针"""
        # 这里需要访问解析数据，我们需要在调用时传递
        # 简化实现：检查是否在指针变量集合中
        return var_name in self.pointer_variables
    
    def _detect_basic_wild_pointer_dereference(self, line_content: str, line_num: int):
        """检测基础野指针解引用 - 专门检测第57-60行类型的问题"""
        
        # 检测 ptr->member 模式，专门针对基础野指针
        struct_member_pattern = r'\b(\w+)\s*->\s*(\w+)'
        struct_member_matches = re.findall(struct_member_pattern, line_content)
        
        for ptr_name, member_name in struct_member_matches:
            # 检查是否是已声明的指针
            if ptr_name in self.pointer_variables:
                # 检查是否已初始化
                if ptr_name in self.variable_states:
                    var_state = self.variable_states[ptr_name]
                    # 如果已通过malloc初始化，跳过
                    if var_state.get('has_allocated_memory', False) or var_state.get('allocated_by') in ['malloc', 'calloc']:
                        continue
                    # 如果已初始化，跳过
                    if var_state.get('is_initialized', False):
                        continue
                
                # 这是基础野指针解引用
                self.error_reporter.add_variable_error(
                    line_num,
                    f"基础野指针解引用：未初始化指针 '{ptr_name}' 被解引用访问成员 '{member_name}'",
                    f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof(struct Point)); 或 {ptr_name} = NULL;",
                    line_content
                )
    
    def _detect_uninitialized_variable_use(self, line_content: str, line_num: int):
        """检测未初始化变量使用 - 排除结构体成员"""
        
        # 提取所有标识符
        var_matches = self.patterns['variable_use'].findall(line_content)
        
        for var_name in var_matches:
            # 跳过关键字和函数名
            if var_name in ['printf', 'scanf', 'malloc', 'free', 'strlen', 'strcpy', 'strcmp', 
                           'main', 'if', 'while', 'for', 'return', 'true', 'false', 'NULL',
                           'sizeof', 'calloc', 'realloc']:
                continue
            
            # 跳过结构体成员访问中的成员名
            if self._is_struct_member_access(line_content, var_name):
                continue
            
            # 检查变量状态
            if var_name in self.variable_states:
                var_state = self.variable_states[var_name]
                
                # 跳过函数参数
                if var_state.get('is_function_param', False):
                    continue
                
                # 跳过已初始化的变量
                if var_state.get('is_initialized', False):
                    continue
                
                # 跳过指针变量（它们有专门的检测逻辑）
                if var_state.get('type') == 'pointer':
                    continue
                
                # 报告未初始化变量使用
                self.error_reporter.add_variable_error(
                    line_num,
                    f"变量 '{var_name}' 在初始化前被使用",
                    f"建议在使用前初始化变量：{var_name} = 初始值;",
                    line_content
                )
    
    def _is_struct_member_access(self, line_content: str, var_name: str) -> bool:
        """检查变量名是否是结构体成员访问的一部分"""
        
        # 检查是否是 ptr->member 中的 member
        if re.search(rf'\w+\s*->\s*{var_name}\b', line_content):
            return True
        
        # 检查是否是 obj.member 中的 member
        if re.search(rf'\w+\s*\.\s*{var_name}\b', line_content):
            return True
        
        return False
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "改进的变量状态监察官"
    
    def get_description(self) -> str:
        """获取模块描述"""
        return "检测变量未初始化即使用，避免误报结构体成员"
