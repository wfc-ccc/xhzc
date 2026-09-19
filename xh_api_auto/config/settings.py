import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


class Config:

    GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
    RETRY_TIMES = int(os.getenv("RETRY_TIMES", "2"))

    TEST_TOKEN = os.getenv("TEST_TOKEN", "your-jwt-token-here")
    INVALID_TOKEN = "Bearer invalid-token-demo"

    TEST_USER_ID = int(os.getenv("TEST_USER_ID", "123"))
    TEST_USERNAME = os.getenv("TEST_USERNAME", "test_user")

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORT_DIR = os.path.join(PROJECT_ROOT, "report")
    ALLURE_DIR = os.path.join(REPORT_DIR, "allure-results")
    LOG_DIR = os.path.join(REPORT_DIR, "logs")
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")

    SUCCESS_CODE = 200
    PARAM_ERROR_CODE = 400
    UNAUTHORIZED_CODE = 401
    FORBIDDEN_CODE = 403
    NOT_FOUND_CODE = 404
    SERVER_ERROR_CODE = 500
    STOCK_NOT_ENOUGH = 1001
    COUPON_INVALID = 1002
    SECKILL_ENDED = 1003
    DUPLICATE_ORDER = 1004

    DEFAULT_PRODUCT_ID = 1001
    DEFAULT_CATEGORY_ID = 10
    DEFAULT_BRAND_ID = 5
    DEFAULT_COUPON_ID = 4001
    DEFAULT_SECKILL_ID = 6001
    DEFAULT_ORDER_ID = 5001
    DEFAULT_ADDRESS_ID = 3001
    DEFAULT_REVIEW_ID = 7001


settings = Config()