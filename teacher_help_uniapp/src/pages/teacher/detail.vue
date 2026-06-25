<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

defineOptions({
  name: 'TeacherDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '老师详情',
  },
})

interface ClassItem {
  id: number
  dateTag: string
  date: string
  title: string
  time: string
  count: string
  countType: 'group' | 'person'
  status?: string
  accent: boolean
}

const teacherId = ref('')
const teacher = ref({
  name: '李明',
  avatarText: '李',
  status: '启用',
  subject: '初中数学',
  level: '高级老师',
  phone: '138 0013 8000',
  monthHours: 48,
})

const tabs = ['课表', '班级', '记录', '资料']
const activeTab = ref('课表')

const upcoming = ref<ClassItem[]>([
  { id: 1, dateTag: '今天', date: '10月24日', title: '初三数学冲刺班 (A班)', time: '14:00 - 15:30', count: '15人', countType: 'group', status: '未开始', accent: true },
  { id: 2, dateTag: '明天', date: '10月25日', title: '初二数学基础班', time: '09:00 - 10:30', count: '22人', countType: 'group', accent: false },
  { id: 3, dateTag: '后天', date: '10月26日', title: '一对一辅导 (张同学)', time: '16:00 - 18:00', count: '1人', countType: 'person', accent: false },
])

const quickActions = computed(() => [
  { key: 'schedule', icon: 'calendar', label: '查看课表' },
  { key: 'call', icon: 'phone', label: '联系老师' },
  { key: 'add', icon: 'plusempty', label: '新增排课' },
  { key: 'edit', icon: 'compose', label: '编辑资料' },
])

function goBack() {
  uni.navigateBack()
}
function onAction(key: string) {
  if (key === 'schedule')
    uni.navigateTo({ url: `/pages/teacher/schedule?id=${teacherId.value}` })
  else if (key === 'call')
    uni.makePhoneCall({ phoneNumber: teacher.value.phone.replace(/\s/g, '') })
  else if (key === 'add')
    uni.navigateTo({ url: '/pages/schedule/create' })
  else if (key === 'edit')
    uni.navigateTo({ url: `/pages/teacher/create?id=${teacherId.value}` })
}

onLoad((query) => {
  teacherId.value = query?.id || ''
})
</script>

<template>
  <view class="td-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        老师详情
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 资料卡 -->
    <view class="profile-card">
      <view class="profile-head">
        <view class="profile-avatar">
          {{ teacher.avatarText }}
        </view>
        <view class="profile-info">
          <view class="profile-name-row">
            <text class="profile-name">
              {{ teacher.name }}
            </text>
            <text class="profile-status">
              {{ teacher.status }}
            </text>
          </view>
          <text class="profile-sub">
            {{ teacher.subject }} · {{ teacher.level }}
          </text>
        </view>
      </view>
      <view class="profile-stats">
        <view class="ps-item">
          <text class="ps-label">
            联系方式
          </text>
          <text class="ps-value">
            {{ teacher.phone }}
          </text>
        </view>
        <view class="ps-item line">
          <text class="ps-label">
            本月课时
          </text>
          <text class="ps-value big">
            {{ teacher.monthHours }} <text class="ps-unit">课时</text>
          </text>
        </view>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-grid">
      <view
        v-for="a in quickActions"
        :key="a.key"
        class="quick-item"
        @click="onAction(a.key)"
      >
        <view class="quick-icon">
          <uni-icons :type="a.icon" size="22" color="#1f7159" />
        </view>
        <text class="quick-label">
          {{ a.label }}
        </text>
      </view>
    </view>

    <!-- 分段 -->
    <view class="seg">
      <view
        v-for="t in tabs"
        :key="t"
        class="seg-item"
        :class="{ on: activeTab === t }"
        @click="activeTab = t"
      >
        {{ t }}
      </view>
    </view>

    <template v-if="activeTab === '课表'">
      <view class="section-head">
        <text class="section-title">
          近期课程
        </text>
        <view class="section-more">
          <text>全部</text>
          <uni-icons type="right" size="14" color="#1f7159" />
        </view>
      </view>

      <view class="class-list">
        <view
          v-for="c in upcoming"
          :key="c.id"
          class="class-card"
        >
          <view class="class-accent" :class="{ on: c.accent }" />
          <view class="class-body">
            <view class="class-top">
              <view class="class-meta">
                <view class="class-tags">
                  <text class="date-tag" :class="{ today: c.dateTag === '今天' }">
                    {{ c.dateTag }}
                  </text>
                  <text class="date-text">
                    {{ c.date }}
                  </text>
                </view>
                <text class="class-title">
                  {{ c.title }}
                </text>
              </view>
              <text v-if="c.status" class="class-status">
                {{ c.status }}
              </text>
            </view>
            <view class="class-info">
              <view class="ci-item">
                <uni-icons type="calendar" size="15" color="#3f4944" />
                <text>{{ c.time }}</text>
              </view>
              <view class="ci-item">
                <uni-icons :type="c.countType === 'person' ? 'person' : 'staff'" size="15" color="#3f4944" />
                <text>{{ c.count }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </template>

    <view v-else class="empty">
      {{ activeTab }}内容待完善
    </view>
  </view>
</template>

<style lang="scss" scoped>
.td-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 60rpx;
  color: #0f1d23;
  background: #f3faff;
}

