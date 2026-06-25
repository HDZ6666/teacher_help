<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'MemberCardGrant',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '发放会员卡',
  },
})

const students = ['请选择学员', '张三 (Zhang San)', '李四 (Li Si)']
const studentIndex = ref(0)

const cardTypes = ['请选择会员卡类型', '年度畅学卡', '秋季强化班卡', '10课时次卡']
const cardIndex = ref(0)

const form = ref({
  amount: '',
  date: '',
  remark: '',
})

const payments = [
  { value: 'wechat', label: '微信', icon: 'weixin', color: '#1AAD19' },
  { value: 'alipay', label: '支付宝', icon: 'wallet', color: '#1677FF' },
  { value: 'cash', label: '现金', icon: 'paperplane', color: '#3f4944' },
  { value: 'balance', label: '余额', icon: 'wallet', color: '#3f4944' },
]
const payment = ref('wechat')

function goBack() {
  uni.navigateBack()
}
function onStudentChange(e: any) {
  studentIndex.value = Number(e.detail.value)
}
function onCardChange(e: any) {
  cardIndex.value = Number(e.detail.value)
}
function onDateChange(e: any) {
  form.value.date = e.detail.value
}
function onConfirm() {
  if (studentIndex.value === 0) {
    uni.showToast({ title: '请选择学员', icon: 'none' })
    return
  }
  if (cardIndex.value === 0) {
    uni.showToast({ title: '请选择会员卡', icon: 'none' })
    return
  }
  uni.showToast({ title: '发放成功', icon: 'success' })
  setTimeout(() => {
    uni.navigateTo({ url: '/pages/member-card/grant-record' })
  }, 700)
}
</script>

<template>
  <view class="grant-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        发放会员卡
      </text>
      <view class="icon-btn" />
    </view>

    <view class="form-card">
      <!-- 选择学员 -->
      <view class="field">
        <text class="field-label">
          选择学员
        </text>
        <picker mode="selector" :range="students" :value="studentIndex" @change="onStudentChange">
          <view class="picker-box" :class="{ ph: studentIndex === 0 }">
            <text>{{ students[studentIndex] }}</text>
            <uni-icons type="bottom" size="18" color="#3f4944" />
          </view>
        </picker>
      </view>

      <!-- 选择会员卡 -->
      <view class="field">
        <text class="field-label">
          选择会员卡
        </text>
        <picker mode="selector" :range="cardTypes" :value="cardIndex" @change="onCardChange">
          <view class="picker-box" :class="{ ph: cardIndex === 0 }">
            <text>{{ cardTypes[cardIndex] }}</text>
            <uni-icons type="bottom" size="18" color="#3f4944" />
          </view>
        </picker>
      </view>

      <!-- 实收金额 -->
      <view class="field">
        <text class="field-label">
          实收金额
        </text>
        <view class="amount-box">
          <text class="cny">
            ¥
          </text>
          <input v-model="form.amount" type="digit" class="amount-input" placeholder="0.00">
        </view>
      </view>

      <view class="divider" />

      <!-- 支付方式 -->
      <view class="field">
        <text class="field-label">
          支付方式
        </text>
        <view class="pay-grid">
          <view
            v-for="p in payments"
            :key="p.value"
            class="pay-item"
            :class="{ on: payment === p.value }"
            @click="payment = p.value"
          >
            <uni-icons :type="p.icon" size="20" :color="p.color" />
            <text>{{ p.label }}</text>
          </view>
        </view>
      </view>

      <!-- 生效日期 -->
      <view class="field">
        <text class="field-label">
          生效日期
        </text>
        <picker mode="date" :value="form.date" @change="onDateChange">
          <view class="picker-box" :class="{ ph: !form.date }">
            <text>{{ form.date || '请选择日期' }}</text>
            <uni-icons type="calendar" size="18" color="#3f4944" />
          </view>
        </picker>
      </view>

      <!-- 备注 -->
      <view class="field">
        <text class="field-label">
          备注
        </text>
        <textarea v-model="form.remark" class="field-area" placeholder="添加备注信息..." />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onConfirm">
        确认发放
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.grant-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 170rpx;
  color: #0f1d23;
  background: #f3faff;
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
  padding: 0 20rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.icon-btn {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #005842;
  text-align: center;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  margin-top: 28rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.field-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #3f4944;
}

.picker-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  height: 88rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #0f1d23;
  background: transparent;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.picker-box.ph {
  color: #6f7974;
}

.amount-box {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 88rpx;
  padding: 0 24rpx;
  background: transparent;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.cny {
  margin-right: 12rpx;
  font-size: 28rpx;
  color: #3f4944;
}

.amount-input {
  flex: 1;
  font-size: 28rpx;
}

.divider {
  height: 1rpx;
  background: #e7ece9;
}

.pay-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.pay-item {
  display: flex;
  gap: 12rpx;
  align-items: center;
  padding: 22rpx;
  font-size: 26rpx;
  color: #0f1d23;
  background: transparent;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.pay-item.on {
  background: #c2ebde;
  border-color: #005842;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: transparent;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn {
  width: 100%;
  height: 92rpx;
  margin: 0;
  font-size: 32rpx;
  font-weight: 600;
  line-height: 92rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
