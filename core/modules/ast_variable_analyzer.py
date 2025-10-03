"""
基于AST的变量分析器 - 处理复杂的存储类说明符和变量状态
"""
import re
from typing import Dict, List, Set, Optional, Tuple
from utils.error_reporter import ErrorReporter

# C语言AST解析器
try:
    from pycparser import c_parser, c_ast, parse_file
    from pycparser.c_ast import *
    C_AST_AVAILABLE = True
except ImportError:
    C_AST_AVAILABLE = False
    print("警告: pycparser未安装，AST变量分析功能不可用")


class ASTVariableAnalyzer:
    """基于AST的变量分析器"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.declared_variables: Dict[str, Dict] = {}
        self.used_variables: Set[str] = set()
        self.current_function: Optional[str] = None
        
    def analyze_with_ast(self, file_content: str) -> List:
        """使用AST分析变量状态"""
        if not C_AST_AVAILABLE:
            return []
            
        self.error_reporter.clear_reports()
        self.declared_variables.clear()
        self.used_variables.clear()
        
        try:
            # 预处理C代码
            processed_content = self._preprocess_c_code(file_content)
            
            # 解析AST
            parser = c_parser.CParser()
            ast = parser.parse(processed_content)
            
            # 遍历AST
            self._visit_ast_node(ast)
            
            # 检测未初始化变量使用
            self._detect_uninitialized_usage()
            
        except Exception as e:
            # AST解析失败时，优雅地处理异常，不影响其他模块
            # print(f"[AST DEBUG] AST分析异常: {e}")
            pass  # 静默处理，避免输出错误信息
            
        return self.error_reporter.get_reports()
    
    def _preprocess_c_code(self, content: str) -> str:
        """预处理C代码，使其能被pycparser解析"""
        lines = content.split('\n')
        processed_lines = []
        in_main_function = False
        brace_count = 0
        
        for line in lines:
            # 移除注释
            line = re.sub(r'//.*$', '', line)
            line = re.sub(r'/\*.*?\*/', '', line)
            
            # 跳过所有预处理指令（pycparser不支持）
            if line.strip().startswith('#'):
                continue
            
            # 跳过空行
            if not line.strip():
                continue
            
            # 检测main函数开始
            if 'int main(' in line:
                in_main_function = True
                processed_lines.append(line)
                continue
            
            # 在main函数内部，跳过嵌套的函数定义（C语言不支持）
            if in_main_function:
                # 计算大括号层级
                brace_count += line.count('{') - line.count('}')
                
                # 检测嵌套函数定义并跳过
                if re.search(r'\w+\s+\w+\s*\([^)]*\)\s*{', line) and brace_count > 1:
                    # 这是一个嵌套函数定义，跳过整个函数
                    nested_brace_count = 1
                    continue
                
                # 如果不是嵌套函数定义，正常处理
                processed_lines.append(line)
                
                # 检测main函数结束
                if brace_count <= 0:
                    in_main_function = False
            else:
                # 在main函数外部，正常处理
                processed_lines.append(line)
        
        # 添加必要的类型声明（不使用#include，直接声明）
        header = """typedef int bool;
