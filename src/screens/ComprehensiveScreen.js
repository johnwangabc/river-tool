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

export default function ComprehensiveScreen() {
  const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [displayData, setDisplayData] = useState(null);
  const [showData, setShowData] = useState(false);
  const logJson = (label, payload, previewCount = 3) => {
    try {
      const data =
        Array.isArray(payload) && payload.length > previewCount
          ? payload.slice(0, previewCount)
          : payload;
      console.log(`${label}:`, JSON.stringify(data, null, 2));
    } catch {
      console.log(label, payload);
    }
  };

  const handleAnalyze = async () => {
    if (!startDate) {
      Alert.alert('错误', '请输入开始日期');
      return;
    }

    setLoading(true);
    setProgress('开始综合统计...');
    setShowData(false);

    try {
      const startDateObj = new Date(startDate);
      let patrolData = [];
      let evaluationData = [];
      let participantsData = [];

      // 1. 获取河流巡护数据
      setProgress('正在获取河流巡护数据...');
      try {
        patrolData = await api.getAllRiverPatrolData(
          startDateObj,
          1,
          (msg) => setProgress(`[巡护] ${msg}`)
        );
      } catch (error) {
        console.error('Error fetching patrol data:', error);
      }

      // 2. 获取河流评测数据
      setProgress('正在获取河流评测数据...');
      try {
        evaluationData = await api.getAllRiverPatrolData(
          startDateObj,
          2,
          (msg) => setProgress(`[评测] ${msg}`)
        );
      } catch (error) {
        console.error('Error fetching evaluation data:', error);
      }

      // 3. 获取活动参与数据
      setProgress('正在获取活动参与数据...');
      try {
        const pageSize = dataProcessor.calculatePageSize(startDate);
        const activitiesResponse = await api.getActivities(1, pageSize);

        if (activitiesResponse.rows && activitiesResponse.rows.length > 0) {
          const filteredActivities = dataProcessor.filterActivitiesByDate(
            activitiesResponse.rows,
            startDate
          );

          if (filteredActivities.length > 0) {
            const activityIds = filteredActivities.map((a) => a.id);
            const detailsData = await api.getActivitiesDetails(
              activityIds,
              (msg) => setProgress(`[活动] ${msg}`)
            );

            if (detailsData.length > 0) {
              participantsData = dataProcessor.analyzeParticipants(detailsData);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching activity data:', error);
      }

      // 处理综合数据
      setProgress('正在计算综合统计...');
      const comprehensiveStats = dataProcessor.calculateComprehensiveStats(
        patrolData,
        evaluationData,
        participantsData
      );
      logJson('综合统计样本(前3)', comprehensiveStats);
      console.log(
        `巡护:${patrolData.length}条 评测:${evaluationData.length}条 活动参与:${participantsData.length}人 综合结果:${comprehensiveStats ? comprehensiveStats.length : 0}人`
      );

      if (!comprehensiveStats || comprehensiveStats.length === 0) {
        Alert.alert('提示', '未获取到统计数据');
        setLoading(false);
        return;
      }

      setDisplayData(comprehensiveStats);
      setShowData(true);
      setProgress('综合统计完成');

      Alert.alert(
        '成功',
        `综合统计完成\n总人数: ${comprehensiveStats.length}\n` +
          `巡护数据: ${patrolData.length}条\n` +
          `评测数据: ${evaluationData.length}条\n` +
          `活动参与: ${participantsData.length}人`
      );
    } catch (error) {
      console.error('Error in comprehensive analysis:', error);
      Alert.alert('错误', '综合统计失败，请检查网络和设置');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!displayData || displayData.length === 0) {
      Alert.alert('提示', '没有可导出的数据');
      return;
    }

    try {
      logJson('准备导出综合统计(前3)', displayData);
      setProgress('正在导出Excel...');
      await excelExporter.exportComprehensiveStats(displayData, startDate);
      Alert.alert('成功', 'Excel文件已生成并准备分享');
    } catch (error) {
      console.error('Error exporting:', error);
      Alert.alert('错误', '导出失败');
    }
  };

  const columns = [
    { key: '姓名', label: '姓名', width: 100 },
    { key: '巡护次数', label: '巡护', width: 70 },
    { key: '评测次数', label: '评测', width: 70 },
    { key: '活动次数', label: '活动', width: 70 },
    { key: '总次数', label: '总计', width: 70 },
  ];

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>综合次数统计</Title>
            <Text style={styles.description}>
              统计每个人的巡护、评测和活动参与次数
            </Text>

            <Text style={styles.label}>开始日期</Text>
            <TextInput
              mode="outlined"
              value={startDate}
              onChangeText={setStartDate}
              placeholder="yyyy-MM-dd"
              style={styles.input}
            />

            <Text style={styles.hint}>
              将统计该日期及以后的所有数据
            </Text>

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

            {showData && displayData && (
              <View style={styles.statsContainer}>
                <Text style={styles.statsTitle}>统计摘要</Text>
                <View style={styles.chipContainer}>
                  <Chip style={styles.chip}>
                    总人数: {displayData.length}
                  </Chip>
                  <Chip style={styles.chip}>
                    总次数:{' '}
                    {displayData.reduce((sum, u) => sum + u.总次数, 0)}
                  </Chip>
                  <Chip style={styles.chip}>
                    平均:{' '}
                    {displayData.length > 0
                      ? (
                          displayData.reduce((sum, u) => sum + u.总次数, 0) /
                          displayData.length
                        ).toFixed(2)
                      : 0}
                  </Chip>
                </View>
              </View>
            )}
          </Card.Content>
        </Card>

        {showData && displayData && (
          <Card style={styles.card}>
            <Card.Content>
              <DataTable
                data={displayData.slice(0, 20)}
                columns={columns}
                title="综合统计 (前20名)"
              />
              {displayData.length > 20 && (
                <Text style={styles.moreDataText}>
                  还有 {displayData.length - 20} 条数据，请导出Excel查看完整数据
                </Text>
              )}
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
    marginBottom: 4,
  },
  hint: {
    fontSize: 12,
    color: '#666',
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
  moreDataText: {
    marginTop: 12,
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
  },
});
