# 巡河宝统计工具 (移动端)

这是一个基于 React Native + Expo 开发的河流巡检数据统计移动应用，从原Python桌面工具移植而来。

## 功能特性

### 1. 活动数据统计
- 获取指定日期及以后的活动信息
- 统计参与者数据
- 导出活动基本信息和参与者统计Excel
- 支持表格形式展示数据

### 2. 河流巡护/评测数据
- 爬取河流巡护数据 (useType=1)
- 爬取河流评测数据 (useType=2)
- 统计用户发帖次数和详情
- 导出用户发帖统计Excel

### 3. 综合次数统计
- 综合统计每个人的巡护次数
- 综合统计每个人的评测次数
- 综合统计每个人的活动参与次数
- 按总次数排序展示
- 导出综合统计Excel

### 4. 配置管理
- 用户可自定义设置认证Token
- 支持修改组织ID
- 配置持久化存储

### 5. 数据展示
- 支持在应用内以表格形式展示数据
- 支持导出Excel文件并分享
- 实时显示数据处理进度

## 技术栈

- **框架**: React Native + Expo
- **导航**: React Navigation
- **UI库**: React Native Paper
- **数据存储**: AsyncStorage
- **网络请求**: Axios
- **Excel导出**: SheetJS (xlsx)
- **日期处理**: date-fns

## 项目结构

```
river-patrol-stats/
├── App.js                          # 应用主入口
├── app.json                        # Expo配置
├── eas.json                        # EAS Build配置
├── package.json                    # 依赖配置
├── src/
│   ├── components/
│   │   └── DataTable.js           # 表格展示组件
│   ├── screens/
│   │   ├── SettingsScreen.js      # 设置页面
│   │   ├── ActivityScreen.js      # 活动统计页面
│   │   ├── RiverPatrolScreen.js   # 河流巡护/评测页面
│   │   └── ComprehensiveScreen.js # 综合统计页面
│   └── utils/
│       ├── storage.js             # 本地存储管理
│       ├── apiClient.js           # API客户端
│       ├── dataProcessor.js       # 数据处理工具
│       └── excelExporter.js       # Excel导出工具
└── README.md                       # 本文件
```

## 安装步骤

### 1. 环境要求

- Node.js 16+
- npm 或 yarn
- Expo CLI (`npm install -g expo-cli`)
- EAS CLI (`npm install -g eas-cli`)

### 2. 安装依赖

```bash
cd new
npm install
```

### 3. 本地运行

```bash
# 启动开发服务器
npm start

# 或直接运行在特定平台
npm run android  # Android
npm run ios      # iOS (需要macOS)
npm run web      # Web浏览器
```

扫描二维码在 Expo Go 应用中打开项目。

## Expo云打包

### 1. 配置Expo账号

首先登录Expo账号：

```bash
eas login
```

### 2. 配置项目

在 `app.json` 中更新项目配置：

```json
{
  "expo": {
    "extra": {
      "eas": {
        "projectId": "your-project-id-here"
      }
    }
  }
}
```

获取项目ID：

```bash
eas project:init
```

### 3. 构建应用

#### Android APK (推荐用于测试)

```bash
eas build --platform android --profile preview
```

#### Android AAB (用于Google Play上架)

```bash
eas build --platform android --profile production
```

#### iOS (需要Apple开发者账号)

```bash
eas build --platform ios --profile production
```

### 4. 下载和安装

构建完成后，可以：
- 通过EAS提供的链接下载APK
- 扫描二维码直接下载
- 在Expo网站查看所有构建历史

## 使用指南

### 1. 首次使用

1. 打开应用，进入"设置"页面
2. 输入认证Token (Bearer + JWT令牌)
3. 可选：修改组织ID (默认843)
4. 点击"保存设置"

### 2. 获取认证Token

1. 在浏览器中登录 xhbr.rwan.org.cn
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签
4. 执行任何需要认证的操作
5. 在请求头中找到 `Authorization` 字段
6. 复制完整的值 (格式: `Bearer eyJ0eXA...`)

### 3. 活动数据统计

1. 进入"活动统计"页面
2. 输入目标日期 (格式: yyyy-MM-dd)
3. 点击"开始统计"
4. 等待数据加载完成
5. 查看表格数据或点击"导出Excel"

### 4. 河流巡护/评测

1. 进入"巡护评测"页面
2. 选择数据类型 (巡护或评测)
3. 输入开始日期
4. 点击"开始爬取"
5. 查看结果或导出Excel

### 5. 综合统计

1. 进入"综合统计"页面
2. 输入开始日期
3. 点击"开始统计"
4. 等待所有数据源加载完成 (可能需要较长时间)
5. 查看综合统计结果

## API端点

应用使用以下API端点：

- **活动列表**: `GET /portal/ums/active/home/list`
- **活动详情**: `GET /portal/ums/active/info/{id}`
- **河流巡护**: `GET /portal/ums/patrol/home/list_new`

所有请求发送到: `https://xhbr.rwan.org.cn/prod-api`

## 数据导出

### Excel文件格式

导出的Excel文件包含多个工作表：

**活动数据导出**:
- 活动基本信息
- 活动统计

**参与者统计导出**:
- 参与者统计
- 活动详情
- 活动统计

**河流巡护导出**:
- 用户发帖统计
- 数据概览

**综合统计导出**:
- 综合次数统计
- 统计摘要

### 文件分享

导出后，应用会自动弹出系统分享对话框，可以：
- 保存到本地文件
- 通过微信/QQ等应用分享
- 发送邮件
- 上传到云盘

## 注意事项

1. **Token过期**: 认证Token会过期，如果遇到401错误，请重新获取Token
2. **网络连接**: 需要稳定的网络连接，建议使用WiFi
3. **数据量大**: 综合统计功能会请求大量数据，请耐心等待
4. **存储权限**: Android设备需要授予存储权限以保存Excel文件

## 故障排除

### Token认证失败

- 检查Token格式是否正确 (必须以"Bearer "开头)
- 重新登录浏览器获取新Token
- 确认复制了完整的Token字符串

### 无法导出Excel

- 检查设备存储权限
- 确保有足够的存储空间
- 尝试重启应用

### 数据加载失败

- 检查网络连接
- 验证日期格式 (必须是 yyyy-MM-dd)
- 查看进度提示了解具体错误

## 开发相关

### 添加新功能

所有业务逻辑都在 `src/utils/` 目录中模块化，方便扩展：

- `apiClient.js`: 添加新的API接口
- `dataProcessor.js`: 添加新的数据处理逻辑
- `excelExporter.js`: 自定义Excel导出格式

### 修改UI

使用 React Native Paper 组件库，参考：
https://callstack.github.io/react-native-paper/

## 版本历史

- **v1.0.0** - 初始版本
  - 活动数据统计
  - 河流巡护/评测数据
  - 综合次数统计
  - Token配置管理
  - Excel导出功能
  - 表格数据展示

## 许可证

本项目仅供内部使用。

## 支持

如有问题或建议，请联系开发团队。
