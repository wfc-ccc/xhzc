# File: testcases/test_login.py
"""登录/登出测试用例（@pytest.mark.parametrize 数据驱动）。

登录数据从 data/login_data.csv 读取，通过 @pytest.mark.parametrize 装饰器注入。
"""
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.csv_reader import read_csv_to_list, get_data_path

# 模块级加载 CSV：@parametrize 在收集阶段求值，必须模块级读取
LOGIN_DATA = read_csv_to_list(get_data_path("login_data.csv"))


class TestLogin:
    """登录模块测试。"""

    @pytest.mark.login
    @pytest.mark.parametrize(
        "case",
        LOGIN_DATA,
        ids=[r["case_name"] for r in LOGIN_DATA],
    )
    def test_login(self, driver, case):
        """参数化登录测试（正向/反向共用一套流程）。"""
        phone = case["phone"]
        password = case["password"]
        expected = case["expected_result"]
        expected_error = case.get("expected_error_msg", "")
        case_name = case["case_name"]

        login_page = LoginPage(driver)
        login_page.open_login_page()
        login_page.login_with_password(phone, password)

        if expected == "success":
            assert login_page.is_login_success(), (
                f"[{case_name}] 期望登录成功，但未检测到用户头像/昵称"
            )
        else:
            assert not login_page.is_login_success(), (
                f"[{case_name}] 期望登录失败，但实际登录成功"
            )
            if expected_error:
                actual = login_page.get_error_tip()
                assert actual, (
                    f"[{case_name}] 期望错误提示包含 '{expected_error}'，但未捕获到"
                )
                assert expected_error in actual, (
                    f"[{case_name}] 错误提示不匹配，"
                    f"期望包含 '{expected_error}'，实际 '{actual}'"
                )

    @pytest.mark.logout
    def test_logout_success(self, logged_in_driver):
        """退出登录后登录入口应重新出现。"""
        home_page = HomePage(logged_in_driver)
        home_page.open_home()
        home_page.logout()
        assert home_page.is_login_entry_visible(), "退出登录后未重新出现登录入口"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
