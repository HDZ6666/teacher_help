<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ItemPurchase',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '采购入库',
  },
})

const form = ref({
  item: '',
  spec: '',
  date: '',
  unitPrice: '',
  quantity: '',
  payment: '',
  handler: '',
  remark: '',
})

const payments = ['银行转账', '企业支付宝', '备用金']

const total = computed(() => {
  const price = Number.parseFloat(form.value.unitPrice) || 0
  const qty = Number.parseInt(form.value.quantity) || 0
  return (price * qty).toFixed(2)
})

function goBack() {
  uni.navigateBack()
}
function onPayment(e: any) {
  form.value.payment = payments[e.detail.value]
}
function onDate(e: any) {
  form.value.date = e.detail.value
}
function confirm() {
  if (!form.value.item) {
    uni.showToast({ title: '请选择物品', icon: 'none' })
    return
  }
  uni.showToast({ title: '已确认入库', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="ip-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        采购入库
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 物品信息 -->
    <view class="card">
      <view class="card-title">
        <uni-icons type="list" size="16" color="#005842" />
        <text>物品信息</text>
      </view>
      <view class="field">
        <text class="field-label">
          选择物品 <text class="req">*</text>
        </text>
        <view class="prefix-input">
          <input v-model="form.item" class="field-input pr" placeholder="搜索物品名称、编码或SKU...">
          <uni-icons type="search" size="22" color="#6f7974" class="suffix" />
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          规格
        </text>
        <input v-model="form.spec" class="field-input readonly" placeholder="选择物品后显示规格" disabled>
      </view>
    </view>

    <!-- 采购数据 -->
    <view class="card">
      <view class="card-title">
        <uni-icons type="wallet" size="16" color="#005842" />
        <text>采购数据</text>
      </view>
      <view class="field">
        <text class="field-label">
          采购日期 <text class="req">*</text>
        </text>
        <picker mode="date" @change="onDate">
          <view class="field-input picker-val">
            <text :class="{ ph: !form.date }">{{ form.date || '请选择日期' }}</text>
            <uni-icons type="calendar" size="22" color="#6f7974" />
          </view>
        </picker>
      </view>
      <view class="two-col">
        <view class="field">
          <text class="field-label">
            单价 <text class="req">*</text>
          </text>
          <view class="prefix-input">
            <text class="prefix">
              ¥
            </text>
            <input v-model="form.unitPrice" type="number" class="field-input pl" placeholder="0.00">
          </view>
        </view>
        <view class="field">
          <text class="field-label">
            数量 <text class="req">*</text>
          </text>
          <input v-model="form.quantity" type="number" class="field-input" placeholder="0">
        </view>
      </view>
      <view class="total-box">
        <text class="total-label">
          总金额
        </text>
        <text class="total-value">
          <text class="cny">¥</text>{{ total }}
        </text>
      </view>
      <view class="field">
        <text class="field-label">
          支付方式
        </text>
        <picker :range="payments" @change="onPayment">
          <view class="field-input picker-val">
            <text :class="{ ph: !form.payment }">{{ form.payment || '请选择支付方式' }}</text>
            <uni-icons type="bottom" size="18" color="#6f7974" />
          </view>
        </picker>
      </view>
    </view>

    <!-- 管理信息 -->
    <view class="card">
      <view class="card-title">
        <uni-icons type="staff" size="16" color="#005842" />
        <text>管理信息</text>
      </view>
      <view class="field">
        <text class="field-label">
          经办人
        </text>
        <view class="prefix-input">
          <uni-icons type="person" size="20" color="#6f7974" class="lead" />
          <input v-model="form.handler" class="field-input pl2" placeholder="经办人姓名">
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          备注
        </text>
        <textarea v-model="form.remark" class="field-area" placeholder="补充说明..." />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="confirm">
        <uni-icons type="checkmarkempty" size="20" color="#ffffff" />
        <text>确认入库</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ip-page {
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
  font-weight: 700;
  color: #005842;
}

.card {
  margin-top: 22rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.card-title {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 24rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
  color: #005842;
  text-transform: uppercase;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-top: 24rpx;
}

.field-label {
  font-size: 24rpx;
  color: #3f4944;
}

.req {
  color: #ba1a1a;
}

.field-input {
  box-sizing: border-box;
  width: 100%;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 8rpx;
}

.field-input.readonly {
  color: #6f7974;
  background: #f3faff;
  border-style: dashed;
}

.prefix-input {
  position: relative;
  display: flex;
  align-items: center;
}

.prefix {
  position: absolute;
  left: 24rpx;
  font-size: 28rpx;
  color: #3f4944;
}

.suffix {
  position: absolute;
  right: 24rpx;
}

.lead {
  position: absolute;
  left: 22rpx;
}

.field-input.pl {
  padding-left: 56rpx;
}

.field-input.pl2 {
  padding-left: 64rpx;
}

.field-input.pr {
  padding-right: 64rpx;
}

.picker-val {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ph {
  color: #6f7974;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.total-box {
  margin-top: 24rpx;
  padding: 22rpx;
  background: #f3faff;
  border: 1rpx solid #bec9c3;
  border-radius: 8rpx;
}

.total-label {
  font-size: 24rpx;
  color: #3f4944;
}

.total-value {
  display: block;
  margin-top: 8rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #1f7159;
}

.cny {
  font-size: 28rpx;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 160rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 8rpx;
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
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 90rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}
</style>
