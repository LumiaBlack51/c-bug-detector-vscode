"""
基于C语言抽象语法树的内存泄漏检测器
通过模拟C语言运行来跟踪内存分配和释放状态
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from utils.error_reporter import ErrorReporter

# C语言AST解析器
try:
    from pycparser import c_parser, c_ast, parse_file
    from pycparser.c_ast import *
    C_AST_AVAILABLE = True
except ImportError:
    C_AST_AVAILABLE = False
    print("警告: pycparser 未安装，AST分析功能不可用")


class MemoryState(Enum):
    """内存状态枚举"""
    UNALLOCATED = "未分配"
    ALLOCATED = "已分配"
    FREED = "已释放"
    UNKNOWN = "未知"


@dataclass
class MemoryBlock:
    """内存块信息"""
    variable_name: str
    allocation_line: int
    allocation_type: str  # malloc, calloc, realloc
    size_expr: str
    freed: bool = False
    freed_line: Optional[int] = None


@dataclass
class Variable:
    """变量信息"""
    name: str
    var_type: str
    declaration_line: int
    is_pointer: bool = False
    memory_block: Optional[MemoryBlock] = None
    scope_level: int = 0


class CMemorySimulator:
    """C语言内存模拟器"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.variables: Dict[str, Variable] = {}
        self.memory_blocks: List[MemoryBlock] = []
        self.scope_level = 0
        self.current_function = None
        
    def analyze(self, parsed_data: Dict[str, List]) -> List:
        """分析内存泄漏"""
        self.error_reporter.clear_reports()
        
        if not C_AST_AVAILABLE:
            return self._fallback_analysis(parsed_data)
        
        try:
            # 重建完整的C代码
            file_content = '\n'.join(parsed_data['lines'])
            
            # 预处理代码
            preprocessed_content = self._preprocess_c_code(file_content)
            
            if not preprocessed_content.strip():
                return self.error_reporter.get_reports()
            
            # 解析AST
            parser = c_parser.CParser()
            ast_root = parser.parse(preprocessed_content)
            
            # 遍历AST进行内存分析
            self._analyze_ast(ast_root)
            
            # 检查未释放的内存
            self._check_memory_leaks()
            
        except Exception as e:
            # print(f"[AST内存分析] 解析失败: {e}")  # 禁用调试输出
            return self._fallback_analysis(parsed_data)
        
        return self.error_reporter.get_reports()
    
    def _preprocess_c_code(self, content: str) -> str:
        """预处理C代码，使其能被pycparser解析"""
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # 移除预处理指令
            if line.strip().startswith('#'):
                continue
            
            # 处理特殊情况
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            processed_lines.append(line)
        
        # 添加必要的声明
        code = '\n'.join(processed_lines)
        
        # 添加函数声明（如果缺失）
        if 'printf' in code and '#include <stdio.h>' not in content:
            code = 'int printf(const char *, ...);\n' + code
        if 'malloc' in code and '#include <stdlib.h>' not in content:
            code = 'void *malloc(unsigned long);\nvoid free(void *);\nvoid *realloc(void *, unsigned long);\n' + code
        if 'strcpy' in code:
            code = 'char *strcpy(char *, const char *);\n' + code
        
        return code
    
    def _analyze_ast(self, node, parent_node=None):
        """递归分析AST节点"""
        if node is None:
            return
        
        # 处理不同类型的AST节点
        if isinstance(node, FuncDef):
            self._handle_function_definition(node)
        elif isinstance(node, Decl):
            self._handle_declaration(node)
        elif isinstance(node, Assignment):
            self._handle_assignment(node)
        elif isinstance(node, FuncCall):
            self._handle_function_call(node)
        elif isinstance(node, Compound):
            self._handle_compound(node)
        elif isinstance(node, If):
            self._handle_if_statement(node)
        elif isinstance(node, While) or isinstance(node, For):
            self._handle_loop(node)
        
        # 递归处理子节点
        for child_name, child in node.children():
            self._analyze_ast(child, node)
    
    def _handle_function_definition(self, node: FuncDef):
        """处理函数定义"""
        self.current_function = node.decl.name
        self.scope_level += 1
        
        # 处理函数体
        if node.body:
            self._analyze_ast(node.body, node)
        
        # 函数结束时检查局部变量的内存泄漏
        self._check_function_memory_leaks()
        self.scope_level -= 1
    
    def _handle_declaration(self, node: Decl):
        """处理变量声明"""
        var_name = node.name
        if not var_name:
            return
        
        # 确定变量类型
        var_type = self._get_type_name(node.type)
        is_pointer = self._is_pointer_type(node.type)
        
        # 获取行号
        line_num = getattr(node, 'coord', None)
        line_num = line_num.line if line_num else 0
        
        # 创建变量对象
        variable = Variable(
            name=var_name,
            var_type=var_type,
            declaration_line=line_num,
            is_pointer=is_pointer,
            scope_level=self.scope_level
        )
        
        self.variables[var_name] = variable
        
        # 检查初始化
        if node.init:
            self._handle_initialization(var_name, node.init, line_num)
    
    def _handle_assignment(self, node: Assignment):
        """处理赋值语句"""
        # 获取左值
        lvalue = self._get_variable_name(node.lvalue)
        if not lvalue:
            return
        
        # 获取行号
        line_num = getattr(node, 'coord', None)
        line_num = line_num.line if line_num else 0
        
        # 检查右值是否是内存分配
        if isinstance(node.rvalue, FuncCall):
            func_name = self._get_function_name(node.rvalue)
            if func_name in ['malloc', 'calloc', 'realloc']:
                self._handle_memory_allocation(lvalue, func_name, node.rvalue, line_num)
    
    def _handle_function_call(self, node: FuncCall):
        """处理函数调用"""
        func_name = self._get_function_name(node)
        if not func_name:
            return
        
        line_num = getattr(node, 'coord', None)
        line_num = line_num.line if line_num else 0
        
        if func_name == 'free':
            self._handle_memory_deallocation(node, line_num)
    
    def _handle_memory_allocation(self, var_name: str, func_name: str, node: FuncCall, line_num: int):
        """处理内存分配"""
        # 获取分配大小表达式
        size_expr = ""
        if node.args and len(node.args.exprs) > 0:
            size_expr = self._expr_to_string(node.args.exprs[0])
        
        # 创建内存块
        memory_block = MemoryBlock(
            variable_name=var_name,
            allocation_line=line_num,
            allocation_type=func_name,
            size_expr=size_expr
        )
        
        self.memory_blocks.append(memory_block)
        
        # 更新变量信息
        if var_name in self.variables:
            self.variables[var_name].memory_block = memory_block
    
    def _handle_memory_deallocation(self, node: FuncCall, line_num: int):
        """处理内存释放"""
        if not node.args or len(node.args.exprs) == 0:
            return
        
        # 获取要释放的变量名
        var_name = self._get_variable_name(node.args.exprs[0])
        if not var_name:
            return
        
        # 查找对应的内存块
        for memory_block in self.memory_blocks:
            if memory_block.variable_name == var_name and not memory_block.freed:
                memory_block.freed = True
                memory_block.freed_line = line_num
                break
    
    def _handle_initialization(self, var_name: str, init_node, line_num: int):
        """处理变量初始化"""
        if isinstance(init_node, FuncCall):
            func_name = self._get_function_name(init_node)
            if func_name in ['malloc', 'calloc', 'realloc']:
                # 获取malloc节点的实际行号
                malloc_line = getattr(init_node, 'coord', None)
                malloc_line = malloc_line.line if malloc_line else line_num
                self._handle_memory_allocation(var_name, func_name, init_node, malloc_line)
    
    def _handle_compound(self, node: Compound):
        """处理复合语句（作用域）"""
        self.scope_level += 1
        
        # 处理复合语句中的所有语句
        if node.block_items:
            for item in node.block_items:
                self._analyze_ast(item, node)
        
        self.scope_level -= 1
    
    def _handle_if_statement(self, node: If):
        """处理if语句"""
        # 分析条件表达式
        if node.cond:
            self._analyze_ast(node.cond, node)
        
        # 分析then分支
        if node.iftrue:
            self._analyze_ast(node.iftrue, node)
        
        # 分析else分支
        if node.iffalse:
            self._analyze_ast(node.iffalse, node)
    
    def _handle_loop(self, node):
        """处理循环语句"""
        # 分析循环体
        if hasattr(node, 'stmt') and node.stmt:
            self._analyze_ast(node.stmt, node)
    
    def _check_memory_leaks(self):
        """检查内存泄漏"""
        for memory_block in self.memory_blocks:
            if not memory_block.freed:
                self.error_reporter.add_memory_error(
                    memory_block.allocation_line,
                    f"变量 '{memory_block.variable_name}' 分配了内存但未释放，可能导致内存泄漏",
                    f"建议在适当位置添加 free({memory_block.variable_name}); 语句",
                    f"{memory_block.variable_name} = {memory_block.allocation_type}({memory_block.size_expr})"
                )
    
    def _check_function_memory_leaks(self):
        """检查函数级别的内存泄漏"""
        for memory_block in self.memory_blocks:
            if (not memory_block.freed and 
                memory_block.variable_name in self.variables and
                self.variables[memory_block.variable_name].scope_level == self.scope_level):
                
                self.error_reporter.add_memory_error(
                    memory_block.allocation_line,
                    f"函数内变量 '{memory_block.variable_name}' 分配了内存但在函数结束前未释放",
                    f"建议在函数结束前添加 free({memory_block.variable_name}); 语句",
                    f"{memory_block.variable_name} = {memory_block.allocation_type}({memory_block.size_expr})"
                )
    
    def _get_type_name(self, type_node) -> str:
        """获取类型名称"""
        if isinstance(type_node, TypeDecl):
            return self._get_type_name(type_node.type)
        elif isinstance(type_node, PtrDecl):
            return self._get_type_name(type_node.type) + "*"
        elif isinstance(type_node, IdentifierType):
            return " ".join(type_node.names)
        elif isinstance(type_node, Struct):
            return f"struct {type_node.name or 'anonymous'}"
        else:
            return "unknown"
    
    def _is_pointer_type(self, type_node) -> bool:
        """判断是否是指针类型"""
        return isinstance(type_node, PtrDecl)
    
    def _get_variable_name(self, node) -> Optional[str]:
        """从AST节点获取变量名"""
        if isinstance(node, ID):
            return node.name
        elif isinstance(node, StructRef):
            return self._get_variable_name(node.name)
        elif isinstance(node, ArrayRef):
            return self._get_variable_name(node.name)
        elif isinstance(node, UnaryOp) and node.op == '*':
            return self._get_variable_name(node.expr)
        return None
    
    def _get_function_name(self, node: FuncCall) -> Optional[str]:
        """获取函数名"""
        if isinstance(node.name, ID):
            return node.name.name
        return None
    
    def _expr_to_string(self, node) -> str:
        """将表达式节点转换为字符串"""
        if isinstance(node, Constant):
            return node.value
        elif isinstance(node, ID):
            return node.name
        elif isinstance(node, BinaryOp):
            left = self._expr_to_string(node.left)
            right = self._expr_to_string(node.right)
            return f"{left} {node.op} {right}"
        elif isinstance(node, FuncCall):
            func_name = self._get_function_name(node)
            return f"{func_name}(...)"
        else:
            return str(node)
    
    def _fallback_analysis(self, parsed_data: Dict[str, List]) -> List:
        """回退到基础分析方法"""
        # print("[AST内存分析] 使用回退分析方法")  # 禁用调试输出
        
        # 简单的malloc/free配对检查
        malloc_vars = set()
        freed_vars = set()
        
        for malloc_call in parsed_data.get('malloc_calls', []):
            var_name = malloc_call.get('variable')
            if var_name:
                malloc_vars.add(var_name)
        
        for free_call in parsed_data.get('free_calls', []):
            line_content = free_call.get('line_content', '')
            # 简单提取free中的变量名
            match = re.search(r'free\s*\(\s*(\w+)\s*\)', line_content)
            if match:
                freed_vars.add(match.group(1))
        
        # 检查未释放的变量
        for malloc_call in parsed_data.get('malloc_calls', []):
            var_name = malloc_call.get('variable')
            line_num = malloc_call.get('line')
            if var_name and var_name not in freed_vars:
                self.error_reporter.add_memory_error(
                    line_num,
                    f"变量 '{var_name}' 分配了内存但未释放，可能导致内存泄漏",
                    f"建议在适当位置添加 free({var_name}); 语句",
                    malloc_call.get('line_content', '')
                )
        
        return self.error_reporter.get_reports()
    
    def get_module_name(self) -> str:
        """Get module name"""
        return "AST Memory Leak Detector"
    
    def get_description(self) -> str:
        """Get module description"""
        return "AST-based memory leak detection, tracks memory allocation and deallocation"
