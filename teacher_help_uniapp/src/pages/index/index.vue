<script lang="ts" setup>
import type { ScheduleEvent } from '@/api/teach/schedule'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'
import { listScheduleEvent } from '@/api/teach/schedule'
import { safeAreaInsets } from '@/utils/systemInfo'

defineOptions({
  name: 'Home',
})
definePage({
  type: 'home',
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '老师帮',
    enablePullDownRefresh: true,
  },
})

const loading = ref(false)
const events = ref<ScheduleEvent[]>([])
const currentDate = ref(new Date())
const loadError = ref('')

const todayLabel = computed(() => `${currentDate.value.getMonth() + 1}月${currentDate.value.getDate()}日`)
const weekLabel = computed(() => ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][currentDate.value.getDay()])
const todayIso = computed(() => formatDate(currentDate.value))

const nextEvent = computed(() => {
  const now = Date.now()
  const actionableEvents = events.value.filter(item => !isClosedEvent(item))
  return actionableEvents.find(item => new Date(item.endTime).getTime() >= now)
    || actionableEvents[actionableEvents.length - 1]
    || events.value[0]
})
const heroKicker = computed(() => {
  if (!nextEvent.value)
    return '今日安排'
  if (isClosedEvent(nextEvent.value))
    return '最近课程'
  const now = Date.now()
  const start = new Date(nextEvent.value.startTime).getTime()
  const end = new Date(nextEvent.value.endTime).getTime()
  if (now >= start && now <= end)
    return '正在上课'
  if (now < start)
    return '下一节课'
  return '待收尾课程'
})
const heroActionText = computed(() => {
  if (!nextEvent.value)
    return '课表'
  return isClosedEvent(nextEvent.value) ? '查看' : '点名'
})

const totalPlanned = computed(() => events.value.reduce((sum, item) => sum + (item.cachedPlanned || 0), 0))
const totalArrived = computed(() => events.value.reduce((sum, item) => sum + getArrivedCount(item), 0))
const pendingCount = computed(() => events.value.reduce((sum, item) => {
  const planned = item.cachedPlanned || 0
  const present = item.cachedPresent || 0
  const late = item.cachedLate || 0
  const excused = item.cachedExcused || 0
  const absent = item.cachedAbsent || 0
  return sum + Math.max(planned - present - late - excused - absent, 0)
}, 0))

function formatDate(date: Date) {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatTime(value?: string) {
  if (!value)
    return '--:--'
  const date = new Date(value)
  return `${`${date.getHours()}`.padStart(2, '0')}:${`${date.getMinutes()}`.padStart(2, '0')}`
}

function eventRange(item: ScheduleEvent) {
  return `${formatTime(item.startTime)}-${formatTime(item.endTime)}`
}

function getEventState(item: ScheduleEvent) {
  const status = String(item.status || '')
  if (status === '2')
    return '已完成'
  if (status === '3')
    return '已取消'
  const now = Date.now()
  const start = new Date(item.startTime).getTime()
  const end = new Date(item.endTime).getTime()
  if (now < start)
    return '待上课'
  if (now <= end)
    return '上课中'
  return '已结束'
}

function getEventStateClass(item: ScheduleEvent) {
  const status = String(item.status || '')
  if (status === '2')
    return 'done'
  if (status === '3')
    return 'cancelled'
  const now = Date.now()
  const start = new Date(item.startTime).getTime()
  const end = new Date(item.endTime).getTime()
  if (now < start)
    return 'scheduled'
  if (now <= end)
    return 'active'
  return 'ended'
}

function isClosedEvent(item?: ScheduleEvent) {
  return !!item && ['2', '3'].includes(String(item.status || ''))
}

function getEventTitle(item: ScheduleEvent) {
  return item.courseName || item.subjectName || item.subjectCode || '未命名课程'
}

function getArrivedCount(item: ScheduleEvent) {
  return (item.cachedPresent || 0) + (item.cachedLate || 0)
}

async function loadToday() {
  currentDate.value = new Date()
  loading.value = true
  loadError.value = ''
  try {
    const res = await listScheduleEvent({
      pageNum: 1,
      pageSize: 50,
      eventDate: todayIso.value,
    })
    events.value = (res.rows || []).sort((a, b) => {
      return new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
    })
  }
  catch (error: any) {
    if (!events.value.length)
      loadError.value = error?.msg || '加载失败，请重试'
  }
  finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

function openEvent(item?: ScheduleEvent) {
  if (!item?.id) {
    openSchedule()
    return
  }
  uni.navigateTo({ url: `/pages/schedule/detail?id=${item.id}` })
}

function openSchedule() {
  uni.switchTab({ url: '/pages/schedule/index' })
}

onShow(() => {
  loadToday()
})

onPullDownRefresh(() => {
  loadToday()
})
</script>

<template>
  <view class="home-page" :style="{ paddingTop: `${safeAreaInsets?.top || 0}px` }">
    <view class="topbar">
      <view>
        <view class="eyebrow">
          {{ todayLabel }} {{ weekLabel }}
        </view>
        <view class="title">
          今日工作台
        </view>
      </view>
      <button class="icon-btn" :disabled="loading" @click="loadToday">
        <uni-icons type="refresh" size="18" color="#253238" />
      </button>
    </view>

    <view class="hero-panel" @click="openEvent(nextEvent)">
      <view class="hero-main">
        <view class="hero-kicker">
          {{ heroKicker }}
        </view>
        <view class="hero-title">
          {{ nextEvent ? getEventTitle(nextEvent) : '今天暂无课程' }}
        </view>
        <view class="hero-meta">
          <text v-if="nextEvent">{{ eventRange(nextEvent) }}</text>
          <text v-if="nextEvent"> · {{ nextEvent.teacherName || '未分配老师' }}</text>
          <text v-if="!nextEvent">可以去课表查看其他日期</text>
        </view>
      </view>
      <view class="hero-action">
        <text>{{ heroActionText }}</text>
        <uni-icons type="right" size="16" color="#ffffff" />
      </view>
    </view>

    <view class="metric-grid">
      <view class="metric-item">
        <view class="metric-value">
          {{ events.length }}
        </view>
        <view class="metric-label">
          今日课程
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ totalPlanned }}
        </view>
        <view class="metric-label">
          应到人次
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ pendingCount }}
        </view>
        <view class="metric-label">
          待处理
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ totalArrived }}
        </view>
        <view class="metric-label">
          已到课
        </view>
      </view>
    </view>

    <view class="section-head">
      <text>今天课程</text>
      <button class="text-btn" @click="openSchedule">
        全部
      </button>
    </view>

    <view v-if="loading && !events.length" class="state-box">
      加载中...
    </view>
    <view v-else-if="loadError && !events.length" class="state-box">
      <view>{{ loadError }}</view>
      <button class="state-action" @click="loadToday">
        重试
      </button>
    </view>
    <view v-else-if="!events.length" class="state-box">
      今天没有排课
    </view>
    <view v-else class="event-list">
      <view v-for="item in events" :key="item.id" class="event-row" @click="openEvent(item)">
        <view class="time-col">
          <view class="time-main">
            {{ formatTime(item.startTime) }}
          </view>
          <view class="time-sub">
            {{ formatTime(item.endTime) }}
          </view>
        </view>
        <view class="event-info">
          <view class="event-title-line">
            <text class="event-title">
              {{ getEventTitle(item) }}
            </text>
            <text class="event-status" :class="getEventStateClass(item)">
              {{ getEventState(item) }}
            </text>
          </view>
          <view class="event-desc">
            {{ item.teacherName || '未分配老师' }} · {{ getArrivedCount(item) }}/{{ item.cachedPlanned || 0 }} 已到
          </view>
        </view>
        <uni-icons type="right" size="16" color="#9aa3aa" />
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-right: 28rpx;
  padding-bottom: 150rpx;
  padding-left: 28rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 0 20rpx;
}

