import allure

from base.request_base import request_base
from utils.logger import logger


class CartPage:

    BASE_PREFIX = "/api/cart"

    @allure.step("调用【添加购物车】接口 POST /api/cart/add")
    def add(self, product_id, quantity=1, spec_info=None, need_auth=True):
        path = f"{self.BASE_PREFIX}/add"
        body = {"productId": product_id, "quantity": quantity}
        if spec_info is not None:
            body["specInfo"] = spec_info
        logger.info(f"添加购物车: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【修改购物车数量】接口 PUT /api/cart/update")
    def update(self, cart_item_id, quantity, need_auth=True):
        path = f"{self.BASE_PREFIX}/update"
        body = {"cartItemId": cart_item_id, "quantity": quantity}
        logger.info(f"修改购物车数量: {body}")
        return request_base.put(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【删除购物车商品】接口 DELETE /api/cart/delete/{cart_item_id}")
    def delete(self, cart_item_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/delete/{cart_item_id}"
        logger.info(f"删除购物车商品: cartItemId={cart_item_id}")
        return request_base.delete(path, need_auth=need_auth)

    @allure.step("调用【查询购物车列表】接口 GET /api/cart/list")
    def list(self, need_auth=True):
        path = f"{self.BASE_PREFIX}/list"
        logger.info("查询购物车列表")
        return request_base.get(path, need_auth=need_auth)


cart_page = CartPage()