button::after {
  border: 0;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 102rpx;
  margin: 0 -28rpx;
  padding: 0 20rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.icon-btn {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #005842;
}

/* 资料卡 */
.profile-card {
  margin-top: 22rpx;
  padding: 28rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
}

.profile-head {
  display: flex;
  gap: 24rpx;
  align-items: center;
}

.profile-avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 110rpx;
  height: 110rpx;
  font-size: 44rpx;
  font-weight: 600;
  color: #00513d;
  background: #a4f2d4;
  border: 3rpx solid #a4f2d4;
  border-radius: 50%;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.profile-name-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.profile-name {
  font-size: 38rpx;
  font-weight: 700;
}

.profile-status {
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  color: #227253;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.profile-sub {
  font-size: 25rpx;
  color: #a7cfc2;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  margin-top: 26rpx;
  padding-top: 26rpx;
  border-top: 1rpx solid rgba(164, 242, 212, 0.2);
}

.ps-item {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.ps-item.line {
  padding-left: 28rpx;
  border-left: 1rpx solid rgba(164, 242, 212, 0.2);
}

.ps-label {
  font-size: 22rpx;
  color: #a7cfc2;
  letter-spacing: 1rpx;
}

.ps-value {
  font-size: 30rpx;
  font-weight: 500;
}

.ps-value.big {
  font-size: 38rpx;
  font-weight: 600;
}

.ps-unit {
  font-size: 22rpx;
  font-weight: 400;
  color: #a7cfc2;
}

/* 快捷操作 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-top: 22rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  align-items: center;
  padding: 22rpx 8rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  background: #e1f0f8;
  border-radius: 50%;
}

.quick-label {
  font-size: 22rpx;
  color: #3f4944;
}

/* 分段 */
.seg {
  display: flex;
  gap: 6rpx;
  margin-top: 24rpx;
  padding: 8rpx;
  background: #d6e5ed;
  border-radius: 14rpx;
}

.seg-item {
  flex: 1;
  font-size: 25rpx;
  line-height: 60rpx;
  color: #3f4944;
  text-align: center;
  border-radius: 10rpx;
}

.seg-item.on {
  font-weight: 700;
  color: #0f1d23;
  background: #ffffff;
}

/* 近期课程 */
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 26rpx;
  padding: 0 6rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
}

.section-more {
  display: flex;
  gap: 4rpx;
  align-items: center;
  font-size: 24rpx;
  color: #1f7159;
}

.class-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  margin-top: 18rpx;
}

.class-card {
  position: relative;
  display: flex;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.class-accent {
  width: 8rpx;
  background: #bec9c3;
}

.class-accent.on {
  background: #1f7159;
}

.class-body {
  flex: 1;
  padding: 24rpx;
}

.class-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.class-meta {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.class-tags {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.date-tag {
  padding: 3rpx 14rpx;
  font-size: 22rpx;
  color: #3f4944;
  background: #d6e5ed;
  border-radius: 6rpx;
}

.date-tag.today {
  color: #1f7159;
  background: #e7f6fe;
}

.date-text {
  font-size: 24rpx;
  color: #3f4944;
}

.class-title {
  font-size: 30rpx;
  font-weight: 600;
}

.class-status {
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  color: #227253;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.class-info {
  display: flex;
  gap: 32rpx;
  margin-top: 18rpx;
}

.ci-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.empty {
  margin-top: 60rpx;
  font-size: 26rpx;
  color: #9aa5aa;
  text-align: center;
}
</style>
