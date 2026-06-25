<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'MemberCardHoldDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '持卡详情',
  },
})

const holdId = ref('')
const hold = ref({
  status: '有效',
  student: '张三',
  cardName: '10次数学精品课卡',
  rest: '8',
  restUnit: '次',
  validTo: '2024-12-31',
})

interface TimelineItem {
  id: number
  time: string
  badge: string
  badgeType: 'minus' | 'system' | 'plus'
  title: string
  titleAccent?: boolean
  desc?: string
  descIcon?: string
  dotType: 'primary' | 'tertiary'
}

const timeline = ref<TimelineItem[]>([
  { id: 1, time: '2023-10-24 14:30', badge: '-1次', badgeType: 'minus', title: '消耗 1 次', desc: '课程: 初中数学强化', descIcon: 'staff', dotType: 'primary' },
  { id: 2, time: '2023-10-15 16:00', badge: '-1次', badgeType: 'minus', title: '消耗 1 次', desc: '课程: 初中数学强化', descIcon: 'staff', dotType: 'primary' },
  { id: 3, time: '2023-10-01 09:00', badge: '系统', badgeType: 'system', title: '生效', titleAccent: true, dotType: 'tertiary' },
  { id: 4, time: '2023-10-01 08:55', badge: '+10次', badgeType: 'plus', title: '开卡', desc: '实收 ¥1,200', descIcon: 'wallet', dotType: 'primary' },
])

function goBack() {
  uni.navigateBack()
}
function onRenew() {
  uni.showToast({ title: '续费', icon: 'none' })
}

onLoad((query) => {
  holdId.value = query?.id || ''
})
</script>

<template>
  <view class="hd-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        持卡详情
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 卡片概要 -->
    <view class="summary-card">
      <view class="blob blob-1" />
      <view class="blob blob-2" />
      <view class="summary-head">
        <view class="sh-left">
          <view class="sh-tags">
            <text class="valid-tag">
              {{ hold.status }}
            </text>
            <text class="sh-student">
              {{ hold.student }}
            </text>
          </view>
          <text class="sh-name">
            {{ hold.cardName }}
          </text>
        </view>
        <view class="sh-rest">
          <text class="rest-label">
            剩余
          </text>
          <view class="rest-num">
            <text class="rest-value">
              {{ hold.rest }}
            </text>
            <text class="rest-unit">
              {{ hold.restUnit }}
            </text>
          </view>
        </view>
      </view>
      <view class="summary-foot">
        <text class="sf-label">
          有效期至
        </text>
        <text class="sf-value">
          {{ hold.validTo }}
        </text>
      </view>
    </view>

    <!-- 操作记录 -->
    <view class="card">
      <view class="card-title">
        <uni-icons type="loop" size="20" color="#005842" />
        <text>操作记录</text>
      </view>
      <view class="timeline">
        <view
          v-for="item in timeline"
          :key="item.id"
          class="tl-item"
        >
          <view class="tl-dot" :class="item.dotType" />
          <view class="tl-body">
            <view class="tl-row">
              <text class="tl-time">
                {{ item.time }}
              </text>
              <text class="tl-badge" :class="item.badgeType">
                {{ item.badge }}
              </text>
            </view>
            <text class="tl-title" :class="{ accent: item.titleAccent }">
              {{ item.title }}
            </text>
            <view v-if="item.desc" class="tl-desc">
              <uni-icons :type="item.descIcon" size="14" color="#3f4944" />
              <text>{{ item.desc }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onRenew">
        <text>续费</text>
        <uni-icons type="loop" size="18" color="#ffffff" />
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.hd-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 170rpx;
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
  margin: 0 -28rpx;
  padding: 0 20rpx;
  background: #ffffff;
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
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #005842;
  text-align: center;
}

.summary-card {
  position: relative;
  margin-top: 24rpx;
  padding: 36rpx;
  overflow: hidden;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
}

.blob {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.blob-1 {
  top: -60rpx;
  right: -60rpx;
  width: 220rpx;
  height: 220rpx;
  background: #a4f2d4;
}

.blob-2 {
  bottom: -50rpx;
  left: -50rpx;
  width: 170rpx;
  height: 170rpx;
  background: #8cf7c7;
}

.summary-head {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.sh-left {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.sh-tags {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.valid-tag {
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  color: #227253;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.sh-student {
  font-size: 24rpx;
  color: #88d6b9;
}

.sh-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #ffffff;
}

.sh-rest {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.rest-label {
  font-size: 24rpx;
  color: #88d6b9;
}

.rest-num {
  display: flex;
  align-items: baseline;
  gap: 6rpx;
}

.rest-value {
  font-size: 64rpx;
  font-weight: 700;
  line-height: 1;
  color: #8cf7c7;
}

.rest-unit {
  font-size: 24rpx;
  color: #88d6b9;
}

.summary-foot {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  margin-top: 30rpx;
  padding-top: 28rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.1);
}

.sf-label {
  font-size: 22rpx;
  color: #88d6b9;
}

.sf-value {
  font-size: 26rpx;
  color: #ffffff;
}

.card {
  margin-top: 24rpx;
  padding: 36rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 18rpx;
}

.card-title {
  display: flex;
  gap: 10rpx;
  align-items: center;
  margin-bottom: 40rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: #005842;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 44rpx;
  padding-left: 36rpx;
  border-left: 4rpx solid #dbebf3;
}

.tl-item {
  position: relative;
}

.tl-dot {
  position: absolute;
  top: 6rpx;
  left: -50rpx;
  z-index: 2;
  width: 26rpx;
  height: 26rpx;
  background: #ffffff;
  border: 4rpx solid #1f7159;
  border-radius: 50%;
}

.tl-dot.tertiary {
  border-color: #007351;
}

.tl-body {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.tl-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.tl-time {
  font-size: 24rpx;
  color: #3f4944;
}

.tl-badge {
  padding: 2rpx 14rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.tl-badge.minus {
  color: #ba1a1a;
  background: #ffdad6;
}

.tl-badge.system {
  color: #00583d;
  background: #e9f6ef;
}

.tl-badge.plus {
  color: #005842;
  background: #c2ebde;
}

.tl-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #0f1d23;
}

.tl-title.accent {
  color: #007351;
}

.tl-desc {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 24rpx;
  color: #3f4944;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn {
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 92rpx;
  margin: 0;
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
