"""测试数据加载工具。

提供：
- read_csv：读取 data/*.csv，返回 list[dict] 或参数化 list[tuple]
- read_yaml：读取 data/*.yaml，返回 dict
- get_csv_params：将 CSV 封装为 pytest.mark.parametrize 可用的参数列表
"""
import csv
import os
from typing import Dict, List, Any

import yaml

from config.settings import settings
from utils.logger import logger


def _abs_path(filename: str) -> str:
    """将文件名转换为 data/ 目录下的绝对路径。"""
    if os.path.isabs(filename):
        return filename
    return os.path.join(settings.DATA_DIR, filename)


def read_csv(filename: str, encoding: str = "utf-8-sig") -> List[Dict[str, str]]:
    """读取 CSV 文件，返回字典列表（每行一个 dict，key 为表头）。

    Args:
        filename: CSV 文件名（绝对路径或相对于 data/ 的相对路径）
        encoding: 文件编码，默认 utf-8-sig（兼容 Excel 导出的中文 CSV）

    Returns:
        List[Dict[str, str]]: 行数据列表
    """
    path = _abs_path(filename)
    logger.info(f"读取 CSV 测试数据: {path}")
    rows: List[Dict[str, str]] = []
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 去除每个字段两端空格
            clean_row = {k.strip(): (v.strip() if isinstance(v, str) else v)
                         for k, v in row.items()}
            rows.append(clean_row)
    logger.info(f"读取 {len(rows)} 条数据")
    return rows


def get_csv_params(filename: str, fields: List[str],
                   add_case_id: bool = True) -> List[tuple]:
    """将 CSV 指定列转换为 pytest.mark.parametrize 用的参数列表。

    例：
        @pytest.mark.parametrize(
            "case_id,keyword,expect_code",
            get_csv_params("product_search_data.csv", ["keyword", "expect_code"])
        )
        def test_xxx(case_id, keyword, expect_code):
            ...

    Args:
        filename: CSV 文件名
        fields: 需要提取的字段名列表（不含 case_id）
        add_case_id: 是否将 CSV 首列 case_id 作为第一个参数注入

    Returns:
        List[tuple]: 每条数据一个 tuple，用于 pytest 参数化
    """
    rows = read_csv(filename)
    params: List[tuple] = []
    for row in rows:
        values = []
        if add_case_id:
            values.append(row.get("case_id", ""))
        for f in fields:
            values.append(row.get(f, ""))
        params.append(tuple(values))
    return params


def parse_int(value: str, default: int = None) -> Any:
    """CSV 字段安全转 int，空值返回 default。"""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return default


def parse_float(value: str, default: float = None) -> Any:
    """CSV 字段安全转 float。"""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_str_list(value: str, sep: str = ",") -> List[str]:
    """CSV 中的 "200,400" -> [200, 400] 的 str/int 列表原始分割。"""
    if not value:
        return []
    return [x.strip() for x in value.split(sep) if x.strip()]


def parse_int_list(value: str, sep: str = ",") -> List[int]:
    """CSV 字段 "200,1001,1002" -> [200, 1001, 1002]。"""
    raw = parse_str_list(value, sep)
    result: List[int] = []
    for x in raw:
        try:
            result.append(int(x))
        except ValueError:
            continue
    return result


def read_yaml(filename: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """读取 YAML 文件返回 dict。

    Args:
        filename: YAML 文件名（相对 data/ 或绝对路径）
        encoding: 文件编码

    Returns:
        dict: YAML 解析结果
    """
    path = _abs_path(filename)
    logger.info(f"读取 YAML 测试数据: {path}")
    with open(path, "r", encoding=encoding) as f:
        data = yaml.safe_load(f) or {}
    logger.info(f"读取成功: {len(data)} 个顶级键")
    return data
