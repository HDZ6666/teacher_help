<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongEdit',
})
definePage({
  style: {
    navigationBarTitleText: '编辑解析',
  },
})

const form = ref({
  question: '一根绳子长 12 米，第一次用去全长的 1/3，第二次用去剩下的 1/2，还剩多少米？',
  subject: '数学',
  point: '分数应用题',
  answer: '4 米',
  steps: '1. 12 × 1/3 = 4，剩 8\n2. 8 × 1/2 = 4\n3. 8 - 4 = 4',
  mistakes: '易把"剩下的 1/2"误算成"全长的 1/2"。',
  remark: '',
})

const subjectOptions = ['语文', '数学', '英语', '物理', '化学', '生物']
const subjectIndex = ref(1)

const masteryOptions = ['未掌握', '已了解', '已掌握']
const mastery = ref('未掌握')

function onSubjectChange(e: any) {
  subjectIndex.value = e.detail.value
  form.value.subject = subjectOptions[e.detail.value]
}

function save() {
  uni.showToast({ title: '已保存解析', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 600)
}

function discard() {
  uni.navigateBack()
}

function remove() {
  uni.showModal({
    title: '删除错题',
    content: '删除后无法恢复，确认删除这道错题？',
    confirmText: '删除',
    confirmColor: '#c0392b',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '已删除', icon: 'none' })
        setTimeout(() => uni.navigateBack({ delta: 2 }), 500)
      }
    },
  })
}
</script>

<template>
  <view class="we-page">
    <view class="form-card">
      <view class="field">
        <text class="field-label">
          题干
        </text>
        <textarea v-model="form.question" class="field-textarea" placeholder="题目内容" />
      </view>
    </view>

    <view class="form-card">
      <picker :value="subjectIndex" :range="subjectOptions" @change="onSubjectChange">
        <view class="row">
          <text class="row-label">
            学科
          </text>
          <view class="row-value">
            {{ form.subject }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="row no-border">
        <text class="row-label">
          知识点
        </text>
        <input v-model="form.point" class="row-input" placeholder="如：分数应用题">
      </view>
    </view>

    <view class="form-card">
      <view class="field">
        <text class="field-label">
          答案
        </text>
        <input v-model="form.answer" class="field-input" placeholder="正确答案">
      </view>
      <view class="field">
        <text class="field-label">
          解题步骤
        </text>
        <textarea v-model="form.steps" class="field-textarea" placeholder="每行一个步骤" />
      </view>
      <view class="field no-mb">
        <text class="field-label">
          易错点
        </text>
        <textarea v-model="form.mistakes" class="field-textarea sm" placeholder="易错原因" />
      </view>
    </view>

    <view class="form-card">
      <text class="field-label">
        掌握状态
      </text>
      <view class="mastery-row">
        <view
          v-for="m in masteryOptions"
          :key="m"
          class="mastery-chip"
          :class="{ active: mastery === m }"
          @click="mastery = m"
        >
          {{ m }}
        </view>
      </view>
    </view>

    <view class="form-card">
      <view class="field no-mb">
        <text class="field-label">
          老师补充说明
        </text>
        <textarea v-model="form.remark" class="field-textarea sm" placeholder="补充说明（可选）" />
      </view>
    </view>

    <button class="del-btn" @click="remove">
      删除错题
    </button>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="discard">
        放弃修改
      </button>
      <button class="primary-btn" @click="save">
        保存
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.we-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.form-card {
  margin-bottom: 16rpx;
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.field {
  margin-bottom: 24rpx;
}

.field.no-mb {
  margin-bottom: 0;
}

.field-label,
.row-label {
  font-size: 26rpx;
  color: #4a565c;
}

.field-input,
.field-textarea {
  width: 100%;
  margin-top: 14rpx;
  padding: 18rpx 20rpx;
  font-size: 27rpx;
  background: #f6f8f7;
  border-radius: 12rpx;
}

.field-input {
  box-sizing: border-box;
  height: 80rpx;
}

.field-textarea {
  box-sizing: border-box;
  height: 160rpx;
}

.field-textarea.sm {
  height: 120rpx;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 92rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.row.no-border {
  border-bottom: 0;
}

.row-value {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 27rpx;
}

.row-input {
  font-size: 27rpx;
  text-align: right;
}

.mastery-row {
  display: flex;
  gap: 14rpx;
  margin-top: 18rpx;
}

.mastery-chip {
  flex: 1;
  font-size: 26rpx;
  line-height: 72rpx;
  text-align: center;
  color: #67757c;
  background: #f1f4f2;
  border-radius: 12rpx;
}

.mastery-chip.active {
  color: #ffffff;
  background: #1f7159;
}

.del-btn {
  margin: 8rpx 0 0;
  font-size: 27rpx;
  line-height: 88rpx;
  color: #a4423a;
  background: #ffeceb;
  border-radius: 16rpx;
}

.del-btn::after {
  border: 0;
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
.primary-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  line-height: 90rpx;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #e6f4ee;
}

.primary-btn {
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
}

.ghost-btn::after,
.primary-btn::after {
  border: 0;
}
</style>
