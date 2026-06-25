<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ClassUpgrade',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '升班/结业',
  },
})

const activeAction = ref('upgrade')

const students = [
  { name: '张子涵', lessons: 2, selected: true },
  { name: '李语桐', lessons: 0, selected: true },
  { name: '王浩宇', lessons: 1, selected: true },
]

function goBack() {
  uni.navigateBack()
}

function confirm() {
  uni.showToast({ title: activeAction.value === 'upgrade' ? '已确认升班' : '已确认结业', icon: 'success' })
}
</script>

<template>
  <view class="upgrade-page">
    <view class="topbar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#1f7159" />
      </button>
      <text class="page-title">
        学员结课与升班
      </text>
      <view class="nav-space" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="step-card">
        <view class="step-item active">
          <text class="step-no">1</text>
          <text>选择学员</text>
        </view>
        <view class="step-line" />
        <view class="step-item">
          <text class="step-no">2</text>
          <text>操作设置</text>
        </view>
      </view>

      <view class="student-card">
        <view class="section-head">
          <text>选择学员 <text class="muted">已选 3 人</text></text>
          <button>全选</button>
        </view>
        <view v-for="item in students" :key="item.name" class="student-row">
          <view class="check" :class="{ active: item.selected }">
            <uni-icons v-if="item.selected" type="checkmarkempty" size="18" color="#ffffff" />
          </view>
          <view class="avatar">
            {{ item.name.slice(0, 1) }}
          </view>
          <view class="student-main">
            <text class="name">
              {{ item.name }}
            </text>
            <text class="lessons">
              剩余课时：{{ item.lessons }}
            </text>
          </view>
        </view>
        <button class="more-btn">
          展开更多
        </button>
      </view>

      <view class="action-card">
        <view class="action-tabs">
          <button class="action-tab" :class="{ active: activeAction === 'upgrade' }" @click="activeAction = 'upgrade'">
            学员升班
          </button>
          <button class="action-tab" :class="{ active: activeAction === 'graduate' }" @click="activeAction = 'graduate'">
            学员结业
          </button>
        </view>

        <view v-if="activeAction === 'upgrade'" class="action-content">
          <view class="field">
            <text class="label">
              目标班级 <text class="required">*</text>
            </text>
            <view class="select-row">
              <text>请选择升入的班级</text>
              <uni-icons type="right" size="16" color="#74828a" />
            </view>
          </view>
          <view class="field">
            <text class="label">
              课时结转方式
            </text>
            <view class="radio-row">
              <text class="radio active">按比例折算</text>
              <text class="radio">1:1 平移</text>
            </view>
          </view>
          <view class="notice">
            <uni-icons type="info" size="18" color="#40655b" />
            <text>升班后，原班级剩余课时将按设置结转至新班级，学员将从原班级移出。</text>
          </view>
        </view>

        <view v-else class="action-content">
          <view class="field">
            <text class="label">
              结业日期 <text class="required">*</text>
            </text>
            <input class="input" value="2026-07-15" disabled>
          </view>
          <view class="field">
            <text class="label">
              结业评语
            </text>
            <textarea class="textarea" placeholder="记录学员学习成果..." />
          </view>
          <view class="switch-row">
            <text>结清剩余课时</text>
            <switch checked color="#1f7159" style="transform: scale(0.84)" />
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="confirm">
        {{ activeAction === 'upgrade' ? '确认升班' : '确认结业' }}
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.upgrade-page {
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
  height: 112rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #e1e8e4;
}

.nav-btn,
.nav-space {
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.page-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #1f7159;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 28rpx 28rpx 148rpx;
}

.step-card,
.student-card,
.action-card {
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
  box-shadow: 0 6rpx 18rpx rgba(15, 29, 35, 0.04);
}

.step-card {
  display: flex;
  align-items: center;
  padding: 18rpx 34rpx;
}

.step-item {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 8rpx;
  font-size: 22rpx;
  color: #74828a;
}

.step-item.active {
  color: #0f1d23;
}

.step-no {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 62rpx;
  height: 62rpx;
  font-size: 24rpx;
  font-weight: 800;
  color: #64737b;
  background: #eef2f0;
  border-radius: 50%;
}

.step-item.active .step-no {
  color: #ffffff;
  background: #1f7159;
}

.step-line {
  flex: 1;
  height: 2rpx;
  margin: 0 22rpx;
  background: #1f7159;
}

.student-card,
.action-card {
  margin-top: 24rpx;
  overflow: hidden;
}

.section-head {
  display: flex;
  justify-content: space-between;
  padding: 28rpx 28rpx 10rpx;
  font-size: 30rpx;
  font-weight: 800;
}

.section-head button {
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  color: #1f7159;
  background: transparent;
}

.muted {
  margin-left: 12rpx;
  font-size: 23rpx;
  font-weight: 500;
  color: #74828a;
}

.student-row {
  display: flex;
  align-items: center;
  padding: 20rpx 28rpx;
}

.check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38rpx;
  height: 38rpx;
  margin-right: 18rpx;
  border: 3rpx solid #b8c4be;
  border-radius: 10rpx;
}

.check.active {
  background: #1f7159;
  border-color: #1f7159;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  margin-right: 18rpx;
  font-size: 28rpx;
  font-weight: 800;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 50%;
}

.student-main {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.name {
  font-size: 28rpx;
  font-weight: 700;
}

.lessons {
  font-size: 23rpx;
  color: #74828a;
}

.more-btn {
  width: 100%;
  height: 76rpx;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  color: #74828a;
  background: transparent;
}

.action-tabs {
  display: flex;
  border-bottom: 1rpx solid #edf1ef;
}

.action-tab {
  flex: 1;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 30rpx;
  font-weight: 800;
  color: #74828a;
  background: transparent;
  border-radius: 0;
}

.action-tab.active {
  color: #1f7159;
  background: #ffffff;
  border-bottom: 4rpx solid #1f7159;
}

.action-content {
  padding: 28rpx;
}

.field {
  margin-bottom: 24rpx;
}

.label {
  display: block;
  margin-bottom: 14rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #64737b;
}

.required {
  color: #a4423a;
}

.select-row,
.input,
.textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 0 22rpx;
  font-size: 27rpx;
  color: #0f1d23;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 14rpx;
}

.select-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  color: #74828a;
}

.input {
  height: 88rpx;
}

.textarea {
  min-height: 140rpx;
  padding-top: 20rpx;
}

.radio-row {
  display: flex;
  gap: 18rpx;
}

.radio {
  padding: 16rpx 22rpx;
  font-size: 25rpx;
  color: #64737b;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 999rpx;
}

.radio.active {
  color: #1f7159;
  background: #e6f4ee;
  border-color: #b8dccc;
}

.notice {
  display: flex;
  gap: 12rpx;
  padding: 20rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: #40655b;
  background: #eef7f3;
  border-radius: 14rpx;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 88rpx;
  padding: 0 20rpx;
  font-size: 27rpx;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 14rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  padding: 20rpx 28rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #e7ece9;
}

.primary-btn {
  width: 100%;
  height: 92rpx;
  padding: 0;
  margin: 0;
  font-size: 30rpx;
  font-weight: 800;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}
</style>
