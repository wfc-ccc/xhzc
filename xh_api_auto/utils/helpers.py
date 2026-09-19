import random
import string
import time
from datetime import datetime
from typing import Any


def gen_random_str(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def gen_order_no(prefix="TEST"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{prefix}{timestamp}{rand}"


def current_time_str(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)


def sleep(seconds):
    time.sleep(seconds)


def assert_common(response, expected_code=200, message_contains=None):
    assert isinstance(response, dict), f"响应类型异常，期望 dict，实际 {type(response)}"
    assert "code" in response, f"响应缺少 code 字段: {response}"
    assert "message" in response, f"响应缺少 message 字段: {response}"
    assert "data" in response, f"响应缺少 data 字段: {response}"
    assert response["code"] == expected_code, (
        f"状态码不匹配：期望 {expected_code}，实际 {response['code']}，"
        f"message={response.get('message')}"
    )
    if message_contains is not None:
        assert message_contains in str(response["message"]), (
            f"message 期望包含 '{message_contains}'，实际为 '{response.get('message')}'"
        )


def assert_pagination(paginated_data, expected_size=None):
    assert "total" in paginated_data, "分页数据缺少 total 字段"
    assert "list" in paginated_data, "分页数据缺少 list 字段"
    assert isinstance(paginated_data["list"], list), "list 字段必须为数组类型"
    assert isinstance(paginated_data["total"], int), "total 字段必须为整数"
    if expected_size is not None:
        assert len(paginated_data["list"]) <= expected_size, (
            f"每页数量超出：期望 <= {expected_size}，实际 {len(paginated_data['list'])}"
        )


def get_nested_value(data, path, default=None):
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        else:
            return default
    return current