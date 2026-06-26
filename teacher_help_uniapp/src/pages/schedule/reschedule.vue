<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ScheduleReschedule',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '调课申请',
  },
})

// 原课程信息（mock）
const original = ref({
  name: '少儿数学提高班',
  date: '6月23日 (周日)',
  time: '14:00 - 16:00',
})

const teacherOptions = ['王老师', '李老师', '张老师']
const roomOptions = ['301 数学活动室', '302 多媒体教室', '205 综合教室']

const form = ref({
  date: '2024-06-30',
  time: '14:00',
  teacherIndex: 0,
  roomIndex: 0,
  reason: '',
  notify: true,
})

const teacherText = computed(() => teacherOptions[form.value.teacherIndex])
const roomText = computed(() => roomOptions[form.value.roomIndex])

function onDateChange(e: any) {
  form.value.date = e.detail.value
}
function onTimeChange(e: any) {
  form.value.time = e.detail.value
}
function onTeacherChange(e: any) {
  form.value.teacherIndex = Number(e.detail.value)
}
function onRoomChange(e: any) {
  form.value.roomIndex = Number(e.detail.value)
}

function goBack() {
  uni.navigateBack()
}

function checkConflict() {
  uni.showToast({ title: '未检测到冲突', icon: 'none' })
}

function confirm() {
  uni.showToast({ title: '调课成功', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="rs-page">
    <view class="topbar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <view class="page-title">
        调课申请
      </view>
      <view class="top-spacer" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <!-- 原课程信息卡 -->
      <view class="origin-card">
        <view class="origin-tag-row">
          <text class="origin-tag">
            原课程信息
          </text>
        </view>
        <view class="origin-name">
          {{ original.name }}
        </view>
        <view class="origin-meta">
          <view class="meta-item">
            <uni-icons type="calendar" size="15" color="#88d6b9" />
            <text>{{ original.date }}</text>
          </view>
          <view class="meta-item">
            <uni-icons type="clock" size="15" color="#88d6b9" />
            <text>{{ original.time }}</text>
          </view>
        </view>
      </view>

      <!-- 新课程安排卡 -->
      <view class="form-card">
        <view class="card-title">
          新课程安排
        </view>

        <!-- 新日期 / 新时间 两列 -->
        <view class="two-col">
          <view class="field">
            <text class="field-label">
              新日期
            </text>
            <picker mode="date" :value="form.date" @change="onDateChange">
              <view class="field-box">
                {{ form.date }}
              </view>
            </picker>
          </view>
          <view class="field">
            <text class="field-label">
              新时间
            </text>
            <picker mode="time" :value="form.time" @change="onTimeChange">
              <view class="field-box">
                {{ form.time }}
              </view>
            </picker>
          </view>
        </view>

        <!-- 任课老师 -->
        <view class="field">
          <text class="field-label">
            任课老师
          </text>
          <picker mode="selector" :range="teacherOptions" :value="form.teacherIndex" @change="onTeacherChange">
            <view class="field-box select">
              <text>{{ teacherText }}</text>
              <uni-icons type="bottom" size="14" color="#3f4944" />
            </view>
          </picker>
        </view>

        <!-- 上课教室 -->
        <view class="field">
          <text class="field-label">
            上课教室
          </text>
          <picker mode="selector" :range="roomOptions" :value="form.roomIndex" @change="onRoomChange">
            <view class="field-box select">
              <text>{{ roomText }}</text>
              <uni-icons type="bottom" size="14" color="#3f4944" />
            </view>
          </picker>
        </view>

        <!-- 调课原因 -->
        <view class="field">
          <text class="field-label">
            调课原因
          </text>
          <textarea
            v-model="form.reason"
            class="field-area"
            placeholder="请输入调课原因，例如：老师请假、教室冲突等..."
          />
        </view>

        <!-- 通知开关 -->
        <view class="notify-row">
          <view class="notify-text">
            <text class="notify-title">
              通知学员/家长
            </text>
            <text class="notify-desc">
              调课成功后自动发送微信/短信通知
            </text>
          </view>
          <switch :checked="form.notify" color="#1f7159" @change="form.notify = $event.detail.value" />
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
  color: #0f1d23;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 102rpx;
  padding: 0 20rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.back-btn,
.top-spacer {
  width: 64rpx;
  height: 64rpx;
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
  font-size: 34rpx;
  font-weight: 700;
  color: #005842;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 102rpx);
  padding: 28rpx 28rpx 180rpx;
}

/* 原课程信息卡 */
.origin-card {
  padding: 28rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.origin-tag-row {
  margin-bottom: 14rpx;
}

.origin-tag {
  padding: 6rpx 20rpx;
  font-size: 22rpx;
  font-weight: 500;
  color: #227253;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.origin-name {
  font-size: 34rpx;
  font-weight: 600;
}

.origin-meta {
  display: flex;
  gap: 32rpx;
  margin-top: 18rpx;
}

.meta-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 25rpx;
  color: #88d6b9;
}

/* 新课程安排卡 */
.form-card {
  margin-top: 18rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.card-title {
  padding-bottom: 22rpx;
  font-size: 32rpx;
  font-weight: 600;
  border-bottom: 1rpx solid #e7ece9;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-top: 28rpx;
}

.field-label {
  font-size: 24rpx;
  color: #3f4944;
}

.field-box {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #0f1d23;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.field-box.select {
  justify-content: space-between;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.notify-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 28rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #e7ece9;
}

.notify-text {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.notify-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #0f1d23;
}

.notify-desc {
  font-size: 23rpx;
  color: #3f4944;
}

/* 底部固定栏 */
.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 18rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #e7ece9;
}

.ghost-btn,
.primary-btn {
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  flex: 1;
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  flex: 2;
  color: #ffffff;
  background: #1f7159;
}
</style>
