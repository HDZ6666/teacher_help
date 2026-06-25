<script lang="ts" setup>
defineOptions({
  name: 'CourseDetail',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '课程详情',
  },
})

const stats = [
  { label: '应到', value: 15, cls: 'primary' },
  { label: '已到', value: 12, cls: 'success' },
  { label: '请假', value: 2, cls: 'secondary' },
  { label: '缺勤', value: 1, cls: 'error' },
]

const students = [
  { name: '张三', status: '已到', cls: 'present' },
  { name: '李四', status: '已到', cls: 'present' },
  { name: '王五', status: '请假', cls: 'leave' },
]

function goBack() {
  uni.navigateBack()
}

function moreAction() {
  uni.showToast({ title: '更多操作', icon: 'none' })
}

function startCheckin() {
  uni.navigateTo({ url: '/pages/schedule/detail?id=1' })
}

function reschedule() {
  uni.navigateTo({ url: '/pages/schedule/reschedule?id=1' })
}

function cancelCourse() {
  uni.showModal({
    title: '取消课次',
    content: '确认取消本节课次？',
    confirmText: '取消课次',
    confirmColor: '#ba1a1a',
  })
}

function copyCourse() {
  uni.showToast({ title: '复制排课', icon: 'none' })
}
</script>

<template>
  <view class="course-page">
    <view class="topbar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="28" color="#1f7159" />
      </button>
      <view class="page-title">
        课程详情
      </view>
      <button class="nav-btn right" @click="moreAction">
        <uni-icons type="more-filled" size="30" color="#3f4944" />
      </button>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="course-hero">
        <view class="hero-glow" />
        <view class="hero-content">
          <view class="hero-head">
            <view class="course-title">
              少儿数学提高班
            </view>
            <view class="status-pill">
              进行中
            </view>
          </view>

          <view class="meta-grid">
            <view class="meta-item">
              <uni-icons type="calendar" size="18" color="#ffffff" />
              <text>6月23日 14:00-15:30</text>
            </view>
            <view class="meta-item">
              <uni-icons type="staff" size="18" color="#ffffff" />
              <text>精英A班</text>
            </view>
            <view class="meta-item">
              <uni-icons type="person" size="18" color="#ffffff" />
              <text>王老师</text>
            </view>
            <view class="meta-item">
              <uni-icons type="home" size="18" color="#ffffff" />
              <text>A区201</text>
            </view>
          </view>
        </view>
      </view>

      <view class="stat-grid">
        <view
          v-for="item in stats"
          :key="item.label"
          class="stat-card"
        >
          <view class="stat-label">
            {{ item.label }}
          </view>
          <view class="stat-value" :class="item.cls">
            {{ item.value }}
          </view>
        </view>
      </view>

      <view class="quick-actions">
        <button class="checkin-btn" @click="startCheckin">
          <uni-icons type="checkbox-filled" size="24" color="#ffffff" />
          <text>去点名</text>
        </button>
        <view class="sub-actions">
          <button class="sub-btn green" @click="reschedule">
            <uni-icons type="loop" size="20" color="#1f7159" />
            <text>调课</text>
          </button>
          <button class="sub-btn" @click="cancelCourse">
            <uni-icons type="closeempty" size="20" color="#3f4944" />
            <text>取消课次</text>
          </button>
          <button class="sub-btn" @click="copyCourse">
            <uni-icons type="paperclip" size="20" color="#3f4944" />
            <text>复制排课</text>
          </button>
        </view>
      </view>

      <view class="student-card">
        <view class="student-head">
          <view class="student-title">
            学员名单
          </view>
          <button class="view-all">
            查看全部
            <uni-icons type="right" size="18" color="#1f7159" />
          </button>
        </view>
        <view class="student-list">
          <view
            v-for="item in students"
            :key="item.name"
            class="student-row"
          >
            <view class="student-main">
              <view class="avatar">
                {{ item.name.slice(0, 1) }}
              </view>
              <text>{{ item.name }}</text>
            </view>
            <view class="student-status" :class="item.cls">
              {{ item.status }}
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.course-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f4f6f5;
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

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 80rpx;
  height: 80rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-btn.right {
  justify-content: flex-end;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1f7159;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 28rpx 28rpx 170rpx;
}

.course-hero {
  position: relative;
  padding: 32rpx;
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
  background: rgba(0, 88, 66, 0.5);
  border-radius: 50%;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-head {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
  justify-content: space-between;
}

.course-title {
  flex: 1;
  font-size: 40rpx;
  font-weight: 800;
  line-height: 1.32;
}

.status-pill {
  flex-shrink: 0;
  padding: 8rpx 18rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #1f7159;
  background: #ffffff;
  border-radius: 999rpx;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx 24rpx;
  margin-top: 28rpx;
}

.meta-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  min-width: 0;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.meta-item text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24rpx;
  margin-top: 28rpx;
}

.stat-card {
  padding: 24rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.stat-label {
  margin-bottom: 8rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.stat-value {
  font-size: 34rpx;
  font-weight: 800;
}

.stat-value.primary {
  color: #1f7159;
}

.stat-value.success {
  color: #007351;
}

.stat-value.secondary {
  color: #40655b;
}

.stat-value.error {
  color: #ba1a1a;
}

.quick-actions {
  margin-top: 28rpx;
}

.checkin-btn {
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 700;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.sub-actions {
  display: flex;
  gap: 18rpx;
  margin-top: 18rpx;
}

.sub-btn {
  display: flex;
  flex: 1;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.sub-btn.green {
  color: #1f7159;
  border-color: #1f7159;
}

.student-card {
  margin-top: 28rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.student-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.student-title {
  font-size: 34rpx;
  font-weight: 700;
}

.view-all {
  display: flex;
  align-items: center;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  color: #1f7159;
  background: transparent;
}

.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 28rpx;
  border-bottom: 1rpx solid #bec9c3;
}

.student-row:last-child {
  border-bottom: 0;
}

.student-main {
  display: flex;
  gap: 18rpx;
  align-items: center;
  font-size: 28rpx;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #00201a;
  background: #c2ebde;
  border-radius: 50%;
}

.student-status {
  padding: 6rpx 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  border-radius: 999rpx;
}

.student-status.present {
  color: #007351;
  background: rgba(0, 115, 81, 0.08);
}

.student-status.leave {
  color: #40655b;
  background: rgba(194, 235, 222, 0.35);
}

.nav-btn::after,
.checkin-btn::after,
.sub-btn::after,
.view-all::after {
  border: 0;
}
</style>
