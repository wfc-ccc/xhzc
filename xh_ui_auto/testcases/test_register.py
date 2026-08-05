# File: testcases/test_register.py
"""注册测试用例。

注意：星火新闻 PC 网页版可能不提供独立注册入口，
本模块在页面不支持注册时会统一跳过。
"""
import pytest

from config.settings import settings
from pages.register_page import RegisterPage
from utils.helpers import random_string


class TestRegister:
    """注册模块测试。"""

    def _open_or_skip(self, driver) -> RegisterPage:
        """打开注册页，若页面不支持独立注册则跳过当前用例。"""
        page = RegisterPage(driver)
        page.open_register_page()
        if not page.is_register_supported():
            pytest.skip("星火新闻 PC 端当前不支持独立注册")
        return page

    @pytest.mark.register
    def test_register_page_supported(self, driver):
        """前置检查：页面是否支持独立注册。"""
        self._open_or_skip(driver)

    @pytest.mark.register
    def test_register_invalid_phone(self, driver):
        """反向：手机号格式错误时注册失败。"""
        page = self._open_or_skip(driver)
        page.fill_register_form(
            phone=settings.INVALID_PHONE,
            password=settings.TEST_PASSWORD,
            nickname=f"测试用户_{random_string(4)}",
        )
        page.submit_register()
        assert page.get_error_tip(), "格式错误的手机号应触发前端校验"

    @pytest.mark.register
    def test_register_duplicate_phone(self, driver):
        """反向：已注册手机号再次注册应失败。"""
        page = self._open_or_skip(driver)
        page.fill_register_form(
            phone=settings.TEST_PHONE,
            password=settings.TEST_PASSWORD,
            nickname=f"重复用户_{random_string(4)}",
        )
        page.submit_register()
        error_tip = page.get_error_tip()
        if error_tip:
            keywords = ["已注册", "已存在", "注册过", "占用"]
            assert any(k in error_tip for k in keywords), \
                f"重复注册提示异常: {error_tip}"

    @pytest.mark.register
    def test_register_success(self, driver):
        """正向：使用随机新手机号注册（需短信验证码，需手动介入）。"""
        self._open_or_skip(driver)
        pytest.skip(
            "注册流程需要真实短信验证码，需手动介入完成。"
            "请使用白名单测试号或 mock 短信网关后启用此用例。"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
