<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'MeBusiness',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '经营管理概览',
  },
})

interface ItemStat {
  key: string
  label: string
  value: string
  prefix?: string
  icon: string
  tone: 'primary' | 'tertiary'
}

interface Room {
  id: number
  name: string
  capacity: string
  status: '使用中' | '空闲'
  extra: string
}

// 物品费用统计卡
const itemStats = ref<ItemStat[]>([
  { key: 'goods', label: '在售商品', value: '124', icon: 'cart', tone: 'primary' },
  { key: 'income', label: '今日收费', value: '2.4k', prefix: '¥', icon: 'wallet', tone: 'tertiary' },
])

// 会员卡概况
const memberCard = ref({
  total: '1,842',
  breakdown: [
    { label: '次卡', value: '856' },
    { label: '月卡/季卡', value: '420' },
    { label: '年卡', value: '566' },
  ],
})

// 场地管理
const occupancy = ref('68%')
const rooms = ref<Room[]>([
  { id: 1, name: 'A区101 舞蹈室', capacity: '容量: 20人', status: '使用中', extra: '当前: 18人' },
  { id: 2, name: 'A区201 钢琴房', capacity: '容量: 2人', status: '空闲', extra: '下一节: 14:00' },
  { id: 3, name: 'B区102 综合教室', capacity: '容量: 30人', status: '使用中', extra: '当前: 25人' },
])

function goBack() {
  uni.navigateBack()
}

function onSettings() {
  uni.showToast({ title: '设置', icon: 'none' })
}

function onAddItem() {
  uni.showToast({ title: '新增物品', icon: 'none' })
}
</script>

<template>
  <view class="business-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        经营管理概览
      </text>
      <button class="icon-btn right" @click="onSettings">
        <uni-icons type="gear" size="26" color="#005842" />
      </button>
    </view>

    <view class="page-body">
      <!-- 物品费用 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">
            物品费用
          </text>
          <button class="link-btn" @click="onAddItem">
            <uni-icons type="plusempty" size="16" color="#005842" />
            <text>新增</text>
          </button>
        </view>
        <view class="stat-grid">
          <view
            v-for="stat in itemStats"
            :key="stat.key"
            class="stat-card"
          >
            <view class="stat-top">
              <view class="stat-icon" :class="stat.tone">
                <uni-icons :type="stat.icon" size="18" :color="stat.tone === 'primary' ? '#1f7159' : '#00583d'" />
              </view>
              <text class="stat-label">
                {{ stat.label }}
              </text>
            </view>
            <view class="stat-value">
              <text v-if="stat.prefix" class="stat-prefix">{{ stat.prefix }}</text>{{ stat.value }}
            </view>
          </view>
        </view>
      </view>

      <!-- 会员卡概况 -->
      <view class="section">
        <text class="section-title">
          会员卡概况
        </text>
        <view class="member-card">
          <view class="member-top">
            <view>
              <text class="member-label">
                总活跃会员
              </text>
              <view class="member-total">
                {{ memberCard.total }}
              </view>
            </view>
            <view class="member-badge">
              <uni-icons type="wallet" size="24" color="#ffffff" />
            </view>
          </view>
          <view class="member-divider" />
          <view class="member-breakdown">
            <view
              v-for="b in memberCard.breakdown"
              :key="b.label"
              class="break-item"
            >
              <text class="break-label">
                {{ b.label }}
              </text>
              <text class="break-value">
                {{ b.value }}
              </text>
            </view>
          </view>
        </view>
      </view>

      <!-- 场地管理 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">
            场地管理 (今日)
          </text>
          <text class="occupancy-pill">
            占用率 {{ occupancy }}
          </text>
        </view>
        <view class="room-list">
          <view
            v-for="room in rooms"
            :key="room.id"
            class="room-card"
          >
            <view class="room-left">
              <view class="room-icon">
                <uni-icons type="location" size="22" :color="room.status === '使用中' ? '#005842' : '#6f7974'" />
              </view>
              <view class="room-info">
                <text class="room-name">
                  {{ room.name }}
                </text>
                <text class="room-cap">
                  {{ room.capacity }}
                </text>
              </view>
            </view>
            <view class="room-right">
              <view class="room-status" :class="room.status === '使用中' ? 'busy' : 'free'">
                <view v-if="room.status === '使用中'" class="status-dot" />
                <text>{{ room.status }}</text>
              </view>
              <text class="room-extra">
                {{ room.extra }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.business-page {
  min-height: 100vh;
  box-sizing: border-box;
  color: #0f1d23;
  background: #f3faff;
}

button::after {
  border: 0;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 102rpx;
  padding: 0 26rpx;
  background: #f3faff;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.icon-btn.right {
  justify-content: flex-end;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #005842;
}

.page-body {
  padding: 16rpx 28rpx 48rpx;
}

.section {
  margin-bottom: 40rpx;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.section-title {
  display: block;
  margin-bottom: 20rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #0f1d23;
}

.section-head .section-title {
  margin-bottom: 0;
}

.link-btn {
  display: flex;
  gap: 6rpx;
  align-items: center;
  padding: 0;
  margin: 0;
  font-size: 26rpx;
  font-weight: 600;
  color: #005842;
  background: transparent;
}

/* 物品费用统计卡 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.stat-top {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
}

.stat-icon.primary {
  background: #e6f4ee;
}

.stat-icon.tertiary {
  background: #e9f6ef;
}

.stat-label {
  font-size: 25rpx;
  font-weight: 600;
  color: #3f4944;
}

.stat-value {
  font-size: 52rpx;
  font-weight: 800;
  color: #0f1d23;
}

.stat-prefix {
  margin-right: 6rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #6f7974;
}

/* 会员卡概况 */
.member-card {
  position: relative;
  padding: 32rpx;
  overflow: hidden;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 8rpx 18rpx rgba(25, 63, 54, 0.18);
}

.member-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.member-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

.member-total {
  margin-top: 8rpx;
  font-size: 60rpx;
  font-weight: 800;
  line-height: 1.1;
}

.member-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88rpx;
  height: 88rpx;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 50%;
}

.member-divider {
  height: 1rpx;
  margin: 28rpx 0 24rpx;
  background: rgba(255, 255, 255, 0.14);
}

.member-breakdown {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.break-item {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.break-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.6);
}

.break-value {
  font-size: 30rpx;
  font-weight: 700;
}

/* 场地管理 */
.occupancy-pill {
  padding: 8rpx 18rpx;
  font-size: 22rpx;
  color: #3f4944;
  background: #e1f0f8;
  border-radius: 999rpx;
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.room-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.room-left {
  display: flex;
  gap: 22rpx;
  align-items: center;
  min-width: 0;
}

.room-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  background: #e1f0f8;
  border-radius: 50%;
}

.room-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}

.room-name {
  overflow: hidden;
  font-size: 30rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-cap {
  font-size: 24rpx;
  color: #3f4944;
}

.room-right {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  align-items: flex-end;
  flex-shrink: 0;
}

.room-status {
  display: inline-flex;
  gap: 8rpx;
  align-items: center;
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.room-status.busy {
  color: #227253;
  background: #e9f6ef;
}

.room-status.free {
  color: #3f4944;
  background: #e1f0f8;
  border: 1rpx solid rgba(190, 201, 195, 0.4);
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  background: #227253;
  border-radius: 50%;
}

.room-extra {
  font-size: 22rpx;
  color: #6f7974;
}
</style>
