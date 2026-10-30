"""code_quality_checker 数据模型模块。

本模块定义了代码质量检查过程中使用的所有数据结构，包括：
- IssueLevel: 问题严重级别枚举
- Issue: 单个问题描述
- FileMetrics: 单个文件的质量指标
- QualityReport: 完整的质量报告
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class IssueLevel(Enum):
    """问题严重级别枚举。

    Attributes:
        INFO: 信息提示，无需处理
        WARNING: 警告，建议处理
        ERROR: 错误，必须处理
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    def __str__(self) -> str:
        """返回级别的字符串表示，便于日志输出。"""
        return self.value.upper()


@dataclass
class Issue:
    """单个问题描述。

    Attributes:
        level: 问题级别
        message: 问题描述文本
        line: 问题所在行号，若与具体行无关则为 None
        metric: 相关指标名称，便于归类
    """

    level: IssueLevel
    message: str
    line: Optional[int] = None
    metric: Optional[str] = None

    def to_dict(self) -> dict:
        """将问题转换为字典，便于序列化输出。"""
        return {
            "level": self.level.value,
            "message": self.message,
            "line": self.line,
            "metric": self.metric,
        }


@dataclass
class FileMetrics:
    """单个文件的质量指标集合。

    Attributes:
        file_path: 文件路径
        language: 源代码语言（python / java）
        total_lines: 总行数
        code_lines: 代码行数
        comment_lines: 注释行数
        blank_lines: 空行数
        complexity: 平均圈复杂度
        max_function_length: 最长函数行数
        max_nesting_depth: 最大嵌套深度
        todo_count: TODO 标记数量
        fixme_count: FIXME 标记数量
        issues: 该文件存在的问题列表
    """

    file_path: str
    language: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    complexity: float = 0.0
    max_function_length: int = 0
    max_nesting_depth: int = 0
    todo_count: int = 0
    fixme_count: int = 0
    issues: List[Issue] = field(default_factory=list)

    @property
    def comment_ratio(self) -> float:
        """注释占比，注释行数 / 代码行数。

        Returns:
            注释占比，若代码行数为 0 则返回 0.0。
        """
        if self.code_lines == 0:
            return 0.0
        return round(self.comment_lines / self.code_lines, 4)

    @property
    def issue_count(self) -> int:
        """问题总数。"""
        return len(self.issues)

    @property
    def error_count(self) -> int:
        """错误级别问题数。"""
        return sum(1 for i in self.issues if i.level == IssueLevel.ERROR)

    @property
    def warning_count(self) -> int:
        """警告级别问题数。"""
        return sum(1 for i in self.issues if i.level == IssueLevel.WARNING)

    def to_dict(self) -> dict:
        """将指标转换为字典，便于序列化输出。"""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "comment_ratio": self.comment_ratio,
            "complexity": self.complexity,
            "max_function_length": self.max_function_length,
            "max_nesting_depth": self.max_nesting_depth,
            "todo_count": self.todo_count,
            "fixme_count": self.fixme_count,
            "issue_count": self.issue_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class QualityReport:
    """完整的质量报告，包含多个文件的指标汇总。

    Attributes:
        files: 各文件的指标列表
        threshold: 质量阈值（圈复杂度门禁）
        generated_at: 报告生成时间
    """

    files: List[FileMetrics] = field(default_factory=list)
    threshold: float = 10.0
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def file_count(self) -> int:
        """分析的文件总数。"""
        return len(self.files)

    @property
    def total_code_lines(self) -> int:
        """所有文件代码行数总和。"""
        return sum(f.code_lines for f in self.files)

    @property
    def total_comment_lines(self) -> int:
        """所有文件注释行数总和。"""
        return sum(f.comment_lines for f in self.files)

    @property
    def total_issues(self) -> int:
        """所有文件问题数总和。"""
        return sum(f.issue_count for f in self.files)

    @property
    def total_errors(self) -> int:
        """所有文件错误数总和。"""
        return sum(f.error_count for f in self.files)

    @property
    def total_warnings(self) -> int:
        """所有文件警告数总和。"""
        return sum(f.warning_count for f in self.files)

    @property
    def average_complexity(self) -> float:
        """所有文件平均圈复杂度。"""
        if not self.files:
            return 0.0
        return round(sum(f.complexity for f in self.files) / len(self.files), 4)

    @property
    def passed(self) -> bool:
        """是否通过质量门禁（无错误且平均复杂度不超过阈值）。"""
        return self.total_errors == 0 and self.average_complexity <= self.threshold

    def to_dict(self) -> dict:
        """将报告转换为字典，便于序列化输出。"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "threshold": self.threshold,
            "summary": {
                "file_count": self.file_count,
                "total_code_lines": self.total_code_lines,
                "total_comment_lines": self.total_comment_lines,
                "average_complexity": self.average_complexity,
                "total_issues": self.total_issues,
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "passed": self.passed,
            },
            "files": [f.to_dict() for f in self.files],
        }
