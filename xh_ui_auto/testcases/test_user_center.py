# File: testcases/test_user_center.py
"""个人中心测试用例（@pytest.mark.parametrize 数据驱动）。

修改昵称用例从 data/user_update_data.csv 读取，通过
@pytest.mark.parametrize 装饰器注入参数。
"""
import pytest

from config.settings import settings
from pages.user_center_page import UserCenterPage
from utils.csv_reader import read_csv_to_list, get_data_path
from utils.helpers import mask_phone

# 模块级加载 CSV：@parametrize 在收集阶段求值，必须模块级读取
USER_UPDATE_DATA = read_csv_to_list(get_data_path("user_update_data.csv"))


class TestUserCenter:
    """个人中心模块测试。"""

    @pytest.mark.user_info
    def test_get_user_info(self, logged_in_driver):
        """获取个人信息：昵称非空、手机号掩码格式正确。"""
        user_center = UserCenterPage(logged_in_driver)
        user_center.open_user_center()

        nickname = user_center.get_nickname()
        assert nickname, "个人中心未显示昵称"

        phone_mask_text = user_center.get_phone_mask()
        assert phone_mask_text, "个人中心未显示手机号信息"
        assert user_center.verify_phone_mask_format(phone_mask_text), \
            f"手机号掩码格式不正确: {phone_mask_text}"

    @pytest.mark.user_info
    @pytest.mark.parametrize(
        "case",
        USER_UPDATE_DATA,
        ids=[r["case_name"] for r in USER_UPDATE_DATA],
    )
    def test_modify_nickname(self, logged_in_driver, case):
        """参数化：修改昵称（正常/特殊字符/超长/空）。"""
        new_nickname = case["new_nickname"]
        expected = case["expected_result"]
        case_name = case["case_name"]

        user_center = UserCenterPage(logged_in_driver)
        user_center.open_user_center()
        user_center.modify_nickname(new_nickname)

        if expected == "success":
            assert user_center.is_modify_success(), (
                f"[{case_name}] 期望修改成功，但未出现成功提示"
            )
            user_center.open_user_center()
            updated = user_center.get_nickname()
            assert new_nickname in updated or updated in new_nickname, (
                f"[{case_name}] 昵称修改未生效，"
                f"期望包含 '{new_nickname}'，实际 '{updated}'"
            )
        else:
            modify_success = user_center.is_modify_success()
            user_center.open_user_center()
            updated = user_center.get_nickname()
            assert not modify_success or new_nickname not in updated, (
                f"[{case_name}] 期望修改失败，但实际修改成功"
            )

    @pytest.mark.user_info
    def test_phone_mask_matches_login(self, logged_in_driver):
        """验证个人中心显示的手机号掩码与登录账号一致。"""
        user_center = UserCenterPage(logged_in_driver)
        user_center.open_user_center()

        phone_mask_text = user_center.get_phone_mask()
        expected_mask = mask_phone(settings.TEST_PHONE)
        assert expected_mask in phone_mask_text, \
            f"手机号掩码与登录账号不一致，期望包含 {expected_mask}，实际 {phone_mask_text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
