"""
控制流图分析器 - 实现基于CFG的数据流分析
解决未初始化变量检测、死循环检测等复杂控制流问题
"""
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from utils.error_reporter import ErrorReporter


class BasicBlock:
    """基本块 - CFG中的节点"""
    def __init__(self, block_id: int, start_line: int, end_line: int):
        self.block_id = block_id
        self.start_line = start_line
        self.end_line = end_line
        self.instructions: List[str] = []
        self.predecessors: List['BasicBlock'] = []
        self.successors: List['BasicBlock'] = []
        
        # 数据流分析状态
        self.gen_set: Set[str] = set()  # 生成的变量定义
        self.kill_set: Set[str] = set()  # 杀死的变量定义
        self.in_set: Set[str] = set()    # 输入状态
        self.out_set: Set[str] = set()   # 输出状态
        
        # 变量状态追踪
        self.variable_states: Dict[str, str] = {}  # 变量名 -> 状态(UNINITIALIZED, INITIALIZED, MAYBE_UNINITIALIZED)


class ControlFlowGraph:
    """控制流图"""
    def __init__(self):
        self.blocks: List[BasicBlock] = []
        self.entry_block: Optional[BasicBlock] = None
        self.exit_block: Optional[BasicBlock] = None
        self.line_to_block: Dict[int, BasicBlock] = {}  # 行号到基本块的映射


