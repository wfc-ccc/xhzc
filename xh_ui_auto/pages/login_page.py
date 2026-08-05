# File: pages/login_page.py
"""登录页面 Page Object。

支持手机号/密码登录，处理 QQ 登录 iframe 切换。
注意：星火新闻登录可能触发滑块验证码，需使用白名单账号或手动预处理 Cookie。
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """登录页面封装。"""

    # ===== 页面元素定位器（统一放在类顶部便于维护） =====
    # 登录入口
    LOGIN_ENTRY = (By.XPATH, "//div[contains(text(),'登录')] | //a[contains(text(),'登录')]")

    # 登录方式切换 Tab
    PHONE_LOGIN_TAB = (By.XPATH, "//*[contains(text(),'手机号登录')]")
    PASSWORD_LOGIN_TAB = (By.XPATH, "//*[contains(text(),'密码登录')]")

    # 输入框
    PHONE_INPUT = (By.XPATH, "//input[@placeholder='请输入手机号' or @name='mobile' or @type='tel']")
    PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='请输入密码' or @type='password' or @name='password']")
    CAPTCHA_INPUT = (By.XPATH, "//input[@placeholder*='验证码' or @name='captcha']")

    # 登录按钮
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(),'登录') or contains(@class,'login-btn')]")

    # 错误提示
    ERROR_TIP = (By.XPATH, "//div[contains(@class,'error') or contains(@class,'tip') or contains(@class,'toast')]")

    # QQ 登录相关
    QQ_LOGIN_ICON = (By.XPATH, "//i[contains(@class,'qq') or @title='QQ登录']")
    QQ_LOGIN_IFRAME = (By.ID, "ptlogin_iframe")
    QQ_ACCOUNT_INPUT = (By.ID, "u")
    QQ_PASSWORD_INPUT = (By.ID, "p")
    QQ_LOGIN_BTN = (By.ID, "login_button")

    # 登录后右上角用户头像/昵称
    USER_AVATAR = (By.XPATH, "//div[contains(@class,'avatar')] | //img[contains(@class,'avatar')]")
    USER_NICKNAME = (By.XPATH, "//div[contains(@class,'user')]//span[contains(@class,'name')]")

    def open_login_page(self):
        """打开登录页面。"""
        self.open()
        # 首页可能直接有登录入口
        if self.is_element_present(self.LOGIN_ENTRY):
            self.click(self.LOGIN_ENTRY)
        logger.info("已打开登录页面")

    def switch_to_password_login(self):
        """切换到密码登录方式（部分入口默认为验证码登录）。"""
        try:
            if self.is_element_present(self.PASSWORD_LOGIN_TAB, timeout=3):
                self.click(self.PASSWORD_LOGIN_TAB)
                logger.info("已切换到密码登录")
        except Exception as e:
            logger.warning(f"切换密码登录方式失败（可能默认即密码登录）: {e}")

    def login_with_password(self, phone: str, password: str):
        """使用手机号 + 密码登录。

        Args:
            phone: 手机号
            password: 密码

        注意：若触发验证码需使用白名单账号或手动预处理 Cookie
        """
        logger.info(f"开始手机号密码登录: phone={phone}")
        self.switch_to_password_login()
        self.input_text(self.PHONE_INPUT, phone)
        self.input_text(self.PASSWORD_INPUT, password)
        # 处理可能的验证码输入框（若存在）
        if self.is_element_present(self.CAPTCHA_INPUT, timeout=2):
            logger.warning("检测到验证码输入框，请使用白名单账号或手动预处理 Cookie")
        self.click(self.LOGIN_BUTTON)
        self.wait_for_ajax_complete()

    def login_with_qq(self, qq_account: str, qq_password: str):
        """使用 QQ 账号登录（处理 iframe 切换）。

        Args:
            qq_account: QQ 号
            qq_password: QQ 密码
        """
        logger.info("使用 QQ 登录")
        self.click(self.QQ_LOGIN_ICON)
        # 切换到 QQ 登录 iframe
        self.switch_to_frame(self.QQ_LOGIN_IFRAME)
        self.input_text(self.QQ_ACCOUNT_INPUT, qq_account)
        self.input_text(self.QQ_PASSWORD_INPUT, qq_password)
        self.click(self.QQ_LOGIN_BTN)
        # QQ 登录完成后切回主文档
        self.switch_to_default_content()

    def get_error_tip(self) -> str:
        """获取登录失败时的错误提示文本。"""
        try:
            return self.get_text(self.ERROR_TIP, timeout=5)
        except Exception:
            return ""

    def is_login_success(self) -> bool:
        """判断是否登录成功（右上角出现用户头像/昵称）。"""
        return self.is_element_visible(self.USER_AVATAR, timeout=10) or \
               self.is_element_visible(self.USER_NICKNAME, timeout=3)
