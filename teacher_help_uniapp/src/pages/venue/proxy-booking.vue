<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'VenueProxyBooking',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '代预约',
  },
})

const booking = ref({
  venue: 'A工作室 - 市中心校区',
  date: '2023年10月24日',
  time: '14:00 - 15:30',
})

const userType = ref<'student' | 'guest'>('student')
const form = ref({
  name: '',
  phone: '',
  discount: '',
  waiver: '',
  remark: '',
})
const payMethods = ['微信', '支付宝', '现金']
const activePay = ref('微信')
const finalAmount = ref('150.00')

function goBack() {
  uni.navigateBack()
}
function onConfirm() {
  if (!form.value.name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' })
    return
  }
  uni.showToast({ title: '预约成功', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.venue)
    booking.value.venue = decodeURIComponent(query.venue)
  if (query?.start && query?.end)
    booking.value.time = `${query.start} - ${query.end}`
})
</script>

<template>
  <view class="pb-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        代预约
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 预约信息（只读） -->
    <view class="card">
      <text class="card-cap">
        预约信息
      </text>
      <view class="info-row">
        <uni-icons type="shop" size="20" color="#6f7974" />
        <view>
          <text class="info-label">
            场地
          </text>
          <text class="info-value">
            {{ booking.venue }}
          </text>
        </view>
      </view>
      <view class="divider" />
      <view class="info-row">
        <uni-icons type="calendar" size="20" color="#6f7974" />
        <view>
          <text class="info-label">
            日期
          </text>
          <text class="info-value">
            {{ booking.date }}
          </text>
        </view>
      </view>
      <view class="divider" />
      <view class="info-row">
        <uni-icons type="loop" size="20" color="#6f7974" />
        <view>
          <text class="info-label">
            时段
          </text>
          <text class="info-value">
            {{ booking.time }}
          </text>
        </view>
      </view>
    </view>

    <!-- 用户信息 -->
    <text class="section-cap">
      用户信息
    </text>
    <view class="seg">
      <view
        class="seg-item"
        :class="{ on: userType === 'student' }"
        @click="userType = 'student'"
      >
        学员
      </view>
      <view
        class="seg-item"
        :class="{ on: userType === 'guest' }"
        @click="userType = 'guest'"
      >
        访客
      </view>
    </view>
    <view class="field">
      <text class="field-label">
        姓名
      </text>
      <input v-model="form.name" class="field-input" placeholder="请输入用户姓名">
    </view>
    <view class="field">
      <text class="field-label">
        手机号
      </text>
      <input v-model="form.phone" type="number" class="field-input" placeholder="请输入手机号">
    </view>

    <!-- 支付信息 -->
    <text class="section-cap">
      支付信息
    </text>
    <view class="two-col">
      <view class="field">
        <text class="field-label">
          折扣 (%)
        </text>
        <input v-model="form.discount" type="number" class="field-input right" placeholder="0">
      </view>
      <view class="field">
        <text class="field-label">
          减免 (￥)
        </text>
        <input v-model="form.waiver" type="number" class="field-input right" placeholder="0.00">
      </view>
    </view>
    <view class="final-box">
      <text class="final-label">
        实付金额
      </text>
      <text class="final-value">
        ￥ {{ finalAmount }}
      </text>
    </view>
    <view class="field">
      <text class="field-label">
        支付方式
      </text>
      <view class="pay-grid">
        <view
          v-for="p in payMethods"
          :key="p"
          class="pay-item"
          :class="{ on: activePay === p }"
          @click="activePay = p"
        >
          {{ p }}
        </view>
      </view>
    </view>
    <view class="field">
      <text class="field-label">
        备注（选填）
      </text>
      <textarea v-model="form.remark" class="field-area" placeholder="为本次预约添加备注..." />
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onConfirm">
        确认预约
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.pb-page {
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
  font-size: 34rpx;
  font-weight: 600;
  color: #005842;
}

.card {
  margin-top: 24rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.card-cap {
  font-size: 22rpx;
  letter-spacing: 2rpx;
  color: #3f4944;
}

.info-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  margin-top: 18rpx;
}

.info-label {
  display: block;
  font-size: 22rpx;
  color: #3f4944;
}

.info-value {
  display: block;
  margin-top: 4rpx;
  font-size: 28rpx;
}

.divider {
  height: 1rpx;
  margin-top: 18rpx;
  background: #d6e5ed;
}

.section-cap {
  display: block;
  margin-top: 36rpx;
  margin-bottom: 16rpx;
  font-size: 22rpx;
  letter-spacing: 2rpx;
  color: #3f4944;
}

.seg {
  display: flex;
  gap: 6rpx;
  padding: 8rpx;
  background: #dbebf3;
  border-radius: 12rpx;
}

.seg-item {
  flex: 1;
  font-size: 26rpx;
  line-height: 64rpx;
  color: #3f4944;
  text-align: center;
  border-radius: 8rpx;
}

.seg-item.on {
  font-weight: 600;
  color: #1f7159;
  background: #ffffff;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-top: 22rpx;
}

.field-label {
  font-size: 24rpx;
  color: #3f4944;
}

.field-input {
  box-sizing: border-box;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.field-input.right {
  text-align: right;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.final-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24rpx;
  padding: 28rpx;
  background: #e7f6fe;
  border: 1rpx solid #1f7159;
  border-radius: 12rpx;
}

.final-label {
  font-size: 26rpx;
  color: #1f7159;
}

.final-value {
  font-size: 36rpx;
  font-weight: 700;
  color: #1f7159;
}

.pay-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.pay-item {
  font-size: 26rpx;
  line-height: 84rpx;
  color: #3f4944;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.pay-item.on {
  color: #1f7159;
  background: #e7f6fe;
  border-color: #1f7159;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #f3faff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn {
  width: 100%;
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
