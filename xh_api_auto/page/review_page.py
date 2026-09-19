import allure

from base.request_base import request_base
from utils.logger import logger


class ReviewPage:

    BASE_PREFIX = "/api/review"

    @allure.step("调用【发表商品评价】接口 POST /api/review/add")
    def add(self, order_id, product_id, rating=5,
            content="很好用，推荐！", images=None, need_auth=True):
        path = f"{self.BASE_PREFIX}/add"
        body = {
            "orderId": order_id,
            "productId": product_id,
            "rating": rating,
            "content": content,
        }
        if images is not None:
            body["images"] = images
        logger.info(f"发表评价: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)

    @allure.step("调用【商品评价列表】接口 GET /api/review/list")
    def list(self, product_id, page=1, size=10,
             sort="time_desc", need_auth=False):
        path = f"{self.BASE_PREFIX}/list"
        params = {
            "productId": product_id,
            "page": page,
            "size": size,
            "sort": sort,
        }
        logger.info(f"查询商品评价: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)

    @allure.step("调用【点赞/取消点赞】接口 POST /api/review/like/{review_id}")
    def like(self, review_id, need_auth=True):
        path = f"{self.BASE_PREFIX}/like/{review_id}"
        logger.info(f"点赞评价: reviewId={review_id}")
        return request_base.post(path, need_auth=need_auth)

    @allure.step("调用【回复评价】接口 POST /api/review/reply")
    def reply(self, review_id, content, need_auth=True):
        path = f"{self.BASE_PREFIX}/reply"
        body = {"reviewId": review_id, "content": content}
        logger.info(f"回复评价: {body}")
        return request_base.post(path, json_body=body, need_auth=need_auth)


review_page = ReviewPage()
