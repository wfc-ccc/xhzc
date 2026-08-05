# File: testcases/conftest.py
"""pytest 全局 fixtures 配置。

提供：
- driver: 每个用例独立的 Chrome WebDriver
- logged_in_driver: 已登录态 WebDriver
- 失败用例自动截图到 reports/screenshots/
"""
import os
import sys
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from utils.logger import logger
from pages.login_page import LoginPage


def _create_chrome_driver() -> webdriver.Chrome:
    """创建 Chrome WebDriver。"""
    options = ChromeOptions()
    if settings.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


@pytest.fixture(scope="function")
def driver():
    """每个用例独立的 Chrome WebDriver。"""
    logger.info("========== 创建 WebDriver ==========")
    drv = _create_chrome_driver()
    drv.get(settings.BASE_URL)
    yield drv
    try:
        drv.quit()
    except Exception as e:
        logger.warning(f"关闭 WebDriver 异常: {e}")
    logger.info("========== WebDriver 已关闭 ==========")


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """已登录态 WebDriver；登录失败（如验证码）则跳过用例。"""
    login_page = LoginPage(driver)
    login_page.open_login_page()
    login_page.login_with_password(settings.TEST_PHONE, settings.TEST_PASSWORD)
    if not login_page.is_login_success():
        pytest.skip("登录失败，可能触发验证码。请使用白名单账号或手动预处理 Cookie。")
    yield driver


# ===== 命令行参数 =====
def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False,
                     help="以 headless 模式运行浏览器")


@pytest.fixture(scope="session", autouse=True)
def _apply_cli_options(request):
    if request.config.getoption("--headless"):
        settings.HEADLESS = True


# ===== 失败自动截图 =====
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver is None:
            return
        try:
            os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
            filename = f"FAIL_{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(settings.SCREENSHOT_DIR, filename)
            driver.save_screenshot(filepath)
            logger.error(f"用例失败截图: {filepath}")
            if hasattr(report, "extra"):
                report.extra.append({"name": "screenshot", "path": filepath})
        except Exception as e:
            logger.error(f"失败截图异常: {e}")
