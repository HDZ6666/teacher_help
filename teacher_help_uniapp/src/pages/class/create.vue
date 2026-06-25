<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ClassCreate',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '创建班级',
  },
})

const classType = ref('group')
const allowOver = ref(false)

function goBack() {
  uni.navigateBack()
}

function save() {
  uni.showToast({ title: '已保存班级', icon: 'success' })
}

function saveAndSchedule() {
  uni.navigateTo({ url: '/pages/schedule/create' })
}
</script>

<template>
  <view class="create-page">
    <view class="topbar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#1f7159" />
      </button>
      <text class="page-title">
        创建班级
      </text>
      <view class="nav-space" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="form-card">
        <view class="field">
          <text class="label">
            班级名称 <text class="required">*</text>
          </text>
          <input class="input" value="春季冲刺A班" placeholder="例如：春季冲刺A班">
        </view>

        <view class="field">
          <text class="label">
            班级类型
          </text>
          <view class="segment">
            <button class="seg-btn" :class="{ active: classType === 'group' }" @click="classType = 'group'">
              班课
            </button>
            <button class="seg-btn" :class="{ active: classType === 'one' }" @click="classType = 'one'">
              一对一
            </button>
          </view>
        </view>

        <view class="field no-bottom">
          <text class="label">
            关联课程
          </text>
          <view class="select-row">
            <text>请选择课程体系</text>
            <uni-icons type="right" size="16" color="#74828a" />
          </view>
        </view>
      </view>

      <view class="form-card">
        <view class="capacity-row">
          <view>
            <text class="label">
              容纳人数
            </text>
            <view class="stepper">
              <button>-</button>
              <text>15</text>
              <button>+</button>
            </view>
          </view>
          <view class="switch-block">
            <text class="label">
              允许超额
            </text>
            <switch :checked="allowOver" color="#1f7159" style="transform: scale(0.84)" @change="allowOver = $event.detail.value" />
          </view>
        </view>

        <view class="row">
          <view class="row-left">
            <uni-icons type="person" size="20" color="#74828a" />
            <text>授课教师</text>
          </view>
          <view class="row-right">
            <text>选择主讲教师</text>
            <uni-icons type="right" size="16" color="#74828a" />
          </view>
        </view>

        <view class="row">
          <view class="row-left">
            <uni-icons type="home" size="20" color="#74828a" />
            <text>默认教室</text>
          </view>
          <view class="row-right">
            <text>选择上课地点</text>
            <uni-icons type="right" size="16" color="#74828a" />
          </view>
        </view>

        <view class="field no-bottom">
          <text class="label">
            开课日期
          </text>
          <input class="input" value="2026-07-01" disabled>
        </view>
      </view>

      <view class="form-card">
        <view class="field no-bottom">
          <text class="label">
            备注信息
          </text>
          <textarea class="textarea" placeholder="添加其他说明事项..." />
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="save">
        保存
      </button>
      <button class="primary-btn" @click="saveAndSchedule">
        保存并排课
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.create-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #e1e8e4;
}

.nav-btn,
.nav-space {
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.page-title {
  font-size: 38rpx;
  font-weight: 800;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 28rpx 28rpx 160rpx;
}

.form-card {
  padding: 0 28rpx;
  margin-bottom: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.field {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.field.no-bottom {
  border-bottom: 0;
}

.label {
  display: block;
  margin-bottom: 14rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #64737b;
}

.required {
  color: #a4423a;
}

.input,
.textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 0 22rpx;
  font-size: 28rpx;
  color: #0f1d23;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 14rpx;
}

.input {
  height: 88rpx;
}

.textarea {
  min-height: 150rpx;
  padding-top: 20rpx;
}

.segment {
  display: flex;
  padding: 6rpx;
  background: #eef2f0;
  border-radius: 14rpx;
}

.seg-btn {
  flex: 1;
  height: 66rpx;
  padding: 0;
  margin: 0;
  font-size: 26rpx;
  font-weight: 700;
  color: #64737b;
  background: transparent;
  border-radius: 10rpx;
}

.seg-btn.active {
  color: #1f7159;
  background: #ffffff;
  box-shadow: 0 4rpx 12rpx rgba(15, 29, 35, 0.06);
}

.select-row,
.row,
.capacity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.select-row {
  height: 88rpx;
  padding: 0 22rpx;
  font-size: 28rpx;
  color: #74828a;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 14rpx;
}

.capacity-row {
  min-height: 138rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.stepper {
  display: flex;
  align-items: center;
  width: 238rpx;
  height: 72rpx;
  overflow: hidden;
  background: #f7faf8;
  border: 1rpx solid #dfe7e3;
  border-radius: 14rpx;
}

.stepper button {
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  font-size: 34rpx;
  color: #1f7159;
  background: transparent;
}

.stepper text {
  flex: 1;
  font-size: 28rpx;
  font-weight: 700;
  text-align: center;
}

.switch-block {
  display: flex;
  align-items: flex-end;
  flex-direction: column;
}

.row {
  min-height: 98rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.row-left,
.row-right {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 27rpx;
}

.row-right {
  color: #74828a;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  display: flex;
  gap: 20rpx;
  padding: 20rpx 28rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #e7ece9;
}

.ghost-btn,
.primary-btn {
  flex: 1;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 30rpx;
  font-weight: 800;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
