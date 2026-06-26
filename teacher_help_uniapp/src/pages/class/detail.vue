<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ClassDetail',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '班级详情',
  },
})

const activeTab = ref('students')

const tabs = [
  { key: 'students', label: '学员' },
  { key: 'schedule', label: '课表' },
  { key: 'checkin', label: '点名' },
  { key: 'leave', label: '请假' },
  { key: 'settings', label: '设置' },
]

const students = [
  { name: '张伟', lessons: 12, status: '全勤', rate: '100%', danger: false },
  { name: '王芳', lessons: 8, status: '缺勤 1', rate: '92%', danger: false },
  { name: '李娜', lessons: 2, status: '全勤', rate: '100%', danger: true },
]

const schedules = [
  { date: '周二', time: '18:30-20:00', room: '302 阶梯教室' },
  { date: '周六', time: '09:00-10:30', room: '302 阶梯教室' },
]

function goBack() {
  uni.navigateBack()
}

function openMore() {
  uni.showActionSheet({
    itemList: ['编辑班级', '升班/结业', '复制班级', '停用班级'],
  })
}

function addStudent() {
  uni.navigateTo({ url: '/pages/student/add' })
}

function createSchedule() {
  uni.navigateTo({ url: '/pages/schedule/create' })
}

function checkin() {
  uni.navigateTo({ url: '/pages/schedule/detail' })
}

function leave() {
  uni.navigateTo({ url: '/pages/student/leave' })
}
</script>

<template>
  <view class="detail-page">
    <view class="topbar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#1f7159" />
      </button>
      <text class="page-title">
        班级详情
      </text>
      <button class="nav-btn" @click="openMore">
        <uni-icons type="more-filled" size="24" color="#64737b" />
      </button>
    </view>

    <view class="class-card">
      <view class="card-head">
        <view>
          <text class="class-name">
            初二英语培优班(秋季)
          </text>
          <text class="type-pill">
            常规班
          </text>
        </view>
        <text class="state-pill">
          进行中
        </text>
      </view>

      <view class="info-grid">
        <view class="info-block">
          <text class="label">课程</text>
          <text class="value">初中英语强化课程</text>
        </view>
        <view class="info-block">
          <text class="label">人数/容量</text>
          <text class="value"><text class="green">24</text> / 30</text>
        </view>
        <view class="info-block">
          <text class="label">主教</text>
          <text class="value">李晓明</text>
        </view>
        <view class="info-block">
          <text class="label">教室</text>
          <text class="value">302 阶梯教室</text>
        </view>
      </view>
    </view>

    <view class="quick-grid">
      <button class="quick-item" @click="addStudent">
        <view class="quick-icon">
          <uni-icons type="personadd" size="22" color="#1f7159" />
        </view>
        <text>添加学员</text>
      </button>
      <button class="quick-item" @click="createSchedule">
        <view class="quick-icon">
          <uni-icons type="calendar" size="22" color="#1f7159" />
        </view>
        <text>新增排课</text>
      </button>
      <button class="quick-item" @click="checkin">
        <view class="quick-icon">
          <uni-icons type="checkbox-filled" size="22" color="#1f7159" />
        </view>
        <text>去点名</text>
      </button>
      <button class="quick-item" @click="leave">
        <view class="quick-icon">
          <uni-icons type="calendar" size="22" color="#1f7159" />
        </view>
        <text>班级请假</text>
      </button>
    </view>

    <scroll-view class="tab-scroll" scroll-x>
      <view class="tab-row">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </view>
    </scroll-view>

    <view v-if="activeTab === 'students'" class="content-list">
      <view class="list-head">
        <text>共 24 名学员</text>
        <button>筛选</button>
      </view>
      <view v-for="item in students" :key="item.name" class="student-card">
        <view class="avatar" :class="{ danger: item.danger }">
          {{ item.name.slice(0, 1) }}
        </view>
        <view class="student-main">
          <text class="student-name">
            {{ item.name }}
          </text>
          <text class="student-sub" :class="{ danger: item.danger }">
            剩余：{{ item.lessons }} 课时
          </text>
        </view>
        <view class="student-right">
          <text class="tag" :class="{ neutral: item.status.includes('缺勤') }">
            {{ item.status }}
          </text>
          <text class="rate">
            出勤率 {{ item.rate }}
          </text>
        </view>
      </view>
      <button class="more-btn">
        加载更多学员...
      </button>
    </view>

    <view v-else-if="activeTab === 'schedule'" class="content-list">
      <view v-for="item in schedules" :key="item.date" class="schedule-card">
        <view>
          <text class="schedule-day">
            {{ item.date }}
          </text>
          <text class="schedule-time">
            {{ item.time }}
          </text>
        </view>
        <text class="schedule-room">
          {{ item.room }}
        </text>
      </view>
    </view>

    <view v-else class="content-list">
      <view class="empty-card">
        {{ tabs.find(item => item.key === activeTab)?.label }} 内容已按静态原型预留
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 70rpx;
  color: #0f1d23;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  margin: 0 -28rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #e1e8e4;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.page-title {
  font-size: 38rpx;
  font-weight: 800;
}

