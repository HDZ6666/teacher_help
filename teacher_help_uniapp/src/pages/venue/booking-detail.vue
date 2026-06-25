<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

defineOptions({
  name: 'VenueBookingDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '预约详情',
  },
})

const checkedIn = ref(false)
const booking = ref({
  id: 'BK202606250014',
  userName: '张三',
  initial: '张',
  phone: '138 0013 8000',
  venue: 'A101 教室 - 北校区',
  address: '北校区 1 号楼 1 层',
  date: '2026年06月25日',
  time: '14:00 - 15:30',
  amount: '¥ 150.00',
  source: 'App',
  orderNo: 'ORD202606250018',
  checkinTime: '',
  operator: '',
})

const detailRows = computed(() => [
  { label: '场地', value: booking.value.venue },
  { label: '日期时间', value: `${booking.value.date}\n${booking.value.time}`, right: true },
  { label: '支付金额', value: booking.value.amount },
  { label: '预约来源', value: booking.value.source },
  { label: '订单编号', value: booking.value.orderNo },
])

function goBack() {
  uni.navigateBack()
}

function onMore() {
  uni.showActionSheet({
    itemList: ['查看订单', '取消预约'],
    success: ({ tapIndex }) => {
      if (tapIndex === 0)
        onViewOrder()
      if (tapIndex === 1)
        onCancel()
    },
  })
}

function onCall() {
  uni.showToast({ title: `联系 ${booking.value.userName}`, icon: 'none' })
}

function onCancel() {
  uni.navigateTo({ url: `/pages/venue/cancel?id=${booking.value.id}` })
}

function onViewOrder() {
  uni.showToast({ title: '查看订单', icon: 'none' })
}

function onCheckIn() {
  if (checkedIn.value) {
    uni.showToast({ title: '该预约已核销', icon: 'none' })
    return
  }
  checkedIn.value = true
  booking.value.checkinTime = '2026-06-25 13:48'
  booking.value.operator = '李老师'
  uni.showToast({ title: '核销成功', icon: 'success' })
}

function onMap() {
  uni.showToast({ title: '查看地图', icon: 'none' })
}

onLoad((query) => {
  if (query?.slot)
    booking.value.time = `${query.slot} - 10:00`
  if (query?.id)
    booking.value.id = `BK2026062500${query.id}`
})
</script>

<template>
  <view class="detail-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        预约详情
      </text>
      <button class="icon-btn" @click="onMore">
        <uni-icons type="more-filled" size="24" color="#005842" />
      </button>
    </view>

    <view class="status-chip" :class="{ checked: checkedIn }">
      <uni-icons :type="checkedIn ? 'checkbox-filled' : 'checkbox'" size="18" :color="checkedIn ? '#ffffff' : '#227253'" />
      <text>{{ checkedIn ? '已核销' : '已预约' }}</text>
    </view>

    <view class="info-card">
      <view class="user-row">
        <view class="avatar">
          {{ booking.initial }}
        </view>
        <view class="user-main">
          <text class="user-name">
            {{ booking.userName }}
          </text>
          <view class="phone-row">
            <uni-icons type="phone" size="16" color="#3f4944" />
            <text>{{ booking.phone }}</text>
          </view>
        </view>
        <button class="call-btn" @click="onCall">
          <uni-icons type="phone-filled" size="24" color="#005842" />
        </button>
      </view>

      <view class="divider" />

      <view class="detail-list">
        <view
          v-for="row in detailRows"
          :key="row.label"
          class="detail-row"
        >
          <text class="row-label">
            {{ row.label }}
          </text>
          <text class="row-value" :class="{ right: row.right }">
            {{ row.value }}
          </text>
        </view>
      </view>
    </view>

    <view v-if="checkedIn" class="check-card">
      <view class="check-head">
        <uni-icons type="auth-filled" size="22" color="#1f7159" />
        <text>核销信息</text>
      </view>
      <view class="check-row">
        <text>核销时间</text>
        <text>{{ booking.checkinTime }}</text>
      </view>
      <view class="check-row">
        <text>操作人</text>
        <text>{{ booking.operator }}</text>
      </view>
    </view>

    <view class="map-card" @click="onMap">
      <view class="map-lines">
        <view class="road road-a" />
        <view class="road road-b" />
        <view class="road road-c" />
        <view class="pin">
          <uni-icons type="location-filled" size="52" color="#1f7159" />
        </view>
      </view>
      <view class="map-action">
        <uni-icons type="location" size="18" color="#3f4944" />
        <text>查看地图</text>
      </view>
    </view>

    <view class="address-row">
      <uni-icons type="location" size="18" color="#6f7974" />
      <text>{{ booking.address }}</text>
    </view>

    <view class="bottom-bar">
      <view class="ghost-row">
        <button class="ghost-btn" @click="onCancel">
          取消预约
        </button>
        <button class="ghost-btn" @click="onViewOrder">
          查看订单
        </button>
      </view>
      <button class="primary-btn" :class="{ done: checkedIn }" @click="onCheckIn">
        {{ checkedIn ? '已核销' : '核销' }}
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 230rpx;
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

