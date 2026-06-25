<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

defineOptions({
  name: 'TeacherSchedule',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '老师课表',
  },
})

interface DateItem {
  day: number
  week: string
}
interface ScheduleItem {
  id: number
  time: string
  title: string
  group: string
  room: string
  status: '待点名' | '已结课' | '已点名'
  accent: 'active' | 'muted' | 'done'
}

const teacherId = ref('')
const teacherName = ref('李老师')
const navTitle = computed(() => `${teacherName.value}的课表`)
const monthText = ref('2023年 10月')

const dates = ref<DateItem[]>([
  { day: 16, week: '一' },
  { day: 17, week: '二' },
  { day: 18, week: '三' },
  { day: 19, week: '四' },
  { day: 20, week: '五' },
  { day: 21, week: '六' },
  { day: 22, week: '日' },
])
const activeDay = ref(17)

const schedules = ref<ScheduleItem[]>([
  { id: 1, time: '09:00 - 10:30', title: '初中数学强化', group: '秋季A班 (30人)', room: 'A102 教室', status: '待点名', accent: 'active' },
  { id: 2, time: '14:00 - 15:30', title: '初二英语培优', group: '秋季C班 (25人)', room: 'B205 教室', status: '已结课', accent: 'muted' },
  { id: 3, time: '16:00 - 17:30', title: '初一语文基础', group: '秋季B班 (40人)', room: 'A105 教室', status: '已点名', accent: 'done' },
])

function goBack() {
  uni.navigateBack()
}
function statusClass(s: ScheduleItem['status']) {
  if (s === '待点名')
    return 'danger'
  if (s === '已点名')
    return 'success'
  return 'muted'
}
function onReschedule() {
  uni.navigateTo({ url: '/pages/schedule/reschedule' })
}
function onDetail(item: ScheduleItem) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${item.id}` })
}
function onCheckin(item: ScheduleItem) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${item.id}` })
}
function onEditAttendance(item: ScheduleItem) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${item.id}` })
}

onLoad((query) => {
  teacherId.value = query?.id || ''
})
</script>

<template>
  <view class="ts-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        {{ navTitle }}
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 日期条 -->
    <view class="date-strip">
      <view class="month-row">
        <text class="month-text">
          {{ monthText }}
        </text>
        <view class="cal-btn">
          <uni-icons type="calendar" size="16" color="#1f7159" />
          <text>日历</text>
        </view>
      </view>
      <scroll-view class="date-scroll" scroll-x>
        <view class="date-row">
          <view
            v-for="d in dates"
            :key="d.day"
            class="date-item"
            :class="{ on: activeDay === d.day }"
            @click="activeDay = d.day"
          >
            <text class="date-week">
              {{ d.week }}
            </text>
            <text class="date-day">
              {{ d.day }}
            </text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 课程列表 -->
    <view class="list">
      <view
        v-for="s in schedules"
        :key="s.id"
        class="sch-card"
        :class="{ dim: s.accent === 'muted' }"
      >
        <view class="sch-accent" :class="s.accent" />
        <view class="sch-body">
          <view class="sch-top">
            <view class="sch-time">
              <uni-icons type="calendar" size="18" :color="s.accent === 'muted' ? '#3f4944' : '#1f7159'" />
              <text>{{ s.time }}</text>
            </view>
            <text class="sch-status" :class="statusClass(s.status)">
              {{ s.status }}
            </text>
          </view>
          <text class="sch-title">
            {{ s.title }}
          </text>
          <view class="sch-info">
            <view class="si-item">
              <uni-icons type="staff" size="15" color="#3f4944" />
              <text>{{ s.group }}</text>
            </view>
            <view class="si-item">
              <uni-icons type="home" size="15" color="#3f4944" />
              <text>{{ s.room }}</text>
            </view>
          </view>
          <view class="sch-actions">
            <template v-if="s.status === '待点名'">
              <button class="act outline" @click="onReschedule">
                调课
              </button>
              <button class="act outline" @click="onDetail(s)">
                详情
              </button>
              <button class="act primary" @click="onCheckin(s)">
                点名
              </button>
            </template>
            <template v-else-if="s.status === '已点名'">
              <button class="act outline" @click="onReschedule">
                调课
              </button>
              <button class="act outline" @click="onDetail(s)">
                详情
              </button>
              <button class="act outline" @click="onEditAttendance(s)">
                修改考勤
              </button>
            </template>
            <template v-else>
              <button class="act ghost" @click="onDetail(s)">
                详情
              </button>
            </template>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ts-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-bottom: 60rpx;
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
  font-size: 32rpx;
  font-weight: 600;
  color: #005842;
}

/* 日期条 */
.date-strip {
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.month-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 28rpx;
}

.month-text {
  font-size: 24rpx;
  color: #3f4944;
}

.cal-btn {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 24rpx;
  color: #1f7159;
}

.date-scroll {
  white-space: nowrap;
}

.date-row {
  display: flex;
  gap: 18rpx;
  padding: 0 28rpx 24rpx;
}

.date-item {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  gap: 8rpx;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 112rpx;
  color: #3f4944;
  background: #e7f6fe;
  border-radius: 14rpx;
}

.date-item.on {
  color: #ffffff;
  background: #1f7159;
}

.date-week {
  font-size: 22rpx;
}

.date-day {
  font-size: 32rpx;
  font-weight: 600;
}

/* 课程列表 */
.list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  padding: 24rpx 28rpx 0;
}

.sch-card {
  position: relative;
  display: flex;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.sch-card.dim {
  opacity: 0.8;
}

.sch-accent {
  width: 8rpx;
}

.sch-accent.active,
.sch-accent.done {
  background: #00583d;
}

.sch-accent.muted {
  background: #6f7974;
}

.sch-body {
  flex: 1;
  padding: 24rpx;
}

.sch-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sch-time {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 30rpx;
  font-weight: 600;
}

.sch-status {
  padding: 6rpx 20rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.sch-status.danger {
  color: #93000a;
  background: #ffdad6;
}

.sch-status.success {
  color: #007351;
  background: #8cf7c7;
}

.sch-status.muted {
  color: #3f4944;
  background: #e1f0f8;
}

.sch-title {
  display: block;
  margin-top: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
}

.sch-info {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-top: 14rpx;
}

.si-item {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.sch-actions {
  display: flex;
  gap: 14rpx;
  justify-content: flex-end;
  margin-top: 22rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #e7ece9;
}

.act {
  height: 64rpx;
  padding: 0 28rpx;
  margin: 0;
  font-size: 25rpx;
  line-height: 64rpx;
  border-radius: 8rpx;
}

.act.primary {
  color: #ffffff;
  background: #1f7159;
}

.act.outline {
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
}

.act.ghost {
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
}
</style>
