"""
错误报告器 - 为初学者提供易懂的错误报告
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """错误类型枚举"""
    MEMORY_SAFETY = "内存安全"
    VARIABLE_STATE = "变量状态"
    STANDARD_LIBRARY = "标准库使用"
    NUMERIC_CONTROL_FLOW = "数值与控制流"


class Severity(Enum):
    """错误严重程度"""
    ERROR = "错误"
    WARNING = "警告"
    INFO = "提示"


@dataclass
class BugReport:
    """Bug报告数据结构"""
    line_number: int
    error_type: ErrorType
    severity: Severity
    message: str
    suggestion: str
    code_snippet: str = ""
    module_name: str = ""


class ErrorReporter:
    """错误报告器类"""
    
    def __init__(self):
        self.reports: List[BugReport] = []
    
    def add_report(self, report: BugReport):
        """添加错误报告"""
        self.reports.append(report)
    
    def add_memory_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = ""):
        """添加内存安全错误"""
        report = BugReport(
            line_number=line_num,
            error_type=ErrorType.MEMORY_SAFETY,
            severity=Severity.ERROR,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
            module_name="内存安全卫士"
        )
        self.add_report(report)
    
    def add_variable_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = ""):
        """添加变量状态错误"""
        report = BugReport(
            line_number=line_num,
            error_type=ErrorType.VARIABLE_STATE,
            severity=Severity.WARNING,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
            module_name="变量状态监察官"
        )
        self.add_report(report)
    
    def add_library_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = ""):
        """添加标准库使用错误"""
        report = BugReport(
            line_number=line_num,
            error_type=ErrorType.STANDARD_LIBRARY,
            severity=Severity.ERROR,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
            module_name="标准库使用助手"
        )
        self.add_report(report)
    
    def add_numeric_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = ""):
        """添加数值与控制流错误"""
        report = BugReport(
            line_number=line_num,
            error_type=ErrorType.NUMERIC_CONTROL_FLOW,
            severity=Severity.ERROR,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
            module_name="数值与控制流分析器"
        )
        self.add_report(report)
    
    def get_reports(self) -> List[BugReport]:
        """获取所有错误报告"""
        return self.reports
    
    def get_reports_by_type(self, error_type: ErrorType) -> List[BugReport]:
        """按类型获取错误报告"""
        return [report for report in self.reports if report.error_type == error_type]
    
    def clear_reports(self):
        """清空所有报告"""
        self.reports.clear()
    
    def format_report(self, report: BugReport) -> str:
        """格式化单个报告"""
        return f"""
🔍 {report.module_name} 检测到问题：

📍 位置：第 {report.line_number} 行
⚠️  类型：{report.error_type.value} - {report.severity.value}
💬 问题：{report.message}
💡 建议：{report.suggestion}
"""
    
    def format_all_reports(self) -> str:
        """格式化所有报告"""
        if not self.reports:
            return "✅ 恭喜！没有发现任何问题。"
        
        result = f"📊 检测完成，共发现 {len(self.reports)} 个问题：\n"
        result += "=" * 50 + "\n"
        
        for i, report in enumerate(self.reports, 1):
            result += f"\n{i}. {self.format_report(report)}"
            result += "-" * 30 + "\n"
        
        return result
