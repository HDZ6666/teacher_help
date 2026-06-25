<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'StudentEnroll',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '报名续费',
  },
})

const hours = ref(10)
const amount = ref('')
const discount = ref('0.00')
const payment = ref('wechat')
const remark = ref('')

const finalAmount = computed(() => {
  const a = Number(amount.value || 0)
  const d = Number(discount.value || 0)
  return Math.max(a - d, 0).toFixed(2)
})

function goBack() {
  uni.navigateBack()
}

function changeHours(delta: number) {
  hours.value = Math.max(1, hours.value + delta)
}

function save(type: 'schedule' | 'enroll') {
  uni.showToast({ title: type === 'schedule' ? '已保存并进入排课' : '报名已保存', icon: 'success' })
}
</script>

<template>
  <view class="enroll-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#34433d" />
      </button>
      <text class="nav-title">
        报名续费
      </text>
      <view class="nav-space" />
    </view>

    <view class="student-card">
      <view class="student-avatar">
        李
      </view>
      <view class="student-info">
        <view class="student-name">
          李明轩
        </view>
        <view class="student-id">
          ID: 20230891
        </view>
      </view>
      <text class="status">
        在读
      </text>
    </view>

    <view class="form-card">
      <view class="field-block">
        <text class="field-label req">
          选择课程
        </text>
        <view class="select-box">
          <text>请点击选择课程</text>
          <uni-icons type="right" size="20" color="#6f7974" />
        </view>
      </view>
      <view class="field-block">
        <text class="field-label req">
          选择班级
        </text>
        <view class="select-box disabled">
          <text>请先选择课程</text>
          <uni-icons type="right" size="20" color="#a6b0ab" />
        </view>
      </view>
      <view class="field-block">
        <text class="field-label req">
          课时数量
        </text>
        <view class="stepper">
          <button @click="changeHours(-1)">
            <uni-icons type="minus" size="22" color="#101f26" />
          </button>
          <text>{{ hours }}</text>
          <button @click="changeHours(1)">
            <uni-icons type="plus" size="22" color="#101f26" />
          </button>
        </view>
      </view>
    </view>

    <view class="form-card">
      <view class="field-block">
        <text class="field-label req">
          费用金额 (¥)
        </text>
        <input v-model="amount" type="digit" class="input-box" placeholder="请输入金额">
      </view>
      <view class="field-block">
        <text class="field-label">
          优惠减免 (¥)
        </text>
        <input v-model="discount" type="digit" class="input-box" placeholder="0.00">
      </view>
      <view class="amount-row">
        <text>实收金额</text>
        <text class="amount">
          ¥ {{ finalAmount }}
        </text>
      </view>
    </view>

    <view class="form-card">
      <text class="field-label req">
        支付方式
      </text>
      <view class="pay-grid">
        <view class="pay-item" :class="{ active: payment === 'wechat' }" @click="payment = 'wechat'">
          <view class="radio" />
          <uni-icons type="chat" size="24" color="#07c160" />
          <text>微信</text>
        </view>
        <view class="pay-item" :class="{ active: payment === 'alipay' }" @click="payment = 'alipay'">
          <view class="radio" />
          <uni-icons type="wallet" size="24" color="#1677ff" />
          <text>支付宝</text>
        </view>
        <view class="pay-item" :class="{ active: payment === 'cash' }" @click="payment = 'cash'">
          <view class="radio" />
          <uni-icons type="wallet" size="24" color="#f5a623" />
          <text>现金</text>
        </view>
        <view class="pay-item" :class="{ active: payment === 'transfer' }" @click="payment = 'transfer'">
          <view class="radio" />
          <uni-icons type="loop" size="24" color="#4a90e2" />
          <text>转账</text>
        </view>
      </view>
    </view>

    <view class="form-card">
      <text class="field-label">
        备注信息
      </text>
      <textarea v-model="remark" class="remark-area" placeholder="请输入备注内容（选填）" />
    </view>

    <view class="bottom-bar">
      <button class="outline-btn" @click="save('schedule')">
        保存并排课
      </button>
      <button class="primary-btn" @click="save('enroll')">
        保存报名
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.enroll-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 170rpx;
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
  color: #00684f;
}

.student-card,
.form-card {
  margin-top: 28rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
}

.student-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.student-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  font-size: 34rpx;
  font-weight: 800;
  color: #ffffff;
  background: #007f5f;
  border-radius: 50%;
}

.student-info {
  flex: 1;
}

.student-name {
  font-size: 32rpx;
  font-weight: 800;
}

.student-id {
  margin-top: 6rpx;
  font-size: 26rpx;
}

.status {
  padding: 8rpx 22rpx;
  font-size: 26rpx;
  font-weight: 800;
  color: #00684f;
  background: #e9f6ef;
  border-radius: 999rpx;
}

.field-block {
  margin-bottom: 28rpx;
}

.field-block:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  margin-bottom: 16rpx;
  font-size: 26rpx;
  font-weight: 800;
  color: #34433d;
}

.field-label.req::after {
  margin-left: 6rpx;
  color: #ba1a1a;
  content: '*';
}

.select-box,
.input-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 78rpx;
  box-sizing: border-box;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 12rpx;
}

.select-box.disabled {
  color: #9aa5aa;
  border-color: #d6e5ed;
}

.stepper {
  display: grid;
  grid-template-columns: 88rpx 1fr 88rpx;
  height: 78rpx;
  overflow: hidden;
  border: 1rpx solid #b8c6c0;
  border-radius: 12rpx;
}

.stepper button {
  padding: 0;
  margin: 0;
  line-height: 78rpx;
  background: #e7f6fe;
  border-radius: 0;
}

.stepper text {
  font-size: 30rpx;
  line-height: 78rpx;
  text-align: center;
}

.amount-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 28rpx;
  margin-top: 30rpx;
  font-size: 28rpx;
  font-weight: 700;
  border-top: 1rpx solid #b8c6c0;
}

.amount {
  font-size: 40rpx;
  color: #00684f;
}

.pay-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
}

.pay-item {
  display: flex;
  gap: 12rpx;
  align-items: center;
  height: 76rpx;
  padding: 0 20rpx;
  border: 1rpx solid #b8c6c0;
  border-radius: 12rpx;
}

.pay-item.active {
  border-color: #1f7159;
}

.radio {
  width: 28rpx;
  height: 28rpx;
  border: 4rpx solid #b8c6c0;
  border-radius: 50%;
}

.pay-item.active .radio {
  border-color: #00684f;
  box-shadow: inset 0 0 0 6rpx #ffffff;
  background: #00684f;
}

.pay-item text {
  font-size: 28rpx;
}

.remark-area {
  width: 100%;
  height: 130rpx;
  box-sizing: border-box;
  padding: 20rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 12rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22rpx;
  padding: 22rpx 28rpx calc(22rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #b8c6c0;
}

.outline-btn,
.primary-btn {
  height: 82rpx;
  padding: 0;
  margin: 0;
  font-size: 30rpx;
  font-weight: 800;
  line-height: 82rpx;
  border-radius: 12rpx;
}

.outline-btn {
  color: #00684f;
  background: #ffffff;
  border: 2rpx solid #00684f;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
