import allure

from base.request_base import request_base
from utils.logger import logger


class OrderPage:

    BASE_PREFIX = "/api/order"

    @allure.step("调用【创建订单】接口 POST /api/order/create")
    def create(self, cart_item_ids, address_id, coupon_id=None,
               remark=None, need_auth=True):
        path = f"{self.BASE_PREFIX}/create"
        body = {"cartItemIds": cart_item_ids, "addressId": address_id}
        if coupon_id is not None:
            body["couponId"] = coupon_id
        if remark is not None:
            body["remark"] = remark
        logger.info(f"创建订单: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【查询订单列表】接口 GET /api/order/list")
    def list(self, status=None, page=1, size=10, need_auth=True):
        path = f"{self.BASE_PREFIX}/list"
        params = {"page": page, "size": size}
        if status is not None:
            params["status"] = status
        logger.info(f"查询订单列表: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)

    @allure.step("调用【订单详情】接口 GET /api/order/detail/{order_id}")
    def detail(self, order_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/detail/{order_id}"
        logger.info(f"查询订单详情: orderId={order_id}")
        return request_base.get(path, need_auth=need_auth)

    @allure.step("调用【取消订单】接口 PUT /api/order/cancel/{order_id}")
    def cancel(self, order_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/cancel/{order_id}"
        logger.info(f"取消订单: orderId={order_id}")
        return request_base.put(path, need_auth=need_auth)


order_page = OrderPage()
