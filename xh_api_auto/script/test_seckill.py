import allure
import pytest

from config.settings import settings
from page.seckill_page import seckill_page
from utils.helpers import assert_common


@allure.epic("B2C 电商平台接口测试")
@allure.feature("秒杀服务 seckill-service")
@pytest.mark.seckill
class TestSeckill:

    @allure.story("秒杀商品列表")
    @allure.title("正向：获取秒杀商品列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.public
    def test_list_seckill(self):
        with allure.step("查询秒杀商品列表"):
            resp = seckill_page.list()
        assert_common(resp, settings.SUCCESS_CODE)
        assert isinstance(resp["data"], list), "秒杀列表应为数组"
        for item in resp["data"]:
            for f in ("seckillId", "productId", "seckillPrice", "stock",
                      "startTime", "endTime", "status"):
                assert f in item, f"秒杀条目缺少字段: {f}"

    @allure.story("秒杀下单")
    @allure.title("正向：执行秒杀下单")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_execute_seckill(self, auth_http_client):
        with allure.step("步骤1：查询获取可用秒杀活动"):
            list_resp = seckill_page.list()
            assert_common(list_resp, settings.SUCCESS_CODE)
            available = [s for s in list_resp["data"] if s.get("status") == "进行中"]
            if not available:
                pytest.skip("当前没有进行中的秒杀活动")
            seckill_id = available[0]["seckillId"]
        with allure.step(f"步骤2：对 seckillId={seckill_id} 执行秒杀"):
            resp = seckill_page.execute(seckill_id=seckill_id, quantity=1)
        assert resp["code"] in (
            settings.SUCCESS_CODE,
            settings.STOCK_NOT_ENOUGH,
            settings.SECKILL_ENDED,
            settings.DUPLICATE_ORDER,
        ), f"秒杀响应异常: {resp}"

    @allure.story("秒杀下单")
    @allure.title("反向：秒杀数量 > 库存 或已结束")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.auth
    def test_execute_seckill_invalid(self, auth_http_client):
        resp = seckill_page.execute(seckill_id=settings.DEFAULT_SECKILL_ID, quantity=99999)
        assert resp["code"] in (
            settings.STOCK_NOT_ENOUGH,
            settings.SECKILL_ENDED,
            settings.NOT_FOUND_CODE,
            settings.PARAM_ERROR_CODE,
        ), f"大数量秒杀未返回预期错误: {resp}"

    @allure.story("秒杀结果查询")
    @allure.title("正向：查询秒杀结果（默认ID）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.auth
    def test_seckill_result(self, auth_http_client):
        with allure.step(f"查询 seckillId={settings.DEFAULT_SECKILL_ID} 结果"):
            resp = seckill_page.result(seckill_id=settings.DEFAULT_SECKILL_ID)
        assert resp["code"] in (settings.SUCCESS_CODE, settings.NOT_FOUND_CODE), (
            f"查询秒杀结果异常: {resp}"
        )
        if resp["code"] == settings.SUCCESS_CODE:
            assert "status" in resp["data"], "结果中应包含 status 字段"
