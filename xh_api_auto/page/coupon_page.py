import allure

from base.request_base import request_base
from utils.logger import logger


class CouponPage:

    BASE_PREFIX = "/api/coupon"

    @allure.step("调用【领取优惠券】接口 POST /api/coupon/receive/{coupon_id}")
    def receive(self, coupon_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/receive/{coupon_id}"
        logger.info(f"领取优惠券: couponId={coupon_id}")
        return request_base.post(path, need_auth=need_auth)

    @allure.step("调用【我的优惠券】接口 GET /api/coupon/list")
    def list(self, status=None, page=1, size=10, need_auth=True):
        path = f"{self.BASE_PREFIX}/list"
        params = {"page": page, "size": size}
        if status is not None:
            params["status"] = status
        logger.info(f"查询用户优惠券: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)

    @allure.step("调用【使用优惠券（内部核销）】接口 POST /api/coupon/use")
    def use(self, coupon_id, order_id, user_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/use"
        body = {"couponId": coupon_id, "orderId": order_id, "userId": user_id}
        logger.info(f"核销优惠券: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)


coupon_page = CouponPage()
