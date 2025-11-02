# -*- coding: utf-8 -*-
"""API客户端模块 - 统一的HTTP请求处理"""

import requests
import json
import time
from typing import Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

from config import get_config
from logger import get_logger
from exceptions import APIError, AuthenticationError, NetworkError

# 禁用SSL警告（如果配置中设置了不验证SSL）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger('api_client')


class APIClient:
    """统一的API客户端"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """设置会话默认参数"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
        })

    def get(self, url: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None, timeout: Optional[int] = None,
            require_auth: bool = False) -> Dict[str, Any]:
        """
        GET请求

        Args:
            url: 请求URL
            params: 查询参数
            headers: 额外的请求头
            timeout: 超时时间
            require_auth: 是否需要认证

        Returns:
            响应JSON数据

        Raises:
            APIError: API错误
            AuthenticationError: 认证错误
            NetworkError: 网络错误
        """
        if timeout is None:
            timeout = self.config.request_timeout

        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # 如果需要认证，添加token
        if require_auth:
            try:
                request_headers['Authorization'] = self.config.auth_token
            except ValueError as e:
                logger.error(f"认证配置错误: {e}")
                raise AuthenticationError(str(e))

        try:
            logger.debug(f"GET请求: {url}, 参数: {params}")

            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=timeout,
                verify=self.config.verify_ssl
            )

            # 检查HTTP状态码
            if response.status_code == 401:
                logger.error("认证失败，请检查token是否有效")
                raise AuthenticationError("认证失败，token可能已过期")

            response.raise_for_status()

            # 解析JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 响应内容: {response.text[:200]}")
                raise APIError(f"无效的JSON响应: {e}")

            # 检查业务状态码
            if isinstance(data, dict):
                code = data.get('code')
                if code is not None and code != 200:
                    error_msg = data.get('msg', f'API返回错误码: {code}')
                    logger.warning(f"API业务错误: {error_msg}")
                    raise APIError(error_msg, status_code=code, response_data=data)

            logger.debug(f"请求成功: {url}")
            return data

        except requests.RequestException as e:
            logger.error(f"网络请求失败: {url}, 错误: {e}")
            raise NetworkError(f"网络请求失败: {e}")

    def get_with_retry(self, url: str, max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """
        带重试的GET请求

        Args:
            url: 请求URL
            max_retries: 最大重试次数
            **kwargs: 传递给get()的其他参数

        Returns:
            响应JSON数据
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return self.get(url, **kwargs)
            except NetworkError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    logger.warning(f"请求失败，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"请求失败，已达到最大重试次数")
            except (APIError, AuthenticationError):
                # 这些错误不需要重试
                raise

        raise last_error

    def batch_get(self, requests_list: list, max_workers: int = None,
                  delay: float = None) -> list:
        """
        并行批量GET请求

        Args:
            requests_list: 请求列表，每项为(url, params, kwargs)元组
            max_workers: 最大并发数
            delay: 请求间隔

        Returns:
            响应列表
        """
        if max_workers is None:
            max_workers = self.config.max_concurrent_requests

        if delay is None:
            delay = self.config.request_delay

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}

            for i, request_info in enumerate(requests_list):
                if len(request_info) == 2:
                    url, params = request_info
                    kwargs = {}
                else:
                    url, params, kwargs = request_info

                # 添加延迟避免请求过快
                if delay > 0 and i > 0:
                    time.sleep(delay)

                future = executor.submit(self.get, url, params, **kwargs)
                future_to_index[future] = i

            # 收集结果
            results = [None] * len(requests_list)
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"批量请求第{index}项失败: {e}")
                    results[index] = None

        return results


# 全局客户端实例
_api_client = None


def get_api_client():
    """获取全局API客户端"""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
