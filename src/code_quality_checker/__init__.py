"""code_quality_checker 包初始化模块。

导出主要类与版本号，便于外部直接引用。
"""

from __future__ import annotations

from .checker import CodeChecker
from .models import FileMetrics, Issue, IssueLevel, QualityReport
from .reporter import Reporter

__version__ = "1.0.0"
__all__ = [
    "CodeChecker",
    "FileMetrics",
    "Issue",
    "IssueLevel",
    "QualityReport",
    "Reporter",
    "__version__",
]
