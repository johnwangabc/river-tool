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
  Chip,
} from 'react-native-paper';
import { storage } from '../utils/storage';

export default function SettingsScreen() {
  const [authToken, setAuthToken] = useState('');
  const [orgId, setOrgId] = useState('843');
  const [loading, setLoading] = useState(false);
  const [tokenVisible, setTokenVisible] = useState(false);

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

  const tokenLength = authToken.trim().length;
  const hasToken = tokenLength > 0;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={[styles.card, styles.heroCard]}>
          <Card.Content>
            <Text style={styles.heroEyebrow}>连接河道数据</Text>
            <Title style={styles.heroTitle}>先配置令牌，再开始统计</Title>
            <Paragraph style={styles.heroSubtitle}>
              令牌与组织 ID 仅保存在本地设备，用于后续的 API 调用。
            </Paragraph>
            <View style={styles.heroChips}>
              <Chip
                icon="shield-check"
                mode="outlined"
                style={styles.heroChip}
                selectedColor="#0c5d35"
              >
                本地安全存储
              </Chip>
              <Chip icon="database" mode="outlined" style={styles.heroChip}>
                影响所有统计
              </Chip>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>API 配置</Title>
            <Paragraph style={styles.description}>
              认证令牌和组织 ID 会用于所有数据请求，请确保与后台环境一致。
            </Paragraph>

            <Divider style={styles.divider} />

            <View style={styles.labelRow}>
              <Text style={styles.label}>认证令牌 (Token) *</Text>
              <Text style={styles.metaText}>
                {hasToken ? `已填长度 ${tokenLength}` : '尚未填写'}
              </Text>
            </View>
            <TextInput
              mode="outlined"
              value={authToken}
              onChangeText={setAuthToken}
              placeholder="Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
              multiline
              numberOfLines={4}
              secureTextEntry={!tokenVisible}
              autoCapitalize="none"
              style={[styles.input, styles.tokenInput]}
              right={
                <TextInput.Icon
                  icon={tokenVisible ? 'eye-off' : 'eye'}
                  onPress={() => setTokenVisible((v) => !v)}
                  forceTextInputFocus={false}
                />
              }
            />

            <Text style={styles.hint}>
              格式: Bearer 后跟完整的JWT令牌
            </Text>

            <View style={styles.labelRow}>
              <Text style={styles.label}>组织ID</Text>
              <Text style={styles.metaText}>默认 843，可按需调整</Text>
            </View>
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
            <View style={styles.tipHeader}>
              <Title>使用说明</Title>
              <Chip mode="outlined" icon="information-outline" compact>
                简短步骤
              </Chip>
            </View>
            <Paragraph style={styles.instructionText}>
              1. 在浏览器/APP 调用接口时，复制 Authorization 请求头的完整值。
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              2. 粘贴到上方令牌输入框，确认以“Bearer ”开头。
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              3. 根据需要调整组织 ID（默认 843），点击保存。
            </Paragraph>
            <Paragraph style={styles.instructionText}>
              4. 若账号或环境切换，先清除设置再重新填写。
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
    backgroundColor: '#f1f3f6',
  },
  scrollContent: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  heroCard: {
    backgroundColor: '#e8f3ff',
    borderWidth: 1,
    borderColor: '#cfe3ff',
  },
  heroEyebrow: {
    color: '#0c5dce',
    fontWeight: 'bold',
    letterSpacing: 1,
    marginBottom: 4,
  },
  heroTitle: {
    fontSize: 22,
    marginBottom: 6,
  },
  heroSubtitle: {
    color: '#335577',
    lineHeight: 20,
  },
  heroChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 12,
  },
  heroChip: {
    borderColor: '#cfe3ff',
    backgroundColor: '#f5f9ff',
    marginRight: 8,
    marginBottom: 8,
  },
  description: {
    marginTop: 8,
    color: '#666',
  },
  divider: {
    marginVertical: 16,
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 12,
    marginBottom: 4,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: 4,
  },
  tokenInput: {
    minHeight: 96,
  },
  hint: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
  },
  metaText: {
    fontSize: 12,
    color: '#466596',
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
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
});
