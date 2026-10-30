"""code-quality-checker 安装配置。

使用 setuptools 构建与安装包。
"""

from setuptools import find_packages, setup

setup(
    name="code-quality-checker",
    version="1.0.0",
    description="一个命令行代码质量检查工具，用于分析 Python 和 Java 源代码文件的质量指标。",
    long_description=(
        "code-quality-checker 是一个轻量级代码质量分析工具，"
        "支持 Python 与 Java 源代码的行数统计、圈复杂度计算、"
        "函数长度检查、嵌套深度检查以及 TODO/FIXME 标记统计。"
    ),
    long_description_content_type="text/plain",
    author="wjhsky666",
    author_email="wjhsky666@users.noreply.github.com",
    url="https://github.com/wjhsky666/code-quality-checker",
    license="MIT",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click>=8.0.0",
        "radon>=6.0.0",
        "pygments>=2.15.0",
    ],
    entry_points={
        "console_scripts": [
            "cqc=code_quality_checker.cli:main",
            "code-quality-checker=code_quality_checker.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
