import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  AUTH_TOKEN: '@river_patrol_auth_token',
  ORG_ID: '@river_patrol_org_id',
};

export const storage = {
  // 保存认证令牌
  async saveAuthToken(token) {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
      return true;
    } catch (error) {
      console.error('Error saving auth token:', error);
      return false;
    }
  },

  // 获取认证令牌
  async getAuthToken() {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      return token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  },

  // 保存组织ID
  async saveOrgId(orgId) {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.ORG_ID, orgId);
      return true;
    } catch (error) {
      console.error('Error saving org ID:', error);
      return false;
    }
  },

  // 获取组织ID
  async getOrgId() {
    try {
      const orgId = await AsyncStorage.getItem(STORAGE_KEYS.ORG_ID);
      return orgId || '843'; // 默认值
    } catch (error) {
      console.error('Error getting org ID:', error);
      return '843';
    }
  },

  // 清除所有数据
  async clearAll() {
    try {
      await AsyncStorage.multiRemove([
        STORAGE_KEYS.AUTH_TOKEN,
        STORAGE_KEYS.ORG_ID,
      ]);
      return true;
    } catch (error) {
      console.error('Error clearing storage:', error);
      return false;
    }
  },
};
