<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'VenueCancel',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '取消预约',
  },
})

const bookingId = ref('BK202606250014')
const refundAmount = ref('150.00')
const selectedReason = ref('schedule')
const remark = ref('')
const notifyUser = ref(true)

const target = ref({
  title: 'A101 教室预约',
  time: '今天 14:00 - 15:30',
  place: 'A101 教室 - 北校区',
  user: '张三',
})

const reasons = [
  { key: 'schedule', label: '时间冲突' },
  { key: 'venue', label: '场地调整' },
  { key: 'user', label: '用户临时取消' },
  { key: 'other', label: '其他原因' },
]

function goBack() {
  uni.navigateBack()
}

function onConfirm() {
  if (!selectedReason.value) {
    uni.showToast({ title: '请选择取消原因', icon: 'none' })
    return
  }
  uni.showToast({ title: '已取消预约', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.id)
    bookingId.value = query.id
})
</script>

<template>
  <view class="cancel-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        取消预约
      </text>
      <view class="icon-btn" />
    </view>

    <view class="warn-card">
      <uni-icons type="info-filled" size="30" color="#ba1a1a" />
      <view class="warn-main">
        <text class="warn-title">
          取消规则
        </text>
        <text class="warn-desc">
          临近开始时间的预约取消可能产生费用，请核对退款金额并记录原因。
        </text>
      </view>
    </view>

    <view class="target-card">
      <text class="card-cap">
        目标预约
      </text>
      <view class="target-row">
        <view class="target-icon">
          <uni-icons type="home" size="26" color="#005842" />
        </view>
        <view class="target-main">
          <text class="target-title">
            {{ target.title }}
          </text>
          <text class="target-sub">
            {{ target.time }} · {{ target.place }}
          </text>
          <text class="target-user">
            预约人：{{ target.user }} · {{ bookingId }}
          </text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-label">
        退款金额（¥）
      </text>
      <view class="money-field">
        <text class="money-symbol">
          ¥
        </text>
        <input v-model="refundAmount" class="money-input" type="digit">
      </view>
      <text class="helper">
        根据当前预约规则自动计算，可在接入后端后由接口返回。
      </text>
    </view>

    <view class="section">
      <text class="section-label">
        取消原因
      </text>
      <view class="reason-list">
        <view
          v-for="r in reasons"
          :key="r.key"
          class="reason-item"
          @click="selectedReason = r.key"
        >
          <view class="radio" :class="{ on: selectedReason === r.key }">
            <view v-if="selectedReason === r.key" class="radio-in" />
          </view>
          <text>{{ r.label }}</text>
        </view>
      </view>
      <textarea v-model="remark" class="reason-area" placeholder="请补充说明取消原因..." />
    </view>

    <view class="notify-card" @click="notifyUser = !notifyUser">
      <view class="notify-text">
        <text class="notify-title">
          通知用户
        </text>
        <text class="notify-desc">
          取消后发送短信 / 微信通知，并同步退款说明。
        </text>
      </view>
      <view class="switch" :class="{ on: notifyUser }">
        <view class="switch-dot" />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onConfirm">
        确认取消
      </button>
      <button class="ghost-btn" @click="goBack">
        返回
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cancel-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 250rpx;
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
  font-size: 34rpx;
  font-weight: 700;
  color: #005842;
}

.warn-card {
  display: flex;
  gap: 18rpx;
  margin-top: 28rpx;
  padding: 24rpx;
  background: #ffdad6;
  border: 1rpx solid rgba(186, 26, 26, 0.3);
  border-radius: 16rpx;
}

.warn-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.warn-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #93000a;
}

.warn-desc {
  font-size: 26rpx;
  line-height: 38rpx;
  color: #93000a;
}

.target-card,
.notify-card {
  margin-top: 28rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.card-cap {
  display: block;
  margin-bottom: 18rpx;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
  color: #3f4944;
}

.target-row {
  display: flex;
  gap: 20rpx;
  align-items: center;
}

.target-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 82rpx;
  height: 82rpx;
  background: #e1f0f8;
  border-radius: 12rpx;
}

.target-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6rpx;
}

.target-title {
  font-size: 30rpx;
  font-weight: 700;
}

.target-sub,
.target-user {
  font-size: 24rpx;
  line-height: 34rpx;
  color: #3f4944;
}

.section {
  margin-top: 30rpx;
}

.section-label {
  display: block;
  margin-bottom: 14rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #3f4944;
}

.money-field {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.money-symbol {
  margin-right: 18rpx;
  font-size: 28rpx;
  color: #3f4944;
}

.money-input {
  flex: 1;
  height: 88rpx;
  font-size: 32rpx;
  font-weight: 600;
}

.helper {
  display: block;
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 34rpx;
  color: #6f7974;
}

.reason-list {
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.reason-item {
  display: flex;
  gap: 18rpx;
  align-items: center;
  min-height: 86rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  border-bottom: 1rpx solid #d6e5ed;
}

.reason-item:last-child {
  border-bottom: 0;
}

.radio {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34rpx;
  height: 34rpx;
  border: 2rpx solid #6f7974;
  border-radius: 50%;
}

.radio.on {
  border-color: #1f7159;
}

.radio-in {
  width: 18rpx;
  height: 18rpx;
  background: #1f7159;
  border-radius: 50%;
}

.reason-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  margin-top: 24rpx;
  padding: 22rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.notify-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.notify-text {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6rpx;
  padding-right: 24rpx;
}

.notify-title {
  font-size: 32rpx;
  font-weight: 700;
}

.notify-desc {
  font-size: 24rpx;
  line-height: 34rpx;
  color: #3f4944;
}

.switch {
  position: relative;
  flex-shrink: 0;
  width: 88rpx;
  height: 48rpx;
  background: #bec9c3;
  border-radius: 999rpx;
}

.switch.on {
  background: #1f7159;
}

.switch-dot {
  position: absolute;
  top: 5rpx;
  left: 5rpx;
  width: 38rpx;
  height: 38rpx;
  background: #ffffff;
  border-radius: 50%;
  transition: left 0.2s ease;
}

.switch.on .switch-dot {
  left: 45rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #f3faff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn,
.ghost-btn {
  width: 100%;
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}

.ghost-btn {
  color: #005842;
  background: transparent;
  border: 1rpx solid #1f7159;
}
</style>
