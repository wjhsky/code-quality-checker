"""code_quality_checker 报告生成器模块。

本模块实现 Reporter 类，负责将 QualityReport 转换为 JSON 或文本格式输出，
并支持写入文件。
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .models import FileMetrics, IssueLevel, QualityReport


class Reporter:
    """质量报告生成器。

    Args:
        report: 待输出的 QualityReport 对象
    """

    def __init__(self, report: QualityReport) -> None:
        self.report = report

    # ------------------------------------------------------------------ #
    # 格式生成
    # ------------------------------------------------------------------ #

    def to_json(self, indent: int = 2) -> str:
        """生成 JSON 格式报告字符串。

        Args:
            indent: JSON 缩进空格数

        Returns:
            JSON 格式字符串
        """
        return json.dumps(self.report.to_dict(), indent=indent, ensure_ascii=False)

    def to_text(self) -> str:
        """生成易读的文本格式报告字符串。

        Returns:
            文本格式字符串
        """
        lines: list[str] = []
        lines.append(self._format_header())
        lines.append(self._format_summary())
        lines.append("")

        if not self.report.files:
            lines.append("未发现可分析的源代码文件。")
            return "\n".join(lines)

        for metrics in self.report.files:
            lines.append(self._format_file(metrics))
            lines.append("")

        lines.append(self._format_footer())
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # 文件输出
    # ------------------------------------------------------------------ #

    def write_json(self, file_path: str, indent: int = 2) -> str:
        """将 JSON 报告写入文件。

        Args:
            file_path: 输出文件路径
            indent: JSON 缩进空格数

        Returns:
            实际写入的文件路径
        """
        content = self.to_json(indent)
        return self._write(file_path, content)

    def write_text(self, file_path: str) -> str:
        """将文本报告写入文件。

        Args:
            file_path: 输出文件路径

        Returns:
            实际写入的文件路径
        """
        content = self.to_text()
        return self._write(file_path, content)

    def write(self, file_path: str, output_format: str = "text") -> str:
        """根据格式写入报告文件。

        Args:
            file_path: 输出文件路径
            output_format: 输出格式，json 或 text

        Returns:
            实际写入的文件路径
        """
        if output_format.lower() == "json":
            return self.write_json(file_path)
        return self.write_text(file_path)

    # ------------------------------------------------------------------ #
    # 内部格式化
    # ------------------------------------------------------------------ #

    def _format_header(self) -> str:
        """格式化报告头部。"""
        return (
            "=" * 70 + "\n"
            "代码质量检查报告\n"
            f"生成时间: {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"质量阈值: {self.report.threshold}\n"
            + "=" * 70
        )

    def _format_summary(self) -> str:
        """格式化汇总信息。"""
        r = self.report
        status = "✓ 通过" if r.passed else "✗ 未通过"
        return (
            f"\n【汇总】\n"
            f"  文件数量      : {r.file_count}\n"
            f"  代码总行数    : {r.total_code_lines}\n"
            f"  注释总行数    : {r.total_comment_lines}\n"
            f"  平均圈复杂度  : {r.average_complexity}\n"
            f"  问题总数      : {r.total_issues}\n"
            f"    - 错误      : {r.total_errors}\n"
            f"    - 警告      : {r.total_warnings}\n"
            f"  质量门禁      : {status}\n"
        )

    def _format_file(self, metrics: FileMetrics) -> str:
        """格式化单个文件指标。"""
        lines = [
            f"【文件】{metrics.file_path}",
            f"  语言          : {metrics.language}",
            f"  总行数        : {metrics.total_lines}",
            f"    - 代码行    : {metrics.code_lines}",
            f"    - 注释行    : {metrics.comment_lines}",
            f"    - 空行      : {metrics.blank_lines}",
            f"  注释占比      : {metrics.comment_ratio:.2%}",
            f"  圈复杂度      : {metrics.complexity}",
            f"  最长函数      : {metrics.max_function_length} 行",
            f"  最大嵌套深度  : {metrics.max_nesting_depth} 层",
            f"  TODO 标记     : {metrics.todo_count}",
            f"  FIXME 标记    : {metrics.fixme_count}",
        ]

        if metrics.issues:
            lines.append(f"  问题列表 ({metrics.issue_count}):")
            for issue in metrics.issues:
                loc = f"行 {issue.line}" if issue.line else "全局"
                lines.append(
                    f"    [{issue.level}] {loc} - {issue.message}"
                )
        else:
            lines.append("  问题列表      : 无")

        return "\n".join(lines)

    def _format_footer(self) -> str:
        """格式化报告尾部。"""
        return "=" * 70

    # ------------------------------------------------------------------ #
    # 辅助方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def _write(file_path: str, content: str) -> str:
        """将内容写入文件，自动创建父目录。

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            实际写入的文件路径
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return file_path
