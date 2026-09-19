import allure

from base.request_base import request_base
from utils.logger import logger


class PaymentPage:

    BASE_PREFIX = "/api/payment"

    @allure.step("调用【创建支付】接口 POST /api/payment/create")
    def create(self, order_id, pay_type="ALIPAY",
               return_url="https://example.com/return", need_auth=True):
        path = f"{self.BASE_PREFIX}/create"
        body = {
            "orderId": order_id,
            "payType": pay_type,
            "returnUrl": return_url,
        }
        logger.info(f"发起支付: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【支付回调】接口 POST /api/payment/callback/{pay_type}")
    def callback(self, pay_type, callback_body=None,
                 extra_headers=None, need_auth=False):
        if callback_body is None:
            import time
            callback_body = {
                "trade_no": f"TP{int(time.time() * 1000)}",
                "out_trade_no": "PAY202310011234",
                "total_amount": "178.00",
                "trade_status": "TRADE_SUCCESS",
            }
        path = f"{self.BASE_PREFIX}/callback/{pay_type}"
        logger.info(f"支付回调: payType={pay_type}, body={callback_body}")
        return request_base.post(path, json_body=callback_body,
                                 extra_headers=extra_headers, need_auth=need_auth)


payment_page = PaymentPage()
