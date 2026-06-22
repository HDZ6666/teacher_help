<script lang="ts" setup>
import type { ScheduleEvent } from '@/api/teach/schedule'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'
import { listScheduleEvent } from '@/api/teach/schedule'

definePage({
  style: {
    navigationBarTitleText: '课表',
    enablePullDownRefresh: true,
  },
})

const loading = ref(false)
const events = ref<ScheduleEvent[]>([])
const selectedDateValue = ref(formatDate(new Date()))
const statusFilter = ref('')
const loadError = ref('')

const dayOptions = [
  { label: '昨天', value: -1 },
  { label: '今天', value: 0 },
  { label: '明天', value: 1 },
]

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待处理', value: '0' },
  { label: '进行中', value: '1' },
  { label: '已完成', value: '2' },
  { label: '已取消', value: '3' },
]

const selectedDate = computed(() => {
  return new Date(`${selectedDateValue.value}T00:00:00`)
})
const selectedDateText = computed(() => `${selectedDate.value.getMonth() + 1}月${selectedDate.value.getDate()}日`)
const selectedWeekText = computed(() => ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][selectedDate.value.getDay()])
const totalPlanned = computed(() => events.value.reduce((sum, item) => sum + (item.cachedPlanned || 0), 0))
const totalArrived = computed(() => events.value.reduce((sum, item) => sum + getArrivedCount(item), 0))
const pendingEventCount = computed(() => events.value.filter(item => !['2', '3'].includes(String(item.status || ''))).length)
const completedEventCount = computed(() => events.value.filter(item => String(item.status || '') === '2').length)

