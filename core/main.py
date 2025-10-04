"""
C语言Bug检测器主程序
整合所有检测模块，提供统一的检测接口
"""
import os
import sys
import argparse
import json
from typing import List, Dict, Any
from colorama import init, Fore, Style

# 强制设置UTF-8编码
import io
import os
# 设置环境变量强制UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
# 重新包装标准输出和错误输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 初始化colorama
init()

# 导入检测模块
from modules.memory_safety import MemorySafetyModule
from modules.ast_memory_tracker import CMemorySimulator
from modules.variable_state import VariableStateModule
from modules.variable_state_improved import ImprovedVariableStateModule
from modules.memory_safety_improved import ImprovedMemorySafetyModule
from modules.standard_library import StandardLibraryModule
from modules.numeric_control_flow import NumericControlFlowModule
from modules.libclang_printf_detector import LibClangPrintfDetector
from modules.libclang_analyzer import LibClangAnalyzer
from modules.libclang_semantic_analyzer import LibClangSemanticAnalyzer
from modules.enhanced_memory_safety import EnhancedMemorySafetyModule

# 导入工具类
from utils.error_reporter import ErrorReporter, BugReport
from utils.report_generator import ReportGenerator
from utils.issue import Issue
from utils.code_parser import CCodeParser


class CBugDetector:
    """C语言Bug检测器主类"""
    
    def __init__(self):
        self.parser = CCodeParser()
        self.error_reporter = ErrorReporter()
        
        # 初始化所有检测模块
        self.modules = {
            'ast_memory_tracker': CMemorySimulator(),
            'memory_safety': ImprovedMemorySafetyModule(),
            'variable_state': ImprovedVariableStateModule(),
            'standard_library': StandardLibraryModule(),
            'numeric_control_flow': NumericControlFlowModule(),
            'libclang_analyzer': LibClangAnalyzer(),
            'libclang_printf': LibClangPrintfDetector(),
            'libclang_semantic': LibClangSemanticAnalyzer(),
            'enhanced_memory_safety': EnhancedMemorySafetyModule(),
        }
        
        # 模块启用状态
        self.module_enabled = {
            'ast_memory_tracker': True,
            'memory_safety': True,  # 启用改进的内存检测器
            'variable_state': False,  # 禁用旧的变量状态检测器
            'standard_library': False,  # 禁用旧的printf检测器
            'numeric_control_flow': True,
            'libclang_analyzer': True,  # 默认启用libclang分析器
            'libclang_printf': True,  # 启用新的libclang printf检测器
            'libclang_semantic': False,  # 暂时禁用语义分析器（有误报问题）
            'enhanced_memory_safety': True,  # 启用增强内存安全模块（使用正确行号映射）
        }
    
    def analyze_file_new(self, file_path: str) -> List[Issue]:
        """Analyze a single C file - using new architecture"""
        print(f"{Fore.CYAN}Analyzing file: {file_path}{Style.RESET_ALL}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: File {file_path} does not exist{Style.RESET_ALL}")
            return []
        
        # Check file extension
        if not file_path.endswith('.c'):
            print(f"{Fore.YELLOW}Warning: File {file_path} is not a C file (.c){Style.RESET_ALL}")
        
        try:
            # Parse C code
            parsed_data = self.parser.parse_file(file_path)
            if not parsed_data:
                print(f"{Fore.RED}Error: Cannot parse file {file_path}{Style.RESET_ALL}")
                return []
            
            # 清空之前的报告
            self.error_reporter.clear_reports()
            
            # 运行所有启用的模块并收集问题
            all_issues = []
            for module_name, module in self.modules.items():
                if self.module_enabled[module_name]:
                    print(f"{Fore.GREEN}Running module: {module.get_module_name()}{Style.RESET_ALL}")
                    try:
                        # libclang分析器、printf检测器、语义分析器和增强内存安全模块使用analyze_file方法
                        if module_name in ['libclang_analyzer', 'libclang_printf', 'libclang_semantic', 'enhanced_memory_safety']:
                            if module_name == 'enhanced_memory_safety':
                                # enhanced_memory_safety返回Issue对象
                                issues = module.analyze_file(file_path)
                            else:
                                # 其他模块返回BugReport对象，需要转换
                                reports = module.analyze_file(file_path)
                                issues = []
                                for report in reports:
                                    issue = Issue(
                                        issue_type=report.error_type,
                                        severity=report.severity,
                                        description=report.message,
                                        suggestion=report.suggestion,
                                        line_number=report.line_number,
                                        variable_name=report.variable_name,
                                        module_name=report.module_name,
                                        error_category=report.error_category,
                                        code_snippet=report.code_snippet
                                    )
                                    issues.append(issue)
                            all_issues.extend(issues)
                        else:
                            # 为其他模块设置文件路径，用于代码片段提取
                            if hasattr(module, 'error_reporter'):
                                module.error_reporter.current_file = file_path
                            reports = module.analyze(parsed_data)
                            # 将BugReport转换为Issue对象
                            for report in reports:
                                issue = Issue(
                                    issue_type=report.error_type,
                                    severity=report.severity,
                                    description=report.message,
                                    suggestion=report.suggestion,
                                    line_number=report.line_number,
                                    variable_name=report.variable_name,
                                    module_name=report.module_name,
                                    error_category=report.error_category,
                                    code_snippet=report.code_snippet
                                )
                                all_issues.append(issue)
                    except Exception as e:
                        print(f"{Fore.RED}模块 {module_name} 运行出错: {e}{Style.RESET_ALL}")
            
            # 按行号排序
            all_issues.sort(key=lambda x: x.line_number)
            
            return all_issues
            
        except Exception as e:
            print(f"{Fore.RED}分析文件时出错: {e}{Style.RESET_ALL}")
            return []
    
    def analyze_file(self, file_path: str) -> List[BugReport]:
        """Analyze a single C file"""
        print(f"{Fore.CYAN}Analyzing file: {file_path}{Style.RESET_ALL}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: File {file_path} does not exist{Style.RESET_ALL}")
            return []
        
        # Check file extension
        if not file_path.endswith('.c'):
            print(f"{Fore.YELLOW}Warning: File {file_path} is not a C file (.c){Style.RESET_ALL}")
        
        try:
            # Parse C code
            parsed_data = self.parser.parse_file(file_path)
            if not parsed_data:
                print(f"{Fore.RED}Error: Cannot parse file {file_path}{Style.RESET_ALL}")
                return []
            
            # 清空之前的报告
            self.error_reporter.clear_reports()
            
            # 运行所有启用的模块并收集报告
            all_reports = []
            for module_name, module in self.modules.items():
                if self.module_enabled[module_name]:
                    print(f"{Fore.GREEN}Running module: {module.get_module_name()}{Style.RESET_ALL}")
                    try:
                        # libclang分析器、printf检测器和语义分析器使用analyze_file方法
                        if module_name in ['libclang_analyzer', 'libclang_printf', 'libclang_semantic']:
                            reports = module.analyze_file(file_path)
                        else:
                            # 为其他模块设置文件路径，用于代码片段提取
                            if hasattr(module, 'error_reporter'):
                                module.error_reporter.current_file = file_path
                            reports = module.analyze(parsed_data)
                        all_reports.extend(reports)
                    except Exception as e:
                        print(f"{Fore.RED}模块 {module_name} 运行出错: {e}{Style.RESET_ALL}")
            
            # Deduplication processing
            deduplicated_reports = self._deduplicate_reports(all_reports)
            
            # Add to error reporter
            for report in deduplicated_reports:
                self.error_reporter.add_report(report)
            
            return deduplicated_reports
            
        except Exception as e:
            print(f"{Fore.RED}Error analyzing file: {e}{Style.RESET_ALL}")
            return []
    
    def analyze_file_quiet(self, file_path: str) -> List[BugReport]:
        """安静模式分析单个C文件（不输出调试信息）"""
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return []
        
        # 检查文件扩展名
        if not file_path.endswith('.c'):
            pass  # 静默跳过警告
        
        try:
            # 解析C代码
            parsed_data = self.parser.parse_file(file_path)
            if not parsed_data:
                return []
            
            # 获取所有报告
            all_reports = []
            
            # 遍历所有启用的检测模块
            for module_name, module in self.modules.items():
                if self.module_enabled[module_name]:
                    try:
                        # libclang分析器、printf检测器和语义分析器使用analyze_file方法
                        if module_name in ['libclang_analyzer', 'libclang_printf', 'libclang_semantic']:
                            module_reports = module.analyze_file(file_path)
                        else:
                            module_reports = module.analyze(parsed_data)
                        all_reports.extend(module_reports)
                    except Exception as e:
                        pass  # 静默忽略模块错误
            
            # 去重
            seen = set()
            deduplicated_reports = []
            for report in all_reports:
                report_key = (report.line_number, report.error_type.value, report.message)
                if report_key not in seen:
                    seen.add(report_key)
                    deduplicated_reports.append(report)
            
            # 添加到错误报告器
            for report in deduplicated_reports:
                self.error_reporter.add_report(report)
            
            return deduplicated_reports
            
        except Exception as e:
            return []
    
    def _deduplicate_reports(self, reports: List[BugReport]) -> List[BugReport]:
        """去重报告 - 消除来自不同模块的重复报告"""
        if not reports:
            return []
        
        # 第一步：按变量名分组，用于智能过滤
        var_reports = {}  # {variable_name: [reports]}
        for report in reports:
            var_name = self._extract_variable_name(report.message)
            if var_name:
                if var_name not in var_reports:
                    var_reports[var_name] = []
                var_reports[var_name].append(report)
        
        # 第二步：对每个变量，过滤掉低优先级的报告
        filtered_reports = []
        for var_name, var_report_list in var_reports.items():
            # 检查是否同时有内存泄漏和NULL检查警告
            has_memory_leak = any('未释放' in r.message or 'memory leak' in r.message.lower() or '泄漏' in r.message 
                                 for r in var_report_list)
            
            for report in var_report_list:
                # 如果存在内存泄漏，跳过NULL检查警告（降低噪音）
                if has_memory_leak and ('未检查返回值' in report.message or 'NULL检查' in report.message):
                    continue
                filtered_reports.append(report)
        
        # 添加没有变量名的报告
        no_var_reports = [r for r in reports if not self._extract_variable_name(r.message)]
        filtered_reports.extend(no_var_reports)
        
        # 第三步：使用原有去重逻辑
        seen_reports = {}
        deduplicated = []
        
        for report in filtered_reports:
            var_name = self._extract_variable_name(report.message)
            report_key = f"{report.line_number}_{report.error_type.value}_{var_name}"
            
            if report_key not in seen_reports:
                seen_reports[report_key] = report
                deduplicated.append(report)
            else:
                existing_report = seen_reports[report_key]
                if self._is_more_specific_report(report, existing_report):
                    deduplicated.remove(existing_report)
                    deduplicated.append(report)
                    seen_reports[report_key] = report
        
        return deduplicated
    
    def _extract_variable_name(self, message: str) -> str:
        """从错误消息中提取变量名"""
        import re
        
        # 匹配中英文的变量名模式
        patterns = [
            r"变量 '([^']+)'",
            r"指针 '([^']+)'",
            r"解引用未初始化指针 '([^']+)'",
            r"未初始化指针 '([^']+)'",
            r"未声明指针 '([^']+)'",
            r"variable '([^']+)'",
            r"pointer '([^']+)'",
            r"Variable '([^']+)'",
            r"Pointer '([^']+)'"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return ""
    
    def _is_more_specific_report(self, report1: BugReport, report2: BugReport) -> bool:
        """判断哪个报告更具体"""
        # Memory Safety Guard reports are usually more specific than Variable State Inspector
        if "Memory Safety" in report1.module_name and "Variable State" in report2.module_name:
            return True
        elif "Variable State" in report1.module_name and "Memory Safety" in report2.module_name:
            return False
        
        # 中文模块名兼容
        if "内存安全" in report1.module_name and "变量状态" in report2.module_name:
            return True
        elif "变量状态" in report1.module_name and "内存安全" in report2.module_name:
            return False
        
        # If message lengths differ, choose the longer one (usually more specific)
        if len(report1.message) != len(report2.message):
            return len(report1.message) > len(report2.message)
        
        # Default: choose the first one
        return False
    
    def analyze_directory(self, directory_path: str) -> Dict[str, List[BugReport]]:
        """Analyze all C files in a directory"""
        print(f"{Fore.CYAN}Analyzing directory: {directory_path}{Style.RESET_ALL}")
        
        if not os.path.exists(directory_path):
            print(f"{Fore.RED}Error: Directory {directory_path} does not exist{Style.RESET_ALL}")
            return {}
        
        results = {}
        
        # 遍历目录中的所有C文件
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.c'):
                    file_path = os.path.join(root, file)
                    reports = self.analyze_file(file_path)
                    if reports:
                        results[file_path] = reports
        
        return results
    
    def enable_module(self, module_name: str):
        """启用指定模块"""
        if module_name in self.modules:
            self.module_enabled[module_name] = True
            print(f"{Fore.GREEN}已启用模块: {self.modules[module_name].get_module_name()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}错误: 模块 {module_name} 不存在{Style.RESET_ALL}")
    
    def disable_module(self, module_name: str):
        """禁用指定模块"""
        if module_name in self.modules:
            self.module_enabled[module_name] = False
            print(f"{Fore.YELLOW}⚠️  已禁用模块: {self.modules[module_name].get_module_name()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}错误: 模块 {module_name} 不存在{Style.RESET_ALL}")
    
    def list_modules(self):
        """列出所有可用模块"""
        print(f"{Fore.CYAN}可用模块列表:{Style.RESET_ALL}")
        print("=" * 50)
        for module_name, module in self.modules.items():
            status = "启用" if self.module_enabled[module_name] else "禁用"
            print(f"{module_name}: {module.get_module_name()} - {status}")
            print(f"  描述: {module.get_description()}")
            print()
    
    def generate_report(self, reports: List[BugReport], output_format: str = 'text') -> str:
        """生成检测报告"""
        if output_format == 'text':
            return self.error_reporter.format_all_reports()
        elif output_format == 'json':
            import json
            report_data = []
            for report in reports:
                report_data.append({
                    'line_number': report.line_number,
                    'error_type': report.error_type.value,
                    'severity': report.severity.value,
                    'message': report.message,
                    'suggestion': report.suggestion,
                    'code_snippet': report.code_snippet,
                    'module_name': report.module_name
                })
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        else:
            return "不支持的输出格式"
    
    def save_report(self, reports: List[BugReport], output_file: str, output_format: str = 'text'):
        """保存检测报告到文件"""
        report_content = self.generate_report(reports, output_format)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"{Fore.GREEN}报告已保存到: {output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}保存报告时出错: {e}{Style.RESET_ALL}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='C语言Bug检测器')
    parser.add_argument('input', nargs='?', help='输入文件或目录路径')
    parser.add_argument('-o', '--output', help='输出报告文件路径')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--disable', nargs='+', help='禁用的模块列表')
    parser.add_argument('--enable', nargs='+', help='启用的模块列表')
    parser.add_argument('--list-modules', action='store_true', help='列出所有可用模块')
    parser.add_argument('--batch', action='store_true', help='批量检测模式：检测目录下所有C文件')
    parser.add_argument('--old-arch', action='store_true', help='使用旧架构（备用选项）')
    
    args = parser.parse_args()
    
    # 创建检测器实例
    detector = CBugDetector()
    
    # 处理模块启用/禁用
    if args.disable:
        for module in args.disable:
            detector.disable_module(module)
    
    if args.enable:
        for module in args.enable:
            detector.enable_module(module)
    
    # 列出模块
    if args.list_modules:
        detector.list_modules()
        return
    
    # 检查输入路径
    if args.input and not os.path.exists(args.input):
        print(f"{Fore.RED}Error: Path {args.input} does not exist{Style.RESET_ALL}")
        return
    
    # 分析文件或目录
    if args.input and os.path.isfile(args.input):
        # 单文件分析
        # 默认使用新架构
        issues = detector.analyze_file_new(args.input)
        
        # 创建报告生成器
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator(args.input)
        
        if args.format == 'json':
            # JSON格式输出
            json_reports = generator.generate_json_report(issues)
            print(json.dumps(json_reports, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            if issues:
                print(f"\n{Fore.YELLOW}Detection completed, found {len(issues)} issue(s){Style.RESET_ALL}")
                print(generator.generate_detailed_report(issues))
                print("\n" + generator.generate_summary(issues))
            else:
                print(f"{Fore.GREEN}恭喜！没有发现任何问题。{Style.RESET_ALL}")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(generator.generate_detailed_report(issues))
                print(f"{Fore.GREEN}报告已保存到: {args.output}{Style.RESET_ALL}")
        
        # 保留旧架构作为备用选项
        if args.old_arch:
            print(f"{Fore.YELLOW}使用旧架构分析...{Style.RESET_ALL}")
            reports = detector.analyze_file(args.input)
            if reports:
                print(f"\n{Fore.YELLOW}检测完成，共发现 {len(reports)} 个问题{Style.RESET_ALL}")
                for i, report in enumerate(reports, 1):
                    print(f"\n{Fore.CYAN}问题 {i}: {report.message}{Style.RESET_ALL}")
                    print(f"位置: {report.file_path}:{report.line_number}")
                    print(f"建议: {report.suggestion}")
            else:
                print(f"{Fore.GREEN}恭喜！没有发现任何问题。{Style.RESET_ALL}")
            
            if args.format == 'json':
                # JSON格式输出，不显示额外信息
                print(detector.generate_report(reports, args.format))
            else:
                if reports:
                    print(f"\n{Fore.YELLOW}Detection completed, found {len(reports)} issue(s){Style.RESET_ALL}")
                    print(detector.generate_report(reports, args.format))
                else:
                    print(f"{Fore.GREEN}Congratulations! No issues found.{Style.RESET_ALL}")
                
                if args.output:
                    detector.save_report(reports, args.output, args.format)
    
    elif args.input and os.path.isdir(args.input):
        # 目录分析（批量检测模式）
        print(f"{Fore.CYAN}开始批量检测目录: {args.input}{Style.RESET_ALL}")
        results = detector.analyze_directory(args.input)
        
        if results:
            total_issues = sum(len(reports) for reports in results.values())
            print(f"\n{Fore.GREEN}Batch detection completed!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}统计结果:{Style.RESET_ALL}")
            print(f"   - 检测文件数: {len(results)}")
            print(f"   - 发现问题数: {total_issues}")
            
            # 只显示有问题的文件
            problem_files = {k: v for k, v in results.items() if v}
            if problem_files:
                print(f"\n{Fore.YELLOW}⚠️  发现问题的文件:{Style.RESET_ALL}")
                for file_path, reports in problem_files.items():
                    print(f"\n{Fore.CYAN}📁 文件: {file_path}{Style.RESET_ALL}")
                    print(detector.generate_report(reports, args.format))
            else:
                print(f"{Fore.GREEN}🎉 所有文件都没有发现问题！{Style.RESET_ALL}")
            
            if args.output:
                # 合并所有报告
                all_reports = []
                for reports in results.values():
                    all_reports.extend(reports)
                detector.save_report(all_reports, args.output, args.format)
                print(f"{Fore.BLUE}报告已保存到: {args.output}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}恭喜！所有文件都没有发现任何问题。{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
