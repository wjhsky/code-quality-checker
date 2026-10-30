"""CLI 命令单元测试。

使用 click.testing.CliRunner 测试 check 与 report 子命令的输入输出。
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from click.testing import CliRunner

from code_quality_checker.cli import cli

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_GOOD = os.path.join(FIXTURES_DIR, "sample_good.py")
SAMPLE_BAD = os.path.join(FIXTURES_DIR, "sample_bad.py")


class TestCliCheckCommand(unittest.TestCase):
    """cqc check 命令测试。"""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_check_single_file_text_output(self) -> None:
        """check 单个文件，text 格式应成功输出。"""
        result = self.runner.invoke(cli, ["check", SAMPLE_GOOD, "--output", "text"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("代码质量检查报告", result.output)

    def test_check_single_file_json_output(self) -> None:
        """check 单个文件，json 格式应输出有效 JSON。"""
        result = self.runner.invoke(cli, ["check", SAMPLE_GOOD, "--output", "json"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIn("summary", data)
        self.assertIn("files", data)

    def test_check_directory(self) -> None:
        """check 目录应分析目录下所有文件。"""
        result = self.runner.invoke(cli, ["check", FIXTURES_DIR, "--output", "json"])
        # fixtures 包含质量差的文件，门禁可能未通过，故不断言退出码
        data = json.loads(result.output)
        self.assertGreater(data["summary"]["file_count"], 0)

    def test_check_with_lang_option(self) -> None:
        """--lang 参数应正常工作。"""
        result = self.runner.invoke(
            cli, ["check", SAMPLE_GOOD, "--lang", "python", "--output", "json"]
        )
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data["files"][0]["language"], "python")

    def test_check_with_threshold_option(self) -> None:
        """--threshold 参数应体现在报告中。"""
        result = self.runner.invoke(
            cli, ["check", SAMPLE_GOOD, "--output", "json", "--threshold", "5"]
        )
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data["threshold"], 5.0)

    def test_check_nonexistent_path(self) -> None:
        """check 不存在的路径应返回非零退出码。"""
        result = self.runner.invoke(cli, ["check", "/nonexistent/path"])
        self.assertNotEqual(result.exit_code, 0)

    def test_check_bad_file_nonzero_exit(self) -> None:
        """check 质量差的文件应因门禁未通过返回非零退出码。"""
        result = self.runner.invoke(cli, ["check", SAMPLE_BAD, "--output", "json"])
        self.assertNotEqual(result.exit_code, 0)


class TestCliReportCommand(unittest.TestCase):
    """cqc report 命令测试。"""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_report_text_output(self) -> None:
        """report 命令应生成文本报告文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "report.txt")
            result = self.runner.invoke(
                cli, ["report", SAMPLE_GOOD, "--output", "text", "--outfile", outfile]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.isfile(outfile))
            with open(outfile, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("代码质量检查报告", content)

    def test_report_json_output(self) -> None:
        """report 命令应生成 JSON 报告文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "report.json")
            result = self.runner.invoke(
                cli, ["report", SAMPLE_GOOD, "--output", "json", "--outfile", outfile]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.isfile(outfile))
            with open(outfile, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertIn("summary", data)

    def test_report_default_outfile(self) -> None:
        """不指定 --outfile 时应使用默认文件名。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = self.runner.invoke(
                    cli, ["report", SAMPLE_GOOD, "--output", "json"]
                )
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(os.path.isfile("quality_report.json"))
            finally:
                os.chdir(old_cwd)

    def test_report_directory(self) -> None:
        """report 目录应生成包含多个文件的报告。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "report.json")
            result = self.runner.invoke(
                cli, ["report", FIXTURES_DIR, "--output", "json", "--outfile", outfile]
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertGreater(data["summary"]["file_count"], 0)


class TestCliHelp(unittest.TestCase):
    """CLI 帮助信息测试。"""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_main_help(self) -> None:
        """主命令帮助应包含子命令说明。"""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("check", result.output)
        self.assertIn("report", result.output)

    def test_check_help(self) -> None:
        """check 子命令帮助应包含参数说明。"""
        result = self.runner.invoke(cli, ["check", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--lang", result.output)
        self.assertIn("--output", result.output)
        self.assertIn("--threshold", result.output)

    def test_report_help(self) -> None:
        """report 子命令帮助应包含参数说明。"""
        result = self.runner.invoke(cli, ["report", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--output", result.output)
        self.assertIn("--outfile", result.output)


if __name__ == "__main__":
    unittest.main()
