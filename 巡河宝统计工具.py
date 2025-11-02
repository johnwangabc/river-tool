import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import datetime
import time
import pandas as pd
from collections import defaultdict
from typing import List, Dict
import threading
import os
import sys
import locale
import urllib3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -*- coding: utf-8 -*-
# 设置系统编码
if sys.platform.startswith('win'):
    # Windows系统
    if hasattr(sys, 'getwindowsversion'):
        if sys.getwindowsversion().major >= 6:  # Windows Vista及以上
            os.system('chcp 65001 > nul')  # 设置控制台编码为UTF-8
    # 设置locale
    try:
        locale.setlocale(locale.LC_ALL, 'chinese')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        except:
            pass

# 设置标准输出编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

class ActivityAnalyzer:
    """活动数据分析功能"""
    
    def get_limited_activities(self, org_id: str = "843", page_size: int = 40) -> List[Dict]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
        }
        
        url = "https://xhbr.rwan.org.cn/prod-api/portal/ums/active/home/list"
        params = {
            'pageNum': 1,
            'pageSize': page_size,
            'orgId': org_id
        }
        
        try:
            # 添加 verify=False 忽略SSL验证
            response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 200 and 'rows' in data:
                return data['rows']
            else:
                return []
                
        except Exception as e:
            return []

    def get_activity_detail(self, activity_id: int) -> Dict:
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOiJYY3g6MjMyMTMzMCIsInJuU3RyIjoiVzZEaW1sUnMyWDhpbXNuY1FlMFYxT25pMlE5Q2tkMHoifQ.3-HgNBeGScmvVdZWl4RS11dPF1KlvduLgvaosmkj-KA',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771',
            'xweb_xhr': '1',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://servicewechat.com/wxbc01292ab8abd5ba/324/page-frame.html'
        }
        
        cookies = {
            'INGRESSCOOKIE': '1760265190.115.27.31074|76c919bb3837d580c82faf757a831e9e'
        }
        
        url = f"https://xhbr.rwan.org.cn/prod-api/portal/ums/active/info/{activity_id}"
        params = {
            'pageSize': 10,
            'pageNum': 1
        }
        
        try:
            # 添加 verify=False 忽略SSL验证
            response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=30, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 200:
                return data
            else:
                return None
                
        except Exception as e:
            return None

    def filter_activities_by_date(self, activities: List[Dict], target_date: str) -> List[Dict]:
        try:
            target_datetime = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            filtered_activities = []
            
            for activity in activities:
                create_time = activity.get('createTime')
                if create_time:
                    activity_datetime = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                    if activity_datetime >= target_datetime:
                        filtered_activities.append(activity)
            
            filtered_activities.sort(key=lambda x: x.get('createTime', ''), reverse=True)
            return filtered_activities
            
        except ValueError:
            return []

    def export_activities_to_excel(self, activities_data: List[Dict], output_file: str):
        activity_basic_data = []
        
        for activity_data in activities_data:
            if activity_data.get('code') == 200 and 'data' in activity_data:
                activity_info = activity_data['data']
                
                activity_basic_data.append({
                    '活动ID': activity_info.get('id'),
                    '活动名称': activity_info.get('actName', '未知'),
                    '发起人': activity_info.get('memberName', '未知'),
                    '发起人电话': activity_info.get('memberMobile', '未提供'),
                    '开始时间': activity_info.get('startTime', '未知'),
                    '活动地址': activity_info.get('address', '未知'),
                    '活动类型': '巡河' if activity_info.get('actType') == 2 else '净滩',
                    '状态': activity_info.get('status'),
                    '最大人数': activity_info.get('maxMemberNum', 0),
                    '实际参与人数': activity_info.get('signInMemberNum', 0),
                    '浏览量': activity_info.get('lookNum', 0),
                    '组织名称': activity_info.get('orgName', '未知')
                })
        
        df = pd.DataFrame(activity_basic_data)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='活动基本信息', index=False)
            
            stats_data = {
                '统计项目': ['活动总数', '巡河活动数', '净滩活动数', '总参与人数', '平均参与人数'],
                '数值': [
                    len(activity_basic_data),
                    len([x for x in activity_basic_data if x['活动类型'] == '巡河']),
                    len([x for x in activity_basic_data if x['活动类型'] == '净滩']),
                    sum([x['实际参与人数'] for x in activity_basic_data]),
                    sum([x['实际参与人数'] for x in activity_basic_data]) / len(activity_basic_data) if activity_basic_data else 0
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='活动统计', index=False)

    def analyze_participants(self, activities_data: List[Dict], output_file: str):
        participants = defaultdict(lambda: {
            'nickName': '', 'mobile': '', 'activity_count': 0, 'activity_names': set(), 'activities': []
        })
        
        for activity_data in activities_data:
            if activity_data.get('code') == 200 and 'data' in activity_data:
                activity_info = activity_data['data']
                activity_id = activity_info.get('id')
                activity_name = activity_info.get('actName', '未知活动')
                start_time = activity_info.get('startTime', '未知时间')
                
                member_info = activity_info.get('activeMemberBoTableDataInfo', {})
                members = member_info.get('rows', [])
                
                for member in members:
                    member_id = member.get('id')
                    nick_name = member.get('nickName', '未知')
                    mobile = member.get('mobile', '')
                    
                    if member_id:
                        participants[member_id]['nickName'] = nick_name
                        if mobile and not participants[member_id]['mobile']:
                            participants[member_id]['mobile'] = mobile
                        
                        participants[member_id]['activity_count'] += 1
                        participants[member_id]['activity_names'].add(activity_name)
                        
                        activity_detail = {
                            'activity_id': activity_id,
                            'activity_name': activity_name,
                            'start_time': start_time,
                            'isSignupStatus': member.get('isSignupStatus', 0)
                        }
                        participants[member_id]['activities'].append(activity_detail)
        
        # 准备Excel数据
        excel_data = []
        for member_id, info in participants.items():
            activity_names_str = '、'.join(sorted(info['activity_names']))
            
            excel_data.append({
                '参与者ID': member_id,
                '昵称': info['nickName'],
                '参与活动数': info['activity_count'],
                '电话号': info['mobile'] if info['mobile'] else '未提供',
                '参加的所有活动名称': activity_names_str
            })
        
        excel_data.sort(key=lambda x: x['参与活动数'], reverse=True)
        df = pd.DataFrame(excel_data)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='参与者统计', index=False)
            
            detail_data = []
            for member_id, info in participants.items():
                for activity in info['activities']:
                    detail_data.append({
                        '参与者ID': member_id,
                        '昵称': info['nickName'],
                        '电话号': info['mobile'] if info['mobile'] else '未提供',
                        '活动ID': activity['activity_id'],
                        '活动名称': activity['activity_name'],
                        '活动时间': activity['start_time'],
                        '报名状态': '已签到' if activity['isSignupStatus'] == 1 else '未签到'
                    })
            
            detail_df = pd.DataFrame(detail_data)
            detail_df.to_excel(writer, sheet_name='活动详情', index=False)
            
            activity_stats = []
            for activity_data in activities_data:
                if activity_data.get('code') == 200 and 'data' in activity_data:
                    activity_info = activity_data['data']
                    activity_stats.append({
                        '活动ID': activity_info.get('id'),
                        '活动名称': activity_info.get('actName'),
                        '活动时间': activity_info.get('startTime'),
                        '活动类型': '巡河' if activity_info.get('actType') == 2 else '净滩',
                        '总参与人数': activity_info.get('signInMemberNum', 0),
                        '最大人数': activity_info.get('maxMemberNum', 0),
                        '实际参与者数': len(activity_info.get('activeMemberBoTableDataInfo', {}).get('rows', []))
                    })
            
            stats_df = pd.DataFrame(activity_stats)
            stats_df.to_excel(writer, sheet_name='活动统计', index=False)
        
        return participants

