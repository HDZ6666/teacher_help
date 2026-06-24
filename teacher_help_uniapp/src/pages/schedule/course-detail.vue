<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'CourseDetail',
})
definePage({
  style: {
    navigationBarTitleText: '课次详情',
  },
})

const course = ref({
  name: '数学提高A班',
  date: '06月23日 周二',
  time: '18:30-20:00',
  className: '数学提高A班',
  teacher: '王老师',
  room: '301教室',
  status: '待点名',
})

const stats = ref({ planned: 8, present: 5, late: 1, absent: 1 })

const students = ref([
  { id: 1, name: '李明轩', remaining: 2, status: '到课', cls: 'present' },
  { id: 2, name: '王诗涵', remaining: 18, status: '迟到', cls: 'late' },
  { id: 3, name: '张子墨', remaining: 6, status: '缺勤', cls: 'absent' },
  { id: 4, name: '陈嘉怡', remaining: 12, status: '到课', cls: 'present' },
  { id: 5, name: '刘梓萱', remaining: 1, status: '未到', cls: 'pending' },
])

const showMore = ref(false)

function startCheckin() {
  uni.navigateTo({ url: '/pages/schedule/detail?id=1' })
}

function editEvent() {
  uni.showToast({ title: '编辑课次', icon: 'none' })
}

function reschedule() {
  uni.navigateTo({ url: '/pages/schedule/reschedule?id=1' })
}

function cancelEvent() {
  uni.showModal({
    title: '取消课次',
    content: '取消后本节课将不再计入考勤，关联学员课时不扣减。确认取消？',
    confirmText: '确认取消',
    confirmColor: '#c0392b',
    success: (res) => {
      if (res.confirm)
        uni.showToast({ title: '已取消课次', icon: 'none' })
    },
  })
}

function viewStudent(id: number) {
  uni.navigateTo({ url: `/pages/student/detail?id=${id}` })
}

onLoad(() => {})
</script>

<template>
  <view class="cd-page">
    <view class="hero-card">
      <view class="hero-top">
        <view class="hero-name">
          {{ course.name }}
        </view>
        <text class="hero-status">
          {{ course.status }}
        </text>
      </view>
      <view class="hero-meta">
        {{ course.date }} · {{ course.time }}
      </view>
      <view class="hero-meta">
        {{ course.className }} · {{ course.teacher }} · {{ course.room }}
      </view>
      <view class="hero-actions">
        <button class="hero-btn primary" @click="startCheckin">
          开始点名
        </button>
        <button class="hero-btn" @click="reschedule">
          调课
        </button>
      </view>
    </view>

    <view class="stat-grid">
      <view class="stat-item">
        <view class="stat-num">
          {{ stats.planned }}
        </view>
        <view class="stat-label">
          应到
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num present">
          {{ stats.present }}
        </view>
        <view class="stat-label">
          已到
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num late">
          {{ stats.late }}
        </view>
        <view class="stat-label">
          迟到
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num absent">
          {{ stats.absent }}
        </view>
        <view class="stat-label">
          缺勤
        </view>
      </view>
    </view>

    <view class="section-head">
      <text>学员名单</text>
      <text class="head-link" @click="showMore = !showMore">
        更多操作
      </text>
    </view>

    <view v-if="showMore" class="more-card">
      <view class="more-row" @click="editEvent">
        <uni-icons type="compose" size="16" color="#1f7159" /><text>编辑课次</text>
      </view>
      <view class="more-row" @click="cancelEvent">
        <uni-icons type="closeempty" size="16" color="#c0392b" /><text class="danger">取消课次</text>
      </view>
    </view>

    <view class="stu-list">
      <view v-for="s in students" :key="s.id" class="stu-card" @click="viewStudent(s.id)">
        <view class="stu-avatar">
          {{ s.name.slice(0, 1) }}
        </view>
        <view class="stu-main">
          <view class="stu-name">
            {{ s.name }}
          </view>
          <view class="stu-sub" :class="{ low: s.remaining <= 3 }">
            剩余 {{ s.remaining }} 课时{{ s.remaining <= 3 ? ' · 课时不足' : '' }}
          </view>
        </view>
        <text class="stu-state" :class="s.cls">
          {{ s.status }}
        </text>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="startCheckin">
        开始点名
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cd-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.hero-card {
  padding: 30rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-name {
  font-size: 38rpx;
  font-weight: 700;
}

.hero-status {
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  color: #a4f2d4;
  background: rgba(42, 157, 115, 0.3);
  border-radius: 999rpx;
}

.hero-meta {
  margin-top: 12rpx;
  font-size: 25rpx;
  color: rgba(255, 255, 255, 0.78);
}

.hero-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 26rpx;
}

.hero-btn {
  flex: 1;
  margin: 0;
  font-size: 27rpx;
  line-height: 78rpx;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.16);
  border-radius: 14rpx;
}

.hero-btn.primary {
  color: #ffffff;
  background: #2a9d73;
}

.hero-btn::after {
  border: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.stat-item {
  padding: 22rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.stat-num {
  font-size: 38rpx;
  font-weight: 700;
  color: #183a34;
}

.stat-num.present {
  color: #227253;
}

.stat-num.late {
  color: #8a671b;
}

.stat-num.absent {
  color: #9a3b33;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #718088;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 30rpx 0 16rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.head-link {
  font-size: 25rpx;
  font-weight: 400;
  color: #1d8b69;
}

.more-card {
  margin-bottom: 16rpx;
  padding: 8rpx 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.more-row {
  display: flex;
  gap: 12rpx;
  align-items: center;
  height: 88rpx;
  font-size: 27rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.more-row:last-child {
  border-bottom: 0;
}

.more-row .danger {
  color: #c0392b;
}

.stu-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.stu-card {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 22rpx 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.stu-avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 18rpx;
}

.stu-main {
  flex: 1;
  min-width: 0;
}

.stu-name {
  font-size: 29rpx;
  font-weight: 600;
}

.stu-sub {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #839099;
}

.stu-sub.low {
  color: #c0392b;
}

.stu-state {
  flex-shrink: 0;
  padding: 7rpx 16rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.stu-state.present {
  color: #227253;
  background: #e9f6ef;
}

.stu-state.late {
  color: #8a671b;
  background: #fff5d8;
}

.stu-state.absent {
  color: #9a3b33;
  background: #ffeceb;
}

.stu-state.pending {
  color: #5d6a70;
  background: #eef2f0;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.primary-btn {
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 90rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.primary-btn::after {
  border: 0;
}
</style>