class CFGAnalyzer:
    """控制流图分析器"""
    
    def __init__(self):
        self.error_reporter = ErrorReporter()
        
        # 正则表达式模式
        self.patterns = {
            'assignment': re.compile(r'^\s*(\w+)\s*=\s*([^;]+);', re.MULTILINE),
            'variable_use': re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'),
            'variable_declaration': re.compile(r'\b(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|bool|struct\s+\w+)\s+(\w+)\s*[;=]', re.MULTILINE),
            'pointer_declaration': re.compile(r'\b(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool|struct\s+\w+)\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
            'struct_pointer_declaration': re.compile(r'\bstruct\s+\w+\s*\*+\s*(\w+)\s*[;=]', re.MULTILINE),
            'struct_member_access': re.compile(r'\b(\w+)\s*->\s*(\w+)', re.MULTILINE),  # ptr->member
            'struct_dot_access': re.compile(r'\b(\w+)\s*\.\s*(\w+)', re.MULTILINE),    # struct.member
        }
        
        # 控制流关键字
        self.control_flow_keywords = {
            'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'goto'
        }
        
        # 分支关键字
        self.branch_keywords = {'if', 'else', 'while', 'for', 'do', 'switch'}
        
        # 循环关键字
        self.loop_keywords = {'while', 'for', 'do'}
    
    def analyze(self, parsed_data: Dict[str, List]) -> Dict[str, Any]:
        """分析控制流和数据流"""
        self._reset()
        
        # 构建控制流图
        cfg = self._build_control_flow_graph(parsed_data)
        
        # 执行数据流分析
        self._perform_data_flow_analysis(cfg, parsed_data)
        
        # 检测问题
        self._detect_uninitialized_variables(cfg, parsed_data)
        self._detect_dead_loops(cfg, parsed_data)
        self._detect_struct_member_access_issues(cfg, parsed_data)
        
        return {
            'cfg': cfg,
            'reports': self.error_reporter.get_reports()
        }
    
    def _reset(self):
        """重置分析器状态"""
        self.error_reporter.clear_reports()
    
    def _build_control_flow_graph(self, parsed_data: Dict[str, List]) -> ControlFlowGraph:
        """构建控制流图"""
        cfg = ControlFlowGraph()
        
        # 识别基本块
        basic_blocks = self._identify_basic_blocks(parsed_data)
        cfg.blocks = basic_blocks
        
        if basic_blocks:
            cfg.entry_block = basic_blocks[0]
            cfg.exit_block = basic_blocks[-1]
            
            # 建立行号到基本块的映射
            for block in basic_blocks:
                for line_num in range(block.start_line, block.end_line + 1):
                    cfg.line_to_block[line_num] = block
        
        # 建立基本块之间的连接
        self._connect_basic_blocks(cfg, parsed_data)
        
        return cfg
    
    def _identify_basic_blocks(self, parsed_data: Dict[str, List]) -> List[BasicBlock]:
        """识别基本块"""
        blocks = []
        current_block_start = 1
        block_id = 0
        
        for line_num, line_content in enumerate(parsed_data['lines'], 1):
            # 检查是否是基本块的结束点
            if self._is_basic_block_end(line_content, parsed_data, line_num):
                # 创建基本块
                if current_block_start <= line_num:
                    block = BasicBlock(block_id, current_block_start, line_num)
                    block.instructions = parsed_data['lines'][current_block_start-1:line_num]
                    blocks.append(block)
                    block_id += 1
                
                # 下一行开始新的基本块
                current_block_start = line_num + 1
        
        # 处理最后一个基本块
        if current_block_start <= len(parsed_data['lines']):
            block = BasicBlock(block_id, current_block_start, len(parsed_data['lines']))
            block.instructions = parsed_data['lines'][current_block_start-1:]
            blocks.append(block)
        
        return blocks
    
    def _is_basic_block_end(self, line_content: str, parsed_data: Dict[str, List], line_num: int) -> bool:
        """判断是否是基本块的结束点"""
        # 分支语句
        for keyword in self.branch_keywords:
            if re.search(rf'\b{keyword}\s*\(', line_content):
                return True
        
        # 跳转语句
        if re.search(r'\b(break|continue|return|goto)\b', line_content):
            return True
        
        # 标签
        if re.search(r'^\s*\w+\s*:', line_content):
            return True
        
        # 函数调用（可能改变控制流）
        if re.search(r'\b\w+\s*\([^)]*\)\s*;', line_content):
            # 检查是否是可能改变控制流的函数
            if re.search(r'\b(exit|abort|longjmp)\s*\(', line_content):
                return True
        
        return False
    
    def _connect_basic_blocks(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """建立基本块之间的连接"""
        for i, block in enumerate(cfg.blocks):
            # 获取基本块的最后一行
            if block.instructions:
                last_line = block.instructions[-1]
                
                # 检查是否是分支语句
                if self._is_branch_statement(last_line):
                    # 查找分支目标
                    targets = self._find_branch_targets(last_line, cfg, block.end_line)
                    for target in targets:
                        if target:
                            block.successors.append(target)
                            target.predecessors.append(block)
                else:
                    # 顺序执行到下一个基本块
                    if i + 1 < len(cfg.blocks):
                        next_block = cfg.blocks[i + 1]
                        block.successors.append(next_block)
                        next_block.predecessors.append(block)
    
    def _is_branch_statement(self, line_content: str) -> bool:
        """判断是否是分支语句"""
        for keyword in self.branch_keywords:
            if re.search(rf'\b{keyword}\s*\(', line_content):
                return True
        return False
    
    def _find_branch_targets(self, line_content: str, cfg: ControlFlowGraph, current_line: int) -> List[Optional[BasicBlock]]:
        """查找分支目标"""
        targets = []
        
        # if语句：true分支和false分支
        if re.search(r'\bif\s*\(', line_content):
            # true分支：下一个基本块
            # false分支：跳过if块后的基本块
            if current_line + 1 in cfg.line_to_block:
                targets.append(cfg.line_to_block[current_line + 1])
            # 简化处理，假设false分支是下一个基本块
            targets.append(None)
        
        # while/for循环：循环体和循环后
        elif re.search(r'\b(while|for)\s*\(', line_content):
            # 循环体：下一个基本块
            if current_line + 1 in cfg.line_to_block:
                targets.append(cfg.line_to_block[current_line + 1])
            # 循环后：跳过循环体后的基本块
            targets.append(None)
        
        # return语句：函数出口
        elif re.search(r'\breturn\b', line_content):
            targets.append(cfg.exit_block)
        
        return targets
    
    def _perform_data_flow_analysis(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """执行数据流分析"""
        # 初始化变量状态
        self._initialize_variable_states(cfg, parsed_data)
        
        # 迭代求解数据流方程
        self._solve_data_flow_equations(cfg)
    
    def _initialize_variable_states(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """初始化变量状态"""
        for block in cfg.blocks:
            block.variable_states = {}
            
            for line_num in range(block.start_line, block.end_line + 1):
                if line_num <= len(parsed_data['lines']):
                    line_content = parsed_data['lines'][line_num - 1]
                    
                    # 识别变量声明
                    self._analyze_variable_declarations(line_content, line_num, block)
                    
                    # 识别变量赋值
                    self._analyze_variable_assignments(line_content, line_num, block)
    
    def _analyze_variable_declarations(self, line_content: str, line_num: int, block: BasicBlock):
        """分析变量声明"""
        # 基本类型变量
        matches = self.patterns['variable_declaration'].findall(line_content)
        for match in matches:
            static_qualifier, const_qualifier, var_type, var_name = match
            
            # 检查是否有初始化
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            if is_initialized:
                block.variable_states[var_name] = 'INITIALIZED'
            else:
                block.variable_states[var_name] = 'UNINITIALIZED'
        
        # 指针变量
        pointer_matches = self.patterns['pointer_declaration'].findall(line_content)
        for match in pointer_matches:
            static_qualifier, const_qualifier, var_type, var_name = match
            
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            if is_initialized:
                block.variable_states[var_name] = 'INITIALIZED'
            else:
                block.variable_states[var_name] = 'UNINITIALIZED'
        
        # 结构体指针
        struct_matches = self.patterns['struct_pointer_declaration'].findall(line_content)
        for var_name in struct_matches:
            is_initialized = '=' in line_content and line_content.index('=') > line_content.index(var_name)
            
            if is_initialized:
                block.variable_states[var_name] = 'INITIALIZED'
            else:
                block.variable_states[var_name] = 'UNINITIALIZED'
    
    def _analyze_variable_assignments(self, line_content: str, line_num: int, block: BasicBlock):
        """分析变量赋值"""
        matches = self.patterns['assignment'].findall(line_content)
        for var_name, value in matches:
            # 标记变量为已初始化
            block.variable_states[var_name] = 'INITIALIZED'
    
    def _solve_data_flow_equations(self, cfg: ControlFlowGraph):
        """求解数据流方程"""
        # 初始化
        for block in cfg.blocks:
            block.in_set = set()
            block.out_set = set()
        
        # 迭代求解
        changed = True
        iteration = 0
        max_iterations = 100  # 防止无限循环
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            for block in cfg.blocks:
                # 计算输入集合：所有前驱基本块输出集合的并集
                old_in = block.in_set.copy()
                block.in_set = set()
                
                for pred in block.predecessors:
                    block.in_set.update(pred.out_set)
                
                # 计算输出集合：输入集合 - 杀死集合 + 生成集合
                old_out = block.out_set.copy()
                block.out_set = (block.in_set - block.kill_set) | block.gen_set
                
                # 检查是否发生变化
                if old_in != block.in_set or old_out != block.out_set:
                    changed = True
    
    def _detect_uninitialized_variables(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """检测未初始化变量使用"""
        for block in cfg.blocks:
            for line_num in range(block.start_line, block.end_line + 1):
                if line_num <= len(parsed_data['lines']):
                    line_content = parsed_data['lines'][line_num - 1]
                    
                    # 查找变量使用
                    var_uses = self.patterns['variable_use'].findall(line_content)
                    
                    for var_name in var_uses:
                        # 跳过关键字和函数名
                        if (var_name in self.control_flow_keywords or
                            var_name.isdigit() or
                            len(var_name) <= 1):
                            continue
                        
                        # 检查变量状态
                        if self._is_variable_uninitialized(var_name, block, cfg):
                            self.error_reporter.add_variable_error(
                                line_num,
                                f"使用未初始化的变量 '{var_name}'",
                                f"建议在使用前初始化变量：{var_name} = 0; // 或适当的初始值",
                                line_content
                            )
    
    def _is_variable_uninitialized(self, var_name: str, block: BasicBlock, cfg: ControlFlowGraph) -> bool:
        """检查变量是否未初始化"""
        # 检查当前基本块中的变量状态
        if var_name in block.variable_states:
            return block.variable_states[var_name] == 'UNINITIALIZED'
        
        # 检查输入集合中是否包含该变量的定义
        for var_def in block.in_set:
            if var_def.startswith(f"{var_name}:"):
                # 解析变量定义状态
                parts = var_def.split(':')
                if len(parts) >= 2:
                    state = parts[1]
                    return state == 'UNINITIALIZED'
        
        return False
    
    def _detect_dead_loops(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """检测死循环"""
        for block in cfg.blocks:
            for line_num in range(block.start_line, block.end_line + 1):
                if line_num <= len(parsed_data['lines']):
                    line_content = parsed_data['lines'][line_num - 1]
                    
                    # 检测无限循环
                    if self._is_infinite_loop(line_content, parsed_data, line_num):
                        self.error_reporter.add_control_flow_error(
                            line_num,
                            f"检测到可能的无限循环",
                            f"建议添加循环退出条件或break语句",
                            line_content
                        )
    
    def _is_infinite_loop(self, line_content: str, parsed_data: Dict[str, List], line_num: int) -> bool:
        """判断是否是无限循环"""
        # 检测 for(;;) 模式
        if re.search(r'\bfor\s*\(\s*;\s*;\s*\)', line_content):
            return True
        
        # 检测 while(1) 模式
        if re.search(r'\bwhile\s*\(\s*1\s*\)', line_content):
            return True
        
        # 检测 do-while 循环中的无限循环
        if re.search(r'\bdo\s*\{', line_content):
            # 查找对应的while条件
            brace_count = 0
            for i in range(line_num, len(parsed_data['lines'])):
                current_line = parsed_data['lines'][i]
                brace_count += current_line.count('{') - current_line.count('}')
                
                if brace_count == 0 and 'while' in current_line:
                    # 检查while条件
                    if re.search(r'\bwhile\s*\(\s*1\s*\)', current_line):
                        return True
                    break
        
        return False
    
    def _detect_struct_member_access_issues(self, cfg: ControlFlowGraph, parsed_data: Dict[str, List]):
        """检测结构体成员访问问题"""
        for block in cfg.blocks:
            for line_num in range(block.start_line, block.end_line + 1):
                if line_num <= len(parsed_data['lines']):
                    line_content = parsed_data['lines'][line_num - 1]
                    
                    # 检测结构体指针成员访问
                    struct_ptr_matches = self.patterns['struct_member_access'].findall(line_content)
                    for ptr_name, member_name in struct_ptr_matches:
                        if self._is_variable_uninitialized(ptr_name, block, cfg):
                            self.error_reporter.add_memory_error(
                                line_num,
                                f"通过未初始化的指针 '{ptr_name}' 访问结构体成员 '{member_name}'",
                                f"建议在使用前初始化指针：{ptr_name} = malloc(sizeof(struct)); 或 {ptr_name} = NULL;",
                                line_content
                            )
                    
                    # 检测结构体成员访问
                    struct_matches = self.patterns['struct_dot_access'].findall(line_content)
                    for struct_name, member_name in struct_matches:
                        if self._is_variable_uninitialized(struct_name, block, cfg):
                            self.error_reporter.add_variable_error(
                                line_num,
                                f"通过未初始化的结构体 '{struct_name}' 访问成员 '{member_name}'",
                                f"建议在使用前初始化结构体：{struct_name} = {{0}}; // 或适当的初始值",
                                line_content
                            )
