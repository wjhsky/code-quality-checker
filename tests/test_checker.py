"""CodeChecker 核心功能单元测试。

覆盖行数统计、圈复杂度、函数长度、嵌套深度、TODO/FIXME 标记等指标，
以及文件不存在、不支持的文件类型等异常路径。
"""

from __future__ import annotations

import os
import unittest

from code_quality_checker.checker import CodeChecker
from code_quality_checker.models import FileMetrics, IssueLevel

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_GOOD = os.path.join(FIXTURES_DIR, "sample_good.py")
SAMPLE_BAD = os.path.join(FIXTURES_DIR, "sample_bad.py")


class TestCodeCheckerFile(unittest.TestCase):
    """CodeChecker.check_file 方法测试。"""

    def setUp(self) -> None:
        self.checker = CodeChecker()

    def test_check_good_file_returns_metrics(self) -> None:
        """检查质量好的文件应返回有效指标对象。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertIsInstance(metrics, FileMetrics)
        self.assertEqual(metrics.language, "python")
        self.assertGreater(metrics.total_lines, 0)
        self.assertGreater(metrics.code_lines, 0)

    def test_good_file_has_no_errors(self) -> None:
        """质量好的文件不应有 ERROR 级别问题。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        errors = [i for i in metrics.issues if i.level == IssueLevel.ERROR]
        self.assertEqual(len(errors), 0)

    def test_good_file_has_no_fixme(self) -> None:
        """质量好的文件不应包含 FIXME 标记。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertEqual(metrics.fixme_count, 0)

    def test_good_file_has_no_todo(self) -> None:
        """质量好的文件不应包含 TODO 标记。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertEqual(metrics.todo_count, 0)

    def test_good_file_function_length_within_threshold(self) -> None:
        """质量好的文件最长函数不应超过 50 行。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertLessEqual(metrics.max_function_length, 50)

    def test_good_file_nesting_within_threshold(self) -> None:
        """质量好的文件最大嵌套深度不应超过 4 层。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertLessEqual(metrics.max_nesting_depth, 4)

    def test_bad_file_has_fixme(self) -> None:
        """质量差的文件应包含 FIXME 标记。"""
        metrics = self.checker.check_file(SAMPLE_BAD)
        self.assertGreater(metrics.fixme_count, 0)

    def test_bad_file_has_todo(self) -> None:
        """质量差的文件应包含 TODO 标记。"""
        metrics = self.checker.check_file(SAMPLE_BAD)
        self.assertGreater(metrics.todo_count, 0)

    def test_bad_file_has_error_issues(self) -> None:
        """质量差的文件应产生 ERROR 级别问题。"""
        metrics = self.checker.check_file(SAMPLE_BAD)
        errors = [i for i in metrics.issues if i.level == IssueLevel.ERROR]
        self.assertGreater(len(errors), 0)

    def test_bad_file_has_deep_nesting(self) -> None:
        """质量差的文件最大嵌套深度应超过 4 层。"""
        metrics = self.checker.check_file(SAMPLE_BAD)
        self.assertGreater(metrics.max_nesting_depth, 4)

    def test_bad_file_has_long_function(self) -> None:
        """质量差的文件最长函数应超过 50 行。"""
        metrics = self.checker.check_file(SAMPLE_BAD)
        self.assertGreater(metrics.max_function_length, 50)

    def test_file_not_found_raises(self) -> None:
        """检查不存在的文件应抛出 FileNotFoundError。"""
        with self.assertRaises(FileNotFoundError):
            self.checker.check_file("/nonexistent/path/file.py")

    def test_unsupported_language_raises(self) -> None:
        """指定不支持的语言应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            self.checker.check_file(SAMPLE_GOOD, language="ruby")

    def test_language_detection_python(self) -> None:
        """根据 .py 扩展名应推断为 python。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertEqual(metrics.language, "python")

    def test_explicit_language_override(self) -> None:
        """显式指定语言应覆盖自动推断。"""
        metrics = self.checker.check_file(SAMPLE_GOOD, language="python")
        self.assertEqual(metrics.language, "python")


