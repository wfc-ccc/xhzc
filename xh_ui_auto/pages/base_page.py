# File: pages/base_page.py
"""Page Object 基类。

封装 Selenium 常用操作：find / click / input / wait / screenshot / iframe。
"""
import os
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import settings
from utils.logger import logger
from utils.helpers import wait_for_ajax, safe_close_popup


class BasePage:
    """所有 Page 类的基类。"""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    # ===== 导航 =====
    def open(self, url=None):
        """打开指定 URL，默认 BASE_URL；等待 Ajax 并尝试关闭弹窗。"""
        target = url or settings.BASE_URL
        logger.info(f"打开页面: {target}")
        self.driver.get(target)
        wait_for_ajax(self.driver)
        safe_close_popup(self.driver)

    # ===== 元素查找 =====
    def find_element(self, locator: tuple, timeout=None) -> WebElement:
        """显式等待并返回出现的元素。"""
        timeout = timeout or settings.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout, settings.POLL_FREQUENCY).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator: tuple, timeout=None):
        """显式等待并返回多个元素。"""
        timeout = timeout or settings.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout, settings.POLL_FREQUENCY).until(
            EC.presence_of_all_elements_located(locator)
        )

    def find_visible_element(self, locator: tuple, timeout=None) -> WebElement:
        """显式等待并返回可见元素。"""
        timeout = timeout or settings.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout, settings.POLL_FREQUENCY).until(
            EC.visibility_of_element_located(locator)
        )

    # ===== 交互 =====
    def click(self, locator: tuple, timeout=None):
        """显式等待可点击后点击，自动滚动到元素中央。"""
        timeout = timeout or settings.EXPLICIT_WAIT
        element = WebDriverWait(self.driver, timeout, settings.POLL_FREQUENCY).until(
            EC.element_to_be_clickable(locator)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        element.click()
        logger.info(f"点击元素: {locator}")

    def click_element(self, element: WebElement):
        """对已查找到的元素点击（滚动到中央后点击）。"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        element.click()

    def input_text(self, locator: tuple, text: str, clear_first=True):
        """向定位器输入文本，默认先清空。"""
        element = self.find_visible_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.info(f"输入文本到 {locator}: {text}")

    def input_text_to_element(self, element: WebElement, text: str, clear_first=True):
        """向已查找到的元素输入文本。"""
        if clear_first:
            element.clear()
        element.send_keys(text)

    # ===== 等待 =====
    def wait_for_ajax_complete(self, timeout=None):
        """等待页面 Ajax 完成。"""
        return wait_for_ajax(self.driver, timeout)

    # ===== 文本 =====
    def get_text(self, locator: tuple, timeout=None) -> str:
        """获取可见元素的文本。"""
        return self.find_visible_element(locator, timeout).text

    # ===== 判断 =====
    def is_element_present(self, locator: tuple, timeout=None) -> bool:
        """元素是否存在（不抛异常）。"""
        try:
            self.find_element(locator, timeout or settings.SHORT_WAIT)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_element_visible(self, locator: tuple, timeout=None) -> bool:
        """元素是否可见。"""
        try:
            self.find_visible_element(locator, timeout or settings.SHORT_WAIT)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    # ===== iframe =====
    def switch_to_frame(self, frame_locator):
        """切换到 iframe（接受定位器元组或 WebElement）。"""
        frame = self.find_element(frame_locator) if isinstance(frame_locator, tuple) \
            else frame_locator
        self.driver.switch_to.frame(frame)
        logger.info(f"切换到 iframe: {frame_locator}")

    def switch_to_default_content(self):
        """切回主文档。"""
        self.driver.switch_to.default_content()
        logger.info("切换回主文档")

    # ===== 截图 =====
    def screenshot(self, filename: str = None) -> str:
        """保存截图到 reports/screenshots/。"""
        os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        filepath = os.path.join(settings.SCREENSHOT_DIR, f"{filename}.png")
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"截图已保存: {filepath}")
        except Exception as e:
            logger.error(f"截图失败: {e}")
        return filepath
