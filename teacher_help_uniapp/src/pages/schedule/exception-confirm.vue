<script lang="ts" setup>
defineOptions({
  name: 'CheckinExceptionConfirm',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '点名异常确认',
  },
})

const abnormalStudents = [
  { name: '张三', status: '迟到', cls: 'late' },
  { name: '李四', status: '请假', cls: 'leave' },
  { name: '王五', status: '缺勤', cls: 'absent' },
]

function backEdit() {
  uni.navigateBack()
}

function confirmSubmit() {
  uni.redirectTo({ url: '/pages/schedule/checkin-done?id=1' })
}
</script>

<template>
  <view class="exception-page">
    <view class="mock-bg">
      <view class="mock-head">
        <view class="mock-title">
          数学集训营 - 秋季班
        </view>
        <view class="mock-pill">
          进行中
        </view>
      </view>
      <view class="mock-card">
        <view class="mock-avatar" />
        <view class="mock-lines">
          <view class="line long" />
          <view class="line short" />
        </view>
        <view class="mock-status red">
          迟到
        </view>
      </view>
      <view class="mock-card">
        <view class="mock-avatar" />
        <view class="mock-lines">
          <view class="line long" />
          <view class="line short" />
        </view>
        <view class="mock-status green">
          请假
        </view>
      </view>
      <view class="mock-card">
        <view class="mock-avatar" />
        <view class="mock-lines">
          <view class="line long" />
          <view class="line short" />
        </view>
        <view class="mock-status red">
          缺勤
        </view>
      </view>
    </view>

    <view class="overlay">
      <view class="dialog">
        <view class="icon-wrap">
          <uni-icons type="info" size="34" color="#ba1a1a" />
        </view>
        <view class="dialog-title">
          点名异常确认
        </view>

        <view class="abnormal-card">
          <view class="abnormal-tip">
            以下学员存在考勤异常：
          </view>
          <view v-for="item in abnormalStudents" :key="item.name" class="abnormal-row">
            <text class="abnormal-name">{{ item.name }}</text>
            <text class="abnormal-tag" :class="item.cls">{{ item.status }}</text>
          </view>
        </view>

        <view class="confirm-text">
          当前存在 <text>3</text> 名异常学员，是否确认提交？
        </view>

        <view class="dialog-actions">
          <button class="action-btn outline" @click="backEdit">
            返回修改
          </button>
          <button class="action-btn primary" @click="confirmSubmit">
            确认提交
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.exception-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: #0f1d23;
  background: #f3faff;
}

.mock-bg {
  box-sizing: border-box;
  min-height: 100vh;
  padding: 30rpx 28rpx;
  filter: blur(10rpx);
  opacity: 0.6;
  transform: scale(1.02);
}

.mock-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 44rpx;
}

.mock-title {
  width: 360rpx;
  height: 42rpx;
  background: #dbe7e2;
  border-radius: 10rpx;
}

.mock-pill {
  width: 116rpx;
  height: 42rpx;
  font-size: 0;
  background: #d7f0e7;
  border-radius: 999rpx;
}

.mock-card {
  display: flex;
  align-items: center;
  gap: 22rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.mock-avatar {
  width: 80rpx;
  height: 80rpx;
  background: #d6e5ed;
  border-radius: 50%;
}

.mock-lines {
  flex: 1;
}

.line {
  height: 24rpx;
  background: #d6e5ed;
  border-radius: 8rpx;
}

.line.short {
  width: 190rpx;
  margin-top: 14rpx;
}

.line.long {
  width: 260rpx;
}

.mock-status {
  width: 92rpx;
  height: 34rpx;
  border-radius: 999rpx;
  font-size: 0;
}

.mock-status.red {
  background: #ffdad6;
}

.mock-status.green {
  background: #e9f6ef;
}

.overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28rpx;
  background: rgba(15, 29, 35, 0.4);
  backdrop-filter: blur(6rpx);
}

.dialog {
  width: 100%;
  overflow: hidden;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 24rpx;
  box-shadow: 0 24rpx 60rpx rgba(15, 29, 35, 0.22);
}

.icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  margin: 44rpx auto 22rpx;
  background: rgba(255, 218, 214, 0.42);
  border-radius: 50%;
}

.dialog-title {
  font-size: 34rpx;
  font-weight: 700;
  text-align: center;
}

.abnormal-card {
  margin: 38rpx 28rpx 34rpx;
  padding: 28rpx 32rpx;
  background: #e7f6fe;
  border: 2rpx solid rgba(190, 201, 195, 0.55);
  border-radius: 14rpx;
}

.abnormal-tip {
  margin-bottom: 18rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.abnormal-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 62rpx;
}

.abnormal-name {
  font-size: 30rpx;
  color: #0f1d23;
}

.abnormal-tag {
  min-width: 88rpx;
  padding: 10rpx 22rpx;
  font-size: 26rpx;
  font-weight: 700;
  text-align: center;
  border-radius: 999rpx;
}

.abnormal-tag.late {
  color: #227253;
  background: #e9f6ef;
  border: 2rpx solid rgba(34, 114, 83, 0.2);
}

.abnormal-tag.leave {
  color: #3f4944;
  background: #d6e5ed;
  border: 2rpx solid rgba(111, 121, 116, 0.36);
}

.abnormal-tag.absent {
  color: #ba1a1a;
  background: rgba(255, 218, 214, 0.5);
  border: 2rpx solid rgba(186, 26, 26, 0.2);
}

.confirm-text {
  margin: 0 28rpx 36rpx;
  font-size: 30rpx;
  text-align: center;
}

.confirm-text text {
  margin: 0 8rpx;
  font-size: 36rpx;
  font-weight: 700;
  color: #ba1a1a;
}

.dialog-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22rpx;
  padding: 28rpx;
  background: #f3faff;
  border-top: 1rpx solid #d6e5ed;
}

.action-btn {
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 88rpx;
  border-radius: 14rpx;
}

.action-btn::after {
  border: 0;
}

.action-btn.outline {
  color: #1f7159;
  background: transparent;
  border: 2rpx solid #1f7159;
}

.action-btn.primary {
  color: #ffffff;
  background: #1f7159;
}
</style>
