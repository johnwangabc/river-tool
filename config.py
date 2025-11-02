# -*- coding: utf-8 -*-
"""配置管理模块"""

import configparser
import os
from pathlib import Path


class Config:
    """配置管理类"""

    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        config_path = Path(self.config_file)

        if not config_path.exists():
            raise FileNotFoundError(
                f"配置文件未找到: {self.config_file}\n"
                f"请确保 config.ini 文件存在于程序目录中"
            )

        self.config.read(config_path, encoding='utf-8')

    def reload(self):
        """重新加载配置"""
        self.load_config()

    # API 配置
    @property
    def api_base_url(self):
        return self.config.get('API', 'base_url', fallback='https://xhbr.rwan.org.cn/prod-api')

    @property
    def org_id(self):
        return self.config.get('API', 'org_id', fallback='843')

    @property
    def auth_token(self):
        token = self.config.get('API', 'auth_token', fallback='')
        if not token:
            raise ValueError(
                "认证令牌未配置！\n"
                "请在 config.ini 文件的 [API] 部分设置 auth_token"
            )
        return token

    # Crawler 配置
    @property
    def max_pages(self):
        return self.config.getint('Crawler', 'max_pages', fallback=100)

    @property
    def page_size(self):
        return self.config.getint('Crawler', 'page_size', fallback=10)

    @property
    def request_delay(self):
        return self.config.getfloat('Crawler', 'request_delay', fallback=0.5)

    @property
    def max_consecutive_empty(self):
        return self.config.getint('Crawler', 'max_consecutive_empty', fallback=3)

    @property
    def request_timeout(self):
        return self.config.getint('Crawler', 'request_timeout', fallback=30)

    @property
    def verify_ssl(self):
        return self.config.getboolean('Crawler', 'verify_ssl', fallback=False)

    @property
    def max_concurrent_requests(self):
        return self.config.getint('Crawler', 'max_concurrent_requests', fallback=5)

    # Statistics 配置
    @property
    def activities_per_day(self):
        return self.config.getint('Statistics', 'activities_per_day', fallback=6)

    @property
    def default_activity_page_size(self):
        return self.config.getint('Statistics', 'default_activity_page_size', fallback=40)

    # UI 配置
    @property
    def window_width(self):
        return self.config.getint('UI', 'window_width', fallback=700)

    @property
    def window_height(self):
        return self.config.getint('UI', 'window_height', fallback=600)

    @property
    def log_height(self):
        return self.config.getint('UI', 'log_height', fallback=12)

    # Files 配置
    @property
    def default_save_dir(self):
        save_dir = self.config.get('Files', 'default_save_dir', fallback='')
        if not save_dir:
            # 默认使用桌面
            return os.path.join(os.path.expanduser("~"), "Desktop")
        return save_dir

    @property
    def excel_engine(self):
        return self.config.get('Files', 'excel_engine', fallback='openpyxl')

    # API URLs
    @property
    def activity_list_url(self):
        return f"{self.api_base_url}/portal/ums/active/home/list"

    @property
    def activity_detail_url(self):
        return f"{self.api_base_url}/portal/ums/active/info"

    @property
    def patrol_list_url(self):
        return f"{self.api_base_url}/portal/ums/patrol/home/list_new"


# 全局配置实例
_config = None


def get_config():
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config():
    """重新加载配置"""
    global _config
    _config = None
    return get_config()
