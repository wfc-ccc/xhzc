import allure
import pytest

from config.settings import settings
from page.order_page import order_page
from page.cart_page import cart_page
from utils.helpers import assert_common, assert_pagination


@allure.epic("B2C 电商平台接口测试")
@allure.feature("订单服务 order-service")
@pytest.mark.order
@pytest.mark.auth
class TestOrder:

    @pytest.fixture(scope="function", autouse=True)
    def _need_token(self, auth_http_client):
        self._client = auth_http_client

    @allure.story("创建订单")
    @allure.title("正向：从购物车创建订单（无优惠券）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_order(self):
        with allure.step("步骤1：先添加商品到购物车"):
            cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=2)
            list_resp = cart_page.list()
            assert_common(list_resp, settings.SUCCESS_CODE)
            cart_item_ids = [item["cartItemId"] for item in list_resp["data"]]
            assert cart_item_ids, "购物车为空，无法下单"
        with allure.step("步骤2：创建订单，不使用优惠券"):
            create_resp = order_page.create(
                cart_item_ids=cart_item_ids,
                address_id=settings.DEFAULT_ADDRESS_ID,
                remark="尽快发货",
            )
        with allure.step("步骤3：断言创建成功与关键字段"):
            assert_common(create_resp, settings.SUCCESS_CODE, message_contains="成功")
            data = create_resp["data"]
            for f in ("orderId", "orderNo", "totalAmount", "payAmount", "status"):
                assert f in data, f"创建订单缺少字段: {f}"
            assert data["status"] == "待支付", f"状态应为 待支付，实际 {data['status']}"

    @allure.story("创建订单")
    @allure.title("反向：创建订单地址ID非法")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_create_order_invalid_address(self):
        resp = order_page.create(cart_item_ids=[999], address_id=-1)
        assert resp["code"] in (settings.PARAM_ERROR_CODE, settings.NOT_FOUND_CODE, 400), (
            f"非法地址未返回预期错误: {resp}"
        )

    @allure.story("查询订单列表")
    @allure.title("正向：查询待支付订单分页列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_orders(self):
        resp = order_page.list(status="待支付", page=1, size=10)
        assert_common(resp, settings.SUCCESS_CODE)
        assert_pagination(resp["data"], expected_size=10)
        for o in resp["data"].get("list", []):
            assert "orderId" in o and "status" in o and "items" in o, (
                f"订单条目字段缺失: {o}"
            )

    @allure.story("订单详情")
    @allure.title("正向：查询订单详情（列表取第一条）")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_detail(self):
        with allure.step("先查询列表获取 orderId"):
            list_resp = order_page.list(page=1, size=1)
            assert_common(list_resp, settings.SUCCESS_CODE)
            items = list_resp["data"].get("list", [])
            if not items:
                pytest.skip("暂无订单数据，跳过详情查询")
            order_id = items[0]["orderId"]
        with allure.step(f"查询 orderId={order_id} 详情"):
            detail_resp = order_page.detail(order_id=order_id)
        assert_common(detail_resp, settings.SUCCESS_CODE)
        assert "orderId" in detail_resp["data"]

    @allure.story("取消订单")
    @allure.title("正向：创建订单后立即取消")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cancel_order(self):
        with allure.step("步骤1：先添加购物车并创建订单"):
            cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=1)
            list_resp = cart_page.list()
            cart_item_ids = [item["cartItemId"] for item in list_resp["data"]]
            pytest.assume(cart_item_ids)
            create_resp = order_page.create(
                cart_item_ids=cart_item_ids,
                address_id=settings.DEFAULT_ADDRESS_ID,
            )
            assert_common(create_resp, settings.SUCCESS_CODE)
            order_id = create_resp["data"]["orderId"]
        with allure.step(f"步骤2：取消 orderId={order_id}"):
            cancel_resp = order_page.cancel(order_id=order_id)
        assert_common(cancel_resp, settings.SUCCESS_CODE, message_contains="取消")