class RiverPatrolCrawler:
    """河流巡查数据爬虫"""
    
    def __init__(self, use_type=2):
        self.base_url = "https://xhbr.rwan.org.cn/prod-api/portal/ums/patrol/home/list_new"
        self.use_type = use_type
        self.headers = {
            'Host': 'xhbr.rwan.org.cn',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771',
            'xweb_xhr': '1',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wxbc01292ab8abd5ba/324/page-frame.html',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
    def crawl_all_data(self, start_date, progress_callback=None):
        """爬取所有分页数据 - 修复提前停止问题"""
        all_data = []
        page_num = 1
        page_size = 10
        max_pages = 100
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        if progress_callback:
            progress_callback("开始爬取所有符合条件的数据...")
        
        while page_num <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            try:
                params = {
                    'pageNum': page_num,
                    'pageSize': page_size,
                    'useType': self.use_type,
                    'orgId': 843
                }
                
                # 已经包含 verify=False
                response = requests.get(
                    self.base_url, 
                    params=params, 
                    headers=self.headers,
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == 200 and data['rows']:
                        rows = data['rows']
                        
                        # 过滤日期
                        filtered_rows = []
                        older_data_count = 0
                        newest_date = None
                        oldest_date = None
                        
                        for row in rows:
                            try:
                                post_time = datetime.datetime.strptime(row['createTime'], '%Y-%m-%d %H:%M:%S')
                                
                                # 记录最旧和最新的日期
                                if newest_date is None or post_time > newest_date:
                                    newest_date = post_time
                                if oldest_date is None or post_time < oldest_date:
                                    oldest_date = post_time
                                
                                if post_time >= start_date:
                                    filtered_rows.append(row)
                                else:
                                    older_data_count += 1
                            except Exception as e:
                                continue
                        
                        # 添加符合条件的数据
                        all_data.extend(filtered_rows)
                        
                        if progress_callback:
                            date_range = f"本页日期范围: {oldest_date.strftime('%Y-%m-%d') if oldest_date else 'N/A'} 到 {newest_date.strftime('%Y-%m-%d') if newest_date else 'N/A'}"
                            progress_callback(f"第{page_num}页: {len(filtered_rows)}条符合条件, {older_data_count}条较早数据. {date_range}")
                        
                        # 判断是否继续
                        if len(filtered_rows) == 0:
                            consecutive_empty_pages += 1
                            if progress_callback:
                                progress_callback(f"第{page_num}页没有符合条件的数据 ({consecutive_empty_pages}/{max_consecutive_empty})")
                        else:
                            consecutive_empty_pages = 0
                        
                        # 修复：不再因为当前页有较早数据就提前停止，继续翻页
                        # 因为数据可能不是按时间顺序排列的
                        page_num += 1
                    else:
                        if progress_callback:
                            progress_callback(f"第{page_num}页无数据或API错误")
                        consecutive_empty_pages += 1
                else:
                    if progress_callback:
                        progress_callback(f"第{page_num}页HTTP请求失败: {response.status_code}")
                    consecutive_empty_pages += 1
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(f"第{page_num}页爬取出错: {str(e)}")
                consecutive_empty_pages += 1
        
        if progress_callback:
            if consecutive_empty_pages >= max_consecutive_empty:
                progress_callback(f"连续{consecutive_empty_pages}页没有符合条件的数据，停止爬取")
            elif page_num > max_pages:
                progress_callback(f"已达到最大页数限制({max_pages})，停止爬取")
            progress_callback(f"爬取完成，共获取{len(all_data)}条符合条件的数据")
        
        return all_data

    def process_user_data(self, data):
        """处理用户数据，整合所有发帖时间和消息"""
        if not data:
            return []
        
        user_stats = {}
        
        for item in data:
            # 处理编码问题
            nickname = self.decode_text(item.get('nickName', '未知用户'))
            post_time = item.get('createTime', '')
            msg = self.decode_text(item.get('msg', ''))
            river_name = self.decode_text(item.get('riverName', ''))
            
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
                '所有发帖时间': self.format_times(stats['所有发帖时间']),
                '所有发帖消息': self.format_messages(stats['所有发帖消息']),
                '所有河流名称': self.format_rivers(stats['所有河流名称']),
                '完整发帖记录': self.create_complete_records(stats['所有发帖时间'], stats['所有发帖消息'], stats['所有河流名称'])
            })
        
        return user_data_list

    def decode_text(self, text):
        """解码文本"""
        if isinstance(text, str):
            try:
                return text.encode('latin-1').decode('utf-8')
            except:
                return text
        return text

    def format_times(self, times):
        """格式化所有发帖时间"""
        if not times:
            return ""
        # 按时间倒序排列
        sorted_times = sorted(times, reverse=True)
        return "\n".join([f"{i+1}. {time}" for i, time in enumerate(sorted_times)])

    def format_messages(self, messages):
        """格式化所有发帖消息"""
        if not messages:
            return ""
        return "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(messages)])

    def format_rivers(self, rivers):
        """格式化所有河流名称"""
        if not rivers:
            return ""
        return "\n".join([f"{i+1}. {river}" for i, river in enumerate(rivers)])

    def create_complete_records(self, times, messages, rivers):
        """创建完整的发帖记录"""
        if not times:
            return ""
        
        records = []
        # 按时间倒序排列所有记录
        combined = list(zip(times, messages, rivers))
        combined_sorted = sorted(combined, key=lambda x: x[0], reverse=True)
        
        for i, (time, msg, river) in enumerate(combined_sorted):
            records.append(f"【第{i+1}次发帖】")
            records.append(f"时间: {time}")
            records.append(f"河流: {river}")
            records.append(f"内容: {msg}")
            records.append("")  # 空行分隔
        
        return "\n".join(records)

    def save_to_excel(self, user_data_list, filename):
        """保存数据到Excel"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 创建用户统计表
                if user_data_list:
                    df_users = pd.DataFrame(user_data_list)
                    df_users = df_users.sort_values('发帖次数', ascending=False)
                    df_users.to_excel(writer, sheet_name='用户发帖统计', index=False)
                
                # 创建数据概览表
                overview_data = [{
                    '总发帖人数': len(user_data_list),
                    '总发帖次数': sum([user['发帖次数'] for user in user_data_list]),
                    '平均发帖次数': round(sum([user['发帖次数'] for user in user_data_list]) / len(user_data_list), 2) if user_data_list else 0,
                    '最多发帖数': max([user['发帖次数'] for user in user_data_list]) if user_data_list else 0,
                    '最少发帖数': min([user['发帖次数'] for user in user_data_list]) if user_data_list else 0,
                    '数据生成时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }]
                df_overview = pd.DataFrame(overview_data)
                df_overview.to_excel(writer, sheet_name='数据概览', index=False)
            
            return True
        except Exception as e:
            print(f"保存Excel时出错: {str(e)}")
            return False

class IntegratedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("河流数据统计工具集")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 初始化功能类
        self.activity_analyzer = ActivityAnalyzer()
        self.river_crawler_2 = RiverPatrolCrawler(use_type=2)  # 河流评测
        self.river_crawler_1 = RiverPatrolCrawler(use_type=1)  # 河流巡护
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建四个选项卡页面
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)  # 新增的综合统计选项卡
        
        self.notebook.add(self.tab1, text="活动数据统计")
        self.notebook.add(self.tab2, text="河流评测数据")
        self.notebook.add(self.tab3, text="河流巡护数据")
        self.notebook.add(self.tab4, text="综合次数统计")
        
        # 设置每个选项卡的UI
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()  # 设置综合统计选项卡
        
    def setup_tab1(self):
        """设置活动数据统计选项卡"""
        # 标题
        title_label = ttk.Label(self.tab1, text="活动数据统计工具", font=("微软雅黑", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 说明文本
        desc_text = """本工具用于获取和统计活动数据：
