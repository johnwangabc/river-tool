# -*- coding: utf-8 -*-
"""配置管理模块 - 用于EXE打包的版本"""

import configparser
import os
from pathlib import Path


class Config:
    """配置管理类 - 只从user_config.ini读取token，其他配置内置"""

    # ==================== 内置配置（不暴露给用户） ====================

    # API配置
    _API_BASE_URL = 'https://xhbr.rwan.org.cn/prod-api'
    _ORG_ID = '843'

    # 爬虫配置
    _MAX_PAGES = 100
    _PAGE_SIZE = 10
    _REQUEST_DELAY = 0.5
    _MAX_CONSECUTIVE_EMPTY = 3
    _REQUEST_TIMEOUT = 30
    _VERIFY_SSL = False
    _MAX_CONCURRENT_REQUESTS = 5

    # 统计配置
    _ACTIVITIES_PER_DAY = 6
    _DEFAULT_ACTIVITY_PAGE_SIZE = 40

    # UI配置
    _WINDOW_WIDTH = 700
    _WINDOW_HEIGHT = 600
    _LOG_HEIGHT = 12

    # 文件配置
    _EXCEL_ENGINE = 'openpyxl'

    def __init__(self, user_config_file='user_config.ini'):
        """
        初始化配置

        Args:
            user_config_file: 用户配置文件路径（只包含token）
        """
        self.user_config_file = user_config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载用户配置文件（只读取token）"""
        # 如果是打包后的exe，配置文件应该在exe同目录
        if getattr(sys, 'frozen', False):
            # 运行在PyInstaller打包的exe中
            application_path = os.path.dirname(sys.executable)
        else:
            # 运行在普通Python环境
            application_path = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(application_path, self.user_config_file)

        # 如果配置文件不存在，创建默认的
        if not os.path.exists(config_path):
            self._create_default_user_config(config_path)

        self.config.read(config_path, encoding='utf-8')

    def _create_default_user_config(self, config_path):
        """创建默认的用户配置文件"""
        default_config = configparser.ConfigParser()
        default_config['API'] = {
            'auth_token': 'Bearer YOUR_TOKEN_HERE'
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('# 河流数据统计工具 - 用户配置\n')
            f.write('# 只需配置认证令牌即可\n\n')
            default_config.write(f)

        print(f"已创建默认配置文件: {config_path}")
        print("请编辑配置文件，填入正确的认证令牌")

    def reload(self):
        """重新加载配置"""
        self.load_config()

    # ==================== API 配置（只有token从文件读取） ====================

    @property
    def api_base_url(self):
        return self._API_BASE_URL

    @property
    def org_id(self):
        return self._ORG_ID

    @property
    def auth_token(self):
        """从用户配置文件读取token"""
        token = self.config.get('API', 'auth_token', fallback='')
        if not token or token == 'Bearer YOUR_TOKEN_HERE':
            raise ValueError(
                "认证令牌未配置！\n"
                f"请编辑 {self.user_config_file} 文件，设置正确的 auth_token"
            )
        return token

    # ==================== Crawler 配置（内置） ====================

    @property
    def max_pages(self):
        return self._MAX_PAGES

    @property
    def page_size(self):
        return self._PAGE_SIZE

    @property
    def request_delay(self):
        return self._REQUEST_DELAY

    @property
    def max_consecutive_empty(self):
        return self._MAX_CONSECUTIVE_EMPTY

    @property
    def request_timeout(self):
        return self._REQUEST_TIMEOUT

    @property
    def verify_ssl(self):
        return self._VERIFY_SSL

    @property
    def max_concurrent_requests(self):
        return self._MAX_CONCURRENT_REQUESTS

    # ==================== Statistics 配置（内置） ====================

    @property
    def activities_per_day(self):
        return self._ACTIVITIES_PER_DAY

    @property
    def default_activity_page_size(self):
        return self._DEFAULT_ACTIVITY_PAGE_SIZE

    # ==================== UI 配置（内置） ====================

    @property
    def window_width(self):
        return self._WINDOW_WIDTH

    @property
    def window_height(self):
        return self._WINDOW_HEIGHT

    @property
    def log_height(self):
        return self._LOG_HEIGHT

    # ==================== Files 配置（内置） ====================

    @property
    def default_save_dir(self):
        """默认保存目录（桌面）"""
        return os.path.join(os.path.expanduser("~"), "Desktop")

    @property
    def excel_engine(self):
        return self._EXCEL_ENGINE

    # ==================== API URLs ====================

    @property
    def activity_list_url(self):
        return f"{self.api_base_url}/portal/ums/active/home/list"

    @property
    def activity_detail_url(self):
        return f"{self.api_base_url}/portal/ums/active/info"

    @property
    def patrol_list_url(self):
        return f"{self.api_base_url}/portal/ums/patrol/home/list_new"


# 需要导入sys来检测是否在打包环境
import sys

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
