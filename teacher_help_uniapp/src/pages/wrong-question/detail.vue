<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongDetail',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '错题详情',
  },
})

const mastered = ref(false)

const detail = {
  question:
    '已知在平面直角坐标系中，抛物线 y = ax² + bx + c 与 x 轴交于 A(-1, 0) 和 B(3, 0) 两点，且过点 C(0, -3)。求该抛物线的解析式并确定其顶点坐标。',
  answer: 'y = x² - 2x - 3，顶点坐标 (1, -4)',
  steps: [
    '因为抛物线交 x 轴于 A(-1, 0)、B(3, 0)，可设交点式方程为 y = a(x + 1)(x - 3)。',
    '将点 C(0, -3) 代入方程，得 -3 = a(0 + 1)(0 - 3)，解得 a = 1。',
    '展开方程得 y = x² - 2x - 3。配方得 y = (x - 1)² - 4，因此顶点坐标为 (1, -4)。',
  ],
  mistakeTitle: '公式混淆',
  mistake:
    '在求抛物线解析式时，未能灵活应用交点式，而是使用一般式列三元一次方程组，导致计算繁琐且在计算 a 的值时出现符号错误。',
  points: ['二次函数解析式', '交点式方程', '配方法求顶点'],
}

function goBack() {
  uni.navigateBack()
}

function openMore() {
  uni.showToast({ title: '更多操作', icon: 'none' })
}

function zoomImage() {
  uni.showToast({ title: '查看题目原图', icon: 'none' })
}

function markMastered() {
  mastered.value = true
  uni.showToast({ title: '已标为掌握', icon: 'success' })
}

function editParse() {
  uni.navigateTo({ url: '/pages/wrong-question/edit?id=1' })
}

function shareToParent() {
  uni.showToast({ title: '已生成家长分享卡片', icon: 'none' })
}

function openPractice() {
  uni.showToast({ title: '生成相似题训练', icon: 'none' })
}

function openVideo() {
  uni.showToast({ title: '打开视频讲解', icon: 'none' })
}
</script>

<template>
  <view class="detail-page">
    <view class="top-bar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="30" color="#0f1d23" />
      </button>
      <view class="top-title">
        错题详情
      </view>
      <button class="nav-btn right" @click="openMore">
        <uni-icons type="more-filled" size="34" color="#0f1d23" />
      </button>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="photo-card" @click="zoomImage">
        <view class="paper-bg">
          <view class="paper-head" />
          <view class="paper-line long" />
          <view class="paper-line mid" />
          <view class="paper-line short" />
          <view class="math-row">
            y = ax² + bx + c
          </view>
          <view class="graph">
            <view class="axis-x" />
            <view class="axis-y" />
            <view class="curve one" />
            <view class="curve two" />
          </view>
        </view>
        <view class="photo-mask" />
        <button class="zoom-btn" @click.stop="zoomImage">
          <uni-icons type="search" size="22" color="#1f7159" />
        </button>
      </view>

      <view class="section-card question-card">
        <view class="left-rail primary" />
        <view class="section-title primary">
          <uni-icons type="paperclip" size="22" color="#1f7159" />
          <text>题目文本</text>
        </view>
        <view class="question-text">
          {{ detail.question }}
        </view>
      </view>

      <view class="section-card">
        <view class="section-title tertiary">
          <uni-icons type="checkbox-filled" size="22" color="#007351" />
          <text>标准答案</text>
        </view>
        <view class="answer-box">
          {{ detail.answer }}
        </view>
      </view>

      <view class="section-card">
        <view class="section-title secondary">
          <uni-icons type="list" size="22" color="#40655b" />
          <text>解题步骤</text>
        </view>
        <view class="step-list">
          <view
            v-for="(step, index) in detail.steps"
            :key="step"
            class="step-row"
          >
            <view class="step-rail" :class="{ last: index === detail.steps.length - 1 }" />
            <view class="step-no">
              {{ index + 1 }}
            </view>
            <view class="step-text">
              {{ step }}
            </view>
          </view>
        </view>
      </view>

      <view class="section-card error-card">
        <view class="left-rail error" />
        <view class="section-title error">
          <uni-icons type="info-filled" size="22" color="#ba1a1a" />
          <text>错因分析</text>
        </view>
        <view class="mistake-box">
          <view class="mistake-icon">
            !
          </view>
          <view class="mistake-content">
            <view class="mistake-title">
              {{ detail.mistakeTitle }}
            </view>
            <view class="mistake-text">
              {{ detail.mistake }}
            </view>
          </view>
        </view>
      </view>

      <view class="section-card">
        <view class="section-title primary">
          <uni-icons type="tag-filled" size="22" color="#1f7159" />
          <text>核心知识点</text>
        </view>
        <view class="point-row">
          <view
            v-for="point in detail.points"
            :key="point"
            class="point-chip"
          >
            <uni-icons type="compose" size="18" color="#1f7159" />
            <text>{{ point }}</text>
          </view>
        </view>
      </view>

      <view class="section-card practice-card">
        <view class="section-title primary">
          <uni-icons type="fire-filled" size="22" color="#1f7159" />
          <text>举一反三</text>
        </view>
        <button class="practice-row" @click="openPractice">
          <view>
            <view class="practice-title">
              相似题型训练（3题）
            </view>
            <view class="practice-desc">
              巩固交点式求解析式的方法
            </view>
          </view>
          <uni-icons type="right" size="22" color="#1f7159" />
        </button>
        <button class="practice-row" @click="openVideo">
          <view>
            <view class="practice-title">
              视频讲解微课
            </view>
            <view class="practice-desc">
              二次函数的三种表达形式对比
            </view>
          </view>
          <uni-icons type="videocam-filled" size="24" color="#1f7159" />
        </button>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="master-btn" :class="{ done: mastered }" @click="markMastered">
        <uni-icons type="checkmarkempty" size="26" color="#ffffff" />
        <text>{{ mastered ? '已掌握' : '标为已掌握' }}</text>
      </button>
      <view class="secondary-actions">
        <button class="secondary-btn" @click="editParse">
          <uni-icons type="compose" size="24" color="#0f1d23" />
          <text>编辑解析</text>
        </button>
        <button class="secondary-btn share" @click="shareToParent">
          <uni-icons type="redo" size="24" color="#1f7159" />
          <text>分享给家长</text>
        </button>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f3faff;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  padding: 0 28rpx;
  background: rgba(243, 250, 255, 0.94);
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.5);
}