.eyebrow {
  font-size: 24rpx;
  color: #64737b;
}

.title {
  margin-top: 6rpx;
  font-size: 42rpx;
  font-weight: 700;
}

.icon-btn,
.text-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
  background: transparent;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  background: #ffffff;
  border-radius: 50%;
}

.icon-btn::after,
.text-btn::after {
  border: 0;
}

.hero-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 208rpx;
  padding: 34rpx;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.hero-main {
  min-width: 0;
}

.hero-kicker {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.68);
}

.hero-title {
  max-width: 440rpx;
  margin-top: 14rpx;
  overflow: hidden;
  font-size: 42rpx;
  font-weight: 700;
  color: #ffffff;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero-meta {
  margin-top: 12rpx;
  font-size: 25rpx;
  color: rgba(255, 255, 255, 0.76);
}

.hero-action {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 4rpx;
  padding: 18rpx 20rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #ffffff;
  background: #2a9d73;
  border-radius: 999rpx;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.metric-item {
  padding: 22rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.metric-value {
  font-size: 38rpx;
  font-weight: 700;
  color: #183a34;
}

.metric-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #718088;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 34rpx;
  margin-bottom: 16rpx;
  font-size: 32rpx;
  font-weight: 700;
}

.text-btn {
  font-size: 26rpx;
  color: #1d8b69;
}

.state-box {
  padding: 70rpx 0;
  font-size: 28rpx;
  color: #7a858b;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.state-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 160rpx;
  height: 64rpx;
  padding: 0;
  margin: 24rpx auto 0;
  font-size: 26rpx;
  line-height: 64rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}

.state-action::after {
  border: 0;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.event-row {
  display: flex;
  align-items: center;
  gap: 22rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.time-col {
  flex-shrink: 0;
  width: 96rpx;
  text-align: center;
}

.time-main {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2d33;
}

.time-sub {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #839099;
}

.event-info {
  flex: 1;
  min-width: 0;
}

.event-title-line {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.event-title {
  flex: 1;
  overflow: hidden;
  font-size: 31rpx;
  font-weight: 650;
  color: #1f2d33;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-status {
  flex-shrink: 0;
  padding: 7rpx 14rpx;
  font-size: 22rpx;
  color: #1f7159;
  background: #e8f5ef;
  border-radius: 999rpx;
}

.event-status.active {
  color: #1f7159;
  background: #dff4eb;
}

.event-status.ended {
  color: #8a671b;
  background: #fff5d8;
}

.event-status.done {
  color: #5d6a70;
  background: #eef2f0;
}

.event-status.cancelled {
  color: #9a3b33;
  background: #ffeceb;
}

.event-desc {
  margin-top: 10rpx;
  overflow: hidden;
  font-size: 25rpx;
  color: #74828a;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
