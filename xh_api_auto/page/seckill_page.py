import allure

from base.request_base import request_base
from utils.logger import logger


class SeckillPage:

    BASE_PREFIX = "/api/seckill"

    @allure.step("调用【秒杀商品列表】接口 GET /api/seckill/list")
    def list(self, need_auth=False):
        path = f"{self.BASE_PREFIX}/list"
        logger.info("获取秒杀商品列表")
        return request_base.get(path, need_auth=need_auth)

    @allure.step("调用【秒杀下单】接口 POST /api/seckill/execute")
    def execute(self, seckill_id, quantity=1, need_auth=True):
        path = f"{self.BASE_PREFIX}/execute"
        body = {"seckillId": seckill_id, "quantity": quantity}
        logger.info(f"执行秒杀: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【查询秒杀结果】接口 GET /api/seckill/result")
    def result(self, seckill_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/result"
        params = {"seckillId": seckill_id}
        logger.info(f"查询秒杀结果: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)


seckill_page = SeckillPage()
