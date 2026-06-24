<script lang="ts" setup>
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

defineOptions({
  name: 'WrongAnalyzing',
})
definePage({
  style: {
    navigationBarTitleText: 'AI 分析中',
  },
})

const steps = [
  { key: 'upload', label: '上传图片' },
  { key: 'ocr', label: 'OCR 识别题干' },
  { key: 'understand', label: '题目理解' },
  { key: 'parse', label: '生成解析' },
  { key: 'reason', label: '整理错因' },
]

const currentStep = ref(0)
let timer: any = null

const progress = computed(() => Math.min(Math.round((currentStep.value / steps.length) * 100), 100))

function stepState(index: number) {
  if (index < currentStep.value)
    return 'done'
  if (index === currentStep.value)
    return 'active'
  return 'wait'
}

function runMock() {
  timer = setInterval(() => {
    if (currentStep.value >= steps.length) {
      clearInterval(timer)
      timer = null
      // 分析完成 → 跳错题详情
      uni.redirectTo({ url: '/pages/wrong-question/detail?id=1&from=analyze' })
      return
    }
    currentStep.value += 1
  }, 1200)
}

function backgroundRun() {
  uni.switchTab({ url: '/pages/wrong-question/index' })
}

function cancelAnalyze() {
  uni.showModal({
    title: '取消分析',
    content: '取消后本次识别任务将终止，已上传图片保留。确认取消？',
    confirmText: '确认取消',
    confirmColor: '#c0392b',
    success: (res) => {
      if (res.confirm)
        uni.navigateBack()
    },
  })
}

onLoad(() => {
  runMock()
})

onUnload(() => {
  if (timer)
    clearInterval(timer)
})
</script>

<template>
  <view class="ana-page">
    <view class="ana-card">
      <view class="thumb">
        <uni-icons type="image" size="44" color="#c2cbce" />
      </view>
      <view class="ana-ring">
        <text class="ring-num">{{ progress }}<text class="ring-unit">%</text></text>
      </view>
      <view class="ana-title">
        AI 正在分析错题
      </view>
      <view class="ana-sub">
        通常 5 到 15 秒，请稍候
      </view>
    </view>

    <view class="step-card">
      <view v-for="(s, idx) in steps" :key="s.key" class="step-row" :class="stepState(idx)">
        <view class="step-dot">
          <uni-icons v-if="stepState(idx) === 'done'" type="checkmarkempty" size="14" color="#ffffff" />
          <view v-else-if="stepState(idx) === 'active'" class="dot-pulse" />
        </view>
        <text class="step-label">
          {{ s.label }}
        </text>
        <text v-if="stepState(idx) === 'done'" class="step-tag">
          完成
        </text>
        <text v-else-if="stepState(idx) === 'active'" class="step-tag ing">
          进行中
        </text>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="backgroundRun">
        后台处理
      </button>
      <button class="danger-btn" @click="cancelAnalyze">
        取消分析
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ana-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 40rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.ana-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50rpx 30rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 18rpx;
}

.thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 160rpx;
  height: 160rpx;
  background: #f1f4f2;
  border-radius: 16rpx;
}

.ana-ring {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 150rpx;
  height: 150rpx;
  margin-top: 34rpx;
  border: 8rpx solid #e6f4ee;
  border-top-color: #1f7159;
  border-radius: 50%;
}

.ring-num {
  font-size: 44rpx;
  font-weight: 700;
  color: #1f7159;
}

.ring-unit {
  font-size: 24rpx;
}

.ana-title {
  margin-top: 30rpx;
  font-size: 32rpx;
  font-weight: 700;
}

.ana-sub {
  margin-top: 12rpx;
  font-size: 25rpx;
  color: #718088;
}

.step-card {
  margin-top: 22rpx;
  padding: 12rpx 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.step-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  height: 92rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.step-row:last-child {
  border-bottom: 0;
}

.step-dot {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  background: #eef2f0;
  border-radius: 50%;
}

.step-row.done .step-dot {
  background: #1f7159;
}

.step-row.active .step-dot {
  background: #dff4eb;
}

.dot-pulse {
  width: 16rpx;
  height: 16rpx;
  background: #1f7159;
  border-radius: 50%;
}

.step-label {
  flex: 1;
  font-size: 27rpx;
  color: #9aa5aa;
}

.step-row.done .step-label,
.step-row.active .step-label {
  color: #1f2d33;
}

.step-tag {
  font-size: 22rpx;
  color: #227253;
}

.step-tag.ing {
  color: #1f7159;
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
.danger-btn {
  flex: 1;
  margin: 0;
  font-size: 28rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #e6f4ee;
}

.danger-btn {
  color: #a4423a;
  background: #ffeceb;
}

.ghost-btn::after,
.danger-btn::after {
  border: 0;
}
</style>
