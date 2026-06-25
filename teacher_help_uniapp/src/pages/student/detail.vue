<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'StudentDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '学员详情',
  },
})

const activeTab = ref('courses')
const showContactSheet = ref(false)

const tabs = [
  { key: 'courses', label: '课程' },
  { key: 'records', label: '上课记录' },
  { key: 'leave', label: '请假' },
  { key: 'wrong', label: '错题' },
  { key: 'follow', label: '跟进' },
]

const courses = [
  { name: '小学六年级奥数秋季冲刺班', type: '正价课', className: '秋季周末A班（周六 09:00-11:00）', teacher: '李明老师', progress: 8, total: 15, done: false },
  { name: '新概念英语第二册强化辅导', type: '正价课', className: '周三晚班（周三 18:30-20:30）', teacher: '王丽老师', progress: 3, total: 20, done: false },
  { name: '暑期语文阅读理解特训营', type: '已结课', className: '暑假第一期', teacher: '赵老师', progress: 20, total: 20, done: true },
]

const records = [
  { date: '10-27', course: '小学六年级奥数秋季冲刺班', status: '到课', cls: 'success' },
  { date: '10-25', course: '新概念英语第二册强化辅导', status: '请假', cls: 'warn' },
  { date: '10-22', course: '小学六年级奥数秋季冲刺班', status: '迟到', cls: 'warn' },
]

const wrongList = [
  { point: '一元二次方程根的判别式', subject: '数学', status: '未掌握' },
  { point: '阅读理解主旨判断', subject: '语文', status: '复习中' },
]

function goBack() {
  uni.navigateBack()
}

function goLeave() {
  uni.navigateTo({ url: '/pages/student/leave?name=张子涵' })
}

function goEnroll() {
  uni.navigateTo({ url: '/pages/student/enroll?name=张子涵' })
}

function addFollow() {
  uni.showToast({ title: '添加跟进记录', icon: 'none' })
}
</script>

