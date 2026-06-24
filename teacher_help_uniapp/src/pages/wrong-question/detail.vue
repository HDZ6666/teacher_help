<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'WrongDetail',
})
definePage({
  style: {
    navigationBarTitleText: '错题详情',
  },
})

// 静态 mock
const detail = ref({
  student: '李明轩',
  subject: '数学',
  grade: '三年级',
  point: '分数应用题',
  mastery: '未掌握',
  question: '一根绳子长 12 米，第一次用去全长的 1/3，第二次用去剩下的 1/2，还剩多少米？',
  answer: '4 米',
  steps: [
    '第一次用去：12 × 1/3 = 4（米），剩下 12 - 4 = 8（米）',
    '第二次用去：8 × 1/2 = 4（米）',
    '还剩：8 - 4 = 4（米）',
  ],
  mistakes: '易把"剩下的 1/2"误算成"全长的 1/2"，导致第二次用去 6 米。注意"剩下"是相对量。',
  similar: [
    '一桶油 20 千克，先用去 2/5，再用去剩下的 1/4，还剩多少千克？',
    '一条路 600 米，第一天修 1/3，第二天修剩下的 2/5，还剩多少米？',
  ],
  remark: '',
})

const masteryClass = ref('danger')

function masteryToClass(m: string) {
  if (m === '未掌握')
    return 'danger'
  if (m === '已了解')
    return 'warn'
  return 'success'
}
masteryClass.value = masteryToClass(detail.value.mastery)

function editParse() {
  uni.navigateTo({ url: '/pages/wrong-question/edit?id=1' })
}

function reAnalyze() {
  uni.navigateTo({ url: '/pages/wrong-question/analyzing' })
}

function markMastered() {
  detail.value.mastery = '已掌握'
  masteryClass.value = 'success'
  uni.showToast({ title: '已标记掌握', icon: 'success' })
}

function genPractice() {
  uni.showToast({ title: '已生成相似练习', icon: 'none' })
}

function shareToParent() {
  uni.showToast({ title: '分享给家长', icon: 'none' })
}

onLoad(() => {})
</script>

<template>
  <view class="wd-page">
    <view class="img-card">
      <view class="img-box">
        <uni-icons type="image" size="60" color="#c2cbce" />
        <text class="img-hint">
          题目原图
        </text>
      </view>
    </view>

    <view class="meta-card">
      <view class="meta-line">
        <text class="meta-name">
          {{ detail.student }}
        </text>
        <text class="mastery" :class="masteryClass">
          {{ detail.mastery }}
        </text>
      </view>
      <view class="meta-tags">
        <text class="meta-tag">{{ detail.subject }}</text>
        <text class="meta-tag">{{ detail.grade }}</text>
        <text class="meta-tag">{{ detail.point }}</text>
      </view>
    </view>

    <view class="sec-card">
      <view class="sec-title">
        <uni-icons type="compose" size="16" color="#1f7159" />
        <text>AI 识别题干</text>
      </view>
      <view class="sec-text">
        {{ detail.question }}
      </view>
    </view>

    <view class="sec-card">
      <view class="sec-title">
        <uni-icons type="checkbox" size="16" color="#1f7159" />
        <text>答案与解析</text>
      </view>
      <view class="answer-line">
        正确答案：<text class="answer-val">{{ detail.answer }}</text>
      </view>
      <view v-for="(s, idx) in detail.steps" :key="idx" class="step-line">
        <text class="step-no">{{ idx + 1 }}</text>
        <text class="step-txt">{{ s }}</text>
      </view>
    </view>

    <view class="sec-card warn-card">
      <view class="sec-title">
        <uni-icons type="info" size="16" color="#8a671b" />
        <text>易错点</text>
      </view>
      <view class="sec-text">
        {{ detail.mistakes }}
      </view>
    </view>

    <view class="sec-card">
      <view class="sec-title">
        <uni-icons type="list" size="16" color="#1f7159" />
        <text>相似练习</text>
      </view>
      <view v-for="(q, idx) in detail.similar" :key="idx" class="similar-line">
        {{ idx + 1 }}. {{ q }}
      </view>
    </view>

    <view class="sec-card">
      <view class="sec-title">
        <uni-icons type="chatbubble" size="16" color="#1f7159" />
        <text>老师备注</text>
      </view>
      <view class="sec-text muted">
        {{ detail.remark || '暂无备注，可在编辑解析中补充' }}
      </view>
    </view>

    <view class="action-grid">
      <button class="grid-btn" @click="reAnalyze">
        重新识别
      </button>
      <button class="grid-btn" @click="markMastered">
        标为已掌握
      </button>
      <button class="grid-btn" @click="genPractice">
        生成练习
      </button>
      <button class="grid-btn" @click="shareToParent">
        分享给家长
      </button>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="editParse">
        编辑解析
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.wd-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.img-card {
  padding: 0;
}

.img-box {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  align-items: center;
  justify-content: center;
  height: 360rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.img-hint {
  font-size: 24rpx;
  color: #9aa5aa;
}

.meta-card,
.sec-card {
  margin-top: 16rpx;
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.meta-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.meta-name {
  font-size: 32rpx;
  font-weight: 700;
}

.mastery {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.mastery.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.mastery.warn {
  color: #8a671b;
  background: #fff5d8;
}

.mastery.success {
  color: #227253;
  background: #e9f6ef;
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 16rpx;
}

.meta-tag {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  color: #5d6a70;
  background: #eef2f0;
  border-radius: 999rpx;
}

.sec-title {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 27rpx;
  font-weight: 700;
}

.sec-text {
  margin-top: 16rpx;
  font-size: 27rpx;
  line-height: 1.7;
  color: #3d484e;
}

.sec-text.muted {
  color: #9aa5aa;
}

.warn-card {
  background: #fffaf0;
  border-color: #f0e3c4;
}

.answer-line {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #4a565c;
}

.answer-val {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f7159;
}

.step-line {
  display: flex;
  gap: 14rpx;
  margin-top: 16rpx;
}

.step-no {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 36rpx;
  height: 36rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 50%;
}

.step-txt {
  flex: 1;
  font-size: 26rpx;
  line-height: 1.6;
  color: #3d484e;
}

.similar-line {
  margin-top: 14rpx;
  font-size: 26rpx;
  line-height: 1.6;
  color: #3d484e;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.grid-btn {
  margin: 0;
  font-size: 26rpx;
  line-height: 80rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 14rpx;
}

.grid-btn::after {
  border: 0;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.primary-btn {
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 90rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.primary-btn::after {
  border: 0;
}
</style>
