# File: pages/article_detail_page.py
"""文章详情页 Page Object。

封装详情查看、内容验证、删除文章等操作。
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class ArticleDetailPage(BasePage):
    """文章详情页封装。"""

    # ===== 元素定位器 =====
    ARTICLE_TITLE = (By.XPATH, "//h1 | //div[contains(@class,'article-title')]")
    ARTICLE_CONTENT = (
        By.XPATH,
        "//div[contains(@class,'article-content')] | //div[contains(@class,'ProseMirror')]",
    )
    MORE_BUTTON = (By.XPATH, "//*[contains(@class,'more') or @aria-label='更多']")
    DELETE_OPTION = (By.XPATH, "//*[contains(text(),'删除')]")
    DELETE_CONFIRM_BUTTON = (By.XPATH, "//button[contains(text(),'确定') or contains(text(),'确认')]")
    SUCCESS_TIP = (By.XPATH, "//*[contains(text(),'删除成功')]")

    def get_article_title(self) -> str:
        """获取文章标题。"""
        return self.get_text(self.ARTICLE_TITLE, timeout=10)

    def get_article_content(self) -> str:
        """获取文章正文内容。"""
        return self.get_text(self.ARTICLE_CONTENT, timeout=10)

    def delete_article(self):
        """删除当前文章：点击更多 -> 删除 -> 确认。"""
        logger.info("执行删除文章")
        self.click(self.MORE_BUTTON)
        self.click(self.DELETE_OPTION)
        if self.is_element_present(self.DELETE_CONFIRM_BUTTON, timeout=3):
            self.click(self.DELETE_CONFIRM_BUTTON)
            self.wait_for_ajax_complete()

    def is_article_deleted(self) -> bool:
        """判断文章是否已被删除（出现删除成功提示或内容失效提示）。"""
        return (
            self.is_element_visible(self.SUCCESS_TIP, timeout=5)
            or self.is_element_visible(
                (By.XPATH, "//*[contains(text(),'已删除') or contains(text(),'不存在')]"),
                timeout=3,
            )
        )

    def verify_content_matches(self, expected_title: str, expected_content_part: str) -> bool:
        """验证详情页内容与发布内容一致。"""
        actual_title = self.get_article_title()
        actual_content = self.get_article_content()
        title_match = expected_title in actual_title or actual_title in expected_title
        content_match = expected_content_part in actual_content
        logger.info(f"内容验证: title_match={title_match}, content_match={content_match}")
        return title_match and content_match
