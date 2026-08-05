# File: pages/home_page.py
"""首页 Page Object。

封装文章列表、点击进入详情、搜索、分类切换等操作。
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage
from utils.logger import logger


class HomePage(BasePage):
    """星火新闻首页封装。"""

    # ===== 元素定位器 =====
    # 顶部导航
    SEARCH_INPUT = (By.XPATH, "//input[@placeholder*='搜索' or contains(@class,'search-input')]")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(@class,'search') or @aria-label='搜索']")

    # 分类 Tab
    CATEGORY_TABS = (By.XPATH, "//div[contains(@class,'channel')]//a | //nav//a[contains(@class,'tab')]")

    # 文章列表项
    ARTICLE_ITEMS = (By.XPATH, "//div[contains(@class,'feed')]//a[contains(@href,'article')] | //div[contains(@class,'article-item')]")

    # 登录入口（未登录状态）
    LOGIN_ENTRY = (By.XPATH, "//*[contains(text(),'登录')]")

    # 发布入口
    PUBLISH_ENTRY = (By.XPATH, "//*[contains(text(),'发布') and (ancestor::button or ancestor::a)]")

    # 用户头像入口
    USER_AVATAR = (By.XPATH, "//div[contains(@class,'avatar')] | //img[contains(@class,'avatar')]")

    # 退出登录
    LOGOUT_BUTTON = (By.XPATH, "//*[contains(text(),'退出') or contains(text(),'退出登录')]")

    def open_home(self):
        """打开星火新闻首页。"""
        self.open()

    def search_article(self, keyword: str):
        """在首页搜索框输入关键词并搜索。

        Args:
            keyword: 搜索关键词
        """
        logger.info(f"搜索文章: {keyword}")
        search_box = self.find_visible_element(self.SEARCH_INPUT)
        self.input_text_to_element(search_box, keyword)
        search_box.send_keys(Keys.ENTER)
        self.wait_for_ajax_complete()

    def get_search_results(self):
        """获取搜索结果列表文本。"""
        results = []
        try:
            items = self.find_elements(self.ARTICLE_ITEMS, timeout=10)
            for item in items:
                text = item.text.strip()
                if text:
                    results.append(text)
        except Exception as e:
            logger.warning(f"获取搜索结果失败: {e}")
        return results

    def click_category(self, category_name: str):
        """点击指定分类 Tab。

        Args:
            category_name: 分类名称（如 "推荐"、"科技"）
        """
        logger.info(f"切换分类: {category_name}")
        locator = (By.XPATH, f"//a[contains(text(),'{category_name}')] | //span[contains(text(),'{category_name}')]")
        self.click(locator)
        self.wait_for_ajax_complete()

    def get_article_list(self):
        """获取首页文章列表的标题文本。"""
        titles = []
        try:
            items = self.find_elements(self.ARTICLE_ITEMS, timeout=10)
            for item in items:
                text = item.text.strip()
                if text:
                    titles.append(text)
        except Exception as e:
            logger.warning(f"获取文章列表失败: {e}")
        return titles

    def click_article_by_title(self, title_keyword: str):
        """根据标题关键词点击文章。

        Args:
            title_keyword: 标题中包含的关键词
        """
        locator = (By.XPATH, f"//a[contains(text(),'{title_keyword}')]")
        self.click(locator)
        self.wait_for_ajax_complete()

    def is_login_entry_visible(self) -> bool:
        """判断登录入口是否可见（用于登出后验证）。"""
        return self.is_element_visible(self.LOGIN_ENTRY, timeout=5)

    def click_publish_entry(self):
        """点击发布按钮。"""
        self.click(self.PUBLISH_ENTRY)
        self.wait_for_ajax_complete()

    def click_user_avatar(self):
        """点击右上角用户头像，弹出下拉菜单。"""
        self.click(self.USER_AVATAR)

    def logout(self):
        """退出登录。"""
        logger.info("执行退出登录")
        self.click_user_avatar()
        if self.is_element_present(self.LOGOUT_BUTTON, timeout=3):
            self.click(self.LOGOUT_BUTTON)
            self.wait_for_ajax_complete()
