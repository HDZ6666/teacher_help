<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ScheduleCheckin',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '点名',
  },
})

type StudentStatus = 'present' | 'pending' | 'late' | 'leave' | 'absent'

interface StudentItem {
  id: number
  name: string
  remaining: number
  status: StudentStatus
  avatarType: 'image' | 'initial'
  initial?: string
}

const students = ref<StudentItem[]>([
  { id: 1, name: '张子涵', remaining: 24, status: 'present', avatarType: 'image' },
  { id: 2, name: '李雨桐', remaining: 18, status: 'pending', avatarType: 'image' },
  { id: 3, name: '王浩然', remaining: 32, status: 'late', avatarType: 'initial', initial: '王' },
])

const statusActions: Array<{ label: string, value: StudentStatus }> = [
  { label: '到', value: 'present' },
  { label: '迟', value: 'late' },
  { label: '假', value: 'leave' },
  { label: '缺', value: 'absent' },
]

const stats = computed(() => {
  const present = students.value.filter(item => item.status === 'present').length
  const late = students.value.filter(item => item.status === 'late').length
  const leave = students.value.filter(item => item.status === 'leave').length
  const absent = students.value.filter(item => item.status === 'absent').length
  return {
    planned: 15,
    present: 12 + Math.max(0, present - 1),
    late: Math.max(1, late),
    leave,
    absent: Math.max(1, absent),
  }
})

function statusText(status: StudentStatus) {
  const map: Record<StudentStatus, string> = {
    present: '已到',
    pending: '',
    late: '迟到',
    leave: '请假',
    absent: '缺勤',
  }
  return map[status]
}

function setStatus(student: StudentItem, status: StudentStatus) {
  student.status = status
}

function markAllPresent() {
  students.value.forEach((item) => {
    item.status = 'present'
  })
  uni.showToast({ title: '已一键全到', icon: 'none' })
}

function markPendingAbsent() {
  students.value.forEach((item) => {
    if (item.status === 'pending')
      item.status = 'absent'
  })
  uni.showToast({ title: '未到已设缺勤', icon: 'none' })
}

function importLeave() {
  uni.showToast({ title: '请假记录已同步', icon: 'none' })
}

function resetCheckin() {
  students.value = [
    { id: 1, name: '张子涵', remaining: 24, status: 'present', avatarType: 'image' },
    { id: 2, name: '李雨桐', remaining: 18, status: 'pending', avatarType: 'image' },
    { id: 3, name: '王浩然', remaining: 32, status: 'late', avatarType: 'initial', initial: '王' },
  ]
}

function finishCheckin() {
  uni.navigateTo({ url: '/pages/schedule/exception-confirm?id=1' })
}

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="checkin-page">
    <view class="top-bar">
      <button class="nav-icon" @click="goBack">
        <uni-icons type="left" size="24" color="#34433d" />
      </button>
      <view class="brand">
        老师帮
      </view>
      <button class="campus-btn">
        切换校区
      </button>
    </view>

    <view class="content">
      <view class="course-card">
        <view class="course-head">
          <view class="course-title">
            少儿数学提高班
          </view>
          <view class="class-pill">
            精英A班
          </view>
        </view>
        <view class="course-grid">
          <view class="course-meta">
            <uni-icons type="calendar" size="16" color="#43514d" />
            <text>14:00 - 15:30</text>
          </view>
          <view class="course-meta">
            <uni-icons type="person" size="16" color="#43514d" />
            <text>王老师</text>
          </view>
          <view class="course-meta full">
            <uni-icons type="location" size="16" color="#43514d" />
            <text>A区201</text>
          </view>
        </view>
      </view>

      <view class="stats-card">
        <view class="stat first">
          <text class="stat-label">应到</text>
          <text class="stat-value dark">{{ stats.planned }}</text>
        </view>
        <view class="stat">
          <text class="stat-label">已到</text>
          <text class="stat-value green">{{ stats.present }}</text>
        </view>
        <view class="stat">
          <text class="stat-label">迟到</text>
          <text class="stat-value orange">{{ stats.late }}</text>
        </view>
        <view class="stat">
          <text class="stat-label">请假</text>
          <text class="stat-value blue">{{ stats.leave || 1 }}</text>
        </view>
        <view class="stat">
          <text class="stat-label">缺勤</text>
          <text class="stat-value red">{{ stats.absent }}</text>
        </view>
      </view>

      <view class="quick-grid">
        <button class="quick-btn active" @click="markAllPresent">
          <uni-icons type="checkmarkempty" size="24" color="#1f7159" />
          <text>一键全到</text>
        </button>
        <button class="quick-btn" @click="markPendingAbsent">
          <uni-icons type="calendar" size="24" color="#34433d" />
          <text>未到设缺勤</text>
        </button>
        <button class="quick-btn" @click="importLeave">
          <uni-icons type="upload" size="24" color="#34433d" />
          <text>请假导入</text>
        </button>
        <button class="quick-btn" @click="resetCheckin">
          <uni-icons type="refresh" size="24" color="#34433d" />
          <text>重置</text>
        </button>
      </view>

      <view class="student-list">
        <view
          v-for="student in students"
          :key="student.id"
          class="student-card"
          :class="student.status"
        >
          <view v-if="statusText(student.status)" class="corner-badge" :class="student.status">
            {{ statusText(student.status) }}
          </view>
          <view class="student-head">
            <view v-if="student.avatarType === 'image'" class="photo-avatar">
              img
            </view>
            <view v-else class="initial-avatar">
              {{ student.initial || student.name.slice(0, 1) }}
            </view>
            <view class="student-main">
              <view class="student-name">
                {{ student.name }}
              </view>
              <view class="student-sub">
                剩余课时: {{ student.remaining }}
              </view>
            </view>
          </view>
          <view class="status-grid">
            <button
              v-for="action in statusActions"
              :key="action.value"
              class="status-btn"
              :class="[action.value, { active: student.status === action.value }]"
              @click="setStatus(student, action.value)"
            >
              {{ action.label }}
            </button>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-action">
      <button class="finish-btn" @click="finishCheckin">
        完成点名
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.checkin-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-bottom: 156rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 96rpx 1fr 152rpx;
  align-items: center;
  height: 112rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.nav-icon,
