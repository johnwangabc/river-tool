import axios from 'axios';
import { storage } from './storage';

const BASE_URL = 'https://xhbr.rwan.org.cn/prod-api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  },
});

// 请求拦截器 - 添加认证令牌
apiClient.interceptors.request.use(
  async (config) => {
    const token = await storage.getAuthToken();
    if (token && config.requireAuth) {
      config.headers.Authorization = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // 服务器响应错误
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // 请求发送但无响应
      console.error('Network Error:', error.message);
    } else {
      // 其他错误
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const api = {
  // 获取活动列表
  async getActivities(pageNum = 1, pageSize = 40) {
    const orgId = await storage.getOrgId();
    const response = await apiClient.get('/portal/ums/active/home/list', {
      params: {
        pageNum,
        pageSize,
        orgId,
      },
    });
    return response.data;
  },

  // 获取活动详情
  async getActivityDetail(activityId) {
    const response = await apiClient.get(`/portal/ums/active/info/${activityId}`, {
      params: {
        pageSize: 10,
        pageNum: 1,
      },
      requireAuth: true,
    });
    return response.data;
  },

  // 获取河流巡护/评测数据
  async getRiverPatrolData(pageNum = 1, pageSize = 10, useType = 2) {
    const orgId = await storage.getOrgId();
    const response = await apiClient.get('/portal/ums/patrol/home/list_new', {
      params: {
        pageNum,
        pageSize,
        useType,
        orgId,
      },
    });
    return response.data;
  },

  // 批量获取所有河流巡护数据
  async getAllRiverPatrolData(startDate, useType = 2, progressCallback) {
    let allData = [];
    let pageNum = 1;
    const pageSize = 10;
    const maxPages = 100;
    let consecutiveEmptyPages = 0;
    const maxConsecutiveEmpty = 3;

    while (pageNum <= maxPages && consecutiveEmptyPages < maxConsecutiveEmpty) {
      try {
        if (progressCallback) {
          progressCallback(`正在获取第 ${pageNum} 页...`);
        }

        const data = await this.getRiverPatrolData(pageNum, pageSize, useType);

        if (data.code === 200 && data.rows && data.rows.length > 0) {
          // 过滤日期
          const filteredRows = data.rows.filter((row) => {
            try {
              const postTime = new Date(row.createTime);
              return postTime >= startDate;
            } catch {
              return false;
            }
          });

          allData = allData.concat(filteredRows);

          if (filteredRows.length === 0) {
            consecutiveEmptyPages++;
          } else {
            consecutiveEmptyPages = 0;
          }

          if (progressCallback) {
            progressCallback(`第 ${pageNum} 页: ${filteredRows.length} 条符合条件`);
          }
        } else {
          consecutiveEmptyPages++;
        }

        pageNum++;

        // 添加延迟避免请求过快
        await new Promise(resolve => setTimeout(resolve, 300));
      } catch (error) {
        console.error(`Error fetching page ${pageNum}:`, error);
        consecutiveEmptyPages++;
      }
    }

    if (progressCallback) {
      progressCallback(`爬取完成，共 ${allData.length} 条数据`);
    }

    return allData;
  },

  // 批量获取活动详情
  async getActivitiesDetails(activityIds, progressCallback) {
    const results = [];

    for (let i = 0; i < activityIds.length; i++) {
      try {
        if (progressCallback) {
          progressCallback(`获取活动详情 ${i + 1}/${activityIds.length}`);
        }

        const detail = await this.getActivityDetail(activityIds[i]);
        if (detail) {
          results.push(detail);
        }

        // 添加延迟避免请求过快
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`Error fetching activity ${activityIds[i]}:`, error);
      }
    }

    return results;
  },
};

export default apiClient;
