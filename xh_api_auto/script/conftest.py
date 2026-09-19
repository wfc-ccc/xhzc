import os
import sys
from datetime import datetime

import allure
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import settings
from utils.logger import logger
from utils.data_loader import (
    read_csv, read_yaml, get_csv_params,
    parse_int, parse_float, parse_int_list,
)
from base.request_base import RequestBase


@pytest.fixture(scope="session", autouse=True)
def _prepare_dirs():
    for d in [settings.REPORT_DIR, settings.ALLURE_DIR, settings.LOG_DIR, settings.DATA_DIR]:
        os.makedirs(d, exist_ok=True)
    logger.info(
        f"测试会话开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"GATEWAY_URL={settings.GATEWAY_URL}"
    )
    yield
    logger.info("测试会话结束")


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev",
                     help="运行环境: dev/test/prod，默认 dev")
    parser.addoption("--gateway", action="store", default=None,
                     help="覆盖配置中的 GATEWAY_URL")


@pytest.fixture(scope="session", autouse=True)
def _apply_cli_options(request):
    env = request.config.getoption("--env")
    gateway = request.config.getoption("--gateway")
    if gateway:
        settings.GATEWAY_URL = gateway
        logger.info(f"使用命令行网关地址: {settings.GATEWAY_URL}")
    env_map = {
        "dev": "http://localhost:8080",
        "test": "http://test-gateway.example.com",
        "prod": "https://gateway.example.com",
    }
    if env in env_map and not gateway:
        settings.GATEWAY_URL = env_map[env]
        logger.info(f"切换到 [{env}] 环境，网关: {settings.GATEWAY_URL}")


@pytest.fixture(scope="session", autouse=True)
def _write_allure_env(request):
    yield
    env_props = {
        "GATEWAY_URL": settings.GATEWAY_URL,
        "Environment": request.config.getoption("--env"),
        "Test.UserId": str(settings.TEST_USER_ID),
        "Python": sys.version.split(" ")[0],
        "RunTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        props_file = os.path.join(settings.ALLURE_DIR, "environment.properties")
        os.makedirs(settings.ALLURE_DIR, exist_ok=True)
        with open(props_file, "w", encoding="utf-8") as f:
            for k, v in env_props.items():
                f.write(f"{k}={v}\n")
        logger.info(f"Allure 环境信息已写入: {props_file}")
    except Exception as e:
        logger.warning(f"写入 Allure 环境信息失败: {e}")


@pytest.fixture(scope="session")
def http_client():
    return RequestBase()


@pytest.fixture(scope="function")
def auth_http_client():
    if not settings.TEST_TOKEN or settings.TEST_TOKEN == "your-jwt-token-here":
        pytest.skip("未配置有效的 TEST_TOKEN（请在 .env 中设置）")
    return RequestBase()


@pytest.fixture(scope="function", autouse=True)
def _case_log_wrapper(request):
    logger.info(f"========== 开始用例: {request.node.name} ==========")
    yield
    logger.info(f"========== 结束用例: {request.node.name} ==========")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        try:
            err_info = (
                f"Case: {item.nodeid}\n"
                f"Repr: {report.longreprtext[:3000] if report.longreprtext else ''}"
            )
            allure.attach(
                err_info,
                name="Failure Info",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            logger.warning(f"附加失败信息异常: {e}")


# ==================== 测试数据 fixtures ====================
@pytest.fixture(scope="session")
def global_config():
    """读取 data/global_config.yaml，返回 dict。"""
    return read_yaml("global_config.yaml")


@pytest.fixture(scope="session")
def product_search_data():
    """商品搜索测试数据 list[dict]。"""
    return read_csv("product_search_data.csv")


@pytest.fixture(scope="session")
def cart_add_data():
    """添加购物车测试数据 list[dict]。"""
    return read_csv("cart_add_data.csv")


@pytest.fixture(scope="session")
def order_create_data():
    """创建订单测试数据 list[dict]。"""
    return read_csv("order_create_data.csv")


@pytest.fixture(scope="session")
def order_list_data():
    """订单列表测试数据 list[dict]。"""
    return read_csv("order_list_data.csv")


@pytest.fixture(scope="session")
def coupon_receive_data():
    """优惠券领取测试数据 list[dict]。"""
    return read_csv("coupon_receive_data.csv")


@pytest.fixture(scope="session")
def seckill_execute_data():
    """秒杀执行测试数据 list[dict]。"""
    return read_csv("seckill_execute_data.csv")


@pytest.fixture(scope="session")
def review_add_data():
    """发表评价测试数据 list[dict]。"""
    return read_csv("review_add_data.csv")


@pytest.fixture(scope="session")
def review_list_data():
    """评价列表测试数据 list[dict]。"""
    return read_csv("review_list_data.csv")
