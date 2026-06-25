<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'StudentLeave',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '学员请假',
  },
})

const studentName = ref('林小明')
const makeup = ref(true)
const remark = ref('')

function goBack() {
  uni.navigateBack()
}

function submit() {
  uni.showToast({ title: '请假已提交', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.name)
    studentName.value = decodeURIComponent(query.name)
})
</script>

<template>
  <view class="leave-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#101f26" />
      </button>
      <text class="nav-title">
        学员请假
      </text>
      <view class="nav-space" />
    </view>

    <view class="form-card">
      <view class="form-row">
        <text class="row-label">
          学员姓名
        </text>
        <view class="row-value">
          <image src="/static/images/avatar.jpg" mode="aspectFill" class="mini-avatar" />
          <text>{{ studentName }}</text>
        </view>
      </view>
      <view class="form-row">
        <text class="row-label">
          请假课程
        </text>
        <view class="row-value">
          <text>少儿钢琴进阶班（周三 16:00）</text>
          <uni-icons type="right" size="17" color="#6f7974" />
        </view>
      </view>
      <view class="form-row">
        <text class="row-label">
          请假日期
        </text>
        <view class="row-value">
          <uni-icons type="calendar" size="18" color="#6f7974" />
          <text>2023-11-15</text>
          <uni-icons type="right" size="17" color="#6f7974" />
        </view>
      </view>
      <view class="form-row">
        <text class="row-label">
          请假原因
        </text>
        <view class="row-value">
          <text>病假</text>
          <uni-icons type="right" size="17" color="#6f7974" />
        </view>
      </view>
      <view class="switch-row">
        <view>
          <view class="row-label">
            是否补课
          </view>
          <view class="row-desc">
            申请后需教务安排
          </view>
        </view>
        <switch :checked="makeup" color="#00684f" @change="makeup = $event.detail.value" />
      </view>
      <view class="remark-block">
        <text class="row-label">
          备注说明
        </text>
        <textarea v-model="remark" class="remark-area" placeholder="请输入详细的请假原因或其他需要老师注意的事项..." />
      </view>
    </view>

    <view class="flow-card">
      <view class="flow-title">
        审批流转
      </view>
      <view class="flow-row">
        <view class="flow-dot muted">
          <view class="inner" />
        </view>
        <view>
          <view class="flow-main">
            发起申请
          </view>
          <view class="flow-sub">
            待提交
          </view>
        </view>
      </view>
      <view class="flow-line" />
      <view class="flow-row">
        <view class="flow-dot active">
          <view class="inner" />
        </view>
        <view>
          <view class="flow-main active-text">
            待确认
          </view>
          <view class="flow-sub">
            需班主任/教务审核通过
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="submit">
        <uni-icons type="paperplane" size="20" color="#d9fff0" />
        <text>提交请假</text>
      </button>
      <button class="text-btn" @click="goBack">
        取消请假
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.leave-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 190rpx;
  color: #101f26;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 102rpx;
  margin: 0 -28rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #b8c6c0;
}

.back-btn,
.nav-space {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 800;
}

.form-card,
.flow-card {
  margin-top: 28rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
}

.form-row,
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 92rpx;
  border-bottom: 1rpx solid #d6e5ed;
}

.row-label {
  font-size: 30rpx;
  color: #101f26;
}

.row-value {
  display: flex;
  flex: 1;
  gap: 10rpx;
  align-items: center;
  justify-content: flex-end;
  min-width: 0;
  font-size: 30rpx;
  color: #34433d;
  text-align: right;
}

.mini-avatar {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
}

.row-desc {
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #6f7974;
}

.switch-row {
  align-items: center;
  padding: 24rpx 0;
}

.remark-block {
  padding-top: 30rpx;
}

.remark-area {
  width: 100%;
  height: 176rpx;
  box-sizing: border-box;
  margin-top: 24rpx;
  padding: 22rpx;
  font-size: 28rpx;
  line-height: 42rpx;
  background: #f3faff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
}

.flow-title {
  margin-bottom: 28rpx;
  font-size: 30rpx;
}

.flow-row {
  display: flex;
  gap: 28rpx;
  align-items: center;
  padding-left: 20rpx;
}

.flow-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42rpx;
  height: 42rpx;
  border: 4rpx solid #b8c6c0;
  border-radius: 50%;
}

.flow-dot.active {
  border-color: #00684f;
}

.flow-dot .inner {
  width: 18rpx;
  height: 18rpx;
  background: #6f7974;
  border-radius: 50%;
}

.flow-dot.active .inner {
  background: #00684f;
}

.flow-line {
  width: 4rpx;
  height: 62rpx;
  margin-left: 40rpx;
  background: #d6e5ed;
}

.flow-main {
  font-size: 30rpx;
}

.flow-main.active-text {
  color: #00684f;
}

.flow-sub {
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #6f7974;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 22rpx 28rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #b8c6c0;
}

.primary-btn {
  display: flex;
  gap: 12rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 82rpx;
  padding: 0;
  margin: 0;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 82rpx;
  color: #d9fff0;
  background: #1f7159;
  border-radius: 12rpx;
}

.text-btn {
  width: 100%;
  padding: 0;
  margin: 24rpx 0 0;
  font-size: 28rpx;
  line-height: 58rpx;
  color: #6f7974;
  background: transparent;
}
</style>
