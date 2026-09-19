import allure
import pytest

from config.settings import settings
from page.coupon_page import coupon_page
from utils.helpers import assert_common, assert_pagination


@allure.epic("B2C 电商平台接口测试")
@allure.feature("优惠券服务 coupon-service")
@pytest.mark.coupon
@pytest.mark.auth
class TestCoupon:

    @pytest.fixture(scope="function", autouse=True)
    def _need_token(self, auth_http_client):
        self._client = auth_http_client

    @allure.story("领取优惠券")
    @allure.title("正向：领取默认优惠券")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_receive_coupon(self):
        with allure.step(f"领取 couponId={settings.DEFAULT_COUPON_ID}"):
            resp = coupon_page.receive(settings.DEFAULT_COUPON_ID)
        assert resp["code"] in (
            settings.SUCCESS_CODE,
            settings.DUPLICATE_ORDER,
            settings.COUPON_INVALID,
        ), f"领取响应异常: {resp}"

    @allure.story("领取优惠券")
    @allure.title("反向：领取不存在的优惠券")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_receive_invalid_coupon(self):
        resp = coupon_page.receive(99999999)
        assert resp["code"] in (settings.COUPON_INVALID, settings.NOT_FOUND_CODE), (
            f"领取不存在优惠券未返回预期错误: {resp}"
        )

    @allure.story("查询用户优惠券")
    @allure.title("正向：查询未使用优惠券列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("status", [0, 1, 2])
    def test_list_coupons_by_status(self, status):
        with allure.step(f"查询 status={status} 的优惠券"):
            resp = coupon_page.list(status=status, page=1, size=10)
        assert_common(resp, settings.SUCCESS_CODE)
        assert_pagination(resp["data"], expected_size=10)

    @allure.story("核销优惠券")
    @allure.title("正向：内部核销优惠券接口")
    @allure.severity(allure.severity_level.NORMAL)
    def test_use_coupon(self):
        with allure.step("调用内部核销接口"):
            resp = coupon_page.use(
                coupon_id=settings.DEFAULT_COUPON_ID,
                order_id=settings.DEFAULT_ORDER_ID,
                user_id=settings.TEST_USER_ID,
            )
        if resp["code"] == settings.SUCCESS_CODE:
            assert "discountAmount" in resp["data"], "核销成功应返回 discountAmount"
        else:
            assert resp["code"] in (settings.COUPON_INVALID,), (
                f"核销响应异常: {resp}"
            )