.status-chip {
  display: inline-flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 32rpx;
  padding: 10rpx 24rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #227253;
  background: #e9f6ef;
  border: 1rpx solid rgba(34, 114, 83, 0.22);
  border-radius: 999rpx;
}

.status-chip.checked {
  color: #ffffff;
  background: #1f7159;
}

.info-card {
  margin-top: 24rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 92rpx;
  height: 92rpx;
  font-size: 38rpx;
  font-weight: 700;
  color: #a4f2d4;
  background: #1f7159;
  border-radius: 50%;
}

.user-main {
  flex: 1;
}

.user-name {
  font-size: 36rpx;
  font-weight: 700;
}

.phone-row {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 6rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.call-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: #e9f6ef;
  border-radius: 50%;
}

.divider {
  height: 1rpx;
  margin: 28rpx 0 18rpx;
  background: #bec9c3;
}

.detail-list {
  display: flex;
  flex-direction: column;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 24rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #d6e5ed;
}

.detail-row:last-child {
  border-bottom: 0;
}

.row-label {
  flex-shrink: 0;
  font-size: 26rpx;
  color: #3f4944;
}

.row-value {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 40rpx;
  text-align: right;
  white-space: pre-line;
}

.row-value.right {
  line-height: 42rpx;
}

.check-card {
  margin-top: 24rpx;
  padding: 24rpx;
  background: #e9f6ef;
  border: 1rpx solid rgba(31, 113, 89, 0.22);
  border-radius: 16rpx;
}

.check-head {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 30rpx;
  font-weight: 700;
  color: #1f7159;
}

.check-row {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.check-row text:last-child {
  font-weight: 600;
  color: #0f1d23;
}

.map-card {
  position: relative;
  height: 230rpx;
  margin-top: 24rpx;
  overflow: hidden;
  background: linear-gradient(135deg, #a7cfc2, #d6e5ed);
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.map-lines {
  position: absolute;
  inset: 0;
}

.road {
  position: absolute;
  height: 14rpx;
  background: rgba(255, 255, 255, 0.62);
  border-radius: 999rpx;
}

.road-a {
  top: 64rpx;
  left: 100rpx;
  width: 520rpx;
  transform: rotate(23deg);
}

.road-b {
  top: 134rpx;
  left: 30rpx;
  width: 560rpx;
  transform: rotate(-20deg);
}

.road-c {
  top: 168rpx;
  left: 210rpx;
  width: 360rpx;
  transform: rotate(17deg);
}

.pin {
  position: absolute;
  top: 42rpx;
  left: 50%;
  transform: translateX(-50%);
}

.map-action {
  position: absolute;
  left: 24rpx;
  bottom: 24rpx;
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 10rpx 18rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #3f4944;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 10rpx;
}

.address-row {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #6f7974;
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

.ghost-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.ghost-btn,
.primary-btn {
  height: 88rpx;
  margin: 0;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  color: #005842;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  width: 100%;
  color: #ffffff;
  background: #1f7159;
}

.primary-btn.done {
  background: #6f7974;
}
</style>
