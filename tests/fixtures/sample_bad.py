"""质量差的示例 Python 文件。

本文件作为测试 fixture，展示低质量代码特征：
- 存在超长函数（超过 50 行）
- 存在深嵌套（超过 4 层）
- 缺少注释与 docstring
- 包含待办与修复标记
"""

import os
import sys


def long_function_with_many_lines(data, threshold, flag, mode):
    result = []
    secondary = []
    tertiary = []
    cache = {}
    counter = 0
    skip = False
    for i in range(len(data)):
        item = data[i]
        counter += 1
        if item is None:
            result.append(0)
            continue
        if skip:
            skip = False
            continue
        if isinstance(item, dict):
            for key in item:
                value = item[key]
                if value is None:
                    continue
                if isinstance(value, list):
                    for v in value:
                        if v is None:
                            continue
                        if v > threshold:
                            result.append(v)
                        else:
                            secondary.append(v)
                elif isinstance(value, dict):
                    for sub_key in value:
                        sub_val = value[sub_key]
                        if sub_val is not None:
                            tertiary.append(sub_val)
                else:
                    if value > threshold:
                        result.append(value)
                    else:
                        secondary.append(value)
        elif isinstance(item, list):
            for v in item:
                if v is None:
                    continue
                if flag and v > threshold:
                    result.append(v)
                else:
                    secondary.append(v)
        elif isinstance(item, (int, float)):
            if mode == "strict" and item > threshold:
                result.append(item)
            elif mode == "loose" and item >= 0:
                result.append(item)
            else:
                tertiary.append(item)
        else:
            cache[counter] = item
        if counter % 100 == 0:
            skip = True
    # TODO: 需要优化这个函数的性能
    # FIXME: 当 data 为 None 时会抛出异常
    return result, secondary, tertiary, cache


def deeply_nested_function(matrix):
    total = 0
    for row in matrix:
        if row:
            for col in row:
                if col:
                    for element in col:
                        if element:
                            for sub in element:
                                if sub:
                                    total += sub
    return total


def no_docstring_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        return x
    return 0


class BadClass:
    def __init__(self):
        self.data = []
    def add(self, item):
        # TODO: 添加类型检查
        self.data.append(item)
    def process(self):
        out = []
        for i in range(len(self.data)):
            if self.data[i] is not None:
                if isinstance(self.data[i], int):
                    if self.data[i] > 0:
                        if self.data[i] < 100:
                            out.append(self.data[i])
        # FIXME: 这里逻辑有 bug
        return out
