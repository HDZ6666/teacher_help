<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongUpload',
})
definePage({
  style: {
    navigationBarTitleText: '拍照上传',
  },
})

const imageList = ref<string[]>([])
const student = ref('')
const subject = ref('')
const course = ref('')

const subjectOptions = ['语文', '数学', '英语', '物理', '化学', '生物']
const subjectIndex = ref(-1)

function chooseImage(source: 'camera' | 'album') {
  uni.chooseImage({
    count: 1,
    sourceType: source === 'camera' ? ['camera'] : ['album'],
    success: (res: any) => {
      imageList.value = res.tempFilePaths
    },
    fail: () => {
      // 原型：无图时放一张占位
      imageList.value = ['placeholder']
    },
  })
}

function removeImage() {
  imageList.value = []
}

function onSubjectChange(e: any) {
  subjectIndex.value = e.detail.value
  subject.value = subjectOptions[e.detail.value]
}

function pickStudent() {
  uni.showActionSheet({
    itemList: ['李明轩', '王诗涵', '张子墨', '陈嘉怡'],
    success: (res) => {
      student.value = ['李明轩', '王诗涵', '张子墨', '陈嘉怡'][res.tapIndex]
    },
  })
}

function startAnalyze() {
  if (!imageList.value.length) {
    uni.showToast({ title: '请先拍照或选择图片', icon: 'none' })
    return
  }
  if (!student.value) {
    uni.showToast({ title: '请关联学生', icon: 'none' })
    return
  }
  uni.navigateTo({ url: '/pages/wrong-question/analyzing' })
}
</script>

<template>
  <view class="upload-page">
    <view class="tip-bar">
      <uni-icons type="info" size="16" color="#1f7159" />
      <text>拍清题目区域，尽量避免阴影和反光</text>
    </view>

    <view class="shot-area">
      <view v-if="!imageList.length" class="shot-empty" @click="chooseImage('camera')">
        <uni-icons type="camera" size="40" color="#9aa5aa" />
        <text class="shot-empty-text">
          点击拍摄题目
        </text>
      </view>
      <view v-else class="shot-preview">
        <view class="preview-img">
          <uni-icons type="image" size="60" color="#c2cbce" />
          <text class="preview-hint">
            题目图片预览
          </text>
        </view>
        <view class="preview-tools">
          <button class="tool-btn" @click="chooseImage('camera')">
            重新拍摄
          </button>
          <button class="tool-btn" @click="removeImage">
            删除
          </button>
        </view>
      </view>
    </view>

    <view class="shot-actions">
      <button class="ghost-btn" @click="chooseImage('camera')">
        <uni-icons type="camera" size="18" color="#1f7159" />
        <text>拍照</text>
      </button>
      <button class="ghost-btn" @click="chooseImage('album')">
        <uni-icons type="image" size="18" color="#1f7159" />
        <text>从相册选</text>
      </button>
    </view>

    <view class="form-card">
      <view class="form-row" @click="pickStudent">
        <text class="form-label">
          关联学生
        </text>
        <view class="form-value" :class="{ ph: !student }">
          {{ student || '请选择学生' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
      <picker :value="subjectIndex" :range="subjectOptions" @change="onSubjectChange">
        <view class="form-row">
          <text class="form-label">
            学科
          </text>
          <view class="form-value" :class="{ ph: !subject }">
            {{ subject || '请选择学科' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="form-row no-border" @click="course = '数学提高A班 · 06-23'">
        <text class="form-label">
          关联课程
        </text>
        <view class="form-value" :class="{ ph: !course }">
          {{ course || '可选' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="startAnalyze">
        开始 AI 分析
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.upload-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.tip-bar {
  display: flex;
  gap: 10rpx;
  align-items: center;
  padding: 18rpx 22rpx;
  font-size: 24rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 12rpx;
}

.shot-area {
  margin-top: 22rpx;
}

.shot-empty {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  align-items: center;
  justify-content: center;
  height: 440rpx;
  background: #ffffff;
  border: 2rpx dashed #cfd9d4;
  border-radius: 18rpx;
}

.shot-empty-text {
  font-size: 26rpx;
  color: #8a969d;
}

.shot-preview {
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 18rpx;
}

.preview-img {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  align-items: center;
  justify-content: center;
  height: 440rpx;
  background: #f1f4f2;
  border-radius: 18rpx 18rpx 0 0;
}

.preview-hint {
  font-size: 24rpx;
  color: #9aa5aa;
}

.preview-tools {
  display: flex;
  gap: 16rpx;
  padding: 20rpx;
}

.tool-btn {
  flex: 1;
  margin: 0;
  font-size: 25rpx;
  line-height: 64rpx;
  color: #1f7159;
  background: #eef2f0;
  border-radius: 12rpx;
}

.tool-btn::after {
  border: 0;
}

.shot-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 22rpx;
}

.ghost-btn {
  display: flex;
  flex: 1;
  gap: 8rpx;
  align-items: center;
  justify-content: center;
  margin: 0;
  font-size: 26rpx;
  line-height: 84rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 14rpx;
}

.ghost-btn::after {
  border: 0;
}

.form-card {
  margin-top: 22rpx;
  padding: 0 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 96rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.form-row.no-border,
.form-row:last-child {
  border-bottom: 0;
}

.form-label {
  font-size: 27rpx;
  color: #4a565c;
}

.form-value {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 27rpx;
  color: #1f2d33;
}

.form-value.ph {
  color: #9aa5aa;
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
