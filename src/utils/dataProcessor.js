import { format, parse } from 'date-fns';

export const dataProcessor = {
  // 过滤指定日期及以后的活动
  filterActivitiesByDate(activities, targetDateStr) {
    try {
      const targetDate = parse(targetDateStr, 'yyyy-MM-dd', new Date());

      return activities.filter((activity) => {
        if (!activity.createTime) return false;

        try {
          const activityDate = parse(
            activity.createTime,
            'yyyy-MM-dd HH:mm:ss',
            new Date()
          );
          return activityDate >= targetDate;
        } catch {
          return false;
        }
      }).sort((a, b) => {
        const dateA = new Date(a.createTime);
        const dateB = new Date(b.createTime);
        return dateB - dateA; // 降序排列
      });
    } catch (error) {
      console.error('Error filtering activities:', error);
      return [];
    }
  },

  // 处理河流巡护用户数据
  processRiverPatrolUserData(data) {
    if (!data || data.length === 0) return [];

    const userStats = {};

    data.forEach((item) => {
      const userId = item.userId || item.memberId || '';
      const nickname = item.nickName || '未知用户';
      const mobile = item.mobile || item.memberMobile || '';
      const postTime = item.createTime || '';
      const msg = item.msg || '';
      const riverName = item.riverName || '';

      // 使用userId作为唯一标识，如果没有则用nickname
      const key = userId || nickname;

      if (!userStats[key]) {
        userStats[key] = {
          用户ID: userId,
          发帖人: nickname,
          手机号: mobile,
          发帖次数: 0,
          发帖时间列表: [],
          发帖消息列表: [],
          河流名称列表: [],
        };
      }

      // 更新手机号（如果当前记录有而之前没有）
      if (mobile && !userStats[key].手机号) {
        userStats[key].手机号 = mobile;
      }

      userStats[key].发帖次数 += 1;
      userStats[key].发帖时间列表.push(postTime);
      userStats[key].发帖消息列表.push(msg);
      userStats[key].河流名称列表.push(riverName);
    });

    // 转换为数组并排序
    return Object.values(userStats).sort((a, b) => b.发帖次数 - a.发帖次数);
  },

  // 分析活动参与者
  analyzeParticipants(activitiesData) {
    const participants = {};

    activitiesData.forEach((activityData) => {
      if (activityData.code !== 200 || !activityData.data) return;

      const activityInfo = activityData.data;
      const activityId = activityInfo.id;
      const activityName = activityInfo.actName || '未知活动';
      const startTime = activityInfo.startTime || '未知时间';

      const memberInfo = activityInfo.activeMemberBoTableDataInfo || {};
      const members = memberInfo.rows || [];

      members.forEach((member) => {
        const memberId = member.id;
        const nickName = member.nickName || '未知';
        const mobile = member.mobile || '';

        if (!memberId) return;

        if (!participants[memberId]) {
          participants[memberId] = {
            id: memberId,
            昵称: nickName,
            手机号: mobile,
            参与活动数: 0,
            活动名称列表: [],
            活动详情列表: [],
          };
        }

        participants[memberId].参与活动数 += 1;
        if (!participants[memberId].活动名称列表.includes(activityName)) {
          participants[memberId].活动名称列表.push(activityName);
        }

        participants[memberId].活动详情列表.push({
          活动ID: activityId,
          活动名称: activityName,
          活动时间: startTime,
          报名状态: member.isSignupStatus === 1 ? '已签到' : '未签到',
        });

        // 更新手机号（如果之前为空）
        if (mobile && !participants[memberId].手机号) {
          participants[memberId].手机号 = mobile;
        }
      });
    });

    // 转换为数组并排序
    return Object.values(participants).sort(
      (a, b) => b.参与活动数 - a.参与活动数
    );
  },

  // 提取活动基本信息
  extractActivityBasicInfo(activitiesData) {
    console.log('开始提取活动基本信息, 输入数据长度:', activitiesData.length);

    if (!activitiesData || activitiesData.length === 0) {
      console.log('输入数据为空');
      return [];
    }

    // 打印第一条数据的结构
    console.log('第一条数据结构:', JSON.stringify(activitiesData[0], null, 2));

    const result = activitiesData
      .map((activityData, index) => {
        // 兼容多种数据结构
        let activity = null;

        // 情况1: {code: 200, data: {...}}
        if (activityData.code === 200 && activityData.data) {
          activity = activityData.data;
        }
        // 情况2: {code: "200", data: {...}}
        else if (activityData.code === "200" && activityData.data) {
          activity = activityData.data;
        }
        // 情况3: 直接是活动对象 {id, actName, ...}
        else if (activityData.id || activityData.actName) {
          activity = activityData;
        }
        // 情况4: data字段直接存在
        else if (activityData.data) {
          activity = activityData.data;
        }

        if (!activity) {
          console.log(`第${index}条数据无法解析, 结构:`, activityData);
          return null;
        }

        return {
          活动ID: activity.id,
          活动名称: activity.actName || '未知',
          发起人: activity.memberName || '未知',
          发起人电话: activity.memberMobile || '未提供',
          开始时间: activity.startTime || '未知',
          活动地址: activity.address || '未知',
          活动类型: activity.actType === 2 ? '巡河' : '净滩',
          状态: activity.status,
          最大人数: activity.maxMemberNum || 0,
          实际参与人数: activity.signInMemberNum || 0,
          浏览量: activity.lookNum || 0,
          组织名称: activity.orgName || '未知',
        };
      })
      .filter(item => item !== null);

    console.log('提取结果数量:', result.length);
    if (result.length > 0) {
      console.log('第一条提取结果:', result[0]);
    }

    return result;
  },

  // 计算活动统计数据
  calculateActivityStats(basicInfoList) {
    if (!basicInfoList || basicInfoList.length === 0) {
      return {
        活动总数: 0,
        巡河活动数: 0,
        净滩活动数: 0,
        总参与人数: 0,
        平均参与人数: 0,
      };
    }

    const totalActivities = basicInfoList.length;
    const riverPatrolCount = basicInfoList.filter(
      (a) => a.活动类型 === '巡河'
    ).length;
    const beachCleanCount = basicInfoList.filter(
      (a) => a.活动类型 === '净滩'
    ).length;
    const totalParticipants = basicInfoList.reduce(
      (sum, a) => sum + a.实际参与人数,
      0
    );

    return {
      活动总数: totalActivities,
      巡河活动数: riverPatrolCount,
      净滩活动数: beachCleanCount,
      总参与人数: totalParticipants,
      平均参与人数:
        totalActivities > 0
          ? (totalParticipants / totalActivities).toFixed(2)
          : 0,
    };
  },

  // 综合统计用户参与次数
  calculateComprehensiveStats(patrolData, evaluationData, participantsData) {
    const userStats = {};

    // 处理巡护数据
    if (patrolData && patrolData.length > 0) {
      const patrolUsers = this.processRiverPatrolUserData(patrolData);
      patrolUsers.forEach((user) => {
        const username = user.发帖人;
        if (!userStats[username]) {
          userStats[username] = {
            姓名: username,
            巡护次数: 0,
            评测次数: 0,
            活动次数: 0,
            总次数: 0,
          };
        }
        userStats[username].巡护次数 = user.发帖次数;
        userStats[username].总次数 += user.发帖次数;
      });
    }

    // 处理评测数据
    if (evaluationData && evaluationData.length > 0) {
      const evaluationUsers = this.processRiverPatrolUserData(evaluationData);
      evaluationUsers.forEach((user) => {
        const username = user.发帖人;
        if (!userStats[username]) {
          userStats[username] = {
            姓名: username,
            巡护次数: 0,
            评测次数: 0,
            活动次数: 0,
            总次数: 0,
          };
        }
        userStats[username].评测次数 = user.发帖次数;
        userStats[username].总次数 += user.发帖次数;
      });
    }

    // 处理活动参与数据
    if (participantsData && participantsData.length > 0) {
      participantsData.forEach((participant) => {
        const username = participant.昵称;
        if (!userStats[username]) {
          userStats[username] = {
            姓名: username,
            巡护次数: 0,
            评测次数: 0,
            活动次数: 0,
            总次数: 0,
          };
        }
        userStats[username].活动次数 = participant.参与活动数;
        userStats[username].总次数 += participant.参与活动数;
      });
    }

    // 转换为数组并排序
    return Object.values(userStats)
      .filter((user) => user.总次数 > 0)
      .sort((a, b) => b.总次数 - a.总次数);
  },

  // 计算页面大小（基于日期范围）
  calculatePageSize(targetDateStr) {
    try {
      const targetDate = parse(targetDateStr, 'yyyy-MM-dd', new Date());
      const currentDate = new Date();

      if (targetDate > currentDate) {
        return 40; // 默认值
      }

      const daysDiff =
        Math.floor((currentDate - targetDate) / (1000 * 60 * 60 * 24)) + 1;
      if (daysDiff <= 0) {
        return 40;
      }

      // 每天约6个活动
      const estimatedActivities = daysDiff * 6;
      // 加10作为缓冲，最大不超过200
      return Math.min(estimatedActivities + 10, 200);
    } catch {
      return 40;
    }
  },
};
