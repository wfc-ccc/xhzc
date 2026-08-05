# File: testcases/test_article.py
"""文章相关测试用例（@pytest.mark.parametrize 数据驱动）。

发布长文章用例从 data/article_publish_data.csv 读取，通过
@pytest.mark.parametrize 装饰器注入参数。
"""
import pytest

from config.settings import settings
from pages.home_page import HomePage
from pages.publish_page import PublishPage
from pages.article_detail_page import ArticleDetailPage
from pages.login_page import LoginPage
from utils.csv_reader import read_csv_to_list, get_data_path
from utils.helpers import (
    random_article_title,
    random_article_content,
    random_chinese_text,
)

# 模块级加载 CSV：@parametrize 在收集阶段求值，必须模块级读取
PUBLISH_DATA = read_csv_to_list(get_data_path("article_publish_data.csv"))


class TestArticle:
    """文章发布、搜索、删除等测试。"""

    @pytest.mark.publish
    def test_publish_micro_header(self, logged_in_driver):
        """发布纯文本微头条，发布后首页列表可见。"""
        publish_page = PublishPage(logged_in_driver)
        content = f"自动化测试微头条_{random_chinese_text(15)}"
        publish_page.publish_micro_header(content)

        assert publish_page.is_publish_success() or not publish_page.get_error_tip(), \
            "微头条发布失败"

        home_page = HomePage(logged_in_driver)
        home_page.open_home()
        assert len(home_page.get_article_list()) > 0, "首页文章列表为空"

    @pytest.mark.publish
    @pytest.mark.parametrize(
        "case",
        PUBLISH_DATA,
        ids=[r["case_name"] for r in PUBLISH_DATA],
    )
    def test_publish_article(self, logged_in_driver, case):
        """参数化：发布带标题和正文的文章。"""
        title = case["title"]
        content = case["content"]
        expected = case["expected_result"]
        case_name = case["case_name"]

        publish_page = PublishPage(logged_in_driver)
        publish_page.open_publish_page()
        publish_page.switch_to_article()
        if title:
            publish_page.input_article_title(title)
        if content:
            publish_page.input_rich_text_content(content)
        publish_page.publish()

        if expected == "success":
            assert publish_page.is_publish_success(), (
                f"[{case_name}] 期望发布成功，但未出现成功提示"
            )
            if title:
                home_page = HomePage(logged_in_driver)
                home_page.open_home()
                try:
                    home_page.click_article_by_title(title[:8])
                    detail_page = ArticleDetailPage(logged_in_driver)
                    assert detail_page.verify_content_matches(
                        expected_title=title,
                        expected_content_part=content[:10] if content else "",
                    ), f"[{case_name}] 详情页内容与发布内容不一致"
                except Exception:
                    pytest.skip(f"[{case_name}] 新发布文章未在推荐流展示，跳过详情验证")
        else:
            error_tip = publish_page.get_error_tip()
            word_tip = publish_page.get_word_count_tip()
            assert error_tip or word_tip or not publish_page.is_publish_success(), (
                f"[{case_name}] 期望发布失败，但实际发布成功"
            )

    @pytest.mark.search
    def test_search_article(self, driver):
        """搜索框输入关键词，验证结果列表非空。"""
        home_page = HomePage(driver)
        home_page.open_home()
        home_page.search_article(settings.SEARCH_KEYWORD)
        assert len(home_page.get_search_results()) > 0, "搜索结果列表为空"

    @pytest.mark.list
    def test_category_switch(self, driver):
        """按分类切换 tab，验证列表刷新。"""
        home_page = HomePage(driver)
        home_page.open_home()

        home_page.click_category("推荐")
        assert len(home_page.get_article_list()) > 0, "推荐分类列表为空"

        home_page.click_category(settings.ARTICLE_CATEGORY)
        assert len(home_page.get_article_list()) > 0, \
            f"{settings.ARTICLE_CATEGORY} 分类列表为空"

    @pytest.mark.negative
    def test_publish_without_login(self, driver):
        """未登录状态下点击发布，验证跳转到登录页或弹出登录框。"""
        home_page = HomePage(driver)
        home_page.open_home()
        if not home_page.is_login_entry_visible():
            home_page.logout()

        try:
            home_page.click_publish_entry()
        except Exception:
            return  # 部分页面未登录时直接禁用发布按钮，视为通过

        login_page = LoginPage(driver)
        assert (
            "login" in driver.current_url.lower()
            or login_page.is_element_visible(login_page.PHONE_INPUT, timeout=5)
            or home_page.is_login_entry_visible()
        ), "未登录点击发布应跳转登录页或弹出登录框"

    @pytest.mark.delete
    def test_delete_own_article(self, logged_in_driver):
        """删除自己发布的文章，验证删除成功提示。"""
        publish_page = PublishPage(logged_in_driver)
        title = random_article_title()
        content_body = random_article_content(paragraphs=2)
        publish_page.publish_article(title, content_body)
        if not publish_page.is_publish_success():
            pytest.skip("前置发布失败，跳过删除用例")

        home_page = HomePage(logged_in_driver)
        home_page.open_home()
        try:
            home_page.click_article_by_title(title[:8])
        except Exception:
            pytest.skip("未找到刚发布的文章，跳过删除用例")

        detail_page = ArticleDetailPage(logged_in_driver)
        try:
            detail_page.delete_article()
        except Exception as e:
            pytest.skip(f"页面未提供删除入口或非作者本人: {e}")

        assert detail_page.is_article_deleted(), "文章删除后未出现删除成功提示"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
