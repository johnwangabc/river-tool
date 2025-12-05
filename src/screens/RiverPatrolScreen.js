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
  SegmentedButtons,
} from 'react-native-paper';
import { format } from 'date-fns';
import { api } from '../utils/apiClient';
import { dataProcessor } from '../utils/dataProcessor';
import { excelExporter } from '../utils/excelExporter';
import { DataTable } from '../components/DataTable';

export default function RiverPatrolScreen() {
  const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [useType, setUseType] = useState('2'); // 2=评测, 1=巡护
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [displayData, setDisplayData] = useState(null);
  const [showData, setShowData] = useState(false);

  const handleCrawl = async () => {
    if (!startDate) {
      Alert.alert('错误', '请输入开始日期');
      return;
    }

    setLoading(true);
    setProgress('开始爬取数据...');
    setShowData(false);

    try {
      const startDateObj = new Date(startDate);
      const dataTypeName = useType === '2' ? '河流评测' : '河流巡护';

      setProgress(`正在爬取${dataTypeName}数据...`);

      // 获取所有数据
      const allData = await api.getAllRiverPatrolData(
        startDateObj,
        parseInt(useType),
        (msg) => setProgress(msg)
      );

      if (!allData || allData.length === 0) {
        Alert.alert('提示', '未获取到符合条件的数据');
        setLoading(false);
        return;
      }

      // 打印原始数据样本到控制台
      console.log('\n\n');
      console.log('🔍🔍🔍🔍🔍 巡护数据样本 - 请复制以下内容 🔍🔍🔍🔍🔍');
      console.log('========== 开始 ==========');
      console.log('总数据条数:', allData.length);
      console.log('\n前3条完整数据:');
      allData.slice(0, 3).forEach((item, index) => {
        console.log(`\n--- 第 ${index + 1} 条 ---`);
        console.log(JSON.stringify(item, null, 2));
      });
      console.log('\n========== 结束 ==========');
      console.log('🔍🔍🔍🔍🔍 请复制上面的内容 🔍🔍🔍🔍🔍');
      console.log('\n\n');

      setProgress('正在处理用户数据...');

      // 处理用户数据
      const userData = dataProcessor.processRiverPatrolUserData(allData);

      setDisplayData(userData);
      setShowData(true);
      setProgress('数据加载完成');

      Alert.alert(
        '成功',
        `已获取 ${allData.length} 条数据，${userData.length} 位用户`
      );
    } catch (error) {
      console.error('Error crawling data:', error);
      Alert.alert('错误', '获取数据失败，请检查网络和设置');
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
      const dataTypeName = useType === '2' ? '河流评测数据' : '河流巡护数据';
      setProgress('正在导出Excel...');
      await excelExporter.exportRiverPatrol(displayData, dataTypeName, startDate);
      Alert.alert('成功', 'Excel文件已生成并准备分享');
    } catch (error) {
      console.error('Error exporting:', error);
      Alert.alert('错误', '导出失败');
    }
  };

  const columns = [
    { key: '用户ID', label: 'ID', width: 80 },
    { key: '发帖人', label: '用户名', width: 100 },
    { key: '手机号', label: '手机号', width: 120 },
    { key: '发帖次数', label: '发帖次数', width: 90 },
  ];

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>河流巡护/评测数据</Title>
            <Text style={styles.description}>
              爬取指定日期开始的河流巡护或评测数据
            </Text>

            <Text style={styles.label}>数据类型</Text>
            <SegmentedButtons
              value={useType}
              onValueChange={setUseType}
              buttons={[
                { value: '2', label: '河流评测 (UseType=2)' },
                { value: '1', label: '河流巡护 (UseType=1)' },
              ]}
              style={styles.segmentedButtons}
            />

            <Text style={styles.label}>开始日期</Text>
            <TextInput
              mode="outlined"
              value={startDate}
              onChangeText={setStartDate}
              placeholder="yyyy-MM-dd"
              style={styles.input}
            />

            <Button
              mode="contained"
              onPress={handleCrawl}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              开始爬取
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
                    总人数: {displayData.length}人
                  </Chip>
                  <Chip style={styles.chip}>
                    总发帖: {displayData.reduce((sum, u) => sum + u.发帖次数, 0)}次
                  </Chip>
                  <Chip style={styles.chip}>
                    平均:{' '}
                    {displayData.length > 0
                      ? (
                          displayData.reduce((sum, u) => sum + u.发帖次数, 0) /
                          displayData.length
                        ).toFixed(2)
                      : 0}
                    次/人
                  </Chip>
                  <Chip style={styles.chip}>
                    最多:{' '}
                    {displayData.length > 0
                      ? Math.max(...displayData.map(u => u.发帖次数))
                      : 0}
                    次
                  </Chip>
                  <Chip style={styles.chip}>
                    最少:{' '}
                    {displayData.length > 0
                      ? Math.min(...displayData.map(u => u.发帖次数))
                      : 0}
                    次
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
                data={displayData.slice(0, 50)}
                columns={columns}
                title={`用户发帖统计 (前50名)`}
              />
              {displayData.length > 50 && (
                <Text style={styles.moreDataText}>
                  还有 {displayData.length - 50} 条数据，请导出Excel查看完整数据
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
  segmentedButtons: {
    marginBottom: 16,
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
  moreDataText: {
    marginTop: 12,
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
  },
});
