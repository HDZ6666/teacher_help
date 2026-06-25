<script lang="ts" setup>
import { safeAreaInsets } from '@/utils/systemInfo'

defineOptions({
  name: 'Home',
})

definePage({
  type: 'home',
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '老师帮',
    enablePullDownRefresh: false,
  },
})

const stats = [
  { label: '今日课程', value: '8', unit: '节', tone: 'white' },
  { label: '待点名', value: '3', unit: '节', tone: 'error' },
  { label: '已完成', value: '5', unit: '', tone: 'white' },
  { label: '待处理错题', value: '12', unit: '', tone: 'mint' },
]

const quickActions = [
  { label: '快速排课', icon: 'flash-filled', url: '/pages/schedule/create' },
  { label: '快速点名', icon: 'checkbox-filled', url: '/pages/schedule/detail' },
  { label: '拍错题', icon: 'camera-filled', url: '/pages/wrong-question/upload' },
  { label: '新增学员', icon: 'personadd-filled', url: '/pages/student/add' },
]

const courses = [
  {
    title: '少儿数学提高班',
    status: '待点名',
    statusClass: 'pending',
    time: '14:00 - 15:30',
    room: 'A区 201教室',
    teacher: '王老师 / 15人',
    done: false,
  },
  {
    title: '少儿英语启蒙班',
    status: '已完成',
    statusClass: 'done',
    time: '09:00 - 10:30',
    room: 'B区 105教室',
    teacher: '李老师 / 12人',
    done: true,
  },
]

const todos = [
  { label: '请假待确认 (2)', icon: 'calendar', tone: 'secondary' },
  { label: '排课冲突 (1)', icon: 'info', tone: 'error' },
]

function switchCampus() {
  uni.showToast({ title: '切换校区', icon: 'none' })
}

function openAction(url: string) {
  uni.navigateTo({ url })
}

function openCheckin() {
  uni.navigateTo({ url: '/pages/schedule/detail' })
}
</script>

