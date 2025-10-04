"""
错误报告器 - 为初学者提供易懂的错误报告，集成全局错误管理
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from .global_error_manager import global_error_manager
from .source_code_extractor import get_source_extractor

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
    variable_name: str = ""
    error_category: str = ""

class ErrorReporter:
    """错误报告器类 - 集成全局错误管理"""
    
    def __init__(self):
        self.reports: List[BugReport] = []
    
    def add_report(self, report: BugReport):
        """添加错误报告"""
        self.reports.append(report)
    
    def _should_report(self, line_number: int, variable_name: str, 
                      error_type: str, error_category: str) -> bool:
        """检查是否应该报告这个错误"""
        return global_error_manager.should_report_error(
            line_number, variable_name, error_type, error_category
        )
    
    def _mark_reported(self, line_number: int, variable_name: str,
                      error_type: str, error_category: str):
        """标记错误已报告"""
        global_error_manager.mark_error_reported(
            line_number, variable_name, error_type, error_category
        )
    
    def add_memory_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = "", file_path: str = ""):
        """添加内存安全错误"""
        # 确定具体的错误类型
        error_type = "memory_leak"
        if "野指针" in message or "wild pointer" in message.lower():
            error_type = "wild_pointer_dereference"
        elif "use after free" in message.lower() or "释放后使用" in message:
            error_type = "use_after_free"
        elif "null pointer" in message.lower() or "空指针" in message:
            error_type = "null_pointer_dereference"
        elif "malloc" in message.lower() and "null" in message.lower():
            error_type = "malloc_null_check"
            
        if self._should_report(line_num, variable_name, error_type, "memory"):
            # 统一代码片段提取
            if not code_snippet and file_path:
                extractor = get_source_extractor(file_path)
                code_snippet = extractor.get_simple_line(line_num)
            
            report = BugReport(
                line_number=line_num,
                error_type=ErrorType.MEMORY_SAFETY,
                severity=Severity.ERROR,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
                module_name="内存安全卫士",
                variable_name=variable_name,
                error_category="memory"
            )
            self.add_report(report)
            self._mark_reported(line_num, variable_name, error_type, "memory")
    
    def add_variable_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = "", file_path: str = ""):
        """添加变量状态错误"""
        error_type = "uninitialized_variable"
        if "unused" in message.lower() or "未使用" in message:
            error_type = "unused_variable"
            
        if self._should_report(line_num, variable_name, error_type, "variable"):
            # 统一代码片段提取
            if not code_snippet and file_path:
                extractor = get_source_extractor(file_path)
                code_snippet = extractor.get_simple_line(line_num)
            
            report = BugReport(
                line_number=line_num,
                error_type=ErrorType.VARIABLE_STATE,
                severity=Severity.ERROR,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
                module_name="变量状态监察官",
                variable_name=variable_name,
                error_category="variable"
            )
            self.add_report(report)
            self._mark_reported(line_num, variable_name, error_type, "variable")
    
    def add_variable_warning(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = ""):
        """添加变量状态警告"""
        error_type = "unused_variable"
        if self._should_report(line_num, variable_name, error_type, "variable"):
            report = BugReport(
                line_number=line_num,
                error_type=ErrorType.VARIABLE_STATE,
                severity=Severity.WARNING,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
                module_name="变量状态监察官",
                variable_name=variable_name,
                error_category="variable"
            )
            self.add_report(report)
            self._mark_reported(line_num, variable_name, error_type, "variable")
    
    def add_library_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = ""):
        """添加标准库使用错误"""
        error_type = "printf_format"
        if self._should_report(line_num, variable_name, error_type, "library"):
            report = BugReport(
                line_number=line_num,
                error_type=ErrorType.STANDARD_LIBRARY,
                severity=Severity.ERROR,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
                module_name="标准库使用助手",
                variable_name=variable_name,
                error_category="library"
            )
            self.add_report(report)
            self._mark_reported(line_num, variable_name, error_type, "library")
    
    def add_numeric_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = ""):
        """添加数值与控制流错误"""
        error_type = "numeric_control_flow"
        if self._should_report(line_num, variable_name, error_type, "numeric"):
            report = BugReport(
                line_number=line_num,
                error_type=ErrorType.NUMERIC_CONTROL_FLOW,
                severity=Severity.ERROR,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
                module_name="数值与控制流分析器",
                variable_name=variable_name,
                error_category="numeric"
            )
            self.add_report(report)
            self._mark_reported(line_num, variable_name, error_type, "numeric")
    
    def add_control_flow_error(self, line_num: int, message: str, suggestion: str, code_snippet: str = "", variable_name: str = ""):
        """添加控制流错误（别名方法）"""
        self.add_numeric_error(line_num, message, suggestion, code_snippet, variable_name)
    
    def get_reports(self) -> List[BugReport]:
        """获取所有错误报告"""
        return self.reports
    
    def get_reports_by_type(self, error_type: ErrorType) -> List[BugReport]:
        """按类型获取错误报告"""
        return [report for report in self.reports if report.error_type == error_type]
    
    def clear_reports(self):
        """清空所有报告"""
        self.reports.clear()
        global_error_manager.clear()
    
    def format_report(self, report: BugReport) -> str:
        """格式化单个报告"""
        return f"""
检测模块: {report.module_name} 检测到问题：

位置：第 {report.line_number} 行
类型：{report.error_type.value} - {report.severity.value}
问题：{report.message}
建议：{report.suggestion}
"""
    
    def format_all_reports(self) -> str:
        """格式化所有报告"""
        if not self.reports:
            return "恭喜！没有发现任何问题。"
        
        result = f"检测完成，共发现 {len(self.reports)} 个问题：\n"
        result += "=" * 50 + "\n"
        
        for i, report in enumerate(self.reports, 1):
            result += f"\n{i}. {self.format_report(report)}"
            result += "-" * 30 + "\n"
        
        return result
