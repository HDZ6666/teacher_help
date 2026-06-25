<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'

defineOptions({
  name: 'WrongAnalyzing',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: 'AI 分析中',
  },
})

const steps = [
  { label: '正在识别题目', state: 'done' },
  { label: '正在分析解法', state: 'active' },
  { label: '正在生成讲解', state: 'wait' },
]

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

onLoad(() => {})
</script>

<template>
  <view class="analyzing-page">
    <view class="illustration-card">
      <view class="paper-line short" />
      <view class="paper-line long" />
      <view class="paper-line mid" />
      <view class="scan-badge">
        <view class="scan-corner tl" />
        <view class="scan-corner tr" />
        <view class="scan-corner bl" />
        <view class="scan-corner br" />
        <view class="scan-doc">
          <view />
          <view />
          <view />
        </view>
      </view>
      <view class="answer-box">
        Σ
      </view>
    </view>

    <view class="step-list">
      <view
        v-for="(step, index) in steps"
        :key="step.label"
        class="step-row"
        :class="step.state"
      >
        <view class="step-rail" :class="{ last: index === steps.length - 1 }" />
        <view class="step-dot">
          <uni-icons v-if="step.state === 'done'" type="checkmarkempty" size="20" color="#ffffff" />
          <view v-else-if="step.state === 'active'" class="active-dot" />
          <view v-else class="wait-dot" />
        </view>
        <view class="step-label">
          {{ step.label }}
        </view>
      </view>
    </view>

    <view class="hint-text">
      正在为您生成深度解析，您可以先处理其他事务，完成后将收到提醒。
    </view>

    <view class="bottom-actions">
      <button class="primary-btn" @click="backgroundRun">
        后台处理
      </button>
      <button class="outline-btn" @click="cancelAnalyze">
        取消分析
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.analyzing-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 296rpx 40rpx 210rpx;
  color: #0f1d23;
  background: #f3faff;
}

.illustration-card {
  position: relative;
  width: 506rpx;
  height: 286rpx;
  margin: 0 auto;
  overflow: hidden;
  background: linear-gradient(180deg, #f1fff8 0%, #ffffff 100%);
  border: 2rpx solid #bec9c3;
  border-radius: 18rpx;
  box-shadow: 0 4rpx 10rpx rgba(15, 29, 35, 0.08);
}

.paper-line {
  position: absolute;
  left: 30rpx;
  height: 20rpx;
  background: #d8e8e3;
  border-radius: 8rpx;
}

.paper-line.short {
  top: 30rpx;
  width: 150rpx;
}

.paper-line.long {
  top: 74rpx;
  width: 446rpx;
}

.paper-line.mid {
  top: 118rpx;
  width: 372rpx;
  background: #dddddd;
}

.scan-badge {
  position: absolute;
  top: 86rpx;
  left: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 126rpx;
  height: 126rpx;
  background: #ffffff;
  border-radius: 50%;
  box-shadow: 0 6rpx 18rpx rgba(15, 29, 35, 0.08);
  transform: translateX(-50%);
}

.scan-corner {
  position: absolute;
  width: 18rpx;
  height: 18rpx;
  border-color: #005842;
}

.scan-corner.tl {
  top: 42rpx;
  left: 42rpx;
  border-top: 4rpx solid #005842;
  border-left: 4rpx solid #005842;
}

.scan-corner.tr {
  top: 42rpx;
  right: 42rpx;
  border-top: 4rpx solid #005842;
  border-right: 4rpx solid #005842;
}

.scan-corner.bl {
  bottom: 42rpx;
  left: 42rpx;
  border-bottom: 4rpx solid #005842;
  border-left: 4rpx solid #005842;
}

.scan-corner.br {
  right: 42rpx;
  bottom: 42rpx;
  border-right: 4rpx solid #005842;
  border-bottom: 4rpx solid #005842;
}

.scan-doc {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  width: 36rpx;
  height: 46rpx;
  padding: 8rpx 6rpx;
  border: 4rpx solid #005842;
  border-radius: 4rpx;
}

.scan-doc view {
  height: 4rpx;
  background: #005842;
  border-radius: 999rpx;
}

.answer-box {
  position: absolute;
  right: 30rpx;
  bottom: 30rpx;
  left: 30rpx;
  height: 78rpx;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 78rpx;
  color: #d0d6d4;
  text-align: center;
  border: 4rpx dashed #d7ddda;
  border-radius: 14rpx;
}

.step-list {
  width: 320rpx;
  margin: 76rpx auto 0;
}

.step-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 34rpx;
  min-height: 102rpx;
}

.step-rail {
  position: absolute;
  top: 48rpx;
  left: 20rpx;
  width: 4rpx;
  height: 100rpx;
  background: #bec9c3;
}

.step-row.done .step-rail {
  background: #1f7159;
}

.step-rail.last {
  display: none;
}

.step-dot {
  z-index: 1;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 42rpx;
  height: 42rpx;
  background: #e7f6fe;
  border-radius: 50%;
}

.step-row.done .step-dot {
  background: #005842;
}

.step-row.active .step-dot {
  background: #e7f6fe;
  border: 6rpx solid #005842;
}

.step-row.wait .step-dot {
  border: 4rpx solid #bec9c3;
}

.active-dot {
  width: 14rpx;
  height: 14rpx;
  background: #005842;
  border-radius: 50%;
}

.wait-dot {
  width: 12rpx;
  height: 12rpx;
  background: #bec9c3;
  border-radius: 50%;
}

.step-label {
  font-size: 34rpx;
  font-weight: 800;
  color: #8a9691;
  white-space: nowrap;
}

.step-row.done .step-label,
.step-row.active .step-label {
  color: #005842;
}

.hint-text {
  margin-top: 38rpx;
  font-size: 29rpx;
  line-height: 1.7;
  color: #0f1d23;
  text-align: center;
}

.bottom-actions {
  position: fixed;
  right: 40rpx;
  bottom: calc(48rpx + env(safe-area-inset-bottom));
  left: 40rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.primary-btn,
.outline-btn {
  height: 80rpx;
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 800;
  line-height: 80rpx;
  border-radius: 14rpx;
}

.primary-btn::after,
.outline-btn::after {
  border: 0;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}

.outline-btn {
  color: #1f7159;
  background: #f3faff;
  border: 2rpx solid #1f7159;
}
</style>
