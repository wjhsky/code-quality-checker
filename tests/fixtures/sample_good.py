"""质量好的示例 Python 文件。

本文件作为测试 fixture，展示高质量代码特征：
- 完整的模块、类、函数 docstring
- 函数长度均不超过 50 行
- 嵌套深度均不超过 4 层
- 无待办与修复标记
- 合理的注释占比
"""

from __future__ import annotations

from typing import List, Optional


def add(a: int, b: int) -> int:
    """返回两个整数的和。

    Args:
        a: 第一个加数
        b: 第二个加数

    Returns:
        a 与 b 的和
    """
    return a + b


def is_even(value: int) -> bool:
    """判断整数是否为偶数。

    Args:
        value: 待判断的整数

    Returns:
        若为偶数返回 True，否则返回 False
    """
    return value % 2 == 0


def filter_positive(numbers: List[int]) -> List[int]:
    """过滤出列表中的正数。

    Args:
        numbers: 整数列表

    Returns:
        仅包含正数的新列表
    """
    result: List[int] = []
    for num in numbers:
        if num > 0:
            result.append(num)
    return result


class Calculator:
    """简易计算器类，支持四则运算。"""

    def __init__(self, initial: float = 0.0) -> None:
        """初始化计算器。

        Args:
            initial: 初始值，默认 0.0
        """
        self.value: float = initial

    def add(self, x: float) -> "Calculator":
        """加法运算。

        Args:
            x: 加数

        Returns:
            self，支持链式调用
        """
        self.value += x
        return self

    def subtract(self, x: float) -> "Calculator":
        """减法运算。

        Args:
            x: 减数

        Returns:
            self，支持链式调用
        """
        self.value -= x
        return self

    def multiply(self, x: float) -> "Calculator":
        """乘法运算。

        Args:
            x: 乘数

        Returns:
            self，支持链式调用
        """
        self.value *= x
        return self

    def divide(self, x: float) -> "Calculator":
        """除法运算。

        Args:
            x: 除数

        Returns:
            self，支持链式调用

        Raises:
            ZeroDivisionError: 除数为 0 时抛出
        """
        if x == 0:
            raise ZeroDivisionError("除数不能为 0")
        self.value /= x
        return self

    def reset(self) -> None:
        """重置计算器值为 0。"""
        self.value = 0.0


def find_max(numbers: List[int]) -> Optional[int]:
    """找出列表中的最大值。

    Args:
        numbers: 整数列表

    Returns:
        最大值，空列表返回 None
    """
    if not numbers:
        return None
    maximum = numbers[0]
    for num in numbers[1:]:
        if num > maximum:
            maximum = num
    return maximum
