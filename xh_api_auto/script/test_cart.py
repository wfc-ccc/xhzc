import allure
import pytest

from config.settings import settings
from page.cart_page import cart_page
from utils.helpers import assert_common


@allure.epic("B2C 电商平台接口测试")
@allure.feature("购物车服务 cart-service")
@pytest.mark.cart
@pytest.mark.auth
class TestCart:

    @pytest.fixture(scope="function", autouse=True)
    def _need_token(self, auth_http_client):
        self._client = auth_http_client

    @allure.story("添加/查询购物车")
    @allure.title("正向：添加商品到购物车并查询")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_add_and_list(self):
        with allure.step("步骤1：添加商品到购物车"):
            add_resp = cart_page.add(
                product_id=settings.DEFAULT_PRODUCT_ID,
                quantity=1,
                spec_info="颜色:红;尺码:M",
            )
        assert_common(add_resp, settings.SUCCESS_CODE, message_contains="成功")

        with allure.step("步骤2：查询购物车列表，确认已添加"):
            list_resp = cart_page.list()
        assert_common(list_resp, settings.SUCCESS_CODE)
        assert isinstance(list_resp["data"], list), "购物车列表应为数组"
        if list_resp["data"]:
            item = list_resp["data"][0]
            for f in ("cartItemId", "productId", "productName", "price", "quantity"):
                assert f in item, f"购物车条目缺少字段: {f}"

    @allure.story("添加购物车")
    @allure.title("反向：添加商品数量为 0")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_add_quantity_zero(self):
        resp = cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=0)
        assert resp["code"] in (settings.PARAM_ERROR_CODE, settings.SUCCESS_CODE), (
            f"数量=0 响应异常: {resp}"
        )

    @allure.story("修改购物车数量")
    @allure.title("正向：先添加再修改数量")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_quantity(self):
        with allure.step("先添加商品"):
            cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=1)
        with allure.step("查询获取 cartItemId"):
            list_resp = cart_page.list()
            assert_common(list_resp, settings.SUCCESS_CODE)
            assert list_resp["data"], "购物车为空，无法修改"
            cart_item_id = list_resp["data"][0]["cartItemId"]
        with allure.step(f"修改 cartItemId={cart_item_id} 数量为 5"):
            upd_resp = cart_page.update(cart_item_id=cart_item_id, quantity=5)
        assert_common(upd_resp, settings.SUCCESS_CODE, message_contains="成功")

    @allure.story("删除购物车商品")
    @allure.title("正向：添加后删除购物车条目")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_cart_item(self):
        with allure.step("添加商品"):
            cart_page.add(product_id=settings.DEFAULT_PRODUCT_ID, quantity=1)
        with allure.step("查询获取 cartItemId"):
            list_resp = cart_page.list()
            assert list_resp["data"], "购物车为空，无法删除"
            cart_item_id = list_resp["data"][0]["cartItemId"]
        with allure.step(f"删除 cartItemId={cart_item_id}"):
            del_resp = cart_page.delete(cart_item_id=cart_item_id)
        assert_common(del_resp, settings.SUCCESS_CODE, message_contains="成功")

    @allure.story("删除购物车商品")
    @allure.title("反向：删除不存在的 cartItemId")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    def test_delete_not_exist(self):
        resp = cart_page.delete(cart_item_id=99999999)
        assert resp["code"] in (settings.NOT_FOUND_CODE, settings.SUCCESS_CODE,
                                settings.PARAM_ERROR_CODE), (
            f"删除不存在条目响应异常: {resp}"
        )
