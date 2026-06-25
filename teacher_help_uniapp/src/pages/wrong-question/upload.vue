<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongUpload',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '拍照上传',
  },
})

const student = ref('')
const subject = ref('数学')
const grade = ref('八年级')
const source = ref('作业')

const sourceOptions = ['作业', '课堂', '考试', '其他']

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera'],
    fail: () => {
      uni.showToast({ title: '已保留示例图片', icon: 'none' })
    },
  })
}

function cropImage() {
  uni.showToast({ title: '裁剪图片', icon: 'none' })
}

function pickStudent() {
  uni.showActionSheet({
    itemList: ['张子涵', '李心怡', '王宇轩'],
    success: (res) => {
      student.value = ['张子涵', '李心怡', '王宇轩'][res.tapIndex]
    },
  })
}

function pickSubject() {
  uni.showActionSheet({
    itemList: ['数学', '物理', '英语'],
    success: (res) => {
      subject.value = ['数学', '物理', '英语'][res.tapIndex]
    },
  })
}

function pickGrade() {
  uni.showActionSheet({
    itemList: ['七年级', '八年级', '九年级'],
    success: (res) => {
      grade.value = ['七年级', '八年级', '九年级'][res.tapIndex]
    },
  })
}

function startAnalyze() {
  uni.navigateTo({ url: '/pages/wrong-question/analyzing' })
}

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="upload-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="30" color="#0f1d23" />
      </button>
      <view class="page-title">
        拍照上传
      </view>
      <view class="top-placeholder" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="preview-card" @click="chooseImage">
        <view class="desk-top" />
        <view class="paper">
          <view class="formula-lines left">
            <view />
            <view />
            <view />
            <view />
          </view>
          <view class="axis">
            <view class="axis-x" />
            <view class="axis-y" />
            <view class="curve one" />
            <view class="curve two" />
          </view>
        </view>
        <view class="desk-bottom" />
        <view class="corner tl" />
        <view class="corner tr" />
        <view class="corner bl" />
        <view class="corner br" />
      </view>

      <view class="image-actions">
        <button class="round-action" @click="cropImage">
          <view class="round-icon crop-icon" />
          <text>裁剪</text>
        </button>
        <button class="round-action" @click="chooseImage">
          <uni-icons type="refresh" size="30" color="#34433d" />
          <text>重新拍照</text>
        </button>
      </view>

      <view class="form-card">
        <view class="form-row" @click="pickStudent">
          <view class="form-left">
            <uni-icons type="person" size="24" color="#34433d" />
            <text>关联学员</text>
          </view>
          <view class="form-value" :class="{ placeholder: !student }">
            <text>{{ student || '请选择' }}</text>
            <uni-icons type="right" size="20" color="#34433d" />
          </view>
        </view>
        <view class="form-row" @click="pickSubject">
          <view class="form-left">
            <uni-icons type="list" size="24" color="#34433d" />
            <text>科目</text>
          </view>
          <view class="form-value">
            <text>{{ subject }}</text>
            <uni-icons type="right" size="20" color="#34433d" />
          </view>
        </view>
        <view class="form-row" @click="pickGrade">
          <view class="form-left">
            <view class="cap-icon" />
            <text>年级</text>
          </view>
          <view class="form-value">
            <text>{{ grade }}</text>
            <uni-icons type="right" size="20" color="#34433d" />
          </view>
        </view>

        <view class="source-block">
          <view class="source-title">
            <view class="source-icon" />
            <text>来源</text>
          </view>
          <view class="source-row">
            <button
              v-for="item in sourceOptions"
              :key="item"
              class="source-chip"
              :class="{ active: source === item }"
              @click="source = item"
            >
              {{ item }}
            </button>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="analyze-btn" @click="startAnalyze">
        <text class="spark">✦</text>
        <text>开始 AI 分析</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.upload-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f3faff;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 88rpx 1fr 88rpx;
  align-items: center;
  height: 104rpx;
  padding: 0 26rpx;
  background: #f3faff;
}

.back-btn,
.round-action,
.source-chip,
.analyze-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
}

.back-btn::after,
.round-action::after,
.source-chip::after,
.analyze-btn::after {
  border: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 72rpx;
  height: 72rpx;
  background: transparent;
}

.page-title {
  font-size: 39rpx;
  font-weight: 800;
  text-align: center;
}

.top-placeholder {
  width: 72rpx;
}

.content-scroll {
  height: calc(100vh - 104rpx);
  box-sizing: border-box;
  padding: 0 24rpx 172rpx;
}

.preview-card {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: #c7843e;
  border: 2rpx solid #bec9c3;
  border-radius: 18rpx;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.06);
}

