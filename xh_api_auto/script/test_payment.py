import time

import allure
import pytest

from config.settings import settings
from page.payment_page import payment_page
from page.order_page import order_page
from page.cart_page import cart_page
from utils.helpers import assert_common


@allure.epic("B2C 电商平台接口测试")
@allure.feature("支付服务 payment-service")
@pytest.mark.payment
class TestPayment:

    @allure.story("发起支付")
    @allure.title("正向：针对待支付订单创建支付单（ALIPAY）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_create_payment_alipay(self, auth_http_client):
        with allure.step("步骤1：准备一个待支付订单"):
            cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=1)
            list_resp = cart_page.list()
            assert_common(list_resp, settings.SUCCESS_CODE)
            cart_item_ids = [i["cartItemId"] for i in list_resp["data"]]
            if not cart_item_ids:
                pytest.skip("购物车为空，无法创建待支付订单")
            create_resp = order_page.create(
                cart_item_ids=cart_item_ids,
                address_id=settings.DEFAULT_ADDRESS_ID,
            )
            assert_common(create_resp, settings.SUCCESS_CODE)
            order_id = create_resp["data"]["orderId"]
        with allure.step("步骤2：发起 ALIPAY 支付"):
            pay_resp = payment_page.create(order_id=order_id, pay_type="ALIPAY")
        assert_common(pay_resp, settings.SUCCESS_CODE)
        data = pay_resp["data"]
        for f in ("payNo", "payUrl", "expireTime"):
            assert f in data, f"支付单缺少字段: {f}"

    @allure.story("发起支付")
    @allure.title("反向：使用不存在的订单ID发起支付")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.auth
    def test_create_payment_order_not_exist(self, auth_http_client):
        resp = payment_page.create(order_id=99999999, pay_type="ALIPAY")
        assert resp["code"] in (settings.NOT_FOUND_CODE, settings.PARAM_ERROR_CODE), (
            f"不存在订单发起支付返回异常: {resp}"
        )

    @allure.story("支付回调")
    @allure.title("正向：模拟支付宝异步回调")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.public
    def test_callback_alipay_success(self):
        with allure.step("模拟支付宝回调通知"):
            callback_body = {
                "trade_no": "ALIPAY202310010001",
                "out_trade_no": f"PAY_{int(time.time() * 1000)}",
                "total_amount": "178.00",
                "trade_status": "TRADE_SUCCESS",
                "sign": "mock_signature",
            }
            resp = payment_page.callback(pay_type="ALIPAY", callback_body=callback_body)
        msg = str(resp.get("message", "")).lower()
        code = resp.get("code")
        ok = (code == settings.SUCCESS_CODE or code == 200 or "success" in msg)
        assert ok, f"回调响应不符合预期: {resp}"
