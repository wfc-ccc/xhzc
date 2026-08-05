# File: utils/csv_reader.py
"""CSV 数据文件读取工具。

提供通用的 CSV 读取函数，用于数据驱动测试。
- 使用 Python 内置 csv 模块，保持轻量，不引入 pandas。
- 自动跳过空行。
- 字符串首尾去空格，TRUE/FALSE 转为 Python 布尔值。
- 文件编码统一使用 utf-8-sig，兼容 Excel 编辑后产生的 BOM 头。
"""
import csv
import os
import logging

logger = logging.getLogger(__name__)

# TRUE/FALSE 字符串候选集合（大小写不敏感），用于布尔值转换
_TRUE_TOKENS = {"true", "t", "yes", "y", "1"}
_FALSE_TOKENS = {"false", "f", "no", "n", "0", ""}


def _convert_value(value: str):
    """对单个字段值进行类型转换。

    - 去除首尾空格
    - 若为 TRUE/FALSE 字符串则转为 Python bool
    - 其余保持字符串

    Args:
        value: 原始字符串值

    Returns:
        转换后的值（str 或 bool）
    """
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    lower = stripped.lower()
    if lower in _TRUE_TOKENS and lower != "":
        return True
    if lower in _FALSE_TOKENS:
        # 空字符串也算 False
        return False
    return stripped


def read_csv_to_list(file_path: str) -> list:
    """读取 CSV 文件并返回字典列表。

    每条记录为一个 dict，键为表头字段名。
    - 自动跳过空行。
    - 字符串首尾去空格，TRUE/FALSE 转布尔值。
    - 文件不存在则抛出 FileNotFoundError。

    Args:
        file_path: CSV 文件路径（相对路径会基于项目根目录解析）

    Returns:
        List[dict]: 测试数据列表

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    # 支持相对路径：基于项目根目录解析
    if not os.path.isabs(file_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"CSV 数据文件不存在: {file_path}。请检查路径或创建示例数据文件。"
        )

    data_list = []
    # 编码使用 utf-8-sig，兼容 Excel 编辑后的 BOM 头
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 跳过完全空白的行（所有字段都为空）
            if not row or all(
                (v is None or str(v).strip() == "") for v in row.values()
            ):
                continue
            # 对每个字段进行类型转换
            converted = {k: _convert_value(v) for k, v in row.items() if k is not None}
            data_list.append(converted)

    logger.info(f"从 {file_path} 读取到 {len(data_list)} 条测试数据")
    return data_list


def get_data_path(filename: str) -> str:
    """根据文件名返回 data 目录下的绝对路径。

    Args:
        filename: CSV 文件名（如 "login_data.csv"）

    Returns:
        绝对路径
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "data", filename)