.campus-btn,
.quick-btn,
.status-btn,
.finish-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
}

.nav-icon::after,
.campus-btn::after,
.quick-btn::after,
.status-btn::after,
.finish-btn::after {
  border: 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 72rpx;
  height: 72rpx;
  background: transparent;
}

.brand {
  font-size: 32rpx;
  font-weight: 700;
  color: #00684f;
  text-align: center;
}

.campus-btn {
  font-size: 28rpx;
  color: #007351;
  background: transparent;
  text-align: right;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  padding: 34rpx 22rpx 0;
}

.course-card,
.stats-card,
.quick-btn,
.student-card {
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
  box-shadow: 0 4rpx 12rpx rgba(31, 45, 51, 0.05);
}

.course-card {
  padding: 26rpx;
}

.course-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}

.course-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 700;
}

.class-pill {
  flex-shrink: 0;
  padding: 8rpx 16rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #007351;
  background: #e7f6fe;
  border-radius: 999rpx;
}

.course-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx 20rpx;
  margin-top: 22rpx;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 10rpx;
  min-width: 0;
  font-size: 26rpx;
  color: #3f4944;
}

.course-meta.full {
  grid-column: 1 / -1;
}

.stats-card {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 20rpx 8rpx;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  min-width: 0;
}

.stat.first {
  border-right: 1rpx solid #bec9c3;
}

.stat-label {
  font-size: 23rpx;
  font-weight: 700;
  color: #3f4944;
}

.stat-value {
  font-size: 25rpx;
  font-weight: 700;
}

.stat-value.dark {
  color: #0f1d23;
}

.stat-value.green {
  color: #007351;
}

.stat-value.orange {
  color: #b45309;
}

.stat-value.blue {
  color: #0369a1;
}

.stat-value.red {
  color: #ba1a1a;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.quick-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  height: 126rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #34433d;
}

.quick-btn.active {
  color: #1f7159;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.student-card {
  position: relative;
  overflow: hidden;
  padding: 32rpx 28rpx 28rpx;
}

.student-card.present {
  border-color: #1f7159;
  box-shadow: inset 0 0 0 1rpx #1f7159;
}

.student-card.late {
  border-color: #f59e0b;
  box-shadow: inset 0 0 0 1rpx #f59e0b;
}

.student-card.leave {
  border-color: #38bdf8;
  box-shadow: inset 0 0 0 1rpx #38bdf8;
}

.student-card.absent {
  border-color: #ba1a1a;
  box-shadow: inset 0 0 0 1rpx #ba1a1a;
}

.corner-badge {
  position: absolute;
  top: 0;
  right: 0;
  padding: 8rpx 14rpx;
  font-size: 21rpx;
  font-weight: 700;
  color: #ffffff;
  border-bottom-left-radius: 14rpx;
}

.corner-badge.present {
  background: #1f7159;
}

.corner-badge.late {
  background: #f59e0b;
}

.corner-badge.leave {
  background: #0369a1;
}

.corner-badge.absent {
  background: #ba1a1a;
}

.student-head {
  display: flex;
  align-items: center;
  gap: 22rpx;
  margin-bottom: 26rpx;
}

.photo-avatar,
.initial-avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
}

.photo-avatar {
  font-size: 28rpx;
  color: #3f4944;
  background: #d7d7d7;
  border-radius: 0;
}

.initial-avatar {
  font-size: 36rpx;
  font-weight: 700;
  color: #1f7159;
  background: #c2ebde;
}

.student-main {
  flex: 1;
  min-width: 0;
}

.student-name {
  overflow: hidden;
  font-size: 30rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-sub {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.status-btn {
  height: 78rpx;
  font-size: 27rpx;
  font-weight: 700;
  color: #0f1d23;
  background: #e7f6fe;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.status-btn.present.active {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.status-btn.late.active {
  color: #b45309;
  background: #fff5d8;
  border-color: #f59e0b;
}

.status-btn.leave.active {
  color: #0369a1;
  background: #e7f6fe;
  border-color: #38bdf8;
}

.status-btn.absent.active {
  color: #ba1a1a;
  background: #ffdad6;
  border-color: #ba1a1a;
}

.bottom-action {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  padding: 28rpx 32rpx calc(28rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #e7ece9;
  box-shadow: 0 -8rpx 20rpx rgba(31, 45, 51, 0.06);
}

.finish-btn {
  width: 100%;
  height: 92rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
