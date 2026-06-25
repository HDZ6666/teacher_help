<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ItemIndex',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '物品费用',
  },
})

const keyword = ref('')
const tabs = ['物品', '费用', '库存流水']
const activeTab = ref('物品')

const stats = ref([
  { key: 'total', label: '物品总数', value: 128, icon: 'list', type: 'normal' },
  { key: 'warn', label: '库存预警', value: 5, icon: 'info', type: 'danger' },
  { key: 'in', label: '今日入库', value: 45, icon: 'paperplane', type: 'normal' },
  { key: 'out', label: '今日出库', value: 12, icon: 'paperplane-filled', type: 'normal' },
])

function goBack() {
  uni.navigateBack()
}
function onAdd() {
  uni.navigateTo({ url: '/pages/item/edit' })
}
function onTab(t: string) {
  activeTab.value = t
  if (t === '物品')
    uni.navigateTo({ url: '/pages/item/list' })
  else if (t === '费用')
    uni.navigateTo({ url: '/pages/item/fee' })
  else if (t === '库存流水')
    uni.navigateTo({ url: '/pages/item/stock-log' })
}
function goPurchase() {
  uni.navigateTo({ url: '/pages/item/purchase' })
}
</script>

<template>
  <view class="item-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        物品费用
      </text>
      <button class="icon-btn" @click="onAdd">
        <uni-icons type="plusempty" size="26" color="#005842" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="24" color="#6f7974" />
      <input v-model="keyword" class="search-input" placeholder="搜索物品或费用名称" placeholder-class="ph">
    </view>

    <view class="seg">
      <view
        v-for="t in tabs"
        :key="t"
        class="seg-item"
        :class="{ on: activeTab === t }"
        @click="onTab(t)"
      >
        {{ t }}
      </view>
    </view>

    <view class="stat-grid">
      <view
        v-for="s in stats"
        :key="s.key"
        class="stat-card"
        :class="{ danger: s.type === 'danger' }"
        @click="s.key === 'warn' ? goPurchase() : null"
      >
        <view class="stat-head">
          <uni-icons :type="s.icon === 'paperplane-filled' ? 'paperplane' : s.icon" size="20" :color="s.type === 'danger' ? '#93000a' : '#3f4944'" />
          <text class="stat-label">
            {{ s.label }}
          </text>
        </view>
        <text class="stat-value" :class="{ danger: s.type === 'danger' }">
          {{ s.value }}
        </text>
      </view>
    </view>

    <view class="quick-grid">
      <view class="quick-btn" @click="goPurchase">
        <uni-icons type="paperplane" size="22" color="#1f7159" />
        <text>采购入库</text>
      </view>
      <view class="quick-btn" @click="uni.navigateTo({ url: '/pages/item/stock-log' })">
        <uni-icons type="loop" size="22" color="#1f7159" />
        <text>库存流水</text>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.item-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 40rpx;
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
  font-size: 36rpx;
  font-weight: 700;
  color: #005842;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
  height: 80rpx;
  margin-top: 24rpx;
  padding: 0 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
}

.ph {
  color: #6f7974;
}

.seg {
  display: flex;
  gap: 6rpx;
  margin-top: 24rpx;
  padding: 8rpx;
  background: #e7f6fe;
  border-radius: 14rpx;
}

.seg-item {
  flex: 1;
  font-size: 25rpx;
  line-height: 60rpx;
  color: #3f4944;
  text-align: center;
  border-radius: 10rpx;
}

.seg-item.on {
  font-weight: 700;
  color: #1f7159;
  background: #ffffff;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
  margin-top: 24rpx;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.stat-card.danger {
  background: #ffeceb;
  border-color: #ffdad6;
}

.stat-head {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 24rpx;
  color: #3f4944;
}

.stat-label {
  font-size: 24rpx;
}

.stat-value {
  font-size: 52rpx;
  font-weight: 700;
  color: #1f7159;
}

.stat-value.danger {
  color: #ba1a1a;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
  margin-top: 24rpx;
}

.quick-btn {
  display: flex;
  gap: 12rpx;
  align-items: center;
  justify-content: center;
  height: 96rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}
</style>
