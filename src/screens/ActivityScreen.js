import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Card,
  Title,
  ProgressBar,
  Chip,
} from 'react-native-paper';
import { format } from 'date-fns';
import { api } from '../utils/apiClient';
import { dataProcessor } from '../utils/dataProcessor';
import { excelExporter } from '../utils/excelExporter';
import { DataTable } from '../components/DataTable';

export default function ActivityScreen() {
  const [targetDate, setTargetDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [displayData, setDisplayData] = useState(null);
  const [showData, setShowData] = useState(false);
  const [stats, setStats] = useState(null);
  const [participantsData, setParticipantsData] = useState(null);

  const handleAnalyze = async () => {
    if (!targetDate) {
      Alert.alert('错误', '请输入目标日期');
      return;
    }

    setLoading(true);
    setProgress('开始获取活动数据...');
    setShowData(false);

    try {
      // 计算页面大小
      const pageSize = dataProcessor.calculatePageSize(targetDate);
      setProgress(`正在获取活动列表 (预计 ${pageSize} 条)...`);

      // 获取活动列表
      const activitiesResponse = await api.getActivities(1, pageSize);

      if (!activitiesResponse.rows || activitiesResponse.rows.length === 0) {
        Alert.alert('提示', '未获取到活动数据');
        setLoading(false);
        return;
      }

      // 过滤活动
      setProgress('正在筛选活动...');
      const filteredActivities = dataProcessor.filterActivitiesByDate(
        activitiesResponse.rows,
        targetDate
      );

      if (filteredActivities.length === 0) {
        Alert.alert('提示', `在 ${targetDate} 及以后没有找到活动`);
        setLoading(false);
        return;
      }

      setProgress(`找到 ${filteredActivities.length} 个活动，正在获取详情...`);

      // 获取活动详情
      const activityIds = filteredActivities.map((a) => a.id);
      const detailsData = await api.getActivitiesDetails(
        activityIds,
        (msg) => setProgress(msg)
      );

      if (detailsData.length === 0) {
        Alert.alert('提示', '未能获取到活动详情');
        setLoading(false);
        return;
      }

      // 分析参与者统计
      setProgress('正在分析参与者数据...');
      const participants = dataProcessor.analyzeParticipants(detailsData);
      const basicInfo = dataProcessor.extractActivityBasicInfo(detailsData);
      const activityStats = dataProcessor.calculateActivityStats(basicInfo);

      console.log('=== 数据处理结果 ===');
      console.log('detailsData长度:', detailsData.length);
      console.log('参与者数量:', participants.length);
      console.log('basicInfo长度:', basicInfo.length);
      console.log('统计数据:', activityStats);

      // 确保先设置数据，再设置显示状态
      setParticipantsData(participants);
      setDisplayData(basicInfo);
      setStats(activityStats);
      setProgress('数据加载完成');

      // 延迟一下再显示，确保状态已更新
      setTimeout(() => {
        setShowData(true);
      }, 100);

      Alert.alert(
        '成功',
        `已获取 ${detailsData.length} 个活动的详细数据\n参与者统计: ${participants.length} 人`
      );
    } catch (error) {
      console.error('Error analyzing activities:', error);
      Alert.alert('错误', '获取数据失败，请检查网络和Token设置');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    console.log('准备导出参与者数据, participantsData:', participantsData);
    console.log('参与者数量:', participantsData ? participantsData.length : 0);

    if (!participantsData || participantsData.length === 0) {
      Alert.alert('提示', '没有可导出的参与者数据');
      return;
    }

    try {
      setProgress('正在导出Excel...');
      await excelExporter.exportParticipants(participantsData, stats, targetDate);
      Alert.alert('成功', 'Excel文件已生成并准备分享');
    } catch (error) {
      console.error('Error exporting:', error);
      Alert.alert('错误', `导出失败: ${error.message}`);
    }
  };

  const columns = [
    { key: '活动ID', label: '活动ID', width: 80 },
    { key: '活动名称', label: '活动名称', width: 150 },
    { key: '发起人', label: '发起人', width: 100 },
    { key: '开始时间', label: '开始时间', width: 150 },
    { key: '活动类型', label: '类型', width: 80 },
    { key: '实际参与人数', label: '参与人数', width: 90 },
    { key: '浏览量', label: '浏览量', width: 80 },
  ];

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>活动数据统计</Title>
            <Text style={styles.description}>
              获取指定日期及以后的活动信息和参与者统计
            </Text>

            <Text style={styles.label}>目标日期</Text>
            <TextInput
              mode="outlined"
              value={targetDate}
              onChangeText={setTargetDate}
              placeholder="yyyy-MM-dd"
              style={styles.input}
            />

            <Button
              mode="contained"
              onPress={handleAnalyze}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              开始统计
            </Button>

            {showData && displayData && (
              <Button
                mode="outlined"
                onPress={handleExport}
                disabled={loading}
                style={styles.exportButton}
              >
                导出Excel
              </Button>
            )}

            {loading && (
              <View style={styles.progressContainer}>
                <ProgressBar indeterminate color="#6200ee" />
                <Text style={styles.progressText}>{progress}</Text>
              </View>
            )}

            {stats && (
              <View style={styles.statsContainer}>
                <Text style={styles.statsTitle}>统计摘要</Text>
                <View style={styles.chipContainer}>
                  <Chip style={styles.chip}>活动总数: {stats.活动总数}</Chip>
                  <Chip style={styles.chip}>巡河: {stats.巡河活动数}</Chip>
                  <Chip style={styles.chip}>净滩: {stats.净滩活动数}</Chip>
                  <Chip style={styles.chip}>总参与: {stats.总参与人数}</Chip>
                  <Chip style={styles.chip}>平均: {stats.平均参与人数}</Chip>
                </View>
              </View>
            )}
          </Card.Content>
        </Card>

        {showData && displayData && (
          <Card style={styles.card}>
            <Card.Content>
              <DataTable
                data={displayData}
                columns={columns}
                title="活动数据"
              />
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  description: {
    marginTop: 8,
    marginBottom: 16,
    color: '#666',
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    paddingVertical: 6,
  },
  exportButton: {
    marginTop: 12,
    paddingVertical: 6,
  },
  progressContainer: {
    marginTop: 16,
  },
  progressText: {
    marginTop: 8,
    fontSize: 12,
    color: '#666',
  },
  statsContainer: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  statsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
});
