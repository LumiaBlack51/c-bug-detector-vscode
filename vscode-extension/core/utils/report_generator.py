#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器 - 重构版本
接收问题对象，调用SourceCodeExtractor，生成统一美观的报告
"""
from typing import List, Dict, Any
from .issue import Issue
from .source_code_extractor import SourceCodeExtractor

class ReportGenerator:
    """报告生成器 - 重构版本"""
    
    def __init__(self, filepath: str):
        """初始化报告生成器"""
        self.filepath = filepath
        self.source_extractor = SourceCodeExtractor(filepath)
    
    def generate_text_report(self, issues: List[Issue]) -> str:
        """生成文本格式的报告"""
        if not issues:
            return "未检测到任何问题。"
        
        report_lines = []
        report_lines.append(f"检测到 {len(issues)} 个问题：\n")
        
        # 按错误类型分组
        issues_by_type = self._group_issues_by_type(issues)
        
        for issue_type, type_issues in issues_by_type.items():
            report_lines.append(f"=== {issue_type.value} ({len(type_issues)}个) ===")
            
            for i, issue in enumerate(type_issues, 1):
                report_lines.append(f"\n{i}. {issue.description}")
                report_lines.append(f"   位置：{self.filepath} 第 {issue.line_number} 行")
                
                # 获取代码片段
                code_snippet = self._get_code_snippet(issue)
                if code_snippet:
                    report_lines.append(f"   代码片段：")
                    for line in code_snippet.split('\n'):
                        report_lines.append(f"   {line}")
                
                report_lines.append(f"   建议：{issue.suggestion}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def generate_json_report(self, issues: List[Issue]) -> List[Dict[str, Any]]:
        """生成JSON格式的报告"""
        json_reports = []
        
        for issue in issues:
            # 获取代码片段
            code_snippet = self._get_code_snippet(issue)
            
            report = {
                "line_number": issue.line_number,
                "error_type": issue.issue_type.value,
                "severity": issue.severity.value,
                "message": issue.description,
                "suggestion": issue.suggestion,
                "code_snippet": code_snippet,
                "module_name": issue.module_name,
                "variable_name": issue.variable_name,
                "error_category": issue.error_category
            }
            json_reports.append(report)
        
        return json_reports
    
    def generate_detailed_report(self, issues: List[Issue]) -> str:
        """生成详细格式的报告（带高亮）"""
        if not issues:
            return "未检测到任何问题。"
        
        report_lines = []
        report_lines.append(f"检测到 {len(issues)} 个问题：\n")
        
        for i, issue in enumerate(issues, 1):
            report_lines.append("=" * 60)
            report_lines.append(f"问题 {i}: {issue.description}")
            report_lines.append(f"模块: {issue.module_name}")
            report_lines.append(f"位置: {self.filepath} 第 {issue.line_number} 行")
            report_lines.append(f"类型: {issue.issue_type.value} - {issue.severity.value}")
            
            # 获取带高亮的代码片段
            code_snippet = self._get_code_snippet(issue, context_lines=2)
            if code_snippet:
                report_lines.append("\n代码片段:")
                for line in code_snippet.split('\n'):
                    report_lines.append(f"  {line}")
            
            report_lines.append(f"\n建议: {issue.suggestion}")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _group_issues_by_type(self, issues: List[Issue]) -> Dict[Any, List[Issue]]:
        """按错误类型分组问题"""
        groups = {}
        for issue in issues:
            issue_type = issue.issue_type
            if issue_type not in groups:
                groups[issue_type] = []
            groups[issue_type].append(issue)
        return groups
    
    def _get_code_snippet(self, issue: Issue, context_lines: int = 1) -> str:
        """获取问题的代码片段"""
        # 优先使用libclang cursor
        if issue.libclang_cursor:
            return self.source_extractor.get_libclang_snippet(issue.libclang_cursor, context_lines)
        
        # 其次使用AST节点
        if issue.ast_node:
            return self.source_extractor.get_ast_node_snippet(issue.ast_node, context_lines)
        
        # 最后使用行号
        return self.source_extractor.get_code_snippet(
            issue.line_number, 
            issue.start_column, 
            issue.end_column, 
            context_lines
        )
    
    def generate_summary(self, issues: List[Issue]) -> str:
        """生成问题摘要"""
        if not issues:
            return "✅ 未检测到任何问题"
        
        # 统计信息
        total_issues = len(issues)
        error_count = sum(1 for issue in issues if issue.severity.value == "错误")
        warning_count = sum(1 for issue in issues if issue.severity.value == "警告")
        
        # 按类型统计
        type_counts = {}
        for issue in issues:
            issue_type = issue.issue_type.value
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        summary_lines = []
        summary_lines.append(f"检测摘要:")
        summary_lines.append(f"   总问题数: {total_issues}")
        summary_lines.append(f"   错误: {error_count}")
        summary_lines.append(f"   警告: {warning_count}")
        summary_lines.append("")
        summary_lines.append("问题类型分布:")
        for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            summary_lines.append(f"   {issue_type}: {count}")
        
        return "\n".join(summary_lines)
