<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ItemStockLog',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '库存流水',
  },
})

interface Log {
  id: number
  type: string
  badge: 'in' | 'sale' | 'usage' | 'audit'
  name: string
  spec: string
  delta: string
  positive: boolean
  time: string
  handler: string
  doc: string
}

const dateRanges = ['近7天', '近30天', '本月', '自定义']
const handlers = ['全部经办人', '张老师', '李老师', '王老师']
const types = ['全部', '采购入库', '销售出库', '领用', '退货', '盘点调整']
const activeType = ref('全部')
const dateIdx = ref(0)
const handlerIdx = ref(0)

const logs = ref<Log[]>([
  { id: 1, type: '采购入库', badge: 'in', name: '少儿英语教材 (Level 1)', spec: '规格: A4全彩精装', delta: '+50', positive: true, time: '2026-06-24 14:00', handler: '张老师', doc: 'PO-202606-042' },
  { id: 2, type: '销售出库', badge: 'sale', name: '学生随堂测验纸', spec: '规格: B5单色 100张/包', delta: '-5', positive: false, time: '2026-06-24 10:15', handler: '李老师', doc: 'SO-202606-118' },
  { id: 3, type: '领用', badge: 'usage', name: '教学白板笔', spec: '规格: 黑色 10支/盒', delta: '-1', positive: false, time: '2026-06-23 16:45', handler: '王老师', doc: 'REQ-202606-088' },
  { id: 4, type: '盘点调整', badge: 'audit', name: '打印A4纸', spec: '规格: 70g 500张/包', delta: '+2', positive: true, time: '2026-06-22 09:30', handler: '系统', doc: 'AUD-202606-001' },
])

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="sl-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        库存流水
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 筛选 -->
    <view class="filters">
      <view class="filter-row">
        <picker class="pk" :range="dateRanges" :value="dateIdx" @change="dateIdx = $event.detail.value">
          <view class="pk-val">
            <text>{{ dateRanges[dateIdx] }}</text>
            <uni-icons type="calendar" size="20" color="#3f4944" />
          </view>
        </picker>
        <picker class="pk" :range="handlers" :value="handlerIdx" @change="handlerIdx = $event.detail.value">
          <view class="pk-val">
            <text>{{ handlers[handlerIdx] }}</text>
            <uni-icons type="person" size="20" color="#3f4944" />
          </view>
        </picker>
      </view>
      <scroll-view class="chip-scroll" scroll-x>
        <view class="chip-row">
          <view
            v-for="t in types"
            :key="t"
            class="chip"
            :class="{ on: activeType === t }"
            @click="activeType = t"
          >
            {{ t }}
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="list">
      <view v-for="l in logs" :key="l.id" class="log-card">
        <view class="accent" :class="l.badge" />
        <view class="log-top">
          <view class="log-left">
            <view class="title-row">
              <text class="badge" :class="l.badge">
                {{ l.type }}
              </text>
              <text class="log-name">
                {{ l.name }}
              </text>
            </view>
            <text class="log-spec">
              {{ l.spec }}
            </text>
          </view>
          <text class="delta" :class="{ pos: l.positive, neg: !l.positive }">
            {{ l.delta }}
          </text>
        </view>
        <view class="divider" />
        <view class="log-meta">
          <view class="meta-item">
            <uni-icons type="calendar" size="16" color="#6f7974" />
            <text>{{ l.time }}</text>
          </view>
          <view class="meta-right">
            <view class="meta-item">
              <uni-icons type="person" size="14" color="#6f7974" />
              <text>{{ l.handler }}</text>
            </view>
            <view class="meta-item">
              <uni-icons type="list" size="14" color="#6f7974" />
              <text>{{ l.doc }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.sl-page {
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

.filters {
  margin: 24rpx -28rpx 0;
  padding: 20rpx 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.filter-row {
  display: flex;
  gap: 20rpx;
}

.pk {
  flex: 1;
}

.pk-val {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 26rpx;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.chip-scroll {
  margin-top: 18rpx;
  white-space: nowrap;
}

.chip-row {
  display: flex;
  gap: 16rpx;
}

.chip {
  flex-shrink: 0;
  padding: 8rpx 24rpx;
  font-size: 24rpx;
  color: #3f4944;
  background: #d6e5ed;
  border: 1rpx solid #bec9c3;
  border-radius: 999rpx;
}

.chip.on {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 24rpx;
}

.log-card {
  position: relative;
  padding: 24rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.accent {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 8rpx;
}

.accent.in {
  background: #00583d;
}

.accent.sale {
  background: #335d9a;
}

.accent.usage {
  background: #c2410c;
}

.accent.audit {
  background: #6f7974;
}

.log-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.log-left {
  flex: 1;
  min-width: 0;
  padding-right: 16rpx;
}

.title-row {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.badge {
  flex-shrink: 0;
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
  border-radius: 999rpx;
}

.badge.in {
  color: #227253;
  background: #e9f6ef;
}

.badge.sale {
  color: #335d9a;
  background: #eaf1ff;
}

.badge.usage {
  color: #c2410c;
  background: #fff5d8;
}

.badge.audit {
  color: #3f4944;
  background: #d6e5ed;
}

.log-name {
  overflow: hidden;
  font-size: 28rpx;
  font-weight: 600;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.log-spec {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.delta {
  flex-shrink: 0;
  font-size: 30rpx;
  font-weight: 700;
}

.delta.pos {
  color: #00583d;
}

.delta.neg {
  color: #ba1a1a;
}

.divider {
  height: 1rpx;
  margin: 16rpx 0;
  background: #e7ece9;
}

.log-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 22rpx;
  color: #6f7974;
}

.meta-right {
  display: flex;
  gap: 24rpx;
}

.meta-item {
  display: flex;
  gap: 6rpx;
  align-items: center;
}
</style>
