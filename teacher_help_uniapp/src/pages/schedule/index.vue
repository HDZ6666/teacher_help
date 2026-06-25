<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'Schedule',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '课表',
    enablePullDownRefresh: false,
  },
})

const activeDay = ref(23)
const activeView = ref('日程')

const days = [
  { week: '一', day: 22 },
  { week: '二', day: 23 },
  { week: '三', day: 24 },
  { week: '四', day: 25 },
  { week: '五', day: 26 },
  { week: '六', day: 27 },
  { week: '日', day: 28 },
]

const viewModes = ['日程', '周', '月', '列表']

const courses = [
  {
    time: '14:00 - 15:30',
    title: '少儿数学提高班',
    teacher: '王老师',
    room: 'A区201',
    status: '待点名',
    statusClass: 'pending',
    active: true,
  },
  {
    time: '09:00 - 10:30',
    title: '少儿英语启蒙班',
    teacher: '李老师',
    room: 'B区105',
    status: '已完成',
    statusClass: 'done',
    active: false,
  },
]

function goCreate() {
  uni.navigateTo({ url: '/pages/schedule/create' })
}

function showFilter() {
  uni.showToast({ title: '筛选课程', icon: 'none' })
}

function openDetail() {
  uni.navigateTo({ url: '/pages/schedule/course-detail' })
}

function reschedule() {
  uni.navigateTo({ url: '/pages/schedule/reschedule' })
}

function checkin() {
  uni.navigateTo({ url: '/pages/schedule/detail' })
}
</script>

<template>
  <view class="schedule-page">
    <view class="topbar">
      <view class="title-wrap">
        <button class="icon-btn">
          <uni-icons type="calendar-filled" size="28" color="#1f7159" />
        </button>
        <view class="page-title">
          我的课表
        </view>
      </view>
      <button class="icon-btn right" @click="goCreate">
        <uni-icons type="plusempty" size="34" color="#1f7159" />
      </button>
    </view>

    <view class="date-panel">
      <scroll-view class="day-scroll" scroll-x>
        <view class="day-row">
          <button
            v-for="item in days"
            :key="item.day"
            class="day-item"
            :class="{ active: activeDay === item.day }"
            @click="activeDay = item.day"
          >
            <text class="day-week">{{ item.week }}</text>
            <text class="day-num">{{ item.day }}</text>
          </button>
        </view>
      </scroll-view>

      <view class="control-row">
        <view class="segment">
          <button
            v-for="item in viewModes"
            :key="item"
            class="segment-btn"
            :class="{ active: activeView === item }"
            @click="activeView = item"
          >
            {{ item }}
          </button>
        </view>
        <button class="filter-btn" @click="showFilter">
          <uni-icons type="bars" size="24" color="#3f4944" />
        </button>
      </view>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="course-list">
        <view
          v-for="item in courses"
          :key="item.title"
          class="course-card"
          :class="{ inactive: !item.active }"
        >
          <view class="left-line" :class="{ muted: !item.active }" />
          <view class="course-head">
            <view>
              <view class="time-line" :class="{ muted: !item.active }">
                {{ item.time }}
                <text class="status-pill" :class="item.statusClass">
                  {{ item.status }}
                </text>
              </view>
              <view class="course-title" :class="{ muted: !item.active }">
                {{ item.title }}
              </view>
            </view>
          </view>

          <view class="meta-row">
            <view class="meta-item">
              <uni-icons type="person" size="18" color="#3f4944" />
              <text>{{ item.teacher }}</text>
            </view>
            <view class="meta-item">
              <uni-icons type="location" size="18" color="#3f4944" />
              <text>{{ item.room }}</text>
            </view>
          </view>

          <view v-if="item.active" class="action-row">
            <button class="outline-btn" @click="openDetail">
              详情
            </button>
            <button class="outline-btn" @click="reschedule">
              调课
            </button>
            <button class="primary-btn" @click="checkin">
              去点名
            </button>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.schedule-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f4f6f5;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.title-wrap {
  display: flex;
  gap: 18rpx;
  align-items: center;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1f7159;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
  border-radius: 50%;
}

.date-panel {
  position: sticky;
  top: 112rpx;
  z-index: 20;
  padding: 16rpx 28rpx 28rpx;
  background: #ffffff;
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.35);
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.04);
}

.day-scroll {
  white-space: nowrap;
}

.day-row {
  display: flex;
  justify-content: space-between;
  min-width: 100%;
  gap: 14rpx;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 80rpx;
  height: 82rpx;
  padding: 0;
  margin: 0;
  color: rgba(15, 29, 35, 0.62);
  background: transparent;
  border-radius: 16rpx;
}

.day-item.active {
  color: #ffffff;
  background: #1f7159;
  box-shadow: 0 4rpx 10rpx rgba(31, 113, 89, 0.15);
}

.day-week {
  font-size: 22rpx;
  line-height: 1.2;
}

.day-num {
  margin-top: 6rpx;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 1.2;
}

.control-row {
  display: flex;
  gap: 28rpx;
  align-items: center;
  margin-top: 28rpx;
}

.segment {
  display: flex;
  flex: 1;
  padding: 6rpx;
  background: #d6e5ed;
  border-radius: 16rpx;
}

.segment-btn {
  flex: 1;
  height: 62rpx;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 62rpx;
  color: #3f4944;
  background: transparent;
  border-radius: 12rpx;
}

.segment-btn.active {
  color: #1f7159;
  background: #ffffff;
  box-shadow: 0 3rpx 10rpx rgba(15, 29, 35, 0.08);
}

.filter-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 292rpx);
  padding: 28rpx 28rpx 170rpx;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.course-card {
  position: relative;
  padding: 32rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid rgba(190, 201, 195, 0.55);
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.04);
}

.course-card.inactive {
  opacity: 0.75;
}

.left-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 8rpx;
  background: #1f7159;
}

.left-line.muted {
  background: #bec9c3;
}

.time-line {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  align-items: center;
  font-size: 40rpx;
  font-weight: 800;
}

.time-line.muted {
  color: #3f4944;
}

.status-pill {
  padding: 4rpx 16rpx;
  font-size: 22rpx;
  font-weight: 700;
  border-radius: 999rpx;
}

.status-pill.pending {
  color: #1f7159;
  background: #d6e5ed;
}

.status-pill.done {
  color: #3f4944;
  background: #e1f0f8;
}

.course-title {
  margin-top: 12rpx;
  font-size: 34rpx;
  font-weight: 700;
}

.course-title.muted {
  color: #3f4944;
}

.meta-row {
  display: flex;
  gap: 40rpx;
  align-items: center;
  margin-top: 28rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.meta-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  gap: 16rpx;
  padding-top: 24rpx;
  margin-top: 28rpx;
  border-top: 1rpx solid rgba(190, 201, 195, 0.35);
}

.outline-btn,
.primary-btn {
  height: 72rpx;
  padding: 0 32rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 72rpx;
  border-radius: 16rpx;
}

.outline-btn {
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}

.icon-btn::after,
.day-item::after,
.segment-btn::after,
.filter-btn::after,
.outline-btn::after,
.primary-btn::after {
  border: 0;
}
</style>
