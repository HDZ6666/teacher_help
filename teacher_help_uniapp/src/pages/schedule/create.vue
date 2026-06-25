<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ScheduleCreate',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '新增排课',
  },
})

const activeMode = ref('single')

const modes = [
  { key: 'single', title: '单次排课', desc: '安排单节课程', icon: 'calendar-filled' },
  { key: 'rule', title: '规则排课', desc: '按周期批量生成', icon: 'loop' },
  { key: 'calendar', title: '日历排课', desc: '手动多选日期', icon: 'calendar' },
]

const infoRows = [
  { label: '课程选择', value: '请选择', icon: 'paperclip', optional: false },
  { label: '班级/学员', value: '请选择', icon: 'staff', optional: false },
  { label: '授课老师', value: '请选择', icon: 'person', optional: false },
  { label: '教室', value: '请选择 (选填)', icon: 'home', optional: true },
]

const timeRows = [
  { label: '上课日期', value: '今天 10月24日', icon: 'calendar' },
  { label: '上课时间', value: '09:00 - 10:30', icon: 'clock' },
]

function goBack() {
  uni.navigateBack()
}

function chooseRow(label: string) {
  uni.showToast({ title: label, icon: 'none' })
}

function confirmCreate() {
  uni.showToast({ title: '已确认排课', icon: 'success' })
}
</script>

<template>
  <view class="create-page">
    <view class="topbar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="28" color="#3f4944" />
      </button>
      <view class="page-title">
        新增排课
      </view>
      <view class="top-spacer" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="section">
        <view class="section-label">
          排课模式
        </view>
        <scroll-view class="mode-scroll" scroll-x>
          <view class="mode-row">
            <button
              v-for="item in modes"
              :key="item.key"
              class="mode-card"
              :class="{ active: activeMode === item.key }"
              @click="activeMode = item.key"
            >
              <uni-icons
                :type="item.icon"
                size="30"
                :color="activeMode === item.key ? '#ffffff' : '#3f4944'"
              />
              <view class="mode-title">
                {{ item.title }}
              </view>
              <view class="mode-desc">
                {{ item.desc }}
              </view>
            </button>
          </view>
        </scroll-view>
      </view>

      <view class="section">
        <view class="section-label">
          基本信息
        </view>
        <view class="form-card">
          <button
            v-for="item in infoRows"
            :key="item.label"
            class="form-row"
            @click="chooseRow(item.label)"
          >
            <view class="row-left">
              <uni-icons :type="item.icon" size="24" color="#40655b" />
              <text>{{ item.label }}</text>
            </view>
            <view class="row-right" :class="{ placeholder: item.value.includes('请选择') }">
              <text>{{ item.value }}</text>
              <uni-icons type="right" size="18" color="#6f7974" />
            </view>
          </button>
        </view>
      </view>

      <view class="section">
        <view class="section-label">
          时间安排
        </view>
        <view class="form-card">
          <button
            v-for="item in timeRows"
            :key="item.label"
            class="form-row"
            @click="chooseRow(item.label)"
          >
            <view class="row-left">
              <uni-icons :type="item.icon" size="24" color="#40655b" />
              <text>{{ item.label }}</text>
            </view>
            <view class="row-right">
              <text>{{ item.value }}</text>
              <uni-icons type="right" size="18" color="#6f7974" />
            </view>
          </button>
        </view>
      </view>

      <view class="section">
        <view class="section-label">
          其他信息
        </view>
        <view class="note-card">
          <textarea class="note-area" placeholder="添加排课备注（选填）" placeholder-class="placeholder" />
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="confirm-btn" @click="confirmCreate">
        确认排课
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.create-page {
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
  font-weight: 700;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 32rpx 28rpx 150rpx;
}

.section {
  margin-bottom: 32rpx;
}

.section-label {
  padding: 0 4rpx;
  margin-bottom: 16rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #3f4944;
}

.mode-scroll {
  white-space: nowrap;
}

.mode-row {
  display: flex;
  gap: 24rpx;
  padding-bottom: 4rpx;
}

.mode-card {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: 300rpx;
  min-height: 188rpx;
  padding: 28rpx;
  margin: 0;
  text-align: left;
  color: #0f1d23;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.mode-card.active {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.mode-title {
  margin-top: 16rpx;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.25;
}

.mode-desc {
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.35;
  color: #3f4944;
}

.mode-card.active .mode-desc {
  color: rgba(255, 255, 255, 0.9);
}

.form-card,
.note-card {
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
  box-shadow: 0 3rpx 10rpx rgba(15, 29, 35, 0.03);
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 104rpx;
  padding: 0 28rpx;
  margin: 0;
  background: #ffffff;
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.35);
  border-radius: 0;
}

.form-row:last-child {
  border-bottom: 0;
}

.row-left,
.row-right {
  display: flex;
  align-items: center;
}

.row-left {
  gap: 18rpx;
  font-size: 28rpx;
  color: #0f1d23;
}

.row-right {
  gap: 6rpx;
  max-width: 360rpx;
  font-size: 27rpx;
  color: #0f1d23;
}

.row-right.placeholder {
  color: #6f7974;
}

.row-right text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-card {
  padding: 28rpx;
}

.note-area {
  width: 100%;
  height: 160rpx;
  font-size: 28rpx;
  line-height: 1.5;
  color: #0f1d23;
}

.placeholder {
  color: #6f7974;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  padding: 24rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.confirm-btn {
  width: 100%;
  height: 92rpx;
  padding: 0;
  margin: 0;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 92rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.back-btn::after,
.mode-card::after,
.form-row::after,
.confirm-btn::after {
  border: 0;
}
</style>
