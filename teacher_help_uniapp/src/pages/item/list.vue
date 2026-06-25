<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ItemList',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '物品列表',
  },
})

interface Item {
  id: number
  name: string
  spec: string
  price: string
  stock: string
  stockState: 'ok' | 'warn'
  tag: string
  icon?: string
  primaryAction: string
  secondaryAction: string
  secondaryDisabled?: boolean
  primaryDanger?: boolean
}

const filters = ['全部', '教材', '文具', '设备']
const activeFilter = ref('全部')

const items = ref<Item[]>([
  { id: 1, name: '少儿英语教材 (Level 1)', spec: '规格: A4全彩精装', price: '¥85.00', stock: '45件', stockState: 'ok', tag: '线上售卖', icon: 'paperplane', secondaryAction: '领用', primaryAction: '入库' },
  { id: 2, name: '学生随堂测验纸', spec: '规格: B5单色 100张/包', price: '¥15.00', stock: '3包', stockState: 'warn', tag: '内部领用', icon: 'list', secondaryAction: '领用', secondaryDisabled: true, primaryAction: '紧急采购', primaryDanger: true },
  { id: 3, name: '教学平板电脑 (备用)', spec: '规格: 10.5英寸 64G', price: '--', stock: '12台', stockState: 'ok', tag: '固定资产', icon: 'gear', secondaryAction: '借用', primaryAction: '归还登记' },
])

const filteredItems = computed(() => items.value)

function goBack() {
  uni.navigateBack()
}
function onDetail() {
  uni.showToast({ title: '查看详情', icon: 'none' })
}
function onEdit() {
  uni.navigateTo({ url: '/pages/item/edit?id=1' })
}
function onPrimary(it: Item) {
  if (it.primaryDanger)
    uni.navigateTo({ url: '/pages/item/purchase' })
  else if (it.primaryAction === '入库')
    uni.navigateTo({ url: '/pages/item/purchase' })
  else
    uni.showToast({ title: it.primaryAction, icon: 'none' })
}
function onSecondary(it: Item) {
  if (it.secondaryDisabled)
    return
  uni.showToast({ title: it.secondaryAction, icon: 'none' })
}
</script>

<template>
  <view class="il-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        物品列表
      </text>
      <button class="icon-btn" @click="onEdit">
        <uni-icons type="search" size="24" color="#3f4944" />
      </button>
    </view>

    <view class="filter-bar">
      <scroll-view class="chip-scroll" scroll-x>
        <view class="chip-row">
          <view
            v-for="f in filters"
            :key="f"
            class="chip"
            :class="{ on: activeFilter === f }"
            @click="activeFilter = f"
          >
            {{ f }}
          </view>
        </view>
      </scroll-view>
      <view class="filter-btn">
        <uni-icons type="list" size="20" color="#1f7159" />
      </view>
    </view>

    <view class="list">
      <view v-for="it in filteredItems" :key="it.id" class="item-card">
        <view class="card-top">
          <view class="thumb">
            <uni-icons :type="it.icon || 'list'" size="34" color="#6f7974" />
          </view>
          <view class="detail">
            <text class="item-name">
              {{ it.name }}
            </text>
            <text class="item-spec">
              {{ it.spec }}
            </text>
            <view class="price-row">
              <text class="price">
                {{ it.price }}
              </text>
              <text class="stock" :class="{ warn: it.stockState === 'warn' }">
                库存: <text class="stock-val">{{ it.stock }}</text>
              </text>
            </view>
            <view class="badges">
              <text class="badge" :class="it.stockState === 'warn' ? 'danger' : 'ok'">
                {{ it.stockState === 'warn' ? '库存预警' : '库存充足' }}
              </text>
              <text class="badge muted">
                {{ it.tag }}
              </text>
            </view>
          </view>
        </view>
        <view class="card-actions">
          <button class="act-btn ghost" @click="onDetail">
            详情
          </button>
          <button class="act-btn ghost" :class="{ disabled: it.secondaryDisabled }" @click="onSecondary(it)">
            {{ it.secondaryAction }}
          </button>
          <button class="act-btn" :class="it.primaryDanger ? 'danger' : 'primary'" @click="onPrimary(it)">
            {{ it.primaryAction }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.il-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 40rpx;
  color: #0f1d23;
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

.filter-bar {
  display: flex;
  align-items: center;
  margin-top: 24rpx;
}

.chip-scroll {
  flex: 1;
  white-space: nowrap;
}

.chip-row {
  display: flex;
  gap: 16rpx;
}

.chip {
  flex-shrink: 0;
  padding: 10rpx 28rpx;
  font-size: 24rpx;
  color: #3f4944;
  background: #f3faff;
  border: 1rpx solid #bec9c3;
  border-radius: 999rpx;
}

.chip.on {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.filter-btn {
  padding-left: 16rpx;
  margin-left: 16rpx;
  border-left: 1rpx solid #bec9c3;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 24rpx;
}

.item-card {
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.card-top {
  display: flex;
  gap: 24rpx;
}

.thumb {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 144rpx;
  height: 144rpx;
  background: #e7f6fe;
  border-radius: 10rpx;
}

.detail {
  flex: 1;
  min-width: 0;
}

.item-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
}

.item-spec {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12rpx;
}

.price {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f7159;
}

.stock {
  font-size: 24rpx;
  color: #3f4944;
}

.stock.warn {
  color: #ba1a1a;
}

.stock-val {
  font-weight: 600;
  color: #0f1d23;
}

.stock.warn .stock-val {
  color: #ba1a1a;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 14rpx;
}

.badge {
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.badge.ok {
  color: #227253;
  background: #e9f6ef;
}

.badge.danger {
  color: #93000a;
  background: #ffeceb;
}

.badge.muted {
  color: #3f4944;
  background: #e1f0f8;
  border: 1rpx solid #bec9c3;
}

.card-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 22rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #bec9c3;
}

.act-btn {
  flex: 1;
  height: 72rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 600;
  line-height: 72rpx;
  border-radius: 10rpx;
}

.act-btn.ghost {
  color: #1f7159;
  background: #f3faff;
  border: 1rpx solid #1f7159;
}

.act-btn.ghost.disabled {
  opacity: 0.5;
}

.act-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.act-btn.danger {
  color: #ffffff;
  background: #ba1a1a;
}
</style>
