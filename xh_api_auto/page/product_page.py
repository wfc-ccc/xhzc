from typing import Dict

import allure

from base.request_base import request_base
from utils.logger import logger


class ProductPage:

    BASE_PREFIX = "/api/product"

    @allure.step("调用【商品搜索】接口 GET /api/product/search")
    def search(self, keyword=None, category_id=None, brand_id=None,
               min_price=None, max_price=None, sort=None,
               page=1, size=10, need_auth=False):
        path = f"{self.BASE_PREFIX}/search"
        params = {"page": page, "size": size}
        if keyword is not None:
            params["keyword"] = keyword
        if category_id is not None:
            params["categoryId"] = category_id
        if brand_id is not None:
            params["brandId"] = brand_id
        if min_price is not None:
            params["minPrice"] = min_price
        if max_price is not None:
            params["maxPrice"] = max_price
        if sort is not None:
            params["sort"] = sort
        logger.info(f"搜索商品: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)

    @allure.step("调用【商品推荐】接口 GET /api/product/recommend")
    def recommend(self, user_id=None, scene=None, size=10, need_auth=False):
        path = f"{self.BASE_PREFIX}/recommend"
        params = {"size": size}
        if user_id is not None:
            params["userId"] = user_id
        if scene is not None:
            params["scene"] = scene
        logger.info(f"获取推荐商品: {params}")
        return request_base.get(path, params=params, need_auth=need_auth)

    @allure.step("调用【商品详情】接口 GET /api/product/detail/{product_id}")
    def detail(self, product_id, need_auth=False):
        path = f"{self.BASE_PREFIX}/detail/{product_id}"
        logger.info(f"获取商品详情: productId={product_id}")
        return request_base.get(path, need_auth=need_auth)


product_page = ProductPage()