.class-card,
.student-card,
.schedule-card,
.empty-card {
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
  box-shadow: 0 6rpx 18rpx rgba(15, 29, 35, 0.04);
}

.class-card {
  padding: 28rpx;
  margin-top: 26rpx;
}

.card-head {
  display: flex;
  justify-content: space-between;
}

.class-name {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
}

.type-pill,
.state-pill {
  display: inline-flex;
  margin-top: 12rpx;
  font-size: 22rpx;
  font-weight: 600;
  border-radius: 999rpx;
}

.type-pill {
  padding: 8rpx 14rpx;
  color: #5d6a70;
  background: #eef2f0;
}

.state-pill {
  align-self: flex-start;
  padding: 8rpx 18rpx;
  color: #1f7159;
  background: #e6f4ee;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 26rpx;
  margin-top: 28rpx;
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.label {
  font-size: 22rpx;
  color: #74828a;
}

.value {
  font-size: 27rpx;
  color: #0f1d23;
}

.green {
  font-weight: 800;
  color: #1f7159;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14rpx;
  margin-top: 22rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 156rpx;
  padding: 16rpx 6rpx;
  margin: 0;
  font-size: 21rpx;
  font-weight: 600;
  color: #0f1d23;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  margin-bottom: 12rpx;
  background: #e6f4ee;
  border-radius: 50%;
}

.tab-scroll {
  margin: 30rpx -28rpx 0;
  white-space: nowrap;
}

.tab-row {
  display: inline-flex;
  padding: 0 28rpx;
  border-bottom: 1rpx solid #dfe7e3;
}

.tab-item {
  position: relative;
  height: 76rpx;
  padding: 0 28rpx;
  margin: 0;
  font-size: 29rpx;
  font-weight: 700;
  color: #64737b;
  background: transparent;
}

.tab-item.active {
  color: #1f7159;
}

.tab-item.active::after {
  position: absolute;
  right: 22rpx;
  bottom: 0;
  left: 22rpx;
  height: 4rpx;
  content: '';
  background: #1f7159;
  border-radius: 999rpx;
}

.content-list {
  margin-top: 24rpx;
}

.list-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #74828a;
}

.list-head button {
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  color: #1f7159;
  background: transparent;
}

.student-card {
  display: flex;
  align-items: center;
  padding: 20rpx;
  margin-bottom: 18rpx;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88rpx;
  height: 88rpx;
  margin-right: 18rpx;
  font-size: 32rpx;
  font-weight: 800;
  color: #ffffff;
  background: #1f7159;
  border-radius: 50%;
}

.avatar.danger {
  background: #a4423a;
}

.student-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.student-name {
  font-size: 29rpx;
  font-weight: 700;
}

.student-sub,
.rate {
  font-size: 23rpx;
  color: #74828a;
}

.student-sub.danger {
  color: #a4423a;
}

.student-right {
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  gap: 8rpx;
}

.tag {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  color: #227253;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.tag.neutral {
  color: #5d6a70;
  background: #eef2f0;
}

.more-btn {
  width: 100%;
  height: 72rpx;
  padding: 0;
  margin: 8rpx 0 0;
  font-size: 24rpx;
  color: #74828a;
  background: transparent;
}

.schedule-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  margin-bottom: 18rpx;
}

.schedule-day {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
}

.schedule-time,
.schedule-room {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #64737b;
}

.empty-card {
  padding: 40rpx 28rpx;
  font-size: 26rpx;
  color: #74828a;
  text-align: center;
}
</style>
