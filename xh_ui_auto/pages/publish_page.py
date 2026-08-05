# File: pages/publish_page.py
"""发布页面 Page Object。

封装发布文章/微头条的操作，包含富文本编辑器 ProseMirror 的处理。
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage
from utils.logger import logger


class PublishPage(BasePage):
    """发布页面封装。"""

    # ===== 元素定位器 =====
    # 发布入口
    PUBLISH_ENTRY = (By.XPATH, "//*[contains(text(),'发布') and (ancestor::button or ancestor::a)]")

    # 发布类型选择
    ARTICLE_TYPE_TAB = (By.XPATH, "//*[contains(text(),'写文章') or contains(text(),'发文章')]")
    MICRO_HEADER_TAB = (By.XPATH, "//*[contains(text(),'微头条') or contains(text(),'发微头条')]")

    # 文章标题
    ARTICLE_TITLE_INPUT = (
        By.XPATH,
        "//input[@placeholder*='标题' or @placeholder*='文章'] | //textarea[contains(@class,'title')]",
    )

    # 富文本编辑器（ProseMirror 是固定的 class，定位稳定）
    PROSEMIRROR_EDITOR = (By.CSS_SELECTOR, ".ProseMirror")
    # 通用富文本编辑器备用定位
    RICH_TEXT_EDITOR = (By.XPATH, "//div[contains(@class,'editor') and @contenteditable='true']")

    # 微头条输入框
    MICRO_HEADER_INPUT = (
        By.XPATH,
        "//div[contains(@class,'micro')]//div[@contenteditable='true'] | //textarea[contains(@class,'micro')]",
    )

    # 发布按钮
    PUBLISH_BUTTON = (By.XPATH, "//button[contains(text(),'发布') and not(contains(text(),'发'))]")

    # 字数提示
    WORD_COUNT_TIP = (By.XPATH, "//*[contains(@class,'count') or contains(text(),'字')]")

    # 错误提示
    ERROR_TIP = (By.XPATH, "//div[contains(@class,'error') or contains(@class,'tip') or contains(@class,'toast')]")

    # 发布成功提示
    SUCCESS_TIP = (By.XPATH, "//*[contains(text(),'发布成功')]")

    def open_publish_page(self):
        """打开发布页面。"""
        self.open()
        if self.is_element_present(self.PUBLISH_ENTRY, timeout=5):
            self.click(self.PUBLISH_ENTRY)
            self.wait_for_ajax_complete()
        logger.info("已打开发布页面")

    def switch_to_article(self):
        """切换到发布文章 Tab。"""
        if self.is_element_present(self.ARTICLE_TYPE_TAB, timeout=3):
            self.click(self.ARTICLE_TYPE_TAB)
            logger.info("切换到发布文章")

    def switch_to_micro_header(self):
        """切换到发布微头条 Tab。"""
        if self.is_element_present(self.MICRO_HEADER_TAB, timeout=3):
            self.click(self.MICRO_HEADER_TAB)
            logger.info("切换到发布微头条")

    def input_article_title(self, title: str):
        """输入文章标题。"""
        self.input_text(self.ARTICLE_TITLE_INPUT, title)

    def input_rich_text_content(self, content: str):
        """向 ProseMirror 富文本编辑器输入正文内容。

        ProseMirror 编辑器是 contenteditable div，需要先点击聚焦再输入。
        换行通过模拟回车键实现。

        Args:
            content: 正文内容，多段用 \n 分隔
        """
        logger.info("向富文本编辑器输入正文")
        # 优先使用 ProseMirror 固定类名定位
        if self.is_element_present(self.PROSEMIRROR_EDITOR, timeout=5):
            editor = self.find_visible_element(self.PROSEMIRROR_EDITOR)
        else:
            editor = self.find_visible_element(self.RICH_TEXT_EDITOR)

        # 点击聚焦
        self.click_element(editor)
        # 按段落输入，使用回车换行
        paragraphs = content.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if i > 0:
                editor.send_keys(Keys.ENTER)
            editor.send_keys(paragraph)

    def input_micro_header(self, content: str):
        """输入微头条内容。

        Args:
            content: 微头条文本内容
        """
        editor = self.find_visible_element(self.MICRO_HEADER_INPUT)
        self.click_element(editor)
        editor.send_keys(content)

    def publish(self):
        """点击发布按钮。"""
        self.click(self.PUBLISH_BUTTON)
        self.wait_for_ajax_complete()
        logger.info("已点击发布按钮")

    def get_error_tip(self) -> str:
        """获取发布错误提示。"""
        try:
            return self.get_text(self.ERROR_TIP, timeout=5)
        except Exception:
            return ""

    def is_publish_success(self) -> bool:
        """判断是否发布成功。"""
        return self.is_element_visible(self.SUCCESS_TIP, timeout=10)

    def get_word_count_tip(self) -> str:
        """获取字数提示文本。"""
        try:
            return self.get_text(self.WORD_COUNT_TIP, timeout=3)
        except Exception:
            return ""

    def publish_article(self, title: str, content: str):
        """发布完整文章（标题 + 正文）的便捷方法。"""
        self.open_publish_page()
        self.switch_to_article()
        self.input_article_title(title)
        self.input_rich_text_content(content)
        self.publish()

    def publish_micro_header(self, content: str):
        """发布微头条的便捷方法。"""
        self.open_publish_page()
        self.switch_to_micro_header()
        self.input_micro_header(content)
        self.publish()
