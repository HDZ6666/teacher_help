<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ItemFee',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '费用项目',
  },
})

interface Fee {
  id: number
  name: string
  price: string
  enabled: boolean
  scope: string
  online: boolean
}

const fees = ref<Fee[]>([
  { id: 1, name: '建档费', price: '¥200.00', enabled: true, scope: '所有课程', online: true },
  { id: 2, name: '保险费', price: '¥150.00', enabled: true, scope: '游泳初级班, 游泳进阶班', online: false },
])

function goBack() {
  uni.navigateBack()
}
function onEdit() {
  uni.navigateTo({ url: '/pages/item/edit' })
}
function onToggle(f: Fee) {
  f.enabled = !f.enabled
  uni.showToast({ title: f.enabled ? '已启用' : '已停用', icon: 'none' })
}
function onDetail() {
  uni.showToast({ title: '查看详情', icon: 'none' })
}
function onAdd() {
  uni.navigateTo({ url: '/pages/item/edit' })
}
</script>

<template>
  <view class="fe-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        费用项目
      </text>
      <view class="icon-btn" />
    </view>

    <view class="list">
      <view v-for="f in fees" :key="f.id" class="fee-card">
        <view class="card-head">
          <view class="head-left">
            <text class="fee-name">
              {{ f.name }}
            </text>
            <text class="fee-price">
              {{ f.price }}
            </text>
          </view>
          <view class="tags">
            <text class="tag ok">
              {{ f.enabled ? '已启用' : '已停用' }}
            </text>
            <text v-if="f.online" class="tag muted">
              线上售卖
            </text>
          </view>
        </view>
        <view class="scope-row">
          <uni-icons type="list" size="16" color="#6f7974" />
          <text>适用课程: {{ f.scope }}</text>
        </view>
        <view class="divider" />
        <view class="card-actions">
          <button class="act-btn ghost" @click="onEdit">
            编辑
          </button>
          <button class="act-btn line" @click="onToggle(f)">
            {{ f.enabled ? '停用' : '启用' }}
          </button>
          <button class="act-btn primary" @click="onDetail">
            详情
          </button>
        </view>
      </view>

      <button class="add-btn" @click="onAdd">
        <uni-icons type="plusempty" size="22" color="#1f7159" />
        <text>新增费用项目</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.fe-page {
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

.list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 24rpx;
}

.fee-card {
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.head-left {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.fee-name {
  font-size: 30rpx;
  font-weight: 600;
}

.fee-price {
  font-size: 44rpx;
  font-weight: 700;
  color: #1f7159;
}

.tags {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  align-items: flex-end;
}

.tag {
  padding: 4rpx 18rpx;
  font-size: 22rpx;
  white-space: nowrap;
  border-radius: 999rpx;
}

.tag.ok {
  color: #227253;
  background: #e9f6ef;
}

.tag.muted {
  color: #3f4944;
  background: #dbebf3;
}

.scope-row {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.divider {
  height: 1rpx;
  margin: 18rpx 0;
  background: #e7ece9;
}

.card-actions {
  display: flex;
  gap: 16rpx;
  justify-content: flex-end;
}

.act-btn {
  height: 68rpx;
  padding: 0 32rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 600;
  line-height: 68rpx;
  border-radius: 10rpx;
}

.act-btn.ghost {
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.act-btn.line {
  color: #6f7974;
  background: transparent;
  border: 1rpx solid #6f7974;
}

.act-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.add-btn {
  display: flex;
  gap: 12rpx;
  align-items: center;
  justify-content: center;
  height: 112rpx;
  margin-top: 14rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1f7159;
  background: transparent;
  border: 2rpx dashed #1f7159;
  border-radius: 14rpx;
}
</style>
