# code-quality-checker

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个命令行代码质量检查工具，用于分析 Python 和 Java 源代码文件的质量指标。

## 项目简介

`code-quality-checker` 是一个轻量级、可扩展的代码质量分析工具。它能够对 Python 和 Java 源代码文件进行静态分析，输出包含代码行数统计、圈复杂度、函数长度、嵌套深度以及 TODO/FIXME 标记在内的综合质量报告。工具支持 JSON 与文本两种输出格式，并可通过阈值参数对质量进行门禁判断。

## 功能特性

- **多语言支持**：Python 与 Java 源代码质量分析
- **行数统计**：总行数、代码行、注释行、空行分类统计
- **圈复杂度**：基于 `radon` 计算 cyclomatic complexity
- **函数长度检查**：超过 50 行的函数自动告警
- **嵌套深度检查**：超过 4 层嵌套自动告警
- **标记统计**：TODO / FIXME 标记数量统计
- **多格式输出**：JSON 与易读的文本格式
- **阈值门禁**：支持通过 `--threshold` 设置质量阈值
- **完整类型注解**：全量类型标注，便于 IDE 静态检查

## 安装方式

### 从源码安装

```bash
git clone https://github.com/wjhsky666/code-quality-checker.git
cd code-quality-checker
pip install -r requirements.txt
pip install -e .
```

### 直接安装依赖

```bash
pip install -r requirements.txt
```

## 使用示例

### 检查单个文件

```bash
cqc check src/code_quality_checker/checker.py
```

### 检查目录（指定语言）

```bash
cqc check src/ --lang python
```

### 以 JSON 格式输出

```bash
cqc check src/ --output json
```

### 设置质量阈值（圈复杂度超过 10 报警）

```bash
cqc check src/ --threshold 10
```

### 生成质量报告文件

```bash
cqc report src/ --output json --threshold 10
```

报告将写入当前目录下的 `quality_report.json`。

### 以文本格式查看报告

```bash
cqc report src/code_quality_checker/ --output text
```

## 项目结构

```
code-quality-checker/
├── LICENSE                          # MIT 许可证
├── README.md                        # 项目说明
├── requirements.txt                 # 依赖清单
├── setup.py                         # 包安装配置
├── .gitignore                       # Git 忽略规则
├── src/
│   └── code_quality_checker/
│       ├── __init__.py              # 包初始化
│       ├── cli.py                   # CLI 入口（click）
│       ├── checker.py               # 核心检查逻辑
│       ├── reporter.py              # 报告生成器
│       └── models.py                # 数据模型
└── tests/
    ├── __init__.py                  # 测试包初始化
    ├── test_checker.py              # 核心检查单元测试
    ├── test_cli.py                  # CLI 命令测试
    └── fixtures/
        ├── sample_good.py           # 质量好的示例文件
        └── sample_bad.py            # 质量差的示例文件
```

## 质量指标说明

| 指标 | 说明 | 告警阈值 |
| --- | --- | --- |
| 总行数 | 文件总行数 | - |
| 代码行 | 实际代码行数 | - |
| 注释行 | 注释行数 | - |
| 空行 | 空白行数 | - |
| 圈复杂度 | cyclomatic complexity | > 10 |
| 函数长度 | 单个函数行数 | > 50 行 |
| 嵌套深度 | 代码块嵌套层数 | > 4 层 |
| TODO/FIXME | 待办与修复标记数 | - |

## 开发

### 运行测试

```bash
pip install pytest
pytest tests/ -v
```

### 代码风格

项目使用完整的类型注解与 docstring，遵循 PEP 8 规范。

## License

[MIT License](LICENSE) - Copyright (c) 2026 wjhsky666