.desk-top,
.desk-bottom {
  position: absolute;
  left: 0;
  width: 100%;
  height: 17%;
  background: linear-gradient(90deg, #b77335, #d89b5d, #bc7836);
}

.desk-top {
  top: 0;
}

.desk-bottom {
  bottom: 0;
}

.paper {
  position: absolute;
  top: 15%;
  right: 0;
  left: 0;
  height: 70%;
  background:
    linear-gradient(rgba(121, 178, 210, 0.18) 1rpx, transparent 1rpx),
    linear-gradient(90deg, rgba(121, 178, 210, 0.18) 1rpx, transparent 1rpx),
    #fffdf7;
  background-size: 26rpx 26rpx;
  box-shadow: 0 10rpx 22rpx rgba(15, 29, 35, 0.22);
}

.formula-lines {
  position: absolute;
  top: 66rpx;
  left: 74rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  width: 190rpx;
}

.formula-lines view {
  height: 5rpx;
  background: #8fbadd;
  border-radius: 999rpx;
  transform: rotate(-8deg);
}

.formula-lines view:nth-child(2) {
  width: 150rpx;
}

.formula-lines view:nth-child(3) {
  width: 170rpx;
}

.formula-lines view:nth-child(4) {
  width: 120rpx;
}

.axis {
  position: absolute;
  top: 94rpx;
  right: 70rpx;
  width: 210rpx;
  height: 210rpx;
}

.axis-x,
.axis-y {
  position: absolute;
  background: #8fbadd;
}

.axis-x {
  top: 104rpx;
  left: 12rpx;
  width: 170rpx;
  height: 4rpx;
}

.axis-y {
  top: 28rpx;
  left: 96rpx;
  width: 4rpx;
  height: 160rpx;
}

.curve {
  position: absolute;
  border: 4rpx solid #8fbadd;
  border-color: #8fbadd transparent transparent #8fbadd;
  border-radius: 50%;
}

.curve.one {
  top: 76rpx;
  left: 86rpx;
  width: 68rpx;
  height: 68rpx;
  transform: rotate(24deg);
}

.curve.two {
  top: 100rpx;
  left: 112rpx;
  width: 92rpx;
  height: 60rpx;
  transform: rotate(-34deg);
}

.corner {
  position: absolute;
  width: 44rpx;
  height: 44rpx;
  border-color: #007351;
}

.corner.tl {
  top: 28rpx;
  left: 28rpx;
  border-top: 4rpx solid #007351;
  border-left: 4rpx solid #007351;
}

.corner.tr {
  top: 28rpx;
  right: 28rpx;
  border-top: 4rpx solid #007351;
  border-right: 4rpx solid #007351;
}

.corner.bl {
  bottom: 28rpx;
  left: 28rpx;
  border-bottom: 4rpx solid #007351;
  border-left: 4rpx solid #007351;
}

.corner.br {
  right: 28rpx;
  bottom: 28rpx;
  border-right: 4rpx solid #007351;
  border-bottom: 4rpx solid #007351;
}

.image-actions {
  display: flex;
  justify-content: center;
  gap: 48rpx;
  padding: 28rpx 0 34rpx;
}

.round-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  font-size: 25rpx;
  font-weight: 700;
  color: #34433d;
  background: transparent;
}

.round-action :deep(.uni-icons),
.crop-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  background: #d6e5ed;
  border-radius: 50%;
}

.crop-icon {
  position: relative;
}

.crop-icon::before,
.crop-icon::after {
  position: absolute;
  content: '';
}

.crop-icon::before {
  width: 30rpx;
  height: 30rpx;
  border: 4rpx solid #34433d;
  border-top: 0;
  border-right: 0;
}

.crop-icon::after {
  width: 36rpx;
  height: 4rpx;
  background: #34433d;
  transform: rotate(90deg) translateX(6rpx);
}

.form-card {
  overflow: hidden;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 18rpx;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.05);
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 82rpx;
  padding: 0 28rpx;
  border-bottom: 1rpx solid #d6e5ed;
}

.form-left,
.form-value,
.source-title {
  display: flex;
  align-items: center;
}

.form-left {
  gap: 18rpx;
  font-size: 29rpx;
  color: #0f1d23;
}

.form-value {
  gap: 8rpx;
  font-size: 26rpx;
  color: #0f1d23;
}

.form-value.placeholder {
  color: #3f4944;
}

.cap-icon {
  width: 24rpx;
  height: 16rpx;
  border: 4rpx solid #34433d;
  border-top-width: 8rpx;
  transform: skewX(-18deg);
}

.source-icon {
  width: 24rpx;
  height: 18rpx;
  border: 4rpx solid #34433d;
  border-radius: 3rpx;
}

.source-block {
  padding: 30rpx 28rpx 34rpx;
}

.source-title {
  gap: 18rpx;
  margin-bottom: 24rpx;
  font-size: 29rpx;
}

.source-row {
  display: flex;
  flex-wrap: wrap;
  gap: 22rpx;
}

.source-chip {
  min-width: 106rpx;
  height: 58rpx;
  padding: 0 24rpx;
  font-size: 27rpx;
  font-weight: 700;
  color: #34433d;
  background: #f3faff;
  border: 2rpx solid #bec9c3;
  border-radius: 999rpx;
}

.source-chip.active {
  color: #466c61;
  background: #c2ebde;
  border-color: #c2ebde;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  padding: 26rpx 24rpx calc(26rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.analyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  width: 100%;
  height: 92rpx;
  font-size: 32rpx;
  font-weight: 800;
  color: #ffffff;
  background: #1f7159;
  border-radius: 14rpx;
}

.spark {
  font-size: 34rpx;
}
</style>