1. 获取指定日期及以后的活动信息
2. 导出活动基本信息Excel
3. 统计参与者信息并导出Excel
        
根据目标日期自动计算获取的数据量（每天约6个活动）"""
        desc_label = ttk.Label(self.tab1, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 10))
        
        # 输入框架
        input_frame = ttk.Frame(self.tab1)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 日期选择
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="目标日期:").pack(side=tk.LEFT)
        self.tab1_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(date_frame, textvariable=self.tab1_date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="(格式: YYYY-MM-DD, 包含此日期及以后的活动)").pack(side=tk.LEFT)
        
        # 预计数据量显示
        info_frame = ttk.Frame(input_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.tab1_info_var = tk.StringVar(value="预计获取数据量: 请选择日期")
        info_label = ttk.Label(info_frame, textvariable=self.tab1_info_var, foreground="blue")
        info_label.pack(side=tk.LEFT)
        
        # 绑定日期变化事件
        date_entry.bind('<KeyRelease>', self.update_page_size_info)
        date_entry.bind('<FocusOut>', self.update_page_size_info)
        
        # 保存路径选择
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="保存路径:").pack(side=tk.LEFT)
        self.tab1_path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.tab1_path_var, width=40)
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="浏览", command=lambda: self.browse_path(self.tab1_path_var)).pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(self.tab1)
        button_frame.pack(pady=10)
        
        self.tab1_start_button = ttk.Button(button_frame, text="开始统计", command=self.start_tab1_analysis)
        self.tab1_start_button.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        progress_frame = ttk.Frame(self.tab1)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.tab1_progress_var = tk.StringVar(value="等待开始...")
        progress_label = ttk.Label(progress_frame, textvariable=self.tab1_progress_var)
        progress_label.pack()
        
        self.tab1_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.tab1_progress.pack(fill=tk.X, pady=5)
        
        # 日志显示
        log_frame = ttk.Frame(self.tab1)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(log_frame, text="执行日志:").pack(anchor=tk.W)
        
        self.tab1_log_text = tk.Text(log_frame, height=12)
        scrollbar = ttk.Scrollbar(log_frame, command=self.tab1_log_text.yview)
        self.tab1_log_text.configure(yscrollcommand=scrollbar.set)
        
        self.tab1_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_tab2(self):
        """设置河流评测数据选项卡"""
        self.setup_crawler_tab(self.tab2, "河流评测数据爬虫 (UseType=2)", "河流评测数据", self.start_tab2_crawling)
        
    def setup_tab3(self):
        """设置河流巡护数据选项卡"""
        self.setup_crawler_tab(self.tab3, "河流巡护数据爬虫 (UseType=1)", "河流巡护数据", self.start_tab3_crawling)
        
    def setup_tab4(self):
        """设置综合次数统计选项卡"""
        # 标题
        title_label = ttk.Label(self.tab4, text="综合次数统计", font=("微软雅黑", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 说明文本
        desc_text = """本功能统计从指定日期开始：
• 每个人的巡护次数（useType=1）
• 每个人的评测次数（useType=2） 
• 每个人的活动参与次数
        
