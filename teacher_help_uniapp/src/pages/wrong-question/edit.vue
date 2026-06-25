<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongEdit',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '编辑解析',
  },
})

const form = ref({
  question: '已知函数 f(x) = ax² + bx + c 经过点 (1, 2) 和 (-1, 0)，且对称轴为 x = 1/2。求函数的解析式。',
  answer: 'f(x) = -2x² + 2x + 2',
  steps:
    '1. 由对称轴 x = -b/(2a) = 1/2，得 b = -a。\n2. 将点 (1, 2) 代入得：a + b + c = 2。\n3. 将点 (-1, 0) 代入得：a - b + c = 0。\n4. 联立上述方程组解得：a = -2，b = 2，c = 2。\n5. 故函数解析式为 f(x) = -2x² + 2x + 2。',
  mistake: '学生在代入对称轴公式时符号混淆，导致 b 的值计算错误，进而影响后续方程组的求解。',
})

const knowledgePoints = ref(['二次函数图像', '待定系数法', '三元一次方程组'])
const newPoint = ref('')

function openMenu() {
  uni.navigateBack()
}

function openSearch() {
  uni.showToast({ title: '搜索错题', icon: 'none' })
}

function polishSteps() {
  uni.showToast({ title: 'AI 已润色步骤', icon: 'success' })
}

function removePoint(index: number) {
  knowledgePoints.value.splice(index, 1)
}

function addPoint() {
  const value = newPoint.value.trim()
  if (!value)
    return
  if (!knowledgePoints.value.includes(value))
    knowledgePoints.value.push(value)
  newPoint.value = ''
}

function discard() {
  uni.navigateBack()
}

