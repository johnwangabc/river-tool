import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import XLSX from 'xlsx';
import { format } from 'date-fns';

// 将 Excel 单元格中的复杂类型转为可读字符串，避免出现 [object Object]
const normalizeValue = (value) => {
  if (value === null || value === undefined) return '';
  if (Array.isArray(value)) {
    return value.map((v) => normalizeValue(v)).join('\n');
  }
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }
  return value;
};

const normalizeRows = (rows) =>
  rows.map((row) => {
    const normalized = {};
    Object.keys(row).forEach((key) => {
      normalized[key] = normalizeValue(row[key]);
    });
    return normalized;
  });

export const excelExporter = {
  // 导出活动数据
  async exportActivities(activitiesData, targetDate) {
    try {
      const workbook = XLSX.utils.book_new();

      // 基本信息工作表
      const basicInfoSheet = XLSX.utils.json_to_sheet(normalizeRows(activitiesData));
      XLSX.utils.book_append_sheet(workbook, basicInfoSheet, '活动基本信息');

      // 生成文件
      const fileName = `活动数据_${targetDate}_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
      return await this.saveAndShare(workbook, fileName);
    } catch (error) {
      console.error('Error exporting activities:', error);
      throw error;
    }
  },

  // 导出参与者统计
  async exportParticipants(participantsData, activitiesStats, targetDate) {
    try {
      const workbook = XLSX.utils.book_new();

      // 参与者统计工作表
      const participantsForExport = participantsData.map((p) => ({
        参与者ID: p.id,
        昵称: p.昵称,
        手机号: p.手机号 || '未提供',
        参与活动数: p.参与活动数,
        活动名称: p.活动名称列表.join('、'),
      }));

      const participantsSheet = XLSX.utils.json_to_sheet(participantsForExport);
      XLSX.utils.book_append_sheet(workbook, participantsSheet, '参与者统计');

      // 活动详情工作表
      const detailData = [];
      participantsData.forEach((p) => {
        p.活动详情列表.forEach((activity) => {
          detailData.push({
            参与者ID: p.id,
            昵称: p.昵称,
            手机号: p.手机号 || '未提供',
            活动ID: activity.活动ID,
            活动名称: activity.活动名称,
            活动时间: activity.活动时间,
            报名状态: activity.报名状态,
          });
        });
      });

      const detailSheet = XLSX.utils.json_to_sheet(detailData);
      XLSX.utils.book_append_sheet(workbook, detailSheet, '活动详情');

      // 统计摘要
      if (activitiesStats) {
        const statsSheet = XLSX.utils.json_to_sheet([activitiesStats]);
        XLSX.utils.book_append_sheet(workbook, statsSheet, '活动统计');
      }

      // 生成文件
      const fileName = `参与者统计_${targetDate}_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
      return await this.saveAndShare(workbook, fileName);
    } catch (error) {
      console.error('Error exporting participants:', error);
      throw error;
    }
  },

  // 导出河流巡护/评测数据
  async exportRiverPatrol(userData, dataType, startDate) {
    try {
      const workbook = XLSX.utils.book_new();

      // 用户发帖统计工作表 - 添加更多列
      const userStatsForExport = userData.map((u, index) => ({
        序号: index + 1,
        用户ID: u.用户ID || '',
        用户名: u.发帖人,
        手机号: u.手机号 || '未提供',
        发帖次数: u.发帖次数,
        所有发帖时间: u.发帖时间列表.join('\n'),
        所有发帖消息: u.发帖消息列表.join('\n'),
        所有河流名称: u.河流名称列表.join('\n'),
      }));

      const userStatsSheet = XLSX.utils.json_to_sheet(normalizeRows(userStatsForExport));
      XLSX.utils.book_append_sheet(workbook, userStatsSheet, '用户发帖统计');

      // 数据概览工作表
      const totalPosts = userData.reduce((sum, u) => sum + u.发帖次数, 0);
      const avgPosts = userData.length > 0 ? (totalPosts / userData.length).toFixed(2) : 0;
      const maxPosts = userData.length > 0 ? Math.max(...userData.map(u => u.发帖次数)) : 0;
      const minPosts = userData.length > 0 ? Math.min(...userData.map(u => u.发帖次数)) : 0;

      const overview = [{
        总发帖人数: userData.length,
        总发帖次数: totalPosts,
        平均发帖次数: avgPosts,
        最多发帖数: maxPosts,
        最少发帖数: minPosts,
        数据生成时间: format(new Date(), 'yyyy-MM-dd HH:mm:ss'),
      }];

      const overviewSheet = XLSX.utils.json_to_sheet(normalizeRows(overview));
      XLSX.utils.book_append_sheet(workbook, overviewSheet, '数据概览');

      // 生成文件
      const fileName = `${dataType}_${startDate}_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
      return await this.saveAndShare(workbook, fileName);
    } catch (error) {
      console.error('Error exporting river patrol data:', error);
      throw error;
    }
  },

  // 导出综合统计
  async exportComprehensiveStats(statsData, startDate) {
    try {
      const workbook = XLSX.utils.book_new();

      // 综合次数统计工作表
      const statsSheet = XLSX.utils.json_to_sheet(normalizeRows(statsData));
      XLSX.utils.book_append_sheet(workbook, statsSheet, '综合次数统计');

      // 统计摘要
      const totalUsers = statsData.length;
      const totalPatrol = statsData.reduce((sum, u) => sum + (u.巡护次数 || 0), 0);
      const totalEvaluation = statsData.reduce((sum, u) => sum + (u.评测次数 || 0), 0);
      const totalActivity = statsData.reduce((sum, u) => sum + (u.活动次数 || 0), 0);
      const totalOverall = statsData.reduce((sum, u) => sum + (u.总次数 || 0), 0);

      const avgTotal = totalUsers > 0 ? (totalOverall / totalUsers).toFixed(2) : 0;
      const avgPatrol = totalUsers > 0 ? (totalPatrol / totalUsers).toFixed(2) : 0;
      const avgEvaluation = totalUsers > 0 ? (totalEvaluation / totalUsers).toFixed(2) : 0;
      const avgActivity = totalUsers > 0 ? (totalActivity / totalUsers).toFixed(2) : 0;

      const summary = [{
        总人数: totalUsers,
        总巡护次数: totalPatrol,
        总评测次数: totalEvaluation,
        总活动次数: totalActivity,
        总计次数: totalOverall,
        平均总次数: avgTotal,
        平均巡护次数: avgPatrol,
        平均评测次数: avgEvaluation,
        平均活动次数: avgActivity,
        最多总次数: totalUsers > 0 ? Math.max(...statsData.map(u => u.总次数)) : 0,
        最少总次数: totalUsers > 0 ? Math.min(...statsData.map(u => u.总次数)) : 0,
      }];

      const summarySheet = XLSX.utils.json_to_sheet(normalizeRows(summary));
      XLSX.utils.book_append_sheet(workbook, summarySheet, '统计摘要');

      // 生成文件
      const fileName = `综合次数统计_${startDate}_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
      return await this.saveAndShare(workbook, fileName);
    } catch (error) {
      console.error('Error exporting comprehensive stats:', error);
      throw error;
    }
  },

  // 保存并分享文件
  async saveAndShare(workbook, fileName) {
    try {
      // 生成Excel文件（二进制字符串）
      const wbout = XLSX.write(workbook, {
        type: 'base64',
        bookType: 'xlsx',
      });

      // 保存到文件系统
      const fileUri = FileSystem.documentDirectory + fileName;
      await FileSystem.writeAsStringAsync(fileUri, wbout, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // 检查是否支持分享
      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          dialogTitle: '保存Excel文件',
          UTI: 'com.microsoft.excel.xlsx',
        });
      }

      return { success: true, fileUri };
    } catch (error) {
      console.error('Error saving and sharing file:', error);
      throw error;
    }
  },
};
