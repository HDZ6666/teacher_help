<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'MemberCardIndex',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '会员卡',
  },
})

interface MemberCard {
  id: number
  name: string
  status: '已启用' | '已停用'
  type: string
  rights: string
  price: string
  validDays: string
  issued: string
}

const keyword = ref('')
const filters = ['全部', '课程卡', '场地折扣卡', '启用', '停用', '线上售卖']
const activeFilter = ref('全部')

const cards = ref<MemberCard[]>([
  { id: 1, name: '10次数学精品课卡', status: '已启用', type: '课程卡', rights: '权益: 10次', price: '¥1,200', validDays: '180天', issued: '24张' },
  { id: 2, name: '暑期钢琴启蒙月卡', status: '已启用', type: '课程卡', rights: '权益: 无限次/月', price: '¥800', validDays: '30天', issued: '56张' },
  { id: 3, name: '画室全天畅玩年卡', status: '已停用', type: '场地折扣卡', rights: '权益: 8折', price: '¥3,600', validDays: '365天', issued: '12张' },
])

const filteredCards = computed(() => {
  return cards.value.filter((c) => {
    if (keyword.value && !c.name.includes(keyword.value))
      return false
    if (activeFilter.value === '全部')
      return true
    if (activeFilter.value === '启用')
      return c.status === '已启用'
    if (activeFilter.value === '停用')
      return c.status === '已停用'
    if (activeFilter.value === '课程卡' || activeFilter.value === '场地折扣卡')
      return c.type === activeFilter.value
    return true
  })
})

function goBack() {
  uni.navigateBack()
}
function onAdd() {
  uni.showToast({ title: '新增会员卡', icon: 'none' })
}
function onShare() {
  uni.showToast({ title: '已分享', icon: 'none' })
}
function onDetail(c: MemberCard) {
  uni.navigateTo({ url: `/pages/member-card/detail?id=${c.id}` })
}
function onGrant(c: MemberCard) {
  uni.navigateTo({ url: `/pages/member-card/grant?id=${c.id}` })
}
</script>

<template>
  <view class="mc-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        会员卡
      </text>
      <button class="icon-btn" @click="onAdd">
        <uni-icons type="plusempty" size="26" color="#005842" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="24" color="#6f7974" />
      <input v-model="keyword" class="search-input" placeholder="搜索卡名称" placeholder-class="ph">
    </view>

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

    <view class="list">
      <view
        v-for="c in filteredCards"
        :key="c.id"
        class="mc-card"
        :class="{ disabled: c.status === '已停用' }"
      >
        <view class="card-head">
          <view class="head-left">
            <view class="name-row">
              <text class="card-name">
                {{ c.name }}
              </text>
              <text class="status-tag" :class="c.status === '已启用' ? 'ok' : 'muted'">
                {{ c.status }}
              </text>
            </view>
            <view class="meta-row">
              <text class="type-tag">
                {{ c.type }}
              </text>
              <text class="dot-sep">
                •
              </text>
              <text>{{ c.rights }}</text>
            </view>
          </view>
          <text class="price">
            {{ c.price }}
          </text>
        </view>

        <view class="stat-box">
          <view class="stat-item">
            <text class="stat-label">
              有效期
            </text>
            <text class="stat-value">
              {{ c.validDays }}
            </text>
          </view>
          <view class="stat-item">
            <text class="stat-label">
              已发卡
            </text>
            <text class="stat-value">
              {{ c.issued }}
            </text>
          </view>
        </view>

        <view class="card-actions">
          <template v-if="c.status === '已启用'">
            <text class="act ghost" @click="onShare">
              分享
            </text>
            <text class="act ghost" @click="onDetail(c)">
              详情
            </text>
            <text class="act fill" @click="onGrant(c)">
              发放
            </text>
          </template>
          <template v-else>
            <text class="act muted-act" @click="onDetail(c)">
              详情
            </text>
          </template>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.mc-page {
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
}

.search-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
  height: 84rpx;
  margin-top: 28rpx;
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

.chip-scroll {
  margin: 24rpx -28rpx 0;
  white-space: nowrap;
}

.chip-row {
  display: flex;
  gap: 16rpx;
  padding: 0 28rpx;
}

.chip {
  flex-shrink: 0;
  padding: 10rpx 26rpx;
  font-size: 24rpx;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 999rpx;
}

.chip.on {
  color: #1f7159;
  background: #e7f6fe;
  border-color: #1f7159;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-top: 28rpx;
}

.mc-card {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.mc-card.disabled {
  opacity: 0.75;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.head-left {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.name-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.card-name {
  font-size: 34rpx;
  font-weight: 600;
}

.status-tag {
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.status-tag.ok {
  color: #227253;
  background: #e9f6ef;
}

.status-tag.muted {
  color: #3f4944;
  background: #d6e5ed;
}

.meta-row {
  display: flex;
  gap: 10rpx;
  align-items: center;
  font-size: 26rpx;
  color: #3f4944;
}

.type-tag {
  padding: 2rpx 14rpx;
  color: #40655b;
  background: #e1f0f8;
  border-radius: 6rpx;
}

.dot-sep {
  color: #6f7974;
}

.price {
  font-size: 34rpx;
  font-weight: 600;
  color: #005842;
}

.stat-box {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  padding: 22rpx;
  background: #e7f6fe;
  border-radius: 10rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.stat-label {
  font-size: 22rpx;
  color: #6f7974;
}

.stat-value {
  font-size: 28rpx;
  color: #0f1d23;
}

.card-actions {
  display: flex;
  gap: 16rpx;
  justify-content: flex-end;
  padding-top: 24rpx;
  border-top: 1rpx solid #e7ece9;
}

.act {
  padding: 10rpx 30rpx;
  font-size: 24rpx;
  border-radius: 10rpx;
}

.act.ghost {
  color: #005842;
  background: transparent;
  border: 1rpx solid #005842;
}

.act.fill {
  color: #ffffff;
  background: #1f7159;
}

.act.muted-act {
  color: #3f4944;
  background: transparent;
  border: 1rpx solid #bec9c3;
}
</style>
