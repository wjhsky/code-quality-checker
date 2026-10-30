"""code_quality_checker CLI 入口模块。

基于 click 库实现命令行接口，提供 check 与 report 两个子命令。

用法示例::

    cqc check src/ --lang python --output text
    cqc report src/ --output json --threshold 10
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import click

from .checker import CodeChecker
from .models import QualityReport
from .reporter import Reporter


@click.group()
@click.version_option(package_name="code-quality-checker")
def cli() -> None:
    """code-quality-checker - 代码质量检查命令行工具。

    支持 Python 与 Java 源代码的静态质量分析。
    """


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--lang",
    type=click.Choice(["python", "java"], case_sensitive=False),
    default=None,
    help="指定源代码语言，不指定则根据扩展名推断。",
)
@click.option(
    "--output",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
    help="输出格式，默认 text。",
)
@click.option(
    "--threshold",
    type=float,
    default=10.0,
    help="圈复杂度质量阈值，默认 10.0。",
)
def check(
    path: str,
    lang: Optional[str],
    output: str,
    threshold: float,
) -> None:
    """检查单个文件或目录的代码质量。

    PATH 可以是文件路径或目录路径。
    """
    checker = CodeChecker(complexity_threshold=threshold)
    report = _run_check(checker, path, lang, threshold)
    _emit(report, output)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--lang",
    type=click.Choice(["python", "java"], case_sensitive=False),
    default=None,
    help="指定源代码语言，不指定则根据扩展名推断。",
)
@click.option(
    "--output",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
    help="输出格式，默认 text。",
)
@click.option(
    "--threshold",
    type=float,
    default=10.0,
    help="圈复杂度质量阈值，默认 10.0。",
)
@click.option(
    "--outfile",
    type=click.Path(),
    default=None,
    help="报告输出文件路径，不指定则使用默认文件名。",
)
def report(
    path: str,
    lang: Optional[str],
    output: str,
    threshold: float,
    outfile: Optional[str],
) -> None:
    """生成质量报告文件。

    PATH 可以是文件路径或目录路径。报告将写入文件。
    """
    checker = CodeChecker(complexity_threshold=threshold)
    quality_report = _run_check(checker, path, lang, threshold)
    reporter = Reporter(quality_report)

    if outfile is None:
        ext = ".json" if output.lower() == "json" else ".txt"
        outfile = f"quality_report{ext}"

    written = reporter.write(outfile, output)
    click.echo(f"报告已写入: {written}")

    # 同时在终端输出摘要
    click.echo("")
    click.echo(reporter.to_text().split("\n【")[0])


# ---------------------------------------------------------------------- #
# 内部辅助函数
# ---------------------------------------------------------------------- #


def _run_check(
    checker: CodeChecker,
    path: str,
    lang: Optional[str],
    threshold: float,
) -> QualityReport:
    """执行检查并构建 QualityReport。

    Args:
        checker: 检查器实例
        path: 文件或目录路径
        lang: 语言限定
        threshold: 质量阈值

    Returns:
        构建完成的 QualityReport
    """
    if os.path.isfile(path):
        metrics = checker.check_file(path, lang)
        files = [metrics]
    else:
        files = checker.check_directory(path, lang)

    return QualityReport(files=files, threshold=threshold)


def _emit(report: QualityReport, output: str) -> None:
    """将报告输出到终端。

    Args:
        report: 质量报告
        output: 输出格式
    """
    reporter = Reporter(report)
    if output.lower() == "json":
        click.echo(reporter.to_json())
    else:
        click.echo(reporter.to_text())

    # 以退出码反映质量门禁结果
    if not report.passed:
        sys.exit(1)


def main() -> None:
    """CLI 主入口，供 setup.py console_scripts 调用。"""
    cli()


if __name__ == "__main__":
    main()