function save() {
  uni.showToast({ title: '已保存修改', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 600)
}
</script>

<template>
  <view class="edit-page">
    <view class="top-bar">
      <button class="icon-btn" @click="openMenu">
        <uni-icons type="bars" size="30" color="#005842" />
      </button>
      <view class="page-title">
        错题本
      </view>
      <button class="icon-btn right" @click="openSearch">
        <uni-icons type="search" size="34" color="#005842" />
      </button>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="intro-block">
        <view class="intro-title">
          编辑 AI 解析内容
        </view>
        <view class="intro-desc">
          您可以修改以下由系统自动提取和生成的解析内容，以确保其准确无误。
        </view>
      </view>

      <view class="form-card">
        <view class="field-title">
          <uni-icons type="compose" size="22" color="#1f7159" />
          <text>题目文本</text>
        </view>
        <textarea
          v-model="form.question"
          class="field-textarea question"
          maxlength="-1"
          placeholder="输入题目内容..."
          placeholder-class="placeholder"
        />
      </view>

      <view class="form-card">
        <view class="field-title">
          <uni-icons type="checkbox" size="22" color="#1f7159" />
          <text>答案</text>
        </view>
        <textarea
          v-model="form.answer"
          class="field-textarea answer"
          maxlength="-1"
          placeholder="输入最终答案..."
          placeholder-class="placeholder"
        />
      </view>

      <view class="form-card">
        <view class="field-head">
          <view class="field-title no-margin">
            <uni-icons type="list" size="22" color="#1f7159" />
            <text>解题步骤</text>
          </view>
          <button class="ai-btn" @click="polishSteps">
            <text class="spark">✦</text>
            <text>AI 润色</text>
          </button>
        </view>
        <textarea
          v-model="form.steps"
          class="field-textarea steps"
          maxlength="-1"
          placeholder="详细输入解题步骤..."
          placeholder-class="placeholder"
        />
      </view>

      <view class="form-card">
        <view class="field-title error">
          <uni-icons type="info" size="22" color="#ba1a1a" />
          <text>错因分析</text>
        </view>
        <textarea
          v-model="form.mistake"
          class="field-textarea mistake"
          maxlength="-1"
          placeholder="记录学生的常见错误原因..."
          placeholder-class="placeholder"
        />
      </view>

      <view class="form-card point-card">
        <view class="field-title">
          <uni-icons type="tag" size="22" color="#1f7159" />
          <text>考察知识点</text>
        </view>
        <view class="point-list">
          <view
            v-for="(point, index) in knowledgePoints"
            :key="point"
            class="point-chip"
          >
            <text>{{ point }}</text>
            <button class="remove-point" @click="removePoint(index)">
              <uni-icons type="closeempty" size="18" color="#6f7974" />
            </button>
          </view>
        </view>
        <view class="add-point">
          <input
            v-model="newPoint"
            class="point-input"
            placeholder="添加新知识点..."
            placeholder-class="placeholder"
            @confirm="addPoint"
          >
          <button class="add-btn" @click="addPoint">
            <uni-icons type="plus-filled" size="26" color="#1f7159" />
          </button>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="discard-btn" @click="discard">
        放弃修改
      </button>
      <button class="save-btn" @click="save">
        保存修改
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.edit-page {
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
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1f7159;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 80rpx;
  height: 80rpx;
  padding: 0;
  margin: 0;
  background: transparent;
  border-radius: 50%;
}

.icon-btn.right {
  justify-content: flex-end;
}

.icon-btn::after,
.ai-btn::after,
.remove-point::after,
.add-btn::after,
.discard-btn::after,
.save-btn::after {
  border: 0;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 32rpx 28rpx 140rpx;
}

.intro-block {
  margin-bottom: 48rpx;
}

.intro-title {
  margin-bottom: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #0f1d23;
}

.intro-desc {
  font-size: 26rpx;
  line-height: 1.45;
  color: #3f4944;
}

.form-card {
  padding: 28rpx;
  margin-bottom: 24rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 16rpx;
}

.field-title,
.field-head {
  display: flex;
  align-items: center;
}

.field-title {
  gap: 10rpx;
  margin-bottom: 16rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #3f4944;
}

.field-title.no-margin {
  margin-bottom: 0;
}

.field-title.error {
  color: #3f4944;
}

.field-head {
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.ai-btn {
  display: flex;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  font-size: 22rpx;
  font-weight: 700;
  line-height: 36rpx;
  color: #1f7159;
  background: transparent;
}

.spark {
  font-size: 24rpx;
}

.field-textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 22rpx;
  font-size: 28rpx;
  line-height: 1.55;
  color: #0f1d23;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 12rpx;
}

.field-textarea.question {
  height: 180rpx;
}

.field-textarea.answer {
  height: 136rpx;
}

.field-textarea.steps {
  height: 330rpx;
}

.field-textarea.mistake {
  height: 150rpx;
}

.placeholder {
  color: #6f7974;
}

.point-card {
  margin-bottom: 24rpx;
}

.point-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-bottom: 20rpx;
}

.point-chip {
  display: inline-flex;
  gap: 8rpx;
  align-items: center;
  padding: 10rpx 14rpx 10rpx 18rpx;
  color: #1f7159;
  background: #e7f6fe;
  border: 2rpx solid #d6e5ed;
  border-radius: 999rpx;
}

.point-chip text {
  font-size: 24rpx;
  font-weight: 700;
}

.remove-point {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28rpx;
  height: 28rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.add-point {
  position: relative;
}

.point-input {
  box-sizing: border-box;
  width: 100%;
  height: 84rpx;
  padding: 0 78rpx 0 22rpx;
  font-size: 28rpx;
  color: #0f1d23;
  background: #f3faff;
  border: 2rpx solid #bec9c3;
  border-radius: 12rpx;
}

.add-btn {
  position: absolute;
  top: 0;
  right: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56rpx;
  height: 84rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  display: flex;
  gap: 24rpx;
  padding: 28rpx 28rpx calc(28rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
  box-shadow: 0 -8rpx 32rpx rgba(15, 29, 35, 0.04);
}

.discard-btn,
.save-btn {
  flex: 1;
  height: 92rpx;
  padding: 0;
  margin: 0;
  font-size: 26rpx;
  font-weight: 700;
  border-radius: 16rpx;
}

.discard-btn {
  color: #1f7159;
  background: transparent;
  border: 2rpx solid #1f7159;
}

.save-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
