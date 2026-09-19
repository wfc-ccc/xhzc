import allure
import pytest

from config.settings import settings
from page.review_page import review_page
from utils.helpers import assert_common, assert_pagination, gen_random_str


@allure.epic("B2C 电商平台接口测试")
@allure.feature("评价互动服务 review-service")
@pytest.mark.review
class TestReview:

    @allure.story("发表评价")
    @allure.title("正向：对某订单商品发表带图评价")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_add_review(self, auth_http_client):
        with allure.step("发表评价"):
            content = f"自动化测试评价内容_{gen_random_str(6)}"
            resp = review_page.add(
                order_id=settings.DEFAULT_ORDER_ID,
                product_id=settings.DEFAULT_PRODUCT_ID,
                rating=5,
                content=content,
                images=["https://img.example.com/1.jpg"],
            )
        assert_common(resp, settings.SUCCESS_CODE, message_contains="成功")

    @allure.story("发表评价")
    @allure.title("反向：评分超出范围（rating=6）")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    @pytest.mark.auth
    def test_add_review_invalid_rating(self, auth_http_client):
        resp = review_page.add(
            order_id=settings.DEFAULT_ORDER_ID,
            product_id=settings.DEFAULT_PRODUCT_ID,
            rating=6,
            content="评分超范围",
        )
        assert resp["code"] == settings.PARAM_ERROR_CODE, (
            f"评分超范围应返回 400，实际: {resp}"
        )

    @allure.story("查询商品评价")
    @allure.title("正向：按时间倒序查询评价列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.public
    @pytest.mark.parametrize("sort", ["time_desc", "rating_desc"])
    def test_list_reviews(self, sort):
        with allure.step(f"按 {sort} 排序查询评价"):
            resp = review_page.list(
                product_id=settings.DEFAULT_PRODUCT_ID,
                page=1, size=10, sort=sort,
            )
        assert_common(resp, settings.SUCCESS_CODE)
        assert_pagination(resp["data"], expected_size=10)
        for r in resp["data"].get("list", []):
            for f in ("reviewId", "rating", "content", "createTime",
                      "likeCount", "replyCount"):
                assert f in r, f"评价条目缺少字段: {f}"

    @allure.story("点赞评价")
    @allure.title("正向：点赞一条评价")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.auth
    def test_like_review(self, auth_http_client):
        with allure.step("先查询评价列表获取 reviewId"):
            list_resp = review_page.list(product_id=settings.DEFAULT_PRODUCT_ID, size=5)
            assert_common(list_resp, settings.SUCCESS_CODE)
            reviews = list_resp["data"].get("list", [])
            if not reviews:
                pytest.skip("暂无评价，跳过点赞用例")
            review_id = reviews[0]["reviewId"]
        with allure.step(f"点赞 reviewId={review_id}"):
            like_resp = review_page.like(review_id=review_id)
        assert_common(like_resp, settings.SUCCESS_CODE, message_contains="成功")
        for f in ("likeCount", "liked"):
            assert f in like_resp["data"], f"点赞响应缺少字段: {f}"

    @allure.story("回复评价")
    @allure.title("正向：回复一条评价")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.auth
    def test_reply_review(self, auth_http_client):
        with allure.step("查询评价列表获取 reviewId"):
            list_resp = review_page.list(product_id=settings.DEFAULT_PRODUCT_ID, size=5)
            reviews = list_resp["data"].get("list", [])
            if not reviews:
                pytest.skip("暂无评价，跳过回复用例")
            review_id = reviews[0]["reviewId"]
        with allure.step(f"回复 reviewId={review_id}"):
            reply_content = f"自动化回复_{gen_random_str(4)}：感谢支持！"
            reply_resp = review_page.reply(review_id=review_id, content=reply_content)
        assert_common(reply_resp, settings.SUCCESS_CODE, message_contains="成功")