<template>
  <view class="detail-page">
    <view class="hero">
      <view class="nav-bar">
        <button class="nav-btn" @click="goBack">
          <uni-icons type="left" size="24" color="#ffffff" />
        </button>
        <text class="nav-title">
          学员详情
        </text>
        <view class="nav-placeholder" />
      </view>

      <view class="student-head">
        <image src="/static/images/avatar.jpg" mode="aspectFill" class="student-avatar" />
        <view class="student-info">
          <view class="name-row">
            <text class="name">
              张子涵
            </text>
            <text class="status">
              在读学员
            </text>
          </view>
          <view class="phone-chip">
            <uni-icons type="phone" size="15" color="#d9fff0" />
            <text>138****8888（张爸爸）</text>
          </view>
        </view>
      </view>

      <view class="metrics-card">
        <view class="metric">
          <text class="metric-label">
            剩余课时
          </text>
          <view class="metric-value">
            24 <text>节</text>
          </view>
        </view>
        <view class="metric-line" />
        <view class="metric">
          <text class="metric-label">
            可用积分
          </text>
          <view class="metric-value white">
            1,250 <text>分</text>
          </view>
        </view>
      </view>
    </view>

    <view class="quick-row">
      <button class="quick-item" @click="showContactSheet = true">
        <view class="quick-icon">
          <uni-icons type="phone" size="24" color="#00684f" />
        </view>
        <text>联系家长</text>
      </button>
      <button class="quick-item" @click="goLeave">
        <view class="quick-icon">
          <uni-icons type="calendar" size="24" color="#00684f" />
        </view>
        <text>学员请假</text>
      </button>
      <button class="quick-item" @click="goEnroll">
        <view class="quick-icon">
          <uni-icons type="wallet" size="24" color="#00684f" />
        </view>
        <text>报名/续费</text>
      </button>
      <button class="quick-item" @click="addFollow">
        <view class="quick-icon">
          <uni-icons type="personadd" size="24" color="#00684f" />
        </view>
        <text>添加跟进</text>
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
          <view v-if="tab.key === 'courses'" class="tab-dot" />
        </button>
      </view>
    </scroll-view>

    <view v-if="activeTab === 'courses'" class="content-list">
      <view v-for="item in courses" :key="item.name" class="course-card" :class="{ done: item.done }">
        <view class="accent" />
        <view class="course-head">
          <text class="course-name">
            {{ item.name }}
          </text>
          <text class="course-type" :class="{ done: item.done }">
            {{ item.type }}
          </text>
        </view>
        <view class="course-line">
          <uni-icons type="home" size="16" color="#6f7974" />
          <text>{{ item.className }}</text>
        </view>
        <view class="course-line">
          <uni-icons type="person" size="16" color="#6f7974" />
          <text>{{ item.teacher }}</text>
        </view>
        <view class="course-bottom">
          <view v-if="!item.done" class="progress-row">
            <text>进度:</text>
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: `${(item.progress / item.total) * 100}%` }" />
            </view>
            <text><text class="green">{{ item.progress }}</text> / {{ item.total }}讲</text>
          </view>
          <text v-else class="done-text">
            完成于 2023-08-25
          </text>
          <button class="detail-btn">
            {{ item.done ? '回顾课程' : '课程详情' }}
          </button>
        </view>
      </view>
    </view>

    <view v-else-if="activeTab === 'records'" class="content-list">
      <view class="list-card">
        <view v-for="item in records" :key="item.date" class="record-row">
          <text class="record-date">
            {{ item.date }}
          </text>
          <text class="record-course">
            {{ item.course }}
          </text>
          <text class="state-tag" :class="item.cls">
            {{ item.status }}
          </text>
        </view>
      </view>
    </view>

    <view v-else-if="activeTab === 'leave'" class="content-list">
      <view class="list-card">
        <view class="empty-tip">
          近 30 天暂无新的请假记录
        </view>
      </view>
    </view>

    <view v-else-if="activeTab === 'wrong'" class="content-list">
      <view v-for="item in wrongList" :key="item.point" class="wrong-card">
        <view class="wrong-thumb">
          <uni-icons type="image" size="24" color="#6f7974" />
        </view>
        <view class="wrong-main">
          <view class="wrong-title">
            {{ item.point }}
          </view>
          <view class="wrong-sub">
            {{ item.subject }} · 最近更新
          </view>
        </view>
        <text class="state-tag warn">
          {{ item.status }}
        </text>
      </view>
    </view>

    <view v-else class="content-list">
      <view class="list-card">
        <view class="record-row">
          <text class="record-date">
            10-21
          </text>
          <text class="record-course">
            已电话沟通，家长确认下周续费
          </text>
        </view>
      </view>
    </view>

    <view v-if="showContactSheet" class="sheet-mask" @click="showContactSheet = false">
      <view class="contact-sheet" @click.stop>
        <view class="sheet-title">
          联系家长 - 张子涵
        </view>
        <view class="sheet-row">
          <uni-icons type="phone" size="20" color="#00684f" />
          <text>打电话 138 0013 8000</text>
          <uni-icons type="right" size="16" color="#87928d" />
        </view>
        <view class="sheet-row">
          <uni-icons type="paperclip" size="20" color="#00684f" />
          <text>复制手机号</text>
          <uni-icons type="right" size="16" color="#87928d" />
        </view>
        <view class="sheet-row">
          <uni-icons type="chat" size="20" color="#00684f" />
          <text>发消息</text>
          <uni-icons type="right" size="16" color="#87928d" />
        </view>
        <view class="sheet-row">
          <uni-icons type="compose" size="20" color="#00684f" />
          <text>添加跟进记录</text>
          <uni-icons type="right" size="16" color="#87928d" />
        </view>
        <button class="sheet-cancel" @click="showContactSheet = false">
          取消
        </button>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  color: #101f26;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.hero {
  padding-bottom: 34rpx;
  overflow: hidden;
  color: #ffffff;
  background: #1f7159;
  border-radius: 0 0 28rpx 28rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 90rpx;
  padding: 0 28rpx;
}

.nav-btn,
.nav-placeholder {
  width: 56rpx;
  height: 56rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 800;
}

.student-head {
  display: flex;
  gap: 26rpx;
  align-items: center;
  padding: 24rpx 28rpx 0;
}

.student-avatar {
  width: 108rpx;
  height: 108rpx;
  border: 4rpx solid #d9fff0;
  border-radius: 50%;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.name {
  font-size: 40rpx;
  font-weight: 800;
}

.status {
  padding: 8rpx 18rpx;
  font-size: 22rpx;
  color: #d9fff0;
  background: rgba(16, 31, 38, 0.22);
  border-radius: 999rpx;
}

.phone-chip {
  display: inline-flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 16rpx;
  padding: 8rpx 16rpx;
  font-size: 26rpx;
  color: #d9fff0;
  background: rgba(255, 255, 255, 0.14);
  border-radius: 12rpx;
}

.metrics-card {
  display: flex;
  align-items: center;
  margin: 44rpx 28rpx 0;
  padding: 30rpx 0;
  background: rgba(255, 255, 255, 0.12);
  border: 1rpx solid rgba(255, 255, 255, 0.18);
  border-radius: 20rpx;
}

.metric {
  flex: 1;
  text-align: center;
}

.metric-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.78);
}

.metric-value {
  margin-top: 14rpx;
  font-size: 50rpx;
  font-weight: 800;
  color: #a4f2d4;
}

.metric-value.white {
  color: #ffffff;
}

.metric-value text {
  font-size: 24rpx;
  font-weight: 500;
}

.metric-line {
  width: 1rpx;
  height: 70rpx;
  background: rgba(255, 255, 255, 0.22);
}