.top-title {
  position: absolute;
  left: 50%;
  font-size: 34rpx;
  font-weight: 700;
  transform: translateX(-50%);
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 80rpx;
  height: 80rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-btn.right {
  justify-content: flex-end;
}

.nav-btn::after,
.zoom-btn::after,
.practice-row::after,
.master-btn::after,
.secondary-btn::after {
  border: 0;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 16rpx 28rpx 278rpx;
}

.photo-card {
  position: relative;
  height: 384rpx;
  overflow: hidden;
  background: #d6e5ed;
  border: 2rpx solid #bec9c3;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.06);
}

.paper-bg {
  position: absolute;
  top: 34rpx;
  right: 34rpx;
  bottom: 26rpx;
  left: 34rpx;
  overflow: hidden;
  background: #ffffff;
  border-radius: 12rpx;
  transform: rotate(-1deg);
}

.paper-head,
.paper-line {
  position: absolute;
  left: 34rpx;
  height: 18rpx;
  background: #d8e8e3;
  border-radius: 999rpx;
}

.paper-head {
  top: 30rpx;
  width: 220rpx;
  height: 24rpx;
  background: #a7cfc2;
}

.paper-line.long {
  top: 82rpx;
  width: 520rpx;
}

.paper-line.mid {
  top: 122rpx;
  width: 420rpx;
}

.paper-line.short {
  top: 162rpx;
  width: 330rpx;
}

.math-row {
  position: absolute;
  top: 210rpx;
  left: 40rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #40655b;
}

.graph {
  position: absolute;
  right: 52rpx;
  bottom: 38rpx;
  width: 190rpx;
  height: 132rpx;
  border: 2rpx solid #d6e5ed;
  border-radius: 8rpx;
}

.axis-x,
.axis-y {
  position: absolute;
  background: #8da19a;
}

.axis-x {
  top: 68rpx;
  left: 18rpx;
  width: 154rpx;
  height: 2rpx;
}

.axis-y {
  top: 18rpx;
  left: 92rpx;
  width: 2rpx;
  height: 96rpx;
}

.curve {
  position: absolute;
  width: 92rpx;
  height: 74rpx;
  border: 4rpx solid #1f7159;
  border-top: 0;
  border-radius: 0 0 90rpx 90rpx;
}

.curve.one {
  top: 38rpx;
  left: 46rpx;
  transform: rotate(180deg);
}

.curve.two {
  top: 42rpx;
  left: 62rpx;
  opacity: 0.35;
  transform: rotate(180deg);
}

.photo-mask {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 160rpx;
  background: linear-gradient(180deg, rgba(15, 29, 35, 0), rgba(15, 29, 35, 0.28));
}

.zoom-btn {
  position: absolute;
  right: 24rpx;
  bottom: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 50%;
  box-shadow: 0 4rpx 14rpx rgba(15, 29, 35, 0.16);
}

.section-card {
  position: relative;
  padding: 28rpx;
  margin-top: 24rpx;
  overflow: hidden;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.04);
}

