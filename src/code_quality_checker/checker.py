"""code_quality_checker 核心检查逻辑模块。

本模块实现 CodeChecker 类，负责对 Python 与 Java 源代码文件进行静态质量分析，
包括行数统计、圈复杂度计算、函数长度检查、嵌套深度检查以及 TODO/FIXME 标记统计。
"""

from __future__ import annotations

import ast
import io
import os
import re
import tokenize
from typing import List, Optional, Tuple

from .models import FileMetrics, Issue, IssueLevel

# 默认告警阈值
DEFAULT_FUNCTION_LENGTH_THRESHOLD = 50
DEFAULT_NESTING_DEPTH_THRESHOLD = 4
DEFAULT_COMPLEXITY_THRESHOLD = 10.0

# TODO / FIXME 标记正则
TODO_PATTERN = re.compile(r"\bTODO\b", re.IGNORECASE)
FIXME_PATTERN = re.compile(r"\bFIXME\b", re.IGNORECASE)


class CodeChecker:
    """代码质量检查器。

    对 Python 与 Java 源代码文件执行静态分析，生成 FileMetrics 指标对象。

    Args:
        function_length_threshold: 函数长度告警阈值，默认 50 行
        nesting_depth_threshold: 嵌套深度告警阈值，默认 4 层
        complexity_threshold: 圈复杂度告警阈值，默认 10.0
    """

    def __init__(
        self,
        function_length_threshold: int = DEFAULT_FUNCTION_LENGTH_THRESHOLD,
        nesting_depth_threshold: int = DEFAULT_NESTING_DEPTH_THRESHOLD,
        complexity_threshold: float = DEFAULT_COMPLEXITY_THRESHOLD,
    ) -> None:
        self.function_length_threshold = function_length_threshold
        self.nesting_depth_threshold = nesting_depth_threshold
        self.complexity_threshold = complexity_threshold

    # ------------------------------------------------------------------ #
    # 公共 API
    # ------------------------------------------------------------------ #

    def check_file(self, file_path: str, language: Optional[str] = None) -> FileMetrics:
        """检查单个文件并返回指标。

        Args:
            file_path: 文件路径
            language: 源代码语言，若为 None 则根据扩展名推断

        Returns:
            该文件的 FileMetrics 指标对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件类型
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if language is None:
            language = self._detect_language(file_path)
        if language not in ("python", "java"):
            raise ValueError(f"不支持的语言: {language}，仅支持 python / java")

        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            source = fh.read()

        metrics = FileMetrics(file_path=file_path, language=language)
        self._analyze_lines(metrics, source, language)
        self._analyze_complexity(metrics, file_path, language)
        self._analyze_functions(metrics, source, language)
        self._analyze_nesting(metrics, source, language)
        self._analyze_markers(metrics, source)
        self._evaluate_issues(metrics)
        return metrics

    def check_directory(
        self,
        dir_path: str,
        language: Optional[str] = None,
    ) -> List[FileMetrics]:
        """递归检查目录下所有支持的源代码文件。

        Args:
            dir_path: 目录路径
            language: 限定语言，若为 None 则同时检查 python 与 java

        Returns:
            各文件指标列表
        """
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"目录不存在: {dir_path}")

        results: List[FileMetrics] = []
        extensions = self._target_extensions(language)

        for root, _dirs, files in os.walk(dir_path):
            for name in sorted(files):
                if os.path.splitext(name)[1] in extensions:
                    full = os.path.join(root, name)
                    try:
                        results.append(self.check_file(full))
                    except (ValueError, OSError):
                        continue
        return results

    # ------------------------------------------------------------------ #
    # 行数统计
    # ------------------------------------------------------------------ #

    def _analyze_lines(self, metrics: FileMetrics, source: str, language: str) -> None:
        """统计总行数、代码行、注释行、空行。"""
        lines = source.splitlines()
        metrics.total_lines = len(lines)

        if language == "python":
            code, comment, blank = self._count_python_lines(source)
        else:
            code, comment, blank = self._count_java_lines(source)

        metrics.code_lines = code
        metrics.comment_lines = comment
        metrics.blank_lines = blank

    @staticmethod
    def _count_python_lines(source: str) -> Tuple[int, int, int]:
        """使用 AST 精确统计 Python 文件行数分类。

        通过 AST 识别文档字符串（docstring），将其计入注释行。

        Returns:
            (代码行数, 注释行数, 空行数)
        """
        lines = source.splitlines()
        total = len(lines)

        code_lines: set[int] = set()
        comment_lines: set[int] = set()
        blank_lines: set[int] = set()

        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                blank_lines.add(index)
            elif stripped.startswith("#"):
                comment_lines.add(index)
            else:
                code_lines.add(index)

        # 使用 AST 识别 docstring，将其从代码行移至注释行
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module),
                ):
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    ):
                        doc_node = node.body[0]
                        start = doc_node.lineno
                        end = getattr(doc_node, "end_lineno", start)
                        for ln in range(start, end + 1):
                            if ln in code_lines:
                                code_lines.discard(ln)
                                comment_lines.add(ln)
        except SyntaxError:
            pass

        return len(code_lines), len(comment_lines), len(blank_lines)

    @staticmethod
    def _count_java_lines(source: str) -> Tuple[int, int, int]:
        """统计 Java 文件行数分类。

        通过逐行扫描识别单行注释 // 与多行注释 /* */。

        Returns:
            (代码行数, 注释行数, 空行数)
        """
        code = comment = blank = 0
        in_block_comment = False

        for line in source.splitlines():
            stripped = line.strip()
            if not stripped:
                blank += 1
                continue

            is_comment_line = False
            cursor = 0
            length = len(stripped)
            line_has_code = False

            while cursor < length:
                if in_block_comment:
                    end_idx = stripped.find("*/", cursor)
                    if end_idx == -1:
                        is_comment_line = True
                        break
                    in_block_comment = False
                    cursor = end_idx + 2
                else:
                    if stripped.startswith("//", cursor):
                        is_comment_line = True
                        break
                    if stripped.startswith("/*", cursor):
                        end_idx = stripped.find("*/", cursor + 2)
                        if end_idx == -1:
                            in_block_comment = True
                            is_comment_line = True
                            break
                        cursor = end_idx + 2
                        is_comment_line = True
                    else:
                        line_has_code = True
                        break

            if line_has_code:
                code += 1
            elif is_comment_line:
                comment += 1
            else:
                blank += 1

        return code, comment, blank

    # ------------------------------------------------------------------ #
    # 圈复杂度
    # ------------------------------------------------------------------ #

    def _analyze_complexity(
        self, metrics: FileMetrics, file_path: str, language: str
    ) -> None:
        """计算圈复杂度。

        Python 文件使用 radon 库计算；Java 文件使用启发式估算。
        """
        if language == "python":
            metrics.complexity = self._python_complexity(file_path)
        else:
            metrics.complexity = self._java_complexity_heuristic(
                open(file_path, "r", encoding="utf-8", errors="replace").read()
            )

    @staticmethod
    def _python_complexity(file_path: str) -> float:
        """使用 radon 计算 Python 文件平均圈复杂度。

        Returns:
            平均圈复杂度，计算失败时返回 0.0。
        """
        try:
            from radon.complexity import cc_visit
            from radon.visitors import ComplexityVisitor

            with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
                code = fh.read()
            results = cc_visit(code)
            if not results:
                return 0.0
            if isinstance(results, ComplexityVisitor):
                functions = results.functions
            else:
                functions = results
            if not functions:
                return 0.0
            return round(
                sum(getattr(f, "complexity", 0) for f in functions) / len(functions),
                4,
            )
        except Exception:
            return 0.0

    @staticmethod
    def _java_complexity_heuristic(source: str) -> float:
        """Java 圈复杂度启发式估算。

        通过统计决策点关键字数量加 1 来估算平均复杂度。

        Returns:
            估算的平均圈复杂度。
        """
        decision_keywords = (
            "if", "else if", "for", "while", "case", "catch", "&&", "||", "?"
        )
        count = 0
        for kw in decision_keywords:
            count += len(re.findall(r"\b" + re.escape(kw) + r"\b", source))
        method_count = max(len(re.findall(r"\b(?:public|private|protected)\b.*?\(.*?\)\s*\{", source)), 1)
        return round((count + method_count) / method_count, 4)

    # ------------------------------------------------------------------ #
    # 函数长度
    # ------------------------------------------------------------------ #

    def _analyze_functions(
        self, metrics: FileMetrics, source: str, language: str
    ) -> None:
        """检查函数长度，记录最长函数行数。"""
        if language == "python":
            lengths = self._python_function_lengths(source)
        else:
            lengths = self._java_function_lengths(source)

        if lengths:
            metrics.max_function_length = max(lengths)

    @staticmethod
    def _python_function_lengths(source: str) -> List[int]:
        """使用 AST 统计 Python 文件中每个函数的行数。

        Returns:
            各函数体行数列表（含 def 行）。
        """
        lengths: List[int] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return lengths
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                lengths.append(end - start + 1)
        return lengths

    @staticmethod
    def _java_function_lengths(source: str) -> List[int]:
        """统计 Java 文件中每个方法的行数。

        Returns:
            各方法体行数列表。
        """
        lengths: List[int] = []
        lines = source.splitlines()
        method_pattern = re.compile(
            r"\b(?:public|private|protected|static)\b.*?\w+\s*\([^;]*\)\s*\{"
        )
        for idx, line in enumerate(lines):
            if method_pattern.search(line):
                depth = 1
                body = 0
                j = idx + 1
                while j < len(lines) and depth > 0:
                    body += 1
                    depth += lines[j].count("{") - lines[j].count("}")
                    j += 1
                lengths.append(max(body, 0))
        return lengths

    # ------------------------------------------------------------------ #
    # 嵌套深度
    # ------------------------------------------------------------------ #

    def _analyze_nesting(
        self, metrics: FileMetrics, source: str, language: str
    ) -> None:
        """检查最大嵌套深度。"""
        if language == "python":
            metrics.max_nesting_depth = self._python_max_nesting(source)
        else:
            metrics.max_nesting_depth = self._brace_max_nesting(source)

    @staticmethod
    def _python_max_nesting(source: str) -> int:
        """计算 Python 文件最大缩进嵌套深度。

        Returns:
            最大嵌套深度（以 4 空格为一级）。
        """
        max_depth = 0
        for line in source.splitlines():
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(stripped)
            depth = indent // 4
            if depth > max_depth:
                max_depth = depth
        return max_depth

    @staticmethod
    def _brace_max_nesting(source: str) -> int:
        """计算花括号语言的最大嵌套深度。

        Returns:
            最大嵌套深度。
        """
        depth = 0
        max_depth = 0
        in_string = False
        string_char = ""
        i = 0
        length = len(source)
        while i < length:
            ch = source[i]
            if in_string:
                if ch == "\\":
                    i += 2
                    continue
                if ch == string_char:
                    in_string = False
            else:
                if ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                elif ch == "{":
                    depth += 1
                    if depth > max_depth:
                        max_depth = depth
                elif ch == "}":
                    depth = max(depth - 1, 0)
            i += 1
        return max_depth

    # ------------------------------------------------------------------ #
    # TODO / FIXME 标记
    # ------------------------------------------------------------------ #

    def _analyze_markers(self, metrics: FileMetrics, source: str) -> None:
        """统计 TODO 与 FIXME 标记数量。"""
        metrics.todo_count = len(TODO_PATTERN.findall(source))
        metrics.fixme_count = len(FIXME_PATTERN.findall(source))

    # ------------------------------------------------------------------ #
    # 问题评估
    # ------------------------------------------------------------------ #

    def _evaluate_issues(self, metrics: FileMetrics) -> None:
        """根据指标生成问题列表。"""
        if metrics.complexity > self.complexity_threshold:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.WARNING,
                    message=(
                        f"平均圈复杂度 {metrics.complexity} "
                        f"超过阈值 {self.complexity_threshold}"
                    ),
                    metric="complexity",
                )
            )

        if metrics.max_function_length > self.function_length_threshold:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.WARNING,
                    message=(
                        f"最长函数 {metrics.max_function_length} 行 "
                        f"超过阈值 {self.function_length_threshold} 行"
                    ),
                    metric="function_length",
                )
            )

        if metrics.max_nesting_depth > self.nesting_depth_threshold:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.WARNING,
                    message=(
                        f"最大嵌套深度 {metrics.max_nesting_depth} "
                        f"超过阈值 {self.nesting_depth_threshold} 层"
                    ),
                    metric="nesting_depth",
                )
            )

        if metrics.code_lines > 0 and metrics.comment_ratio < 0.1:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.INFO,
                    message=f"注释占比 {metrics.comment_ratio:.1%} 偏低，建议补充文档",
                    metric="comment_ratio",
                )
            )

        if metrics.fixme_count > 0:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.ERROR,
                    message=f"存在 {metrics.fixme_count} 个 FIXME 标记，需立即处理",
                    metric="fixme",
                )
            )

        if metrics.todo_count > 0:
            metrics.issues.append(
                Issue(
                    level=IssueLevel.INFO,
                    message=f"存在 {metrics.todo_count} 个 TODO 标记",
                    metric="todo",
                )
            )

    # ------------------------------------------------------------------ #
    # 辅助方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def _detect_language(file_path: str) -> str:
        """根据文件扩展名推断语言。

        Raises:
            ValueError: 不支持的文件扩展名
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".py":
            return "python"
        if ext in (".java", ".jav"):
            return "java"
        raise ValueError(f"不支持的文件扩展名: {ext}")

    @staticmethod
    def _target_extensions(language: Optional[str]) -> set[str]:
        """返回目标语言对应的文件扩展名集合。"""
        if language == "python":
            return {".py"}
        if language == "java":
            return {".java", ".jav"}
        return {".py", ".java", ".jav"}