统计结果将按总次数排序，方便了解每个人的综合参与情况"""
        desc_label = ttk.Label(self.tab4, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 10))
        
        # 输入框架
        input_frame = ttk.Frame(self.tab4)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 日期选择
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="开始日期:").pack(side=tk.LEFT)
        self.tab4_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(date_frame, textvariable=self.tab4_date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="(格式: YYYY-MM-DD, 统计此日期及以后的数据)").pack(side=tk.LEFT)
        
        # 保存路径选择
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="保存路径:").pack(side=tk.LEFT)
        self.tab4_path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.tab4_path_var, width=40)
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="浏览", command=lambda: self.browse_path(self.tab4_path_var)).pack(side=tk.LEFT, padx=5)
        
        # 文件名预览
        filename_frame = ttk.Frame(self.tab4)
        filename_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filename_frame, text="生成文件名:").pack(side=tk.LEFT)
        self.tab4_filename_var = tk.StringVar()
        filename_label = ttk.Label(filename_frame, textvariable=self.tab4_filename_var, foreground="blue")
        filename_label.pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(self.tab4)
        button_frame.pack(pady=10)
        
        self.tab4_start_button = ttk.Button(button_frame, text="开始统计", command=self.start_tab4_analysis)
        self.tab4_start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="生成图表", command=self.generate_tab4_charts).pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        progress_frame = ttk.Frame(self.tab4)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.tab4_progress_var = tk.StringVar(value="等待开始...")
        progress_label = ttk.Label(progress_frame, textvariable=self.tab4_progress_var)
        progress_label.pack()
        
        self.tab4_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.tab4_progress.pack(fill=tk.X, pady=5)
        
        # 日志显示
        log_frame = ttk.Frame(self.tab4)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(log_frame, text="执行日志:").pack(anchor=tk.W)
        
        self.tab4_log_text = tk.Text(log_frame, height=12)
        scrollbar = ttk.Scrollbar(log_frame, command=self.tab4_log_text.yview)
        self.tab4_log_text.configure(yscrollcommand=scrollbar.set)
        
        self.tab4_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置默认文件夹和绑定事件
        self.set_default_folder(self.tab4_path_var)
        self.tab4_date_var.trace('w', self.update_tab4_filename_preview)
        self.tab4_path_var.trace('w', self.update_tab4_filename_preview)
        self.update_tab4_filename_preview()
        
    def setup_crawler_tab(self, tab, title, data_type, start_command):
        """设置爬虫选项卡的通用UI"""
        # 标题
        title_label = ttk.Label(tab, text=title, font=("微软雅黑", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 开始日期选择
        date_frame = ttk.Frame(tab)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="开始日期:").pack(side=tk.LEFT)
        date_var = tk.StringVar(value=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'))
        setattr(self, f"{tab}_date_var", date_var)
        
        date_entry_frame = ttk.Frame(date_frame)
        date_entry_frame.pack(side=tk.LEFT, padx=5)
        
        date_entry = ttk.Entry(date_entry_frame, textvariable=date_var, width=15)
        date_entry.pack(side=tk.LEFT)
        ttk.Button(date_entry_frame, text="选择日期", 
                  command=lambda: self.choose_date(date_var)).pack(side=tk.LEFT, padx=5)
        
        # 文件保存文件夹
        path_frame = ttk.Frame(tab)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="保存文件夹:").pack(side=tk.LEFT)
        path_var = tk.StringVar()
        setattr(self, f"{tab}_path_var", path_var)
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        path_entry = ttk.Entry(path_entry_frame, textvariable=path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_entry_frame, text="选择文件夹", 
                  command=lambda: self.choose_folder(path_var)).pack(side=tk.LEFT, padx=5)
        
        # 文件名预览
        filename_frame = ttk.Frame(tab)
        filename_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filename_frame, text="生成文件名:").pack(side=tk.LEFT)
        filename_var = tk.StringVar()
        setattr(self, f"{tab}_filename_var", filename_var)
        filename_label = ttk.Label(filename_frame, textvariable=filename_var, foreground="blue")
        filename_label.pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(tab)
        button_frame.pack(pady=10)
        
        start_button = ttk.Button(button_frame, text="开始爬取", command=start_command)
        start_button.pack(side=tk.LEFT, padx=5)
        setattr(self, f"{tab}_start_button", start_button)
        
        ttk.Button(button_frame, text="生成图表", 
                  command=lambda: self.generate_charts(tab)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空日志", 
                  command=lambda: getattr(self, f"{tab}_log_text").delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        progress = ttk.Progressbar(tab, mode='indeterminate')
        progress.pack(fill=tk.X, pady=5)
        setattr(self, f"{tab}_progress", progress)
        
        # 日志文本框
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(log_frame, text="运行日志:").pack(anchor=tk.W)
        
        log_text = tk.Text(log_frame, height=12)
        scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        setattr(self, f"{tab}_log_text", log_text)
        
        # 设置默认文件夹和绑定事件
        self.set_default_folder(path_var)
        date_var.trace('w', lambda *args: self.update_filename_preview(tab, data_type))
        path_var.trace('w', lambda *args: self.update_filename_preview(tab, data_type))
        self.update_filename_preview(tab, data_type)
        
    # 选项卡1的方法
    def browse_path(self, path_var):
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)
    
    def update_page_size_info(self, event=None):
        """更新预计数据量信息"""
        try:
            target_date_str = self.tab1_date_var.get()
            if not target_date_str:
                return
                
            target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            current_date = datetime.datetime.now().date()
            
            if target_date > current_date:
                self.tab1_info_var.set("预计获取数据量: 目标日期不能晚于今天")
                return
                
            # 计算天数差
            days_diff = (current_date - target_date).days + 1  # 包含目标日期当天
            if days_diff <= 0:
                self.tab1_info_var.set("预计获取数据量: 目标日期不能晚于今天")
                return
            
            # 计算预计数据量（每天6个活动）
            estimated_activities = days_diff * 6
            page_size = min(estimated_activities + 10, 200)  # 加10作为缓冲，最大200
            
            self.tab1_info_var.set(f"预计获取数据量: {estimated_activities}个活动 (将获取{page_size}条数据)")
            
        except ValueError:
            pass
    
    def calculate_page_size(self, target_date_str):
        """根据目标日期计算合适的page_size"""
        try:
            target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            current_date = datetime.datetime.now().date()
            
            if target_date > current_date:
                return 40  # 默认值
            
            # 计算天数差
            days_diff = (current_date - target_date).days + 1  # 包含目标日期当天
            if days_diff <= 0:
                return 40  # 默认值
            
            # 计算预计数据量（每天6个活动）
            estimated_activities = days_diff * 6
            # 设置page_size为预计数据量加10作为缓冲，最大不超过200
            page_size = min(estimated_activities + 10, 200)
            
            return page_size
            
        except ValueError:
            return 40  # 默认值
    
    def log_tab1(self, message):
        self.tab1_log_text.insert(tk.END, f"{message}\n")
        self.tab1_log_text.see(tk.END)
        self.root.update()
    
    def start_tab1_analysis(self):
        if not self.validate_tab1_inputs():
            return
        
        # 禁用开始按钮
        self.tab1_start_button.config(state='disabled')
        self.tab1_progress.start()
        
        # 在新线程中执行分析
        thread = threading.Thread(target=self.run_tab1_analysis)
        thread.daemon = True
        thread.start()
    
    def validate_tab1_inputs(self):
        # 验证日期格式
        try:
            target_date = datetime.datetime.strptime(self.tab1_date_var.get(), "%Y-%m-%d")
            current_date = datetime.datetime.now()
            
            if target_date.date() > current_date.date():
                messagebox.showerror("错误", "目标日期不能晚于今天")
                return False
                
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return False
        
        # 验证保存路径
        if not self.tab1_path_var.get():
            messagebox.showerror("错误", "请选择保存路径")
            return False
        
        if not os.path.exists(self.tab1_path_var.get()):
            try:
                os.makedirs(self.tab1_path_var.get())
            except:
                messagebox.showerror("错误", "保存路径无效或无法创建")
                return False
        
        return True
    
    def run_tab1_analysis(self):
        try:
            target_date = self.tab1_date_var.get()
            save_path = self.tab1_path_var.get()
            
            # 根据时间差计算page_size
            page_size = self.calculate_page_size(target_date)
            
            self.log_tab1("=== 开始执行活动数据统计 ===")
            self.log_tab1(f"目标日期: {target_date}")
            self.log_tab1(f"自动计算获取数量: {page_size} 条数据")
            
            # 获取活动数据
            self.log_tab1("正在获取活动列表数据...")
            activities = self.activity_analyzer.get_limited_activities(page_size=page_size)
            
            if not activities:
                self.log_tab1("❌ 没有获取到任何活动数据")
                self.tab1_analysis_complete(False)
                return
            
            # 筛选活动
            self.log_tab1(f"正在筛选 {target_date} 及以后的活动...")
            filtered_activities = self.activity_analyzer.filter_activities_by_date(activities, target_date)
            
            if not filtered_activities:
                self.log_tab1(f"❌ 在 {target_date} 之后没有找到任何活动")
                self.tab1_analysis_complete(False)
                return
            
            self.log_tab1(f"✅ 找到 {len(filtered_activities)} 个在 {target_date} 及以后的活动")
            
            # 获取详细信息
            self.log_tab1("正在获取每个活动的详细信息...")
            info_responses = []
            
            for i, activity in enumerate(filtered_activities, 1):
                activity_id = activity.get('id')
                activity_name = activity.get('actName', '未知')
                
                if activity_id:
                    self.log_tab1(f"[{i}/{len(filtered_activities)}] 获取活动: {activity_name} (ID: {activity_id})")
                    
                    info_data = self.activity_analyzer.get_activity_detail(activity_id)
                    if info_data:
                        info_responses.append(info_data)
                        self.log_tab1(f"  ✅ 成功获取活动详情")
                    else:
                        self.log_tab1(f"  ❌ 获取活动详情失败")
                    
                    time.sleep(0.5)
            
            if not info_responses:
                self.log_tab1("❌ 未能获取到任何活动的详细信息")
                self.tab1_analysis_complete(False)
                return
            
            # 生成时间戳
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON文件
            json_filename = os.path.join(save_path, f"info_responses_{target_date}_{timestamp}.json")
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(info_responses, f, ensure_ascii=False, indent=2)
            self.log_tab1(f"💾 JSON数据已保存到: {json_filename}")
            
            # 导出活动基本信息
            activities_excel = os.path.join(save_path, f"活动基本信息_{target_date}_{timestamp}.xlsx")
            self.activity_analyzer.export_activities_to_excel(info_responses, activities_excel)
            self.log_tab1(f"📋 活动基本信息已保存到: {activities_excel}")
            
            # 导出参与者统计
            participants_excel = os.path.join(save_path, f"参与者统计_{target_date}_{timestamp}.xlsx")
            participants = self.activity_analyzer.analyze_participants(info_responses, participants_excel)
            self.log_tab1(f"📊 参与者统计已保存到: {participants_excel}")
            
            # 完成
            self.log_tab1(f"\n🎉 程序执行完成！")
            self.log_tab1(f"📈 共分析 {len(info_responses)} 个活动，{len(participants)} 位参与者")
            self.log_tab1(f"📁 所有文件已保存到: {save_path}")
            
            self.tab1_analysis_complete(True)
            
        except Exception as e:
            self.log_tab1(f"❌ 执行过程中发生错误: {str(e)}")
            self.tab1_analysis_complete(False)
    
    def tab1_analysis_complete(self, success):
        self.tab1_progress.stop()
        self.tab1_start_button.config(state='normal')
        
        if success:
            messagebox.showinfo("完成", "活动数据统计完成！")
        else:
            messagebox.showerror("错误", "执行过程中出现错误，请查看日志")
    
    # 选项卡2和3的通用方法
    def choose_date(self, date_var):
        """选择日期"""
        from tkinter import simpledialog
        date_str = simpledialog.askstring("输入日期", "请输入开始日期 (YYYY-MM-DD):", 
                                         initialvalue=date_var.get())
        if date_str:
            try:
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date_var.set(date_str)
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
    
    def choose_folder(self, folder_var):
        """选择文件夹"""
        try:
            initial_dir = folder_var.get() if folder_var.get() else os.path.expanduser("~")
            
            folder = filedialog.askdirectory(
                title="选择保存文件夹",
                initialdir=initial_dir
            )
            
            if folder:
                folder_var.set(folder)
                
        except Exception as e:
            messagebox.showerror("错误", f"选择文件夹时出错: {str(e)}")
    
    def set_default_folder(self, folder_var):
        """设置默认保存文件夹"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        folder_var.set(desktop)
        
    def generate_filename(self, tab, data_type):
        """生成文件名"""
        try:
            date_var = getattr(self, f"{tab}_date_var")
            folder_var = getattr(self, f"{tab}_path_var")
            
            start_date = datetime.datetime.strptime(date_var.get(), '%Y-%m-%d')
            folder = folder_var.get()
            
            if folder:
                # 格式化文件名
                date_str = start_date.strftime('%Y年%m月%d日')
                filename = f"{data_type}_{date_str}开始.xlsx"
                full_path = os.path.join(folder, filename)
                return full_path
            return ""
        except:
            return ""
        
    def update_filename_preview(self, tab, data_type):
        """更新文件名预览"""
        filename = self.generate_filename(tab, data_type)
        filename_var = getattr(self, f"{tab}_filename_var")
        if filename:
            filename_var.set(os.path.basename(filename))
        else:
            filename_var.set("请选择文件夹和日期")
            
    def log_crawler(self, tab, message):
        """添加日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_text = getattr(self, f"{tab}_log_text")
        log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        log_text.see(tk.END)
        self.root.update()
    
    def start_tab2_crawling(self):
        """开始选项卡2的爬取"""
        self.start_crawler(self.tab2, self.river_crawler_2, "河流评测")
    
    def start_tab3_crawling(self):
        """开始选项卡3的爬取"""
        self.start_crawler(self.tab3, self.river_crawler_1, "河流巡护")
    
    def start_crawler(self, tab, crawler, data_type):
        """开始爬取"""
        folder_var = getattr(self, f"{tab}_path_var")
        if not folder_var.get():
            messagebox.showerror("错误", "请选择保存文件夹")
            return
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_var.get()):
            try:
                os.makedirs(folder_var.get())
                self.log_crawler(tab, f"创建文件夹: {folder_var.get()}")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建文件夹: {str(e)}")
                return
        
        date_var = getattr(self, f"{tab}_date_var")
        try:
            start_date = datetime.datetime.strptime(date_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return
        
        # 生成完整文件路径
        filename = self.generate_filename(tab, data_type)
        if not filename:
            messagebox.showerror("错误", "无法生成文件名")
            return
        
        # 禁用开始按钮，启动进度条
        start_button = getattr(self, f"{tab}_start_button")
        progress = getattr(self, f"{tab}_progress")
        
        start_button.config(state='disabled')
        progress.start()
        
        # 在新线程中运行爬虫
        thread = threading.Thread(target=self.run_crawler, args=(tab, crawler, start_date, filename, data_type))
        thread.daemon = True
        thread.start()
    
    def run_crawler(self, tab, crawler, start_date, filename, data_type):
        """运行爬虫"""
        try:
            self.log_crawler(tab, f"开始爬取{data_type}...")
            self.log_crawler(tab, f"开始日期: {start_date.strftime('%Y-%m-%d')}")
            self.log_crawler(tab, f"保存文件: {filename}")
            self.log_crawler(tab, "注意: 已跳过SSL证书验证")
            self.log_crawler(tab, "正在爬取所有分页数据，请耐心等待...")
            
            # 爬取数据
            data = crawler.crawl_all_data(start_date, progress_callback=lambda msg: self.log_crawler(tab, msg))
            
            if not data:
                self.log_crawler(tab, "未获取到符合条件的数据")
                return
            
            self.log_crawler(tab, f"爬取完成，共获取 {len(data)} 条符合条件的数据")
            
            # 处理用户数据
            self.log_crawler(tab, "正在整合用户发帖数据...")
            user_data_list = crawler.process_user_data(data)
            
            # 保存到Excel
            self.log_crawler(tab, "正在保存数据到Excel...")
            success = crawler.save_to_excel(user_data_list, filename)
            
            if success:
                self.log_crawler(tab, f"数据已成功保存到: {filename}")
                
                # 显示统计信息
                self.log_crawler(tab, "=== 统计汇总 ===")
                self.log_crawler(tab, f"总发帖人数: {len(user_data_list)}")
                self.log_crawler(tab, f"总发帖次数: {sum([user['发帖次数'] for user in user_data_list])}")
                
                # 显示发帖最多的前5名
                top_posters = sorted(user_data_list, key=lambda x: x['发帖次数'], reverse=True)[:5]
                self.log_crawler(tab, "发帖最多的前5名:")
                for i, user in enumerate(top_posters, 1):
                    self.log_crawler(tab, f"  {i}. {user['发帖人']}: {user['发帖次数']}次")
                
                self.log_crawler(tab, "数据已按用户整合，包含所有发帖时间和消息内容")
                    
                # 打开文件所在目录
                try:
                    save_dir = os.path.dirname(filename)
                    os.startfile(save_dir)  # Windows
                    self.log_crawler(tab, f"已打开文件所在目录: {save_dir}")
                except:
                    try:
                        import subprocess
                        subprocess.run(['open', save_dir])  # macOS
                    except:
                        try:
                            subprocess.run(['xdg-open', save_dir])  # Linux
                        except:
                            pass
                    
            else:
                self.log_crawler(tab, "保存文件时出错")
                
        except Exception as e:
            self.log_crawler(tab, f"程序运行出错: {str(e)}")
        finally:
            # 恢复界面状态
            self.root.after(0, lambda: self.crawling_finished(tab))
    
    def crawling_finished(self, tab):
        """爬取完成后的清理工作"""
        progress = getattr(self, f"{tab}_progress")
        start_button = getattr(self, f"{tab}_start_button")
        
        progress.stop()
        start_button.config(state='normal')
    
    def generate_charts(self, tab):
        """生成统计图表"""
        data_type = "河流评测数据" if tab == self.tab2 else "河流巡护数据"
        filename = self.generate_filename(tab, data_type)
        if not filename or not os.path.exists(filename):
            messagebox.showerror("错误", "请先完成爬取并保存文件")
            return
        
        try:
            # 读取数据
            df_users = pd.read_excel(filename, sheet_name='用户发帖统计')
            
            # 设置中文字体
            try:
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
            except:
                self.log_crawler(tab, "警告: 中文字体设置失败，图表可能显示乱码")
            
            # 创建图表
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 发帖数前10的用户
            top_users = df_users.head(10)
            ax1.barh(range(len(top_users)), top_users['发帖次数'])
            ax1.set_yticks(range(len(top_users)))
            ax1.set_yticklabels(top_users['发帖人'])
            ax1.set_xlabel('发帖次数')
            ax1.set_title('发帖次数前十的用户')
            ax1.grid(True, alpha=0.3)
            
            # 发帖数分布
            post_counts = df_users['发帖次数']
            ax2.hist(post_counts, bins=20, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('发帖次数')
            ax2.set_ylabel('用户数量')
            ax2.set_title('发帖次数分布')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            self.log_crawler(tab, "图表生成完成")
            
        except Exception as e:
            self.log_crawler(tab, f"生成图表时出错: {str(e)}")
    
    # 选项卡4的方法
    def update_tab4_filename_preview(self, *args):
        """更新选项卡4的文件名预览"""
        try:
            start_date = datetime.datetime.strptime(self.tab4_date_var.get(), '%Y-%m-%d')
            folder = self.tab4_path_var.get()
            
            if folder:
                date_str = start_date.strftime('%Y年%m月%d日')
                filename = f"综合次数统计_{date_str}开始.xlsx"
                full_path = os.path.join(folder, filename)
                self.tab4_filename_var.set(os.path.basename(filename))
            else:
                self.tab4_filename_var.set("请选择文件夹和日期")
        except:
            self.tab4_filename_var.set("请选择文件夹和日期")
    
    def log_tab4(self, message):
        """选项卡4的日志记录"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tab4_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.tab4_log_text.see(tk.END)
        self.root.update()
    
    def start_tab4_analysis(self):
        """开始综合次数统计"""
        if not self.validate_tab4_inputs():
            return
        
        # 禁用开始按钮
        self.tab4_start_button.config(state='disabled')
        self.tab4_progress.start()
        
        # 在新线程中执行分析
        thread = threading.Thread(target=self.run_tab4_analysis)
        thread.daemon = True
        thread.start()
    
    def validate_tab4_inputs(self):
        """验证选项卡4的输入"""
        # 验证日期格式
        try:
            start_date = datetime.datetime.strptime(self.tab4_date_var.get(), "%Y-%m-%d")
            current_date = datetime.datetime.now()
            
            if start_date.date() > current_date.date():
                messagebox.showerror("错误", "开始日期不能晚于今天")
                return False
                
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return False
        
        # 验证保存路径
        if not self.tab4_path_var.get():
            messagebox.showerror("错误", "请选择保存路径")
            return False
        
        if not os.path.exists(self.tab4_path_var.get()):
            try:
                os.makedirs(self.tab4_path_var.get())
            except:
                messagebox.showerror("错误", "保存路径无效或无法创建")
                return False
        
        return True
    
    def run_tab4_analysis(self):
        """运行综合次数统计 - 修复统计逻辑"""
        try:
            start_date_str = self.tab4_date_var.get()
            save_path = self.tab4_path_var.get()
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            
            self.log_tab4("=== 开始执行综合次数统计 ===")
            self.log_tab4(f"统计开始日期: {start_date_str}")
            
            # 初始化统计字典
            user_stats = defaultdict(lambda: {
                '巡护次数': 0,
                '评测次数': 0, 
                '活动次数': 0,
                '总次数': 0
            })
            
            total_users = 0
            
            # 1. 统计河流巡护数据 (useType=1)
            self.log_tab4("正在获取河流巡护数据...")
            patrol_data = self.river_crawler_1.crawl_all_data(
                start_date, 
                progress_callback=lambda msg: self.log_tab4(f"[巡护] {msg}")
            )
            
            if patrol_data:
                patrol_users = self.river_crawler_1.process_user_data(patrol_data)
                for user in patrol_users:
                    username = user['发帖人']
                    user_stats[username]['巡护次数'] = user['发帖次数']
                    user_stats[username]['总次数'] += user['发帖次数']
                self.log_tab4(f"✅ 河流巡护数据统计完成: {len(patrol_users)}人")
                total_users += len(patrol_users)
            else:
                self.log_tab4("❌ 未获取到河流巡护数据")
            
            # 2. 统计河流评测数据 (useType=2)
            self.log_tab4("正在获取河流评测数据...")
            evaluation_data = self.river_crawler_2.crawl_all_data(
                start_date,
                progress_callback=lambda msg: self.log_tab4(f"[评测] {msg}")
            )
            
            if evaluation_data:
                evaluation_users = self.river_crawler_2.process_user_data(evaluation_data)
                for user in evaluation_users:
                    username = user['发帖人']
                    user_stats[username]['评测次数'] = user['发帖次数']
                    user_stats[username]['总次数'] += user['发帖次数']
                self.log_tab4(f"✅ 河流评测数据统计完成: {len(evaluation_users)}人")
                total_users += len(evaluation_users)
            else:
                self.log_tab4("❌ 未获取到河流评测数据")
            
            # 3. 统计活动参与数据
            self.log_tab4("正在获取活动参与数据...")
            # 根据时间差计算page_size
            page_size = self.calculate_page_size(start_date_str)
            activities = self.activity_analyzer.get_limited_activities(page_size=page_size)
            
            if activities:
                filtered_activities = self.activity_analyzer.filter_activities_by_date(activities, start_date_str)
                self.log_tab4(f"找到 {len(filtered_activities)} 个在 {start_date_str} 及以后的活动")
                
                if filtered_activities:
                    # 获取活动详情并统计参与者
                    info_responses = []
                    for i, activity in enumerate(filtered_activities, 1):
                        activity_id = activity.get('id')
                        if activity_id:
                            self.log_tab4(f"[{i}/{len(filtered_activities)}] 获取活动详情...")
                            info_data = self.activity_analyzer.get_activity_detail(activity_id)
                            if info_data:
                                info_responses.append(info_data)
                                self.log_tab4(f"  ✅ 成功获取活动详情")
                            else:
                                self.log_tab4(f"  ❌ 获取活动详情失败")
                            time.sleep(0.3)  # 避免请求过快
                    
                    if info_responses:
                        # 统计活动参与者
                        activity_participants = defaultdict(int)
                        for activity_data in info_responses:
                            if activity_data.get('code') == 200 and 'data' in activity_data:
                                activity_info = activity_data['data']
                                member_info = activity_info.get('activeMemberBoTableDataInfo', {})
                                members = member_info.get('rows', [])
                                for member in members:
                                    nick_name = member.get('nickName', '未知')
                                    activity_participants[nick_name] += 1
                        
                        for user, count in activity_participants.items():
                            user_stats[user]['活动次数'] = count
                            user_stats[user]['总次数'] += count
                        
                        self.log_tab4(f"✅ 活动参与数据统计完成: {len(activity_participants)}人")
                        total_users += len(activity_participants)
                    else:
                        self.log_tab4("❌ 未能获取到活动详情")
                else:
                    self.log_tab4("❌ 筛选后没有符合条件的活动")
            else:
                self.log_tab4("❌ 未获取到活动数据")
            
            # 转换为DataFrame并排序
            stats_list = []
            for user, stats in user_stats.items():
                if stats['总次数'] > 0:  # 只统计有参与记录的用户
                    stats_list.append({
                        '姓名': user,
                        '巡护次数': stats['巡护次数'],
                        '评测次数': stats['评测次数'],
                        '活动次数': stats['活动次数'],
                        '总次数': stats['总次数']
                    })
            
            # 按总次数降序排序
            stats_list.sort(key=lambda x: x['总次数'], reverse=True)
            
            if not stats_list:
                self.log_tab4("❌ 没有获取到任何统计数据")
                self.tab4_analysis_complete(False)
                return
            
            # 生成时间戳和文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = os.path.join(save_path, f"综合次数统计_{start_date_str}_{timestamp}.xlsx")
            
            # 保存到Excel
            df = pd.DataFrame(stats_list)
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='综合次数统计', index=False)
                
                # 添加统计摘要
                summary_data = {
                    '统计项目': ['总人数', '平均总次数', '最多总次数', '最少总次数', 
                              '平均巡护次数', '平均评测次数', '平均活动次数'],
                    '数值': [
                        len(stats_list),
                        round(sum([x['总次数'] for x in stats_list]) / len(stats_list), 2),
                        max([x['总次数'] for x in stats_list]),
                        min([x['总次数'] for x in stats_list]),
                        round(sum([x['巡护次数'] for x in stats_list]) / len(stats_list), 2),
                        round(sum([x['评测次数'] for x in stats_list]) / len(stats_list), 2),
                        round(sum([x['活动次数'] for x in stats_list]) / len(stats_list), 2)
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
            
            self.log_tab4(f"💾 综合次数统计已保存到: {excel_filename}")
            
            # 显示统计结果
            self.log_tab4("\n=== 统计结果 ===")
            self.log_tab4(f"总统计人数: {len(stats_list)}")
            self.log_tab4(f"平均每人总次数: {round(sum([x['总次数'] for x in stats_list]) / len(stats_list), 2)}")
            
            # 显示前10名
            self.log_tab4("\n📊 参与次数前十名:")
            for i, user in enumerate(stats_list[:10], 1):
                self.log_tab4(f"  {i}. {user['姓名']}: {user['总次数']}次 "
                            f"(巡护:{user['巡护次数']} 评测:{user['评测次数']} 活动:{user['活动次数']})")
            
            self.log_tab4(f"\n🎉 综合次数统计完成！")
            self.log_tab4(f"📁 文件已保存到: {save_path}")
            
            self.tab4_analysis_complete(True)
            
        except Exception as e:
            self.log_tab4(f"❌ 执行过程中发生错误: {str(e)}")
            self.tab4_analysis_complete(False)
    
    def tab4_analysis_complete(self, success):
        self.tab4_progress.stop()
        self.tab4_start_button.config(state='normal')
        
        if success:
            messagebox.showinfo("完成", "综合次数统计完成！")
        else:
            messagebox.showerror("错误", "执行过程中出现错误，请查看日志")
    
    def generate_tab4_charts(self):
        """为选项卡4生成统计图表"""
        try:
            start_date_str = self.tab4_date_var.get()
            folder = self.tab4_path_var.get()
            
            if not folder:
                messagebox.showerror("错误", "请先选择保存文件夹")
                return
            
            # 查找最新的统计文件
            pattern = f"综合次数统计_{start_date_str}_*.xlsx"
            files = [f for f in os.listdir(folder) if f.startswith(f"综合次数统计_{start_date_str}_")]
            
            if not files:
                messagebox.showerror("错误", f"在 {folder} 中未找到综合次数统计文件，请先执行统计")
                return
            
            # 使用最新的文件
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(folder, x)))
            file_path = os.path.join(folder, latest_file)
            
            # 读取数据
            df = pd.read_excel(file_path, sheet_name='综合次数统计')
            
            # 设置中文字体
            try:
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
            except:
                self.log_tab4("警告: 中文字体设置失败，图表可能显示乱码")
            
            # 创建图表
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 总次数前10的用户
            top_users = df.head(10)
            ax1.barh(range(len(top_users)), top_users['总次数'])
            ax1.set_yticks(range(len(top_users)))
            ax1.set_yticklabels(top_users['姓名'])
            ax1.set_xlabel('总参与次数')
            ax1.set_title('总参与次数前十名')
            ax1.grid(True, alpha=0.3)
            
            # 各类活动次数分布
            categories = ['巡护次数', '评测次数', '活动次数']
            category_sums = [df['巡护次数'].sum(), df['评测次数'].sum(), df['活动次数'].sum()]
            ax2.pie(category_sums, labels=categories, autopct='%1.1f%%', startangle=90)
            ax2.set_title('各类活动次数分布')
            
            # 总次数分布直方图
            ax3.hist(df['总次数'], bins=20, alpha=0.7, edgecolor='black')
            ax3.set_xlabel('总参与次数')
            ax3.set_ylabel('人数')
            ax3.set_title('总参与次数分布')
            ax3.grid(True, alpha=0.3)
            
            # 各类活动平均次数
            avg_counts = [df['巡护次数'].mean(), df['评测次数'].mean(), df['活动次数'].mean()]
            ax4.bar(categories, avg_counts, alpha=0.7)
            ax4.set_ylabel('平均次数')
            ax4.set_title('各类活动平均参与次数')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            self.log_tab4("图表生成完成")
            
        except Exception as e:
            self.log_tab4(f"生成图表时出错: {str(e)}")

def main():
    root = tk.Tk()
    app = IntegratedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()