.left-rail {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 8rpx;
}

.left-rail.primary {
  background: #88d6b9;
}

.left-rail.error {
  background: #ba1a1a;
}

.section-title {
  display: flex;
  gap: 10rpx;
  align-items: center;
  margin-bottom: 18rpx;
  font-size: 24rpx;
  font-weight: 700;
}

.section-title.primary {
  color: #1f7159;
}

.section-title.secondary {
  color: #40655b;
}

.section-title.tertiary {
  color: #007351;
}

.section-title.error {
  color: #ba1a1a;
}

.question-text {
  font-size: 28rpx;
  line-height: 1.68;
  color: #0f1d23;
}

.answer-box {
  padding: 26rpx 22rpx;
  font-size: 32rpx;
  font-weight: 800;
  line-height: 1.5;
  color: #007351;
  text-align: center;
  background: rgba(140, 247, 199, 0.2);
  border: 2rpx solid #6fdaac;
  border-radius: 16rpx;
}

.step-list {
  position: relative;
}

.step-row {
  position: relative;
  display: flex;
  gap: 22rpx;
  min-height: 84rpx;
  padding-bottom: 24rpx;
}

.step-row:last-child {
  padding-bottom: 0;
}

.step-rail {
  position: absolute;
  top: 12rpx;
  bottom: -12rpx;
  left: 22rpx;
  width: 2rpx;
  background: rgba(190, 201, 195, 0.72);
}

.step-rail.last {
  display: none;
}

.step-no {
  z-index: 1;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 48rpx;
  height: 48rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #ffffff;
  background: #40655b;
  border: 8rpx solid #ffffff;
  border-radius: 50%;
  box-shadow: 0 2rpx 6rpx rgba(15, 29, 35, 0.1);
}

.step-text {
  flex: 1;
  padding-top: 4rpx;
  font-size: 28rpx;
  line-height: 1.62;
  color: #0f1d23;
}

.mistake-box {
  display: flex;
  gap: 18rpx;
  padding: 22rpx;
  background: rgba(255, 218, 214, 0.35);
  border: 2rpx solid #ffdad6;
  border-radius: 16rpx;
}

.mistake-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  font-size: 26rpx;
  font-weight: 800;
  color: #ffffff;
  background: #ba1a1a;
  border-radius: 50%;
}

.mistake-title {
  margin-bottom: 8rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #93000a;
}

.mistake-text {
  font-size: 26rpx;
  line-height: 1.58;
  color: #3f4944;
}

.point-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.point-chip {
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 12rpx 18rpx;
  font-size: 23rpx;
  font-weight: 700;
  color: #1f7159;
  background: rgba(31, 113, 89, 0.1);
  border: 2rpx solid rgba(31, 113, 89, 0.18);
  border-radius: 999rpx;
}

.practice-card {
  margin-bottom: 24rpx;
}

.practice-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 22rpx;
  margin: 0 0 18rpx;
  text-align: left;
  background: #e1f0f8;
  border-radius: 16rpx;
}

.practice-row:last-child {
  margin-bottom: 0;
}

.practice-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #0f1d23;
}

.practice-desc {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #3f4944;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  padding: 28rpx 28rpx calc(28rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid rgba(190, 201, 195, 0.5);
  box-shadow: 0 -8rpx 32rpx rgba(15, 29, 35, 0.06);
}

.master-btn {
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 92rpx;
  padding: 0;
  margin: 0 0 18rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.master-btn.done {
  background: #227253;
}

.secondary-actions {
  display: flex;
  gap: 18rpx;
}

.secondary-btn {
  display: flex;
  flex: 1;
  gap: 8rpx;
  align-items: center;
  justify-content: center;
  height: 76rpx;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  font-weight: 700;
  color: #0f1d23;
  background: #ffffff;
  border: 2rpx solid #6f7974;
  border-radius: 16rpx;
}

.secondary-btn.share {
  color: #1f7159;
  border-color: #1f7159;
}
</style>