class TestLineCounting(unittest.TestCase):
    """行数统计测试。"""

    def setUp(self) -> None:
        self.checker = CodeChecker()

    def test_total_lines_equals_sum(self) -> None:
        """总行数应等于代码行、注释行、空行之和。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        total = metrics.code_lines + metrics.comment_lines + metrics.blank_lines
        self.assertEqual(metrics.total_lines, total)

    def test_good_file_has_comments(self) -> None:
        """质量好的文件应有注释行。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertGreater(metrics.comment_lines, 0)

    def test_comment_ratio_property(self) -> None:
        """comment_ratio 属性应返回非负比值。"""
        metrics = self.checker.check_file(SAMPLE_GOOD)
        self.assertGreaterEqual(metrics.comment_ratio, 0.0)


class TestDirectoryCheck(unittest.TestCase):
    """目录检查测试。"""

    def setUp(self) -> None:
        self.checker = CodeChecker()

    def test_check_fixtures_directory(self) -> None:
        """检查 fixtures 目录应返回多个文件指标。"""
        results = self.checker.check_directory(FIXTURES_DIR)
        self.assertGreater(len(results), 0)
        for metrics in results:
            self.assertIsInstance(metrics, FileMetrics)

    def test_check_directory_python_only(self) -> None:
        """限定 python 语言应只返回 .py 文件。"""
        results = self.checker.check_directory(FIXTURES_DIR, language="python")
        for metrics in results:
            self.assertEqual(metrics.language, "python")

    def test_check_nonexistent_directory_raises(self) -> None:
        """检查不存在的目录应抛出 FileNotFoundError。"""
        with self.assertRaises(FileNotFoundError):
            self.checker.check_directory("/nonexistent/directory")


class TestThresholds(unittest.TestCase):
    """阈值配置测试。"""

    def test_custom_complexity_threshold(self) -> None:
        """自定义圈复杂度阈值应生效。"""
        checker = CodeChecker(complexity_threshold=0.0)
        metrics = checker.check_file(SAMPLE_GOOD)
        warnings = [
            i for i in metrics.issues
            if i.level == IssueLevel.WARNING and i.metric == "complexity"
        ]
        # 阈值为 0 时，任何非零复杂度都应告警
        if metrics.complexity > 0:
            self.assertGreater(len(warnings), 0)

    def test_custom_function_length_threshold(self) -> None:
        """自定义函数长度阈值应生效。"""
        checker = CodeChecker(function_length_threshold=1)
        metrics = checker.check_file(SAMPLE_GOOD)
        warnings = [
            i for i in metrics.issues
            if i.level == IssueLevel.WARNING and i.metric == "function_length"
        ]
        if metrics.max_function_length > 1:
            self.assertGreater(len(warnings), 0)

    def test_custom_nesting_threshold(self) -> None:
        """自定义嵌套深度阈值应生效。"""
        checker = CodeChecker(nesting_depth_threshold=0)
        metrics = checker.check_file(SAMPLE_GOOD)
        warnings = [
            i for i in metrics.issues
            if i.level == IssueLevel.WARNING and i.metric == "nesting_depth"
        ]
        if metrics.max_nesting_depth > 0:
            self.assertGreater(len(warnings), 0)


class TestModels(unittest.TestCase):
    """数据模型测试。"""

    def test_file_metrics_to_dict(self) -> None:
        """FileMetrics.to_dict 应返回完整字典。"""
        metrics = FileMetrics(file_path="test.py", language="python")
        data = metrics.to_dict()
        self.assertEqual(data["file_path"], "test.py")
        self.assertEqual(data["language"], "python")
        self.assertIn("comment_ratio", data)
        self.assertIn("issues", data)

    def test_issue_to_dict(self) -> None:
        """Issue.to_dict 应返回完整字典。"""
        from code_quality_checker.models import Issue

        issue = Issue(level=IssueLevel.WARNING, message="test", line=10)
        data = issue.to_dict()
        self.assertEqual(data["level"], "warning")
        self.assertEqual(data["message"], "test")
        self.assertEqual(data["line"], 10)

    def test_issue_level_str(self) -> None:
        """IssueLevel 字符串表示应为大写。"""
        self.assertEqual(str(IssueLevel.WARNING), "WARNING")
        self.assertEqual(str(IssueLevel.ERROR), "ERROR")
        self.assertEqual(str(IssueLevel.INFO), "INFO")


if __name__ == "__main__":
    unittest.main()