.quick-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8rpx;
  padding: 32rpx 28rpx;
  background: #f4f6f5;
}

.quick-item {
  padding: 0;
  margin: 0;
  background: transparent;
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 86rpx;
  height: 86rpx;
  margin: 0 auto 12rpx;
  background: #e1f0f8;
  border: 1rpx solid #d6e5ed;
  border-radius: 22rpx;
}

.quick-item text {
  font-size: 23rpx;
  color: #34433d;
}

.tab-scroll {
  background: #ffffff;
  border-bottom: 1rpx solid #d6e5ed;
  white-space: nowrap;
}

.tab-row {
  display: flex;
  gap: 40rpx;
  padding: 0 28rpx;
}

.tab-item {
  position: relative;
  padding: 26rpx 0 20rpx;
  margin: 0;
  font-size: 28rpx;
  line-height: 1;
  color: #34433d;
  background: transparent;
}

.tab-item.active {
  font-weight: 800;
  color: #00684f;
}

.tab-item.active::after {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 58rpx;
  height: 4rpx;
  content: '';
  background: #00684f;
}

.tab-dot {
  position: absolute;
  top: 18rpx;
  right: -12rpx;
  width: 10rpx;
  height: 10rpx;
  background: #ba1a1a;
  border-radius: 50%;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  padding: 28rpx;
}

.course-card,
.wrong-card,
.list-card {
  position: relative;
  padding: 28rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #d6e5ed;
  border-radius: 18rpx;
}

.course-card.done {
  opacity: 0.68;
}

.accent {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 6rpx;
  background: #1f7159;
}

.course-card.done .accent {
  background: #6f7974;
}

.course-head {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  justify-content: space-between;
}

.course-name {
  flex: 1;
  font-size: 30rpx;
  font-weight: 800;
  line-height: 42rpx;
}

.course-type {
  flex-shrink: 0;
  padding: 8rpx 18rpx;
  font-size: 22rpx;
  color: #1f7159;
  background: #e9f6ef;
  border: 1rpx solid #b8dccc;
  border-radius: 8rpx;
}

.course-type.done {
  color: #5d6a70;
  background: #eef2f0;
  border-color: #d6e5ed;
}

.course-line {
  display: flex;
  gap: 12rpx;
  align-items: center;
  margin-top: 18rpx;
  font-size: 25rpx;
  color: #5d6a70;
}

.course-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #edf1ef;
}

.progress-row {
  display: flex;
  gap: 12rpx;
  align-items: center;
  font-size: 24rpx;
}

.progress-bar {
  width: 90rpx;
  height: 10rpx;
  overflow: hidden;
  background: #d6e5ed;
  border-radius: 999rpx;
}

.progress-fill {
  height: 100%;
  background: #1f7159;
}

.green {
  font-weight: 800;
  color: #1f7159;
}

.detail-btn {
  padding: 0 26rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 58rpx;
  color: #00684f;
  background: #eef2f0;
  border-radius: 999rpx;
}

.done-text {
  font-size: 24rpx;
  color: #718088;
}

.record-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.record-row:last-child {
  border-bottom: 0;
}

.record-date {
  width: 76rpx;
  font-size: 26rpx;
  font-weight: 800;
  color: #1f7159;
}

.record-course {
  flex: 1;
  font-size: 25rpx;
  color: #34433d;
}

.state-tag {
  padding: 6rpx 14rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.state-tag.success {
  color: #227253;
  background: #e9f6ef;
}

.state-tag.warn {
  color: #8a671b;
  background: #fff5d8;
}

.empty-tip {
  padding: 50rpx 0;
  font-size: 26rpx;
  color: #718088;
  text-align: center;
}

.wrong-card {
  display: flex;
  gap: 20rpx;
  align-items: center;
}

.wrong-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 82rpx;
  height: 82rpx;
  background: #e7f6fe;
  border-radius: 14rpx;
}

.wrong-main {
  flex: 1;
}

.wrong-title {
  font-size: 27rpx;
  font-weight: 700;
}

.wrong-sub {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #718088;
}

.sheet-mask {
  position: fixed;
  inset: 0;
  z-index: 99;
  display: flex;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.35);
}

.contact-sheet {
  width: 100%;
  padding: 28rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-radius: 24rpx 24rpx 0 0;
}

.sheet-title {
  margin-bottom: 14rpx;
  font-size: 30rpx;
  font-weight: 800;
}

.sheet-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  min-height: 88rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.sheet-row text {
  flex: 1;
  font-size: 27rpx;
}

.sheet-cancel {
  width: 100%;
  padding: 0;
  margin: 24rpx 0 0;
  font-size: 28rpx;
  line-height: 82rpx;
  color: #5d6a70;
  background: #eef2f0;
  border-radius: 14rpx;
}
</style>