function formatDate(date: Date) {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

function getOffsetDate(offset: number) {
  const date = new Date()
  date.setDate(date.getDate() + offset)
  return formatDate(date)
}

function formatTime(value?: string) {
  if (!value)
    return '--:--'
  const date = new Date(value)
  return `${`${date.getHours()}`.padStart(2, '0')}:${`${date.getMinutes()}`.padStart(2, '0')}`
}

function getEventTitle(item: ScheduleEvent) {
  return item.courseName || item.subjectName || item.subjectCode || '未命名课程'
}

function getArrivedCount(item: ScheduleEvent) {
  return (item.cachedPresent || 0) + (item.cachedLate || 0)
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

async function loadSchedule() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await listScheduleEvent({
      pageNum: 1,
      pageSize: 100,
      eventDate: selectedDateValue.value,
      status: statusFilter.value || undefined,
    })
    events.value = (res.rows || []).sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime())
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

function setDay(value: number) {
  selectedDateValue.value = getOffsetDate(value)
  loadSchedule()
}

function isQuickDayActive(value: number) {
  return selectedDateValue.value === getOffsetDate(value)
}

function handleDatePick(event: any) {
  selectedDateValue.value = event.detail.value
  loadSchedule()
}

function setStatus(value: string) {
  statusFilter.value = value
  loadSchedule()
}

function openDetail(item: ScheduleEvent) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${item.id}` })
}

onShow(() => {
  loadSchedule()
})

onPullDownRefresh(() => {
  loadSchedule()
})
</script>

<template>
  <view class="schedule-page">
    <view class="date-panel">
      <picker mode="date" :value="selectedDateValue" @change="handleDatePick">
        <view class="date-picker">
          <view>
            <view class="date-main">
              {{ selectedDateText }}
            </view>
            <view class="date-sub">
              {{ selectedWeekText }}
            </view>
          </view>
          <uni-icons type="bottom" size="16" color="#74828a" />
        </view>
      </picker>
      <view class="day-switch">
        <button
          v-for="item in dayOptions"
          :key="item.value"
          class="switch-btn"
          :class="{ active: isQuickDayActive(item.value) }"
          @click="setDay(item.value)"
        >
          {{ item.label }}
        </button>
      </view>
    </view>

    <scroll-view class="filter-scroll" scroll-x>
      <view class="filter-row">
        <button
          v-for="item in statusOptions"
          :key="item.value"
          class="filter-btn"
          :class="{ active: statusFilter === item.value }"
          @click="setStatus(item.value)"
        >
          {{ item.label }}
        </button>
      </view>
    </scroll-view>

    <view class="summary-strip">
      <text>{{ events.length }} 节课</text>
      <text>待处理 {{ pendingEventCount }}</text>
      <text>已完成 {{ completedEventCount }}</text>
      <text>已到 {{ totalArrived }}/{{ totalPlanned }}</text>
    </view>

    <view v-if="loading && !events.length" class="state-box">
      加载中...
    </view>
    <view v-else-if="loadError && !events.length" class="state-box">
      <view>{{ loadError }}</view>
      <button class="state-action" @click="loadSchedule">
        重试
      </button>
    </view>
    <view v-else-if="!events.length" class="state-box">
      当天没有课程
    </view>
    <view v-else class="schedule-list">
      <view v-for="item in events" :key="item.id" class="schedule-card" @click="openDetail(item)">
        <view class="card-time">
          <text>{{ formatTime(item.startTime) }}</text>
          <text>{{ formatTime(item.endTime) }}</text>
        </view>
        <view class="card-main">
          <view class="card-title-line">
            <text class="card-title">
              {{ getEventTitle(item) }}
            </text>
            <text class="status-pill" :class="getEventStateClass(item)">
              {{ getEventState(item) }}
            </text>
          </view>
          <view class="card-desc">
            {{ item.teacherName || '未分配老师' }} · 已到 {{ getArrivedCount(item) }}/{{ item.cachedPlanned || 0 }}
          </view>
          <view class="progress-line">
            <view class="progress-item present">
              出勤 {{ item.cachedPresent || 0 }}
            </view>
            <view class="progress-item late">
              迟到 {{ item.cachedLate || 0 }}
            </view>
            <view class="progress-item absent">
              缺勤 {{ item.cachedAbsent || 0 }}
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.schedule-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 150rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.date-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.date-main {
  font-size: 40rpx;
  font-weight: 700;
}

.date-sub {
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #77858d;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.day-switch {
  display: flex;
  padding: 6rpx;
  background: #eef2f0;
  border-radius: 999rpx;
}

.switch-btn,
.filter-btn {
  padding: 0;
  margin: 0;
  font-size: 25rpx;
  line-height: 1;
  color: #67757c;
  background: transparent;
}

.switch-btn::after,
.filter-btn::after {
  border: 0;
}

.switch-btn {
  padding: 15rpx 20rpx;
  border-radius: 999rpx;
}

.switch-btn.active {
  color: #ffffff;
  background: #1f7159;
}

.filter-scroll {
  margin: 22rpx -28rpx 18rpx;
  white-space: nowrap;
}

.filter-row {
  display: flex;
  gap: 14rpx;
  padding: 0 28rpx;
}

.filter-btn {
  padding: 16rpx 24rpx;
  background: #ffffff;
  border: 1rpx solid #e2e8e5;
  border-radius: 999rpx;
}

.filter-btn.active {
  color: #1e7259;
  background: #e6f4ee;
  border-color: #b8dccc;
}

.summary-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 18rpx;
  padding: 18rpx 22rpx;
  font-size: 24rpx;
  color: #627178;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.summary-strip text {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.state-box {
  padding: 80rpx 0;
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

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.schedule-card {
  display: flex;
  gap: 24rpx;
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.card-time {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  gap: 8rpx;
  width: 96rpx;
  padding-top: 4rpx;
  font-size: 27rpx;
  font-weight: 700;
  color: #1d463d;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.card-title-line {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.card-title {
  flex: 1;
  overflow: hidden;
  font-size: 32rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-pill {
  flex-shrink: 0;
  padding: 7rpx 14rpx;
  font-size: 22rpx;
  color: #1f7159;
  background: #e8f5ef;
  border-radius: 999rpx;
}

.status-pill.active {
  color: #1f7159;
  background: #dff4eb;
}

.status-pill.ended {
  color: #8a671b;
  background: #fff5d8;
}

.status-pill.done {
  color: #5d6a70;
  background: #eef2f0;
}

.status-pill.cancelled {
  color: #9a3b33;
  background: #ffeceb;
}

.card-desc {
  margin-top: 12rpx;
  font-size: 25rpx;
  color: #75838a;
}

.progress-line {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 18rpx;
}

.progress-item {
  padding: 8rpx 14rpx;
  font-size: 23rpx;
  border-radius: 999rpx;
}

.present {
  color: #227253;
  background: #e9f6ef;
}

.late {
  color: #8a671b;
  background: #fff5d8;
}

.absent {
  color: #9a3b33;
  background: #ffeceb;
}
</style>
