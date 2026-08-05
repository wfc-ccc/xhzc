# File: pages/user_center_page.py
"""个人中心 Page Object。

封装查看/修改昵称、查看手机号掩码等操作。
"""
import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class UserCenterPage(BasePage):
    """个人中心页面封装。"""

    # ===== 元素定位器 =====
    USER_AVATAR = (By.XPATH, "//div[contains(@class,'avatar')] | //img[contains(@class,'avatar')]")
    USER_CENTER_LINK = (By.XPATH, "//*[contains(text(),'个人主页') or contains(text(),'我的主页')]")

    NICKNAME_DISPLAY = (
        By.XPATH,
        "//div[contains(@class,'name') or contains(@class,'nickname')]//span | //h2[contains(@class,'name')]",
    )
    PHONE_MASK_DISPLAY = (
        By.XPATH,
        "//*[contains(text(),'手机') or contains(@class,'mobile') or contains(@class,'phone')]",
    )

    EDIT_PROFILE_BUTTON = (By.XPATH, "//*[contains(text(),'编辑') or contains(text(),'修改资料')]")
    NICKNAME_INPUT = (
        By.XPATH,
        "//input[@placeholder*='昵称' or @name='nickname'] | //input[contains(@class,'nickname')]",
    )
    SAVE_BUTTON = (By.XPATH, "//button[contains(text(),'保存') or contains(text(),'确定')]")

    SUCCESS_TIP = (By.XPATH, "//*[contains(text(),'修改成功') or contains(text(),'保存成功')]")

    def open_user_center(self):
        """进入个人中心。"""
        self.open()
        self.click(self.USER_AVATAR)
        if self.is_element_present(self.USER_CENTER_LINK, timeout=3):
            self.click(self.USER_CENTER_LINK)
            self.wait_for_ajax_complete()
        logger.info("已进入个人中心")

    def get_nickname(self) -> str:
        """获取当前显示的昵称。"""
        return self.get_text(self.NICKNAME_DISPLAY, timeout=10)

    def get_phone_mask(self) -> str:
        """获取手机号掩码展示文本。"""
        return self.get_text(self.PHONE_MASK_DISPLAY, timeout=5)

    def modify_nickname(self, new_nickname: str):
        """修改昵称。"""
        logger.info(f"修改昵称为: {new_nickname}")
        self.click(self.EDIT_PROFILE_BUTTON)
        self.input_text(self.NICKNAME_INPUT, new_nickname)
        self.click(self.SAVE_BUTTON)
        self.wait_for_ajax_complete()

    def is_modify_success(self) -> bool:
        """判断修改是否成功。"""
        return self.is_element_visible(self.SUCCESS_TIP, timeout=5)

    def verify_phone_mask_format(self, phone_mask: str) -> bool:
        """校验手机号掩码格式（如 138****0000）。"""
        return re.search(r"1\d{2}\*{4}\d{4}", phone_mask) is not None
