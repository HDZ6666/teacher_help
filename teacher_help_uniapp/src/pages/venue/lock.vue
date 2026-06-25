<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'VenueLock',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '锁场',
  },
})

const venues = ['主报告厅A', '主报告厅B', '化学实验室101', '室内运动馆', '音乐教室C']
const venueIndex = ref(-1)
const dateStart = ref('')
const dateEnd = ref('')
const timeStart = ref('08:00')
const timeEnd = ref('17:00')
const repeat = ref<'none' | 'daily' | 'weekly'>('none')
const repeatOptions = [
  { key: 'none', label: '不重复' },
  { key: 'daily', label: '每天' },
  { key: 'weekly', label: '每周' },
] as const
const reasons = ['维护 / 维修', '深度清洁', '考试布置', '私人活动', '其他（在下方说明）']
const reasonIndex = ref(0)
const notes = ref('')

function goBack() {
  uni.navigateBack()
}
function onVenueChange(e: any) {
  venueIndex.value = Number(e.detail.value)
}
function onReasonChange(e: any) {
  reasonIndex.value = Number(e.detail.value)
}
function onConfirm() {
  if (venueIndex.value < 0) {
    uni.showToast({ title: '请选择场地', icon: 'none' })
    return
  }
  uni.showToast({ title: '已锁场', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.name) {
    const name = decodeURIComponent(query.name)
    const i = venues.indexOf(name)
    if (i >= 0)
      venueIndex.value = i
  }
})
</script>

<template>
  <view class="lock-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        锁场
      </text>
      <view class="icon-btn" />
    </view>

    <text class="intro">
      临时关闭场地的可预约状态，用于场地维护或私人活动。
    </text>

    <!-- 目标场地 -->
    <view class="card">
      <text class="field-label">
        目标场地
      </text>
      <picker class="picker" :range="venues" @change="onVenueChange">
        <view class="picker-inner">
          <text :class="{ ph: venueIndex < 0 }">
            {{ venueIndex < 0 ? '请选择场地...' : venues[venueIndex] }}
          </text>
          <uni-icons type="bottom" size="18" color="#3f4944" />
        </view>
      </picker>
    </view>

    <!-- 日期与时间 -->
    <view class="card">
      <view class="block">
        <text class="field-label">
          日期范围
        </text>
        <view class="range-row">
          <picker mode="date" class="range-item" :value="dateStart" @change="dateStart = $event.detail.value">
            <view class="range-inner">
              <uni-icons type="calendar" size="18" color="#3f4944" />
              <text :class="{ ph: !dateStart }">
                {{ dateStart || '开始' }}
              </text>
            </view>
          </picker>
          <text class="dash">
            —
          </text>
          <picker mode="date" class="range-item" :value="dateEnd" @change="dateEnd = $event.detail.value">
            <view class="range-inner">
              <uni-icons type="calendar" size="18" color="#3f4944" />
              <text :class="{ ph: !dateEnd }">
                {{ dateEnd || '结束' }}
              </text>
            </view>
          </picker>
        </view>
      </view>

      <view class="block">
        <text class="field-label">
          时间段
        </text>
        <view class="range-row">
          <picker mode="time" class="range-item" :value="timeStart" @change="timeStart = $event.detail.value">
            <view class="range-inner">
              <uni-icons type="loop" size="18" color="#3f4944" />
              <text>{{ timeStart }}</text>
            </view>
          </picker>
          <text class="dash">
            —
          </text>
          <picker mode="time" class="range-item" :value="timeEnd" @change="timeEnd = $event.detail.value">
            <view class="range-inner">
              <uni-icons type="loop" size="18" color="#3f4944" />
              <text>{{ timeEnd }}</text>
            </view>
          </picker>
        </view>
      </view>

      <view class="block bordered">
        <text class="field-label">
          重复方式
        </text>
        <view class="radio-row">
          <view
            v-for="r in repeatOptions"
            :key="r.key"
            class="radio"
            @click="repeat = r.key"
          >
            <view class="dot" :class="{ on: repeat === r.key }">
              <view v-if="repeat === r.key" class="dot-in" />
            </view>
            <text>{{ r.label }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 锁场原因与备注 -->
    <view class="card">
      <view class="block">
        <text class="field-label">
          锁场原因
        </text>
        <picker class="picker" :range="reasons" :value="reasonIndex" @change="onReasonChange">
          <view class="picker-inner">
            <text>{{ reasons[reasonIndex] }}</text>
            <uni-icons type="bottom" size="18" color="#3f4944" />
          </view>
        </picker>
      </view>
      <view class="block">
        <text class="field-label">
          补充说明
        </text>
        <textarea v-model="notes" class="field-area" placeholder="填写必要的说明（如：维修内容、负责人等）..." />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onConfirm">
        <uni-icons type="locked" size="20" color="#ffffff" />
        <text>确认锁场</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.lock-page {
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
  font-size: 34rpx;
  font-weight: 600;
  color: #005842;
}

.intro {
  display: block;
  margin-top: 28rpx;
  font-size: 24rpx;
  line-height: 36rpx;
  color: #3f4944;
}

.card {
  margin-top: 20rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.block {
  margin-top: 26rpx;
}

.block:first-child {
  margin-top: 0;
}

.block.bordered {
  padding-top: 26rpx;
  border-top: 1rpx solid #d6e5ed;
}

.field-label {
  display: block;
  margin-bottom: 14rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.picker {
  width: 100%;
}

.picker-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.ph {
  color: #9aa5aa;
}

.range-row {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.range-item {
  flex: 1;
}

.range-inner {
  display: flex;
  gap: 10rpx;
  align-items: center;
  box-sizing: border-box;
  height: 84rpx;
  padding: 0 18rpx;
  font-size: 26rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.dash {
  color: #3f4944;
}

.radio-row {
  display: flex;
  gap: 40rpx;
}

.radio {
  display: flex;
  gap: 12rpx;
  align-items: center;
  font-size: 28rpx;
}

.dot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #6f7974;
  border-radius: 50%;
}

.dot.on {
  border-color: #1f7159;
}

.dot-in {
  width: 18rpx;
  height: 18rpx;
  background: #1f7159;
  border-radius: 50%;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #f3faff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn {
  display: flex;
  gap: 12rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