<template>
  <view class="home-page" :style="{ paddingTop: `${safeAreaInsets?.top || 0}px` }">
    <view class="topbar">
      <view class="avatar">
        <image src="/static/images/default-avatar.png" mode="aspectFill" />
      </view>
      <view class="brand-title">
        老师帮
      </view>
      <button class="campus-btn" @click="switchCampus">
        切换校区
      </button>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="page-title">
        <view class="title-main">
          今日
        </view>
        <view class="date-row">
          <uni-icons type="calendar" size="18" color="#3f4944" />
          <text>6月23日 周二</text>
        </view>
      </view>

      <view class="hero-card">
        <view class="hero-glow" />
        <view class="stats-grid">
          <view
            v-for="item in stats"
            :key="item.label"
            class="stat-item"
          >
            <view class="stat-label">
              {{ item.label }}
            </view>
            <view class="stat-value" :class="item.tone">
              {{ item.value }}<text v-if="item.unit">{{ item.unit }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="quick-grid">
        <button
          v-for="item in quickActions"
          :key="item.label"
          class="quick-btn"
          @click="openAction(item.url)"
        >
          <view class="quick-icon">
            <uni-icons :type="item.icon" size="28" color="#1f7159" />
          </view>
          <text>{{ item.label }}</text>
        </button>
      </view>

      <view class="section">
        <view class="section-title">
          今日课程
        </view>
        <view
          v-for="item in courses"
          :key="item.title"
          class="course-card"
          :class="{ done: item.done }"
        >
          <view class="course-head">
            <view class="course-title" :class="{ done: item.done }">
              {{ item.title }}
            </view>
            <view class="status-pill" :class="item.statusClass">
              <uni-icons
                :type="item.done ? 'checkbox-filled' : 'info-filled'"
                size="14"
                :color="item.done ? '#3f4944' : '#93000a'"
              />
              <text>{{ item.status }}</text>
            </view>
          </view>

          <view class="course-meta">
            <view class="meta-item">
              <uni-icons type="calendar" size="18" color="#3f4944" />
              <text>{{ item.time }}</text>
            </view>
            <view class="meta-item">
              <uni-icons type="location" size="18" color="#3f4944" />
              <text>{{ item.room }}</text>
            </view>
            <view class="meta-item wide">
              <uni-icons type="staff" size="18" color="#3f4944" />
              <text>{{ item.teacher }}</text>
            </view>
          </view>

          <view v-if="!item.done" class="course-actions">
            <button class="checkin-btn" @click="openCheckin">
              去点名
            </button>
          </view>
        </view>
      </view>

      <view class="section todo-section">
        <view class="section-title">
          待办事项
        </view>
        <view
          v-for="item in todos"
          :key="item.label"
          class="todo-row"
          :class="item.tone"
        >
          <view class="todo-main">
            <view class="todo-icon">
              <uni-icons :type="item.icon" size="22" :color="item.tone === 'error' ? '#93000a' : '#466c61'" />
            </view>
            <text>{{ item.label }}</text>
          </view>
          <uni-icons type="right" size="18" color="#6f7974" />
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f3faff;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.avatar {
  width: 64rpx;
  height: 64rpx;
  overflow: hidden;
  background: #d6e5ed;
  border: 1rpx solid #bec9c3;
  border-radius: 50%;
}

.avatar image {
  width: 100%;
  height: 100%;
}

.brand-title {
  position: absolute;
  left: 50%;
  font-size: 34rpx;
  font-weight: 800;
  color: #1f7159;
  transform: translateX(-50%);
}

.campus-btn {
  padding: 10rpx 14rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 1.2;
  color: #1f7159;
  background: transparent;
  border-radius: 8rpx;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 32rpx 28rpx 170rpx;
}

.page-title {
  margin-bottom: 48rpx;
}

.title-main {
  font-size: 48rpx;
  font-weight: 800;
  line-height: 1.2;
}

.date-row {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.hero-card {
  position: relative;
  padding: 40rpx;
  overflow: hidden;
  color: #ffffff;
  background: #1f7159;
  border-radius: 24rpx;
  box-shadow: 0 6rpx 16rpx rgba(31, 113, 89, 0.12);
}

.hero-glow {
  position: absolute;
  top: -80rpx;
  right: -80rpx;
  width: 260rpx;
  height: 260rpx;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}

.stats-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  row-gap: 48rpx;
  column-gap: 32rpx;
}

.stat-label {
  margin-bottom: 8rpx;
  font-size: 22rpx;
  color: rgba(164, 242, 212, 0.9);
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #ffffff;
}

.stat-value text {
  margin-left: 6rpx;
  font-size: 24rpx;
  font-weight: 400;
  opacity: 0.72;
}

.stat-value.error {
  color: #ffdad6;
}

.stat-value.mint {
  color: #c2ebde;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-top: 40rpx;
}

.quick-btn {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  align-items: center;
  padding: 0;
  margin: 0;
  font-size: 22rpx;
  font-weight: 600;
  line-height: 1.25;
  color: #0f1d23;
  background: transparent;
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  background: #e7f6fe;
  border-radius: 50%;
}

.section {
  margin-top: 48rpx;
}

.section-title {
  margin-bottom: 20rpx;
  font-size: 34rpx;
  font-weight: 700;
}

.course-card {
  padding: 28rpx;
  margin-bottom: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 10rpx rgba(15, 29, 35, 0.04);
}

.course-card.done {
  opacity: 0.8;
}

.course-head {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
  justify-content: space-between;
}

.course-title {
  flex: 1;
  font-size: 34rpx;
  font-weight: 700;
}

.course-title.done {
  color: #3f4944;
  text-decoration: line-through;
  text-decoration-color: #bec9c3;
}

.status-pill {
  display: flex;
  flex-shrink: 0;
  gap: 6rpx;
  align-items: center;
  padding: 8rpx 16rpx;
  font-size: 22rpx;
  font-weight: 600;
  border-radius: 999rpx;
}

.status-pill.pending {
  color: #93000a;
  background: #ffdad6;
}

.status-pill.done {
  color: #3f4944;
  background: #d6e5ed;
}

.course-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  padding-top: 24rpx;
  margin-top: 24rpx;
  border-top: 1rpx solid #d6e5ed;
}

.meta-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  min-width: 0;
  font-size: 26rpx;
  color: #3f4944;
}

.meta-item.wide {
  grid-column: span 2;
}

.meta-item text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24rpx;
}

.checkin-btn {
  width: 176rpx;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 26rpx;
  font-weight: 700;
  line-height: 88rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.todo-section {
  margin-top: 40rpx;
}

.todo-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: #e7f6fe;
  border-left: 8rpx solid #40655b;
  border-radius: 16rpx;
}

.todo-row.error {
  border-left-color: #ba1a1a;
}

.todo-main {
  display: flex;
  gap: 18rpx;
  align-items: center;
  font-size: 26rpx;
}

.todo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  background: #c2ebde;
  border-radius: 50%;
}

.todo-row.error .todo-icon {
  background: #ffdad6;
}

.campus-btn::after,
.quick-btn::after,
.checkin-btn::after {
  border: 0;
}
</style>
