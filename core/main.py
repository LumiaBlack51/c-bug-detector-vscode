"""
C语言Bug检测器主程序
整合所有检测模块，提供统一的检测接口
"""
import os
import sys
import argparse
from typing import List, Dict, Any
from colorama import init, Fore, Style

# 初始化colorama
init()

# 导入检测模块
from modules.memory_safety import MemorySafetyModule
from modules.variable_state import VariableStateModule
from modules.standard_library import StandardLibraryModule
from modules.numeric_control_flow import NumericControlFlowModule

# 导入工具类
from utils.error_reporter import ErrorReporter, BugReport
from utils.code_parser import CCodeParser


class CBugDetector:
    """C语言Bug检测器主类"""
    
    def __init__(self):
        self.parser = CCodeParser()
        self.error_reporter = ErrorReporter()
        
        # 初始化所有检测模块
        self.modules = {
            'memory_safety': MemorySafetyModule(),
            'variable_state': VariableStateModule(),
            'standard_library': StandardLibraryModule(),
            'numeric_control_flow': NumericControlFlowModule(),
        }
        
        # 模块启用状态
        self.module_enabled = {
            'memory_safety': True,
            'variable_state': True,
            'standard_library': True,
            'numeric_control_flow': True,
        }
    
    def analyze_file(self, file_path: str) -> List[BugReport]:
        """分析单个C文件"""
        print(f"{Fore.CYAN}🔍 正在分析文件: {file_path}{Style.RESET_ALL}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"{Fore.RED}❌ 错误: 文件 {file_path} 不存在{Style.RESET_ALL}")
            return []
        
        # 检查文件扩展名
        if not file_path.endswith('.c'):
            print(f"{Fore.YELLOW}⚠️  警告: 文件 {file_path} 不是C文件(.c){Style.RESET_ALL}")
        
        try:
            # 解析C代码
            parsed_data = self.parser.parse_file(file_path)
            if not parsed_data:
                print(f"{Fore.RED}❌ 错误: 无法解析文件 {file_path}{Style.RESET_ALL}")
                return []
            
            # 清空之前的报告
            self.error_reporter.clear_reports()
            
            # 运行所有启用的模块
            for module_name, module in self.modules.items():
                if self.module_enabled[module_name]:
                    print(f"{Fore.GREEN}📋 运行模块: {module.get_module_name()}{Style.RESET_ALL}")
                    try:
                        reports = module.analyze(parsed_data)
                        for report in reports:
                            self.error_reporter.add_report(report)
                    except Exception as e:
                        print(f"{Fore.RED}❌ 模块 {module_name} 运行出错: {e}{Style.RESET_ALL}")
            
            return self.error_reporter.get_reports()
            
        except Exception as e:
            print(f"{Fore.RED}❌ 分析文件时出错: {e}{Style.RESET_ALL}")
            return []
    
    def analyze_directory(self, directory_path: str) -> Dict[str, List[BugReport]]:
        """分析目录中的所有C文件"""
        print(f"{Fore.CYAN}🔍 正在分析目录: {directory_path}{Style.RESET_ALL}")
        
        if not os.path.exists(directory_path):
            print(f"{Fore.RED}❌ 错误: 目录 {directory_path} 不存在{Style.RESET_ALL}")
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
            print(f"{Fore.GREEN}✅ 已启用模块: {self.modules[module_name].get_module_name()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ 错误: 模块 {module_name} 不存在{Style.RESET_ALL}")
    
    def disable_module(self, module_name: str):
        """禁用指定模块"""
        if module_name in self.modules:
            self.module_enabled[module_name] = False
            print(f"{Fore.YELLOW}⚠️  已禁用模块: {self.modules[module_name].get_module_name()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ 错误: 模块 {module_name} 不存在{Style.RESET_ALL}")
    
    def list_modules(self):
        """列出所有可用模块"""
        print(f"{Fore.CYAN}📋 可用模块列表:{Style.RESET_ALL}")
        print("=" * 50)
        for module_name, module in self.modules.items():
            status = "✅ 启用" if self.module_enabled[module_name] else "❌ 禁用"
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
            print(f"{Fore.GREEN}✅ 报告已保存到: {output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ 保存报告时出错: {e}{Style.RESET_ALL}")


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
        print(f"{Fore.RED}❌ 错误: 路径 {args.input} 不存在{Style.RESET_ALL}")
        return
    
    # 分析文件或目录
    if args.input and os.path.isfile(args.input):
        # 单文件分析
        reports = detector.analyze_file(args.input)
        
        if reports:
            print(f"\n{Fore.YELLOW}📊 检测完成，共发现 {len(reports)} 个问题{Style.RESET_ALL}")
            print(detector.generate_report(reports, args.format))
            
            if args.output:
                detector.save_report(reports, args.output, args.format)
        else:
            print(f"{Fore.GREEN}✅ 恭喜！没有发现任何问题。{Style.RESET_ALL}")
    
    elif args.input and os.path.isdir(args.input):
        # 目录分析（批量检测模式）
        print(f"{Fore.CYAN}🔍 开始批量检测目录: {args.input}{Style.RESET_ALL}")
        results = detector.analyze_directory(args.input)
        
        if results:
            total_issues = sum(len(reports) for reports in results.values())
            print(f"\n{Fore.GREEN}✅ 批量检测完成！{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 统计结果:{Style.RESET_ALL}")
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
                print(f"{Fore.BLUE}💾 报告已保存到: {args.output}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ 恭喜！所有文件都没有发现任何问题。{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
