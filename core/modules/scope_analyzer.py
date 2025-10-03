"""
作用域分析器 - 基于AST实现精确的作用域管理
解决同名变量覆盖问题，实现变量遮蔽(Variable Shadowing)的正确处理
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter


class ScopeInfo:
    """作用域信息"""
    def __init__(self, scope_type: str, start_line: int, end_line: int = -1):
        self.scope_type = scope_type  # 'global', 'function', 'block'
        self.start_line = start_line
        self.end_line = end_line
        self.variables: Dict[str, Dict] = {}  # 变量名 -> 变量信息
        self.parent_scope: Optional['ScopeInfo'] = None
        self.child_scopes: List['ScopeInfo'] = []


class ScopeAnalyzer:
    """作用域分析器 - 实现符号表栈"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.scope_stack: List[ScopeInfo] = []  # 符号表栈
        self.global_scope: Optional[ScopeInfo] = None
        self.current_scope: Optional[ScopeInfo] = None
        
        # 正则表达式模式
        self.patterns = {
            'function_def': re.compile(r'(\w+\s+)*(\w+)\s*\([^)]*\)\s*{', re.MULTILINE),
            'block_start': re.compile(r'{', re.MULTILINE),
            'block_end': re.compile(r'}', re.MULTILINE),
            'variable_declaration': re.compile(r'\b(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool|struct\s+\w+)\s+(\w+)\s*[;=]', re.MULTILINE),
            'pointer_declaration': re.compile(r'\b(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool|struct\s+\w+)\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
            'struct_pointer_declaration': re.compile(r'\bstruct\s+\w+\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
        }
    
    def analyze(self, parsed_data: Dict[str, List]) -> Dict[str, Dict]:
        """分析作用域并返回变量信息"""
        self._reset()
        self._build_scope_tree(parsed_data)
        self._populate_variables(parsed_data)
        return self._extract_variable_info()
    
    def _reset(self):
        """重置分析器状态"""
        self.scope_stack.clear()
        self.global_scope = None
        self.current_scope = None
    
    def _build_scope_tree(self, parsed_data: Dict[str, List]):
        """构建作用域树"""
        brace_stack = []  # 用于跟踪大括号嵌套
        function_stack = []  # 用于跟踪函数嵌套
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检测函数定义
            func_match = self.patterns['function_def'].search(line_content)
            if func_match:
                func_name = func_match.group(2)
                # 创建函数作用域
                func_scope = ScopeInfo('function', line_num)
                func_scope.variables['__function_name'] = {'name': func_name, 'type': 'function'}
                
                if not self.global_scope:
                    self.global_scope = ScopeInfo('global', 1)
                    self.scope_stack.append(self.global_scope)
                
                func_scope.parent_scope = self.current_scope
                if self.current_scope:
                    self.current_scope.child_scopes.append(func_scope)
                
                self.scope_stack.append(func_scope)
                self.current_scope = func_scope
                function_stack.append((func_name, line_num))
                continue
            
            # 检测块开始
            block_matches = self.patterns['block_start'].findall(line_content)
            for _ in block_matches:
                if not self.current_scope:
                    # 如果没有当前作用域，创建全局作用域
                    self.global_scope = ScopeInfo('global', line_num)
                    self.scope_stack.append(self.global_scope)
                    self.current_scope = self.global_scope
                
                # 创建块作用域
                block_scope = ScopeInfo('block', line_num)
                block_scope.parent_scope = self.current_scope
                self.current_scope.child_scopes.append(block_scope)
                
                self.scope_stack.append(block_scope)
                self.current_scope = block_scope
                brace_stack.append(line_num)
            
            # 检测块结束
            block_end_matches = self.patterns['block_end'].findall(line_content)
            for _ in block_end_matches:
                if brace_stack and self.current_scope:
                    # 结束当前作用域
                    self.current_scope.end_line = line_num
                    self.scope_stack.pop()
                    
                    if self.scope_stack:
                        self.current_scope = self.scope_stack[-1]
                    else:
                        self.current_scope = None
                    
                    brace_stack.pop()
        
        # 处理未结束的作用域
        while self.scope_stack:
            scope = self.scope_stack.pop()
            if scope.end_line == -1:
                scope.end_line = len(parsed_data['lines'])
    
    def _populate_variables(self, parsed_data: Dict[str, List]):
        """填充变量信息到作用域"""
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 找到包含当前行的作用域
            scope = self._find_scope_for_line(line_num)
            if not scope:
                continue
            
            # 检测变量声明
            self._detect_variable_declarations(line_content, line_num, scope)
            self._detect_pointer_declarations(line_content, line_num, scope)
            self._detect_struct_pointer_declarations(line_content, line_num, scope)
    
    def _find_scope_for_line(self, line_num: int) -> Optional[ScopeInfo]:
        """找到包含指定行的作用域"""
        def search_scope(scope: ScopeInfo) -> Optional[ScopeInfo]:
            if scope.start_line <= line_num <= scope.end_line:
                # 检查子作用域
                for child in scope.child_scopes:
                    result = search_scope(child)
                    if result:
                        return result
                return scope
            return None
        
        if self.global_scope:
            return search_scope(self.global_scope)
        return None
    
    def _detect_variable_declarations(self, line_content: str, line_num: int, scope: ScopeInfo):
        """检测变量声明"""
        matches = self.patterns['variable_declaration'].findall(line_content)
        for match in matches:
            static_qualifier, const_qualifier, var_type, var_name = match
            
            # 检查是否有初始化
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            var_info = {
                'name': var_name,
                'type': var_type,
                'line': line_num,
                'is_static': bool(static_qualifier),
                'is_const': bool(const_qualifier),
                'is_initialized': is_initialized,
                'is_pointer': False,
                'scope_level': len(self.scope_stack),
                'scope_type': scope.scope_type,
                'line_content': line_content.strip()
            }
            
            scope.variables[var_name] = var_info
    
    def _detect_pointer_declarations(self, line_content: str, line_num: int, scope: ScopeInfo):
        """检测指针声明"""
        matches = self.patterns['pointer_declaration'].findall(line_content)
        for match in matches:
            static_qualifier, const_qualifier, var_type, var_name = match
            
            # 检查是否有初始化
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            var_info = {
                'name': var_name,
                'type': var_type,
                'line': line_num,
                'is_static': bool(static_qualifier),
                'is_const': bool(const_qualifier),
                'is_initialized': is_initialized,
                'is_pointer': True,
                'scope_level': len(self.scope_stack),
                'scope_type': scope.scope_type,
                'line_content': line_content.strip()
            }
            
            scope.variables[var_name] = var_info
    
    def _detect_struct_pointer_declarations(self, line_content: str, line_num: int, scope: ScopeInfo):
        """检测结构体指针声明"""
        matches = self.patterns['struct_pointer_declaration'].findall(line_content)
        for match in matches:
            var_name = match
            
            # 检查是否有初始化
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            # 提取类型信息
            var_type = line_content.split('*')[0].strip()
            
            var_info = {
                'name': var_name,
                'type': var_type,
                'line': line_num,
                'is_static': False,
                'is_const': False,
                'is_initialized': is_initialized,
                'is_pointer': True,
                'scope_level': len(self.scope_stack),
                'scope_type': scope.scope_type,
                'line_content': line_content.strip()
            }
            
            scope.variables[var_name] = var_info
    
    def _extract_variable_info(self) -> Dict[str, Dict]:
        """提取所有变量信息"""
        all_variables = {}
        
        def collect_variables(scope: ScopeInfo):
            for var_name, var_info in scope.variables.items():
                if var_name != '__function_name':
                    # 添加作用域信息
                    var_info['scope_path'] = self._get_scope_path(scope)
                    all_variables[var_name] = var_info
            
            # 递归处理子作用域
            for child_scope in scope.child_scopes:
                collect_variables(child_scope)
        
        if self.global_scope:
            collect_variables(self.global_scope)
        
        return all_variables
    
    def _get_scope_path(self, scope: ScopeInfo) -> List[str]:
        """获取作用域路径"""
        path = []
        current = scope
        while current:
            if current.scope_type == 'function':
                func_name = current.variables.get('__function_name', {}).get('name', 'unknown')
                path.append(f"function:{func_name}")
            elif current.scope_type == 'block':
                path.append(f"block:{current.start_line}")
            elif current.scope_type == 'global':
                path.append("global")
            current = current.parent_scope
        
        return list(reversed(path))
    
    def find_variable_in_scope(self, var_name: str, line_num: int) -> Optional[Dict]:
        """在指定行找到变量的定义（考虑作用域）"""
        scope = self._find_scope_for_line(line_num)
        if not scope:
            return None
        
        # 从当前作用域向上搜索
        current = scope
        while current:
            if var_name in current.variables:
                return current.variables[var_name]
            current = current.parent_scope
        
        return None
