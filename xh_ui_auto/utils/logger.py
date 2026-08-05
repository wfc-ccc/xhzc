# File: utils/logger.py
"""日志配置模块。

提供统一的日志记录器，输出到控制台和文件。
"""
import logging
import os
from datetime import datetime

from config.settings import settings


def get_logger(name="xh_ui"):
    """获取统一配置的 logger 实例。

    Args:
        name: logger 名称

    Returns:
        logging.Logger: 配置好的 logger
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        # 已配置过，避免重复添加 handler
        return logger

    logger.setLevel(logging.DEBUG)

    # 控制台 handler：输出 INFO 及以上
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)

    # 文件 handler：输出 DEBUG 及以上
    log_dir = os.path.join(settings.REPORT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


# 全局 logger 实例
logger = get_logger()
