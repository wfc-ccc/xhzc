# File: utils/helpers.py
"""辅助函数集合。

仅保留 base_page 不便承载的工具函数：
- 随机数据生成（手机号/字符串/中文/文章标题/正文）
- Ajax 等待（page 层会复用）
- 广告弹窗安全关闭
- 手机号掩码格式化
"""
import random
import string
import time

from config.settings import settings


def random_string(length=8):
    """生成指定长度的随机字符串（大小写字母 + 数字）。"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_chinese_text(length=10):
    """生成指定长度的随机中文字符串。"""
    return "".join(chr(random.randint(0x4E00, 0x9FA5)) for _ in range(length))


def random_article_title():
    """生成随机的文章标题。"""
    return f"自动化测试文章_{random_string(6)}_{random_chinese_text(4)}"


def random_article_content(paragraphs=3):
    """生成随机的文章正文内容。"""
    return "\n".join(
        f"第{i + 1}段：{random_chinese_text(20)}。" for i in range(paragraphs)
    )


def wait_for_ajax(driver, timeout=None):
    """等待页面 Ajax 请求完成（兼容 jQuery 与原生 readyState）。"""
    timeout = timeout or settings.AJAX_WAIT_TIMEOUT
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            jquery_active = driver.execute_script(
                "return (typeof jQuery != 'undefined') ? jQuery.active : 0;"
            )
            ready_state = driver.execute_script("return document.readyState;")
            if jquery_active == 0 and ready_state == "complete":
                return True
        except Exception:
            return False
        time.sleep(settings.POLL_FREQUENCY)
    return False


def safe_close_popup(driver):
    """安全关闭常见广告弹窗，失败则忽略继续。"""
    popup_locators = [
        ("xpath", "//div[contains(@class,'ad')]//i[contains(@class,'close')]"),
        ("xpath", "//button[contains(text(),'关闭')]"),
        ("xpath", "//div[contains(@class,'modal')]//span[contains(@class,'close')]"),
    ]
    for by, value in popup_locators:
        try:
            element = driver.find_element(by, value)
            if element.is_displayed():
                element.click()
                time.sleep(0.5)
        except Exception:
            continue


def mask_phone(phone):
    """返回手机号掩码格式（如 138****0000）。"""
    if len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[7:]}"
