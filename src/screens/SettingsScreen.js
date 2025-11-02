import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Card,
  Title,
  Paragraph,
  Divider,
} from 'react-native-paper';
import { storage } from '../utils/storage';

export default function SettingsScreen() {
  const [authToken, setAuthToken] = useState('');
  const [orgId, setOrgId] = useState('843');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const token = await storage.getAuthToken();
      const org = await storage.getOrgId();

      if (token) setAuthToken(token);
      if (org) setOrgId(org);
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async () => {
    if (!authToken.trim()) {
      Alert.alert('错误', '请输入认证令牌');
      return;
    }

    setLoading(true);
    try {
      await storage.saveAuthToken(authToken.trim());
      await storage.saveOrgId(orgId.trim() || '843');

      Alert.alert('成功', '设置已保存');
    } catch (error) {
      Alert.alert('错误', '保存设置失败');
      console.error('Error saving settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    Alert.alert(
      '确认',
      '确定要清除所有设置吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          style: 'destructive',
          onPress: async () => {
            await storage.clearAll();
            setAuthToken('');
            setOrgId('843');
            Alert.alert('成功', '设置已清除');
          },
        },
      ]
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>API 配置</Title>
            <Paragraph style={styles.description}>
              配置您的认证令牌以访问河流巡检API
            </Paragraph>

            <Divider style={styles.divider} />

            <Text style={styles.label}>认证令牌 (Token) *</Text>
            <TextInput
              mode="outlined"
              value={authToken}
              onChangeText={setAuthToken}
              placeholder="Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
              multiline
              numberOfLines={4}
              style={styles.input}
            />

            <Text style={styles.hint}>
              格式: Bearer 后跟完整的JWT令牌
            </Text>

            <Text style={styles.label}>组织ID</Text>
            <TextInput
              mode="outlined"
              value={orgId}
              onChangeText={setOrgId}
              placeholder="843"
              keyboardType="numeric"
              style={styles.input}
            />

            <Text style={styles.hint}>
              默认值: 843
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>使用说明</Title>
            <Paragraph style={styles.instructionText}>
              1. 从浏览器开发者工具中获取认证令牌
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              2. 完整复制 Authorization 请求头的值
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              3. 粘贴到上方的认证令牌输入框
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              4. 点击保存设置
            </Paragraph>
          </Card.Content>
        </Card>

        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={handleSave}
            loading={loading}
            disabled={loading}
            style={styles.saveButton}
          >
            保存设置
          </Button>

          <Button
            mode="outlined"
            onPress={handleClear}
            disabled={loading}
            style={styles.clearButton}
          >
            清除设置
          </Button>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
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
    color: '#666',
  },
  divider: {
    marginVertical: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 12,
    marginBottom: 8,
  },
  input: {
    marginBottom: 4,
  },
  hint: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
  },
  instructionText: {
    marginVertical: 4,
    lineHeight: 20,
  },
  buttonContainer: {
    marginTop: 8,
    marginBottom: 32,
  },
  saveButton: {
    marginBottom: 12,
    paddingVertical: 6,
  },
  clearButton: {
    paddingVertical: 6,
  },
});
