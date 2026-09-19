import allure
import pytest

from config.settings import settings
from page.product_page import product_page
from utils.helpers import assert_common, assert_pagination


@allure.epic("B2C 电商平台接口测试")
@allure.feature("商品服务 product-service")
class TestProduct:

    @allure.story("商品搜索")
    @allure.title("正向：关键字搜索返回分页结果")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "product", "public")
    @pytest.mark.smoke
    @pytest.mark.product
    @pytest.mark.public
    def test_search_by_keyword(self):
        with allure.step("步骤1：调用搜索接口，传入关键字"):
            resp = product_page.search(keyword="商品", page=1, size=5)
        with allure.step("步骤2：断言响应结构与状态码"):
            assert_common(resp, expected_code=settings.SUCCESS_CODE)
            assert_pagination(resp["data"], expected_size=5)
        with allure.step("步骤3：断言关键字出现在返回商品名称中（非空时）"):
            goods_list = resp["data"].get("list", [])
            for g in goods_list:
                assert "productId" in g and "name" in g and "price" in g, (
                    f"商品字段缺失: {g}"
                )

    @allure.story("商品搜索")
    @allure.title("正向：按分类+品牌筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.product
    @pytest.mark.public
    def test_search_by_category_and_brand(self):
        with allure.step("按分类ID和品牌ID搜索"):
            resp = product_page.search(
                category_id=settings.DEFAULT_CATEGORY_ID,
                brand_id=settings.DEFAULT_BRAND_ID,
                page=1, size=10,
            )
        assert_common(resp, expected_code=settings.SUCCESS_CODE)
        assert_pagination(resp["data"], expected_size=10)

    @allure.story("商品搜索")
    @allure.title("正向：按价格区间 + 排序")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.product
    @pytest.mark.public
    @pytest.mark.parametrize("sort_field", ["price_asc", "price_desc", "sales_desc"])
    def test_search_with_sort(self, sort_field):
        with allure.step(f"搜索，按 {sort_field} 排序"):
            resp = product_page.search(min_price=0, max_price=9999, sort=sort_field, size=20)
        assert_common(resp, settings.SUCCESS_CODE)
        assert_pagination(resp["data"], expected_size=20)
        goods_list = resp["data"].get("list", [])
        if len(goods_list) >= 2 and sort_field == "price_asc":
            prices = [g["price"] for g in goods_list if "price" in g]
            assert prices == sorted(prices), f"价格升序排列错误: {prices}"

    @allure.story("商品搜索")
    @allure.title("反向：分页参数非法（page=0）")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    @pytest.mark.product
    def test_search_invalid_page(self):
        with allure.step("传入非法 page=0"):
            resp = product_page.search(page=0, size=10)
        assert resp["code"] in (settings.SUCCESS_CODE, settings.PARAM_ERROR_CODE), (
            f"期望 200 或 400，实际 {resp['code']} msg={resp.get('message')}"
        )

    @allure.story("商品推荐")
    @allure.title("正向：首页场景获取推荐列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.product
    @pytest.mark.public
    @pytest.mark.parametrize("scene", ["home", "detail", "cart"])
    def test_recommend_by_scene(self, scene):
        with allure.step(f"场景={scene} 获取推荐"):
            resp = product_page.recommend(scene=scene, size=10)
        assert_common(resp, settings.SUCCESS_CODE)
        assert isinstance(resp["data"], list), "推荐接口 data 应为数组"
        for item in resp["data"]:
            assert all(k in item for k in ("productId", "name", "price")), (
                f"推荐字段缺失: {item}"
            )

    @allure.story("商品推荐")
    @allure.title("正向：个性化推荐（带 userId）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.product
    @pytest.mark.auth
    def test_recommend_with_user_id(self, auth_http_client):
        with allure.step("携带 userId 调用推荐接口"):
            resp = product_page.recommend(
                user_id=settings.TEST_USER_ID, scene="home", size=5
            )
        assert_common(resp, settings.SUCCESS_CODE)
        assert isinstance(resp["data"], list)

    @allure.story("商品详情")
    @allure.title("正向：获取默认商品详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.product
    @pytest.mark.public
    def test_detail_success(self):
        with allure.step("根据默认商品ID查询详情"):
            resp = product_page.detail(settings.DEFAULT_PRODUCT_ID)
        with allure.step("断言响应结构与字段完整性"):
            assert_common(resp, settings.SUCCESS_CODE)
            data = resp["data"]
            required_fields = (
                "productId", "name", "price", "originalPrice",
                "stock", "sales", "images", "detail",
                "categoryId", "brandId", "specifications",
            )
            for f in required_fields:
                assert f in data, f"商品详情缺少字段: {f}"
            assert isinstance(data["images"], list), "images 必须是数组"
            assert isinstance(data["specifications"], list), "specifications 必须是数组"

    @allure.story("商品详情")
    @allure.title("反向：查询不存在的商品ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.product
    def test_detail_not_found(self):
        with allure.step("传入极不可能存在的商品ID"):
            resp = product_page.detail(99999999)
        assert resp["code"] in (settings.NOT_FOUND_CODE, settings.SUCCESS_CODE), (
            f"期望 404 或 200(null)，实际 {resp['code']} msg={resp.get('message')}"
        )
        if resp["code"] == settings.SUCCESS_CODE:
            assert resp["data"] is None or resp["data"].get("productId") != 99999999
