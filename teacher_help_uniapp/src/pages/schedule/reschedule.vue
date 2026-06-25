<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ScheduleReschedule',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '调课申请',
  },
})

const current = ref({
  course: '数学提高A班',
  date: '06月23日 周二',
  time: '18:30-20:00',
  teacher: '王老师',
  room: '301教室',
})

const form = ref({
  date: '',
  start: '',
  end: '',
  teacher: '王老师',
  room: '301教室',
  reason: '',
  notify: true,
})

const commonTimes = ['08:00-09:00', '10:00-11:30', '14:00-15:30', '18:30-20:00']

function onDateChange(e: any) {
  form.value.date = e.detail.value
}

function applyCommonTime(t: string) {
  const [s, e] = t.split('-')
  form.value.start = s
  form.value.end = e
}

function checkConflict() {
  uni.navigateTo({ url: '/pages/schedule/conflict' })
}

function goBack() {
  uni.navigateBack()
}

function confirm() {
  if (!form.value.date) {
    uni.showToast({ title: '请选择新日期', icon: 'none' })
    return
  }
  uni.showToast({ title: '调课成功', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

</script>

<template>
  <view class="rs-page">
    <view class="topbar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="28" color="#1f7159" />
      </button>
      <view class="page-title">
        调课申请
      </view>
      <view class="top-spacer" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
    <view class="current-card">
      <view class="cur-title">
        当前课次
      </view>
      <view class="cur-name">
        {{ current.course }}
      </view>
      <view class="cur-meta">
        {{ current.date }} · {{ current.time }}
      </view>
      <view class="cur-meta">
        {{ current.teacher }} · {{ current.room }}
      </view>
    </view>

    <view class="form-card">
      <picker mode="date" :value="form.date" @change="onDateChange">
        <view class="row">
          <text class="row-label">
            新日期
          </text>
          <view class="row-value" :class="{ ph: !form.date }">
            {{ form.date || '请选择新日期' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="row no-border">
        <text class="row-label">
          新时间
        </text>
        <view class="row-value" :class="{ ph: !form.start }">
          {{ form.start && form.end ? `${form.start} - ${form.end}` : '选择常用时间段' }}
        </view>
      </view>
      <view class="time-chips">
        <view
          v-for="t in commonTimes"
          :key="t"
          class="time-chip"
          :class="{ active: `${form.start}-${form.end}` === t }"
          @click="applyCommonTime(t)"
        >
          {{ t }}
        </view>
      </view>
    </view>

    <view class="form-card">
      <view class="row" @click="form.teacher = '李老师'">
        <text class="row-label">
          老师
        </text>
        <view class="row-value">
          {{ form.teacher }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
      <view class="row no-border" @click="form.room = '302教室'">
        <text class="row-label">
          教室
        </text>
        <view class="row-value">
          {{ form.room }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
    </view>

    <view class="form-card">
      <view class="row column no-border">
        <text class="row-label">
          调课原因
        </text>
        <textarea v-model="form.reason" class="full-textarea" placeholder="请填写调课原因" />
      </view>
    </view>

    <view class="form-card">
      <view class="row no-border">
        <text class="row-label">
          通知学员/家长
        </text>
        <switch :checked="form.notify" color="#1f7159" style="transform: scale(0.85)" @change="form.notify = $event.detail.value" />
      </view>
    </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="checkConflict">
        检查冲突
      </button>
      <button class="primary-btn" @click="confirm">
        确认调课
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.rs-page {
  min-height: 100vh;
  color: #1f2d33;
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

.back-btn,
.top-spacer {
  width: 72rpx;
  height: 72rpx;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  background: transparent;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1f7159;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 28rpx 28rpx 180rpx;
}

.current-card {
  padding: 28rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.cur-title {
  font-size: 23rpx;
  color: rgba(255, 255, 255, 0.68);
}

.cur-name {
  margin-top: 12rpx;
  font-size: 36rpx;
  font-weight: 700;
}

.cur-meta {
  margin-top: 10rpx;
  font-size: 25rpx;
  color: rgba(255, 255, 255, 0.78);
}

.form-card {
  margin-top: 16rpx;
  padding: 0 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 96rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.row.no-border {
  border-bottom: 0;
}

.row.column {
  display: block;
  padding: 24rpx 0;
}

.row-label {
  font-size: 27rpx;
  color: #4a565c;
}

.row-value {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 27rpx;
}

.row-value.ph {
  color: #9aa5aa;
}

.time-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  padding: 0 0 24rpx;
}

.time-chip {
  padding: 12rpx 22rpx;
  font-size: 24rpx;
  color: #67757c;
  background: #f1f4f2;
  border-radius: 999rpx;
}

.time-chip.active {
  color: #ffffff;
  background: #1f7159;
}

.full-textarea {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  margin-top: 16rpx;
  padding: 18rpx 20rpx;
  font-size: 27rpx;
  background: #f6f8f7;
  border-radius: 12rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 16rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.ghost-btn,
.primary-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  line-height: 90rpx;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #e6f4ee;
}

.primary-btn {
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
}

.ghost-btn::after,
.primary-btn::after,
.back-btn::after {
  border: 0;
}
</style>
