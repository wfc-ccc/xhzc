# File: pages/register_page.py
"""注册页面 Page Object。

星火新闻 PC 网页版可能没有独立的注册入口（通常依赖移动端 App 或第三方登录注册），
本类提供基础封装，若页面无对应入口则相关方法会优雅降级。
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class RegisterPage(BasePage):
    """注册页面封装。"""

    # ===== 元素定位器 =====
    REGISTER_ENTRY = (By.XPATH, "//*[contains(text(),'注册') or contains(text(),'立即注册')]")
    PHONE_INPUT = (By.XPATH, "//input[@placeholder*='手机号' or @name='mobile']")
    SMS_CODE_INPUT = (By.XPATH, "//input[@placeholder*='验证码' or @name='code']")
    SEND_SMS_BUTTON = (By.XPATH, "//button[contains(text(),'获取验证码') or contains(text(),'发送')]")
    PASSWORD_INPUT = (By.XPATH, "//input[@type='password' or @name='password']")
    NICKNAME_INPUT = (By.XPATH, "//input[@placeholder*='昵称' or @name='nickname']")
    AGREE_CHECKBOX = (By.XPATH, "//input[@type='checkbox']")
    REGISTER_SUBMIT_BUTTON = (By.XPATH, "//button[contains(text(),'注册') and not(contains(text(),'获取'))]")
    ERROR_TIP = (By.XPATH, "//div[contains(@class,'error') or contains(@class,'tip')]")

    def open_register_page(self):
        """打开注册页面（若存在独立注册入口）。"""
        self.open()
        try:
            if self.is_element_present(self.REGISTER_ENTRY, timeout=3):
                self.click(self.REGISTER_ENTRY)
                logger.info("已打开注册页面")
            else:
                logger.warning("未找到注册入口，可能星火新闻 PC 端不支持独立注册")
        except Exception as e:
            logger.warning(f"打开注册页面失败: {e}")

    def fill_register_form(self, phone: str, password: str, nickname: str = "", sms_code: str = ""):
        """填写注册表单。

        Args:
            phone: 手机号
            password: 密码
            nickname: 昵称（可选）
            sms_code: 短信验证码（实际场景需手动获取并传入）
        """
        self.input_text(self.PHONE_INPUT, phone)
        if self.is_element_present(self.SEND_SMS_BUTTON, timeout=2):
            self.click(self.SEND_SMS_BUTTON)
        if sms_code:
            self.input_text(self.SMS_CODE_INPUT, sms_code)
        self.input_text(self.PASSWORD_INPUT, password)
        if nickname and self.is_element_present(self.NICKNAME_INPUT, timeout=2):
            self.input_text(self.NICKNAME_INPUT, nickname)
        # 勾选同意协议
        try:
            checkbox = self.find_element(self.AGREE_CHECKBOX, timeout=2)
            if not checkbox.is_selected():
                checkbox.click()
        except Exception:
            pass

    def submit_register(self):
        """提交注册。"""
        self.click(self.REGISTER_SUBMIT_BUTTON)
        self.wait_for_ajax_complete()
        logger.info("已提交注册")

    def get_error_tip(self) -> str:
        """获取注册错误提示。"""
        try:
            return self.get_text(self.ERROR_TIP, timeout=5)
        except Exception:
            return ""

    def is_register_supported(self) -> bool:
        """判断页面是否支持独立注册。"""
        return self.is_element_present(self.REGISTER_ENTRY, timeout=3)
