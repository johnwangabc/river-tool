# -*- coding: utf-8 -*-
"""自定义异常类"""


class RiverPatrolException(Exception):
    """基础异常类"""
    pass


class ConfigError(RiverPatrolException):
    """配置错误"""
    pass


class APIError(RiverPatrolException):
    """API请求错误"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(APIError):
    """认证错误"""
    pass


class DataProcessingError(RiverPatrolException):
    """数据处理错误"""
    pass


class NetworkError(RiverPatrolException):
    """网络错误"""
    pass
