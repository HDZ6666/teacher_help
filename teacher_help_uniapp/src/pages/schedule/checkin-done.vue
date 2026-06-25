<script lang="ts" setup>
defineOptions({
  name: 'CheckinDone',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '点名完成',
  },
})

const stats = [
  { label: '应到人数', value: 15, icon: 'person', tone: 'normal' },
  { label: '实到人数', value: 13, icon: 'checkmarkempty', tone: 'green' },
  { label: '异常人数', value: 2, icon: 'info', tone: 'red' },
]

function writeComment() {
  uni.navigateTo({ url: '/pages/schedule/comment?id=1' })
}

function viewRecord() {
  uni.navigateTo({ url: '/pages/schedule/course-detail?id=1' })
}

function nextCheckin() {
  uni.redirectTo({ url: '/pages/schedule/detail?id=2' })
}

function backToday() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<template>
  <view class="done-page">
    <view class="success-area">
      <view class="success-circle">
        <uni-icons type="checkmarkempty" size="66" color="#00684f" />
      </view>
      <view class="success-title">
        点名已完成
      </view>
      <view class="success-time">
        提交时间: 2023-10-27 14:30
      </view>
    </view>

    <view class="stats-card">
      <view class="card-title">
        本次点名统计
      </view>
      <view v-for="item in stats" :key="item.label" class="stat-row">
        <view class="stat-name">
          <uni-icons
            :type="item.icon"
            size="26"
            :color="item.tone === 'red' ? '#ba1a1a' : '#00684f'"
          />
          <text>{{ item.label }}</text>
        </view>
        <text class="stat-value" :class="item.tone">
          {{ item.value }}
        </text>
      </view>
    </view>

    <view class="action-stack">
      <button class="action-btn primary" @click="writeComment">
        <uni-icons type="compose" size="26" color="#ffffff" />
        <text>写课后点评</text>
      </button>
      <button class="action-btn outline" @click="viewRecord">
        <uni-icons type="loop" size="26" color="#1f7159" />
        <text>查看上课记录</text>
      </button>
      <button class="action-btn soft" @click="nextCheckin">
        <text class="play-icon">▸</text>
        <text>继续点下一节</text>
      </button>
      <button class="back-btn" @click="backToday">
        <uni-icons type="left" size="30" color="#34433d" />
        <text>返回今日</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.done-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 146rpx 40rpx 56rpx;
  color: #0f1d23;
  background: #f3faff;
}

.success-area {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.success-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 176rpx;
  height: 176rpx;
  background: #e7f6fe;
  border-radius: 50%;
  box-shadow: 0 6rpx 12rpx rgba(31, 45, 51, 0.04);
}

.success-title {
  margin-top: 64rpx;
  font-size: 44rpx;
  font-weight: 700;
  letter-spacing: 0;
}

.success-time {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: #3f4944;
}

.stats-card {
  margin-top: 78rpx;
  padding: 34rpx 32rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 10rpx rgba(31, 45, 51, 0.08);
}

.card-title {
  margin-bottom: 22rpx;
  font-size: 33rpx;
  font-weight: 700;
}

.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 94rpx;
  border-bottom: 1rpx solid #bec9c3;
}

.stat-row:last-child {
  border-bottom: 0;
}

.stat-name {
  display: flex;
  align-items: center;
  gap: 20rpx;
  font-size: 29rpx;
  color: #3f4944;
}

.stat-value {
  font-size: 38rpx;
  font-weight: 700;
  color: #0f1d23;
}

.stat-value.green {
  color: #00684f;
}

.stat-value.red {
  color: #ba1a1a;
}

.action-stack {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-top: 312rpx;
}

.action-btn,
.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18rpx;
  padding: 0;
  margin: 0;
  line-height: 1;
}

.action-btn::after,
.back-btn::after {
  border: 0;
}

.action-btn {
  height: 92rpx;
  font-size: 30rpx;
  font-weight: 700;
  border-radius: 14rpx;
}

.action-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.action-btn.outline {
  color: #1f7159;
  background: #ffffff;
  border: 2rpx solid #1f7159;
}

.action-btn.soft {
  color: #34433d;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
}

.play-icon {
  font-size: 34rpx;
  color: #34433d;
}

.back-btn {
  height: 80rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: #34433d;
  background: transparent;
}
</style>
