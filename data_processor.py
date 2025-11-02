# -*- coding: utf-8 -*-
"""数据处理模块 - 提取公共的数据处理逻辑"""

import datetime
from typing import List, Dict
from collections import defaultdict

from logger import get_logger

logger = get_logger('data_processor')


class DataProcessor:
    """数据处理工具类"""

    @staticmethod
    def decode_text(text: str) -> str:
        """解码文本"""
        if isinstance(text, str):
            try:
                return text.encode('latin-1').decode('utf-8')
            except Exception:
                return text
        return text

    @staticmethod
    def filter_by_date(items: List[Dict], target_date: str,
                       date_field: str = 'createTime',
                       date_format: str = '%Y-%m-%d %H:%M:%S') -> List[Dict]:
        """
        按日期过滤数据

        Args:
            items: 数据列表
            target_date: 目标日期 (YYYY-MM-DD)
            date_field: 日期字段名
            date_format: 日期格式

        Returns:
            过滤后的数据列表
        """
        try:
            target_datetime = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            filtered_items = []

            for item in items:
                create_time = item.get(date_field)
                if create_time:
                    try:
                        item_datetime = datetime.datetime.strptime(create_time, date_format)
                        if item_datetime >= target_datetime:
                            filtered_items.append(item)
                    except ValueError as e:
                        logger.warning(f"日期解析失败: {create_time}, 错误: {e}")
                        continue

            # 按日期倒序排序
            filtered_items.sort(key=lambda x: x.get(date_field, ''), reverse=True)
            logger.info(f"日期过滤: 原始{len(items)}条 -> 过滤后{len(filtered_items)}条")
            return filtered_items

        except ValueError as e:
            logger.error(f"目标日期格式错误: {target_date}, 错误: {e}")
            return []

    @staticmethod
    def aggregate_user_posts(data: List[Dict],
                            nick_field: str = 'nickName',
                            time_field: str = 'createTime',
                            msg_field: str = 'msg',
                            river_field: str = 'riverName') -> List[Dict]:
        """
        聚合用户发帖数据

        Args:
            data: 原始数据列表
            nick_field: 昵称字段
            time_field: 时间字段
            msg_field: 消息字段
            river_field: 河流字段

        Returns:
            聚合后的用户统计列表
        """
        user_stats = {}

        for item in data:
            nickname = DataProcessor.decode_text(item.get(nick_field, '未知用户'))
            post_time = item.get(time_field, '')
            msg = DataProcessor.decode_text(item.get(msg_field, ''))
            river_name = DataProcessor.decode_text(item.get(river_field, ''))

            if nickname not in user_stats:
                user_stats[nickname] = {
                    '发帖次数': 0,
                    '所有发帖时间': [],
                    '所有发帖消息': [],
                    '所有河流名称': []
                }

            user_stats[nickname]['发帖次数'] += 1
            user_stats[nickname]['所有发帖时间'].append(post_time)
            user_stats[nickname]['所有发帖消息'].append(msg)
            user_stats[nickname]['所有河流名称'].append(river_name)

        # 转换为列表格式
        user_data_list = []
        for user, stats in user_stats.items():
            user_data_list.append({
                '发帖人': user,
                '发帖次数': stats['发帖次数'],
                '所有发帖时间': DataProcessor._format_times(stats['所有发帖时间']),
                '所有发帖消息': DataProcessor._format_messages(stats['所有发帖消息']),
                '所有河流名称': DataProcessor._format_rivers(stats['所有河流名称']),
                '完整发帖记录': DataProcessor._create_complete_records(
                    stats['所有发帖时间'],
                    stats['所有发帖消息'],
                    stats['所有河流名称']
                )
            })

        logger.info(f"用户聚合完成: {len(user_data_list)}个用户, {len(data)}条发帖")
        return user_data_list

    @staticmethod
    def _format_times(times: List[str]) -> str:
        """格式化所有发帖时间"""
        if not times:
            return ""
        sorted_times = sorted(times, reverse=True)
        return "\n".join([f"{i+1}. {time}" for i, time in enumerate(sorted_times)])

    @staticmethod
    def _format_messages(messages: List[str]) -> str:
        """格式化所有发帖消息"""
        if not messages:
            return ""
        return "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(messages)])

    @staticmethod
    def _format_rivers(rivers: List[str]) -> str:
        """格式化所有河流名称"""
        if not rivers:
            return ""
        return "\n".join([f"{i+1}. {river}" for i, river in enumerate(rivers)])

    @staticmethod
    def _create_complete_records(times: List[str], messages: List[str],
                                 rivers: List[str]) -> str:
        """创建完整的发帖记录"""
        if not times:
            return ""

        records = []
        combined = list(zip(times, messages, rivers))
        combined_sorted = sorted(combined, key=lambda x: x[0], reverse=True)

        for i, (time, msg, river) in enumerate(combined_sorted):
            records.append(f"【第{i+1}次发帖】")
            records.append(f"时间: {time}")
            records.append(f"河流: {river}")
            records.append(f"内容: {msg}")
            records.append("")  # 空行分隔

        return "\n".join(records)

    @staticmethod
    def calculate_page_size(target_date_str: str, activities_per_day: int = 6) -> int:
        """
        根据目标日期计算合适的page_size

        Args:
            target_date_str: 目标日期字符串 (YYYY-MM-DD)
            activities_per_day: 每天预估活动数

        Returns:
            建议的page_size
        """
        try:
            target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            current_date = datetime.datetime.now().date()

            if target_date > current_date:
                return 40  # 默认值

            days_diff = (current_date - target_date).days + 1
            if days_diff <= 0:
                return 40

            estimated_activities = days_diff * activities_per_day
            page_size = min(estimated_activities + 10, 200)  # 加10缓冲，最大200

            logger.info(f"计算page_size: {days_diff}天 * {activities_per_day} = {estimated_activities}, "
                       f"建议page_size={page_size}")
            return page_size

        except ValueError:
            logger.warning(f"日期格式错误: {target_date_str}, 使用默认值")
            return 40

    @staticmethod
    def aggregate_comprehensive_stats(patrol_users: List[Dict],
                                      evaluation_users: List[Dict],
                                      activity_participants: Dict[str, int]) -> List[Dict]:
        """
        聚合综合统计数据

        Args:
            patrol_users: 巡护用户数据
            evaluation_users: 评测用户数据
            activity_participants: 活动参与者数据 {昵称: 次数}

        Returns:
            综合统计列表
        """
        user_stats = defaultdict(lambda: {
            '巡护次数': 0,
            '评测次数': 0,
            '活动次数': 0,
            '总次数': 0
        })

        # 统计巡护
        for user in patrol_users:
            username = user['发帖人']
            count = user['发帖次数']
            user_stats[username]['巡护次数'] = count
            user_stats[username]['总次数'] += count

        # 统计评测
        for user in evaluation_users:
            username = user['发帖人']
            count = user['发帖次数']
            user_stats[username]['评测次数'] = count
            user_stats[username]['总次数'] += count

        # 统计活动
        for username, count in activity_participants.items():
            user_stats[username]['活动次数'] = count
            user_stats[username]['总次数'] += count

        # 转换为列表
        stats_list = []
        for user, stats in user_stats.items():
            if stats['总次数'] > 0:
                stats_list.append({
                    '姓名': user,
                    '巡护次数': stats['巡护次数'],
                    '评测次数': stats['评测次数'],
                    '活动次数': stats['活动次数'],
                    '总次数': stats['总次数']
                })

        # 按总次数降序排序
        stats_list.sort(key=lambda x: x['总次数'], reverse=True)

        logger.info(f"综合统计聚合完成: {len(stats_list)}个用户")
        return stats_list