typedef unsigned long size_t;
int printf(const char *format, ...);
void *malloc(size_t size);
void free(void *ptr);
"""
        
        processed_code = header + '\n'.join(processed_lines)
        return processed_code
    
    def _visit_ast_node(self, node, parent=None):
        """递归访问AST节点"""
        if node is None:
            return
            
        # 处理函数定义
        if isinstance(node, FuncDef):
            self.current_function = node.decl.name
            self._analyze_function_params(node)
            
        # 处理变量声明
        elif isinstance(node, Decl):
            self._analyze_variable_declaration(node)
            
        # 处理变量使用
        elif isinstance(node, ID):
            self._analyze_variable_usage(node, parent)
            
        # 处理赋值
        elif isinstance(node, Assignment):
            self._analyze_assignment(node)
            
        # 处理指针解引用 - 暂时禁用，因为行号映射问题
        # elif isinstance(node, UnaryOp) and node.op == '*':
        #     self._analyze_pointer_dereference(node)
        
        # 递归访问子节点
        for child_name, child in node.children():
            self._visit_ast_node(child, node)
    
    def _analyze_variable_declaration(self, decl_node: Decl):
        """分析变量声明"""
        var_name = decl_node.name
        if not var_name:
            return
            
        # 获取存储类说明符
        storage_class = []
        if hasattr(decl_node, 'storage') and decl_node.storage:
            storage_class = decl_node.storage
            
        # 获取类型限定符
        type_quals = []
        if hasattr(decl_node.type, 'quals') and decl_node.type.quals:
            type_quals = decl_node.type.quals
            
        # 获取基本类型
        base_type = self._get_base_type(decl_node.type)
        
        # 检查是否有初始化
        is_initialized = decl_node.init is not None
        
        # 检查是否是指针
        is_pointer = self._is_pointer_type(decl_node.type)
        
        # static变量的特殊处理
        is_static = 'static' in storage_class
        is_const = 'const' in type_quals
        is_extern = 'extern' in storage_class
        
        # static变量默认初始化，但我们仍然要检查使用
        if is_static and not is_initialized:
            if is_pointer:
                # static指针默认为NULL，但仍然是未初始化的野指针
                is_initialized = False  # 对于指针，我们认为NULL也是未初始化
            else:
                # static非指针变量默认初始化为0，但标记为需要警告
                is_initialized = False  # 保持为False以便后续检测
        
        # extern变量不需要初始化检查
        if is_extern:
            is_initialized = True
            
        self.declared_variables[var_name] = {
            'type': base_type,
            'is_pointer': is_pointer,
            'is_static': is_static,
            'is_const': is_const,
            'is_extern': is_extern,
            'is_initialized': is_initialized,
            'storage_class': storage_class,
            'type_quals': type_quals,
            'line': getattr(decl_node, 'coord', None),
            'is_function_param': self.current_function is not None
        }
        
# print(f"[AST DEBUG] 声明变量: {var_name}, static: {is_static}, const: {is_const}, "
              # f"pointer: {is_pointer}, initialized: {is_initialized}")
    
    def _analyze_variable_usage(self, id_node: ID, parent):
        """分析变量使用"""
        var_name = id_node.name
        
        # 跳过函数名和关键字
        if var_name in ['printf', 'scanf', 'malloc', 'free', 'main', 'if', 'while', 'for', 
                       'return', 'true', 'false', 'NULL', 'sizeof']:
            return
            
        # 跳过函数调用中的函数名
        if isinstance(parent, FuncCall) and parent.name == id_node:
            return
            
        self.used_variables.add(var_name)
        
        # 检查是否是赋值的左侧（这种情况下是初始化，不是使用）
        if isinstance(parent, Assignment) and parent.lvalue == id_node:
            if var_name in self.declared_variables:
                self.declared_variables[var_name]['is_initialized'] = True
            return
            
# print(f"[AST DEBUG] 使用变量: {var_name} 在 {getattr(id_node, 'coord', 'unknown')}")
    
    def _analyze_assignment(self, assign_node: Assignment):
        """分析赋值语句"""
        # 如果左侧是变量，标记为已初始化
        if isinstance(assign_node.lvalue, ID):
            var_name = assign_node.lvalue.name
            if var_name in self.declared_variables:
                self.declared_variables[var_name]['is_initialized'] = True
                # print(f"[AST DEBUG] 变量 {var_name} 通过赋值初始化")
    
    def _analyze_pointer_dereference(self, unary_node: UnaryOp):
        """分析指针解引用"""
        if isinstance(unary_node.expr, ID):
            ptr_name = unary_node.expr.name
            
            if ptr_name in self.declared_variables:
                ptr_info = self.declared_variables[ptr_name]
                
                if ptr_info['is_pointer'] and not ptr_info['is_initialized']:
                    coord = getattr(unary_node, 'coord', None)
                    line_num = coord.line if coord else 0
                    
                    # 调试信息：检查行号是否正确
                    # print(f"[AST DEBUG] 检测到指针解引用: {ptr_name} 在行 {line_num}, coord: {coord}")
                    
                    if ptr_info['is_static']:
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"野指针解引用：static指针 '{ptr_name}' 默认为NULL，解引用将导致段错误",
                            f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof({ptr_info['type']}));",
                            f"*{ptr_name}"
                        )
                    else:
                        self.error_reporter.add_memory_error(
                            line_num,
                            f"野指针解引用：未初始化指针 '{ptr_name}' 被解引用",
                            f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof({ptr_info['type']}));",
                            f"*{ptr_name}"
                        )
    
    def _analyze_function_params(self, func_node: FuncDef):
        """分析函数参数"""
        if func_node.decl.type.args:
            for param in func_node.decl.type.args.params:
                if isinstance(param, Decl):
                    param_name = param.name
                    if param_name:
                        self.declared_variables[param_name] = {
                            'type': self._get_base_type(param.type),
                            'is_pointer': self._is_pointer_type(param.type),
                            'is_static': False,
                            'is_const': 'const' in getattr(param.type, 'quals', []),
                            'is_extern': False,
                            'is_initialized': True,  # 函数参数总是已初始化
                            'is_function_param': True
                        }
    
    def _detect_uninitialized_usage(self):
        """检测未初始化变量使用"""
        for var_name in self.used_variables:
            if var_name in self.declared_variables:
                var_info = self.declared_variables[var_name]
                
                # 跳过函数参数
                if var_info['is_function_param']:
                    continue
                    
                # 跳过extern变量
                if var_info['is_extern']:
                    continue
                    
                # 检查static变量的特殊情况
                if var_info['is_static'] and not var_info['is_pointer']:
                    # static非指针变量默认初始化为0，但使用未显式初始化的static变量是不好的实践
                    if not var_info['is_initialized']:
                        self.error_reporter.add_variable_error(
                            0,  # AST中获取准确行号比较复杂，这里简化
                            f"使用未显式初始化的static变量 '{var_name}'（虽然默认为0，但不是好的编程实践）",
                            f"建议显式初始化以提高代码清晰度：static {var_info['type']} {var_name} = 0;",
                            ""
                        )
                    continue
                
                # 检查未初始化使用
                if not var_info['is_initialized']:
                    self.error_reporter.add_variable_error(
                        0,
                        f"变量 '{var_name}' 在初始化前被使用",
                        f"建议在使用前初始化变量：{var_name} = 初始值;",
                        ""
                    )
    
    def _get_base_type(self, type_node) -> str:
        """获取基本类型名"""
        if isinstance(type_node, TypeDecl):
            return self._get_base_type(type_node.type)
        elif isinstance(type_node, PtrDecl):
            return self._get_base_type(type_node.type) + "*"
        elif isinstance(type_node, IdentifierType):
            return ' '.join(type_node.names)
        elif isinstance(type_node, Struct):
            return f"struct {type_node.name}" if type_node.name else "struct"
        else:
            return str(type(type_node).__name__)
    
    def _is_pointer_type(self, type_node) -> bool:
        """检查是否是指针类型"""
        if isinstance(type_node, PtrDecl):
            return True
        elif isinstance(type_node, TypeDecl):
            return self._is_pointer_type(type_node.type)
        return False
