# File: config/settings.py
"""全局配置类。

集中管理 BASE_URL、超时、Headless 开关、测试账号等。
敏感账号从 .env 读取，避免硬编码。
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


class Config:
    """自动化测试全局配置。"""

    # ===== 站点 =====
    BASE_URL = "https://www.xinhup.com/"

    # ===== 浏览器 =====
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    WINDOW_WIDTH = 1440
    WINDOW_HEIGHT = 900
    PAGE_LOAD_TIMEOUT = 30  # 页面加载超时（秒）
    IMPLICIT_WAIT = 5  # 隐式等待（秒）

    # ===== 显式等待 =====
    EXPLICIT_WAIT = 15  # 显式等待最长时长（秒）
    SHORT_WAIT = 5
    POLL_FREQUENCY = 0.5  # 轮询间隔（秒）

    # ===== 测试账号（从 .env 读取） =====
    # 注意：星火新闻登录可能触发验证码，需白名单账号或预处理 Cookie
    TEST_PHONE = os.getenv("TEST_PHONE", "13800000000")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test123456")
    INVALID_PHONE = "12345"  # 格式错误的手机号

    # ===== 路径 =====
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
    SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")

    # ===== 异步加载 =====
    AJAX_WAIT_TIMEOUT = 10

    # ===== 测试数据 =====
    SEARCH_KEYWORD = "科技"
    ARTICLE_CATEGORY = "科技"


# 全局单例
settings = Config()
