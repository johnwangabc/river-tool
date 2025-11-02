# -*- coding: utf-8 -*-
"""日志管理模块"""

import logging
import os
from datetime import datetime
from pathlib import Path


class AppLogger:
    """应用日志管理器"""

    def __init__(self, log_dir='logs', log_level=logging.INFO):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_level = log_level
        self.loggers = {}

    def get_logger(self, name):
        """获取或创建logger"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        # 避免重复添加handler
        if logger.handlers:
            return logger

        # 创建文件handler
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)

        # 创建控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加handler
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        self.loggers[name] = logger
        return logger


# 全局日志管理器实例
_app_logger = None


def get_app_logger():
    """获取全局日志管理器"""
    global _app_logger
    if _app_logger is None:
        _app_logger = AppLogger()
    return _app_logger


def get_logger(name):
    """获取指定名称的logger"""
    return get_app_logger().get_logger(name)


class GUILogHandler(logging.Handler):
    """GUI文本框日志处理器"""

    def __init__(self, text_widget, callback=None):
        """
        Args:
            text_widget: tkinter Text widget
            callback: 可选的回调函数，在写入日志后调用
        """
        super().__init__()
        self.text_widget = text_widget
        self.callback = callback

        # 设置格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.setFormatter(formatter)

    def emit(self, record):
        """输出日志到GUI"""
        try:
            msg = self.format(record)
            self.text_widget.insert('end', msg + '\n')
            self.text_widget.see('end')

            # 根据日志级别设置颜色
            if record.levelno >= logging.ERROR:
                # 可以在这里添加颜色标记
                pass

            if self.callback:
                self.callback()

        except Exception:
            self.handleError(record)


def setup_gui_logger(logger, text_widget, callback=None):
    """为logger添加GUI处理器"""
    gui_handler = GUILogHandler(text_widget, callback)
    logger.addHandler(gui_handler)
    return gui_handler
