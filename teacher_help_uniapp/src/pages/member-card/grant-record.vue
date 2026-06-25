<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'MemberCardGrantRecord',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '发放记录',
  },
})

interface GrantRecord {
  id: number
  name: string
  avatar: string
  status: '正常' | '已停用'
  cardNo: string
  price: string
  cardName: string
  rest: string
  validTo: string
  source: string
}

const keyword = ref('')

const records = ref<GrantRecord[]>([
  { id: 1, name: '张三', avatar: '张', status: '正常', cardNo: 'MC882039', price: '¥1,200', cardName: '10次数学精品课卡', rest: '8次', validTo: '2024-12-31', source: '后台发放' },
  { id: 2, name: '李四', avatar: '李', status: '已停用', cardNo: 'MC882040', price: '¥800', cardName: '英语基础月卡', rest: '0天', validTo: '2023-11-15', source: '学员购卡' },
])

function goBack() {
  uni.navigateBack()
}
function onView(r: GrantRecord) {
  uni.navigateTo({ url: `/pages/member-card/hold-detail?id=${r.id}` })
}
function onRenew() {
  uni.showToast({ title: '续费', icon: 'none' })
}
function onDisable() {
  uni.showToast({ title: '已停用', icon: 'none' })
}
function onLoadMore() {
  uni.showToast({ title: '没有更多了', icon: 'none' })
}
</script>

<template>
  <view class="gr-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        发放记录
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 搜索与筛选 -->
    <view class="filter-card">
      <view class="search-box">
        <uni-icons type="search" size="22" color="#3f4944" />
        <input v-model="keyword" class="search-input" placeholder="搜索学员姓名/卡号" placeholder-class="ph">
      </view>
      <view class="filter-row">
        <view class="filter-btn">
          <text>全部时间</text>
          <uni-icons type="bottom" size="16" color="#3f4944" />
        </view>
        <view class="filter-btn">
          <text>全部状态</text>
          <uni-icons type="bottom" size="16" color="#3f4944" />
        </view>
        <view class="filter-icon-btn">
          <uni-icons type="list" size="20" color="#3f4944" />
        </view>
      </view>
    </view>

    <!-- 记录列表 -->
    <view class="list">
      <view
        v-for="r in records"
        :key="r.id"
        class="rec-card"
        :class="{ inactive: r.status === '已停用' }"
      >
        <view class="rec-head">
          <view class="rec-left">
            <view class="avatar" :class="{ muted: r.status === '已停用' }">
              {{ r.avatar }}
            </view>
            <view class="rec-info">
              <view class="name-row">
                <text class="rec-name">
                  {{ r.name }}
                </text>
                <text class="status-tag" :class="r.status === '正常' ? 'ok' : 'muted'">
                  {{ r.status }}
                </text>
              </view>
              <text class="card-no">
                {{ r.cardNo }}
              </text>
            </view>
          </view>
          <text class="price" :class="{ muted: r.status === '已停用' }">
            {{ r.price }}
          </text>
        </view>

        <view class="rec-grid">
          <view class="grid-item">
            <text class="g-label">
              卡片名称
            </text>
            <text class="g-value">
              {{ r.cardName }}
            </text>
          </view>
          <view class="grid-item">
            <text class="g-label">
              剩余权益
            </text>
            <text class="g-value" :class="{ accent: r.status === '正常' }">
              {{ r.rest }}
            </text>
          </view>
          <view class="grid-item">
            <text class="g-label">
              有效期至
            </text>
            <text class="g-value">
              {{ r.validTo }}
            </text>
          </view>
          <view class="grid-item">
            <text class="g-label">
              来源
            </text>
            <text class="g-value">
              {{ r.source }}
            </text>
          </view>
        </view>

        <view class="rec-actions">
          <text class="act ghost" @click="onView(r)">
            查看
          </text>
          <text class="act primary" @click="onRenew">
            续费
          </text>
          <text v-if="r.status === '正常'" class="act danger" @click="onDisable">
            停用
          </text>
        </view>
      </view>

      <view class="load-more" @click="onLoadMore">
        <text>加载更多</text>
        <uni-icons type="bottom" size="16" color="#3f4944" />
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.gr-page {
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
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #005842;
  text-align: center;
}

.filter-card {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 28rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
  height: 84rpx;
  padding: 0 24rpx;
  background: #f3faff;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
}

.ph {
  color: #3f4944;
}

.filter-row {
  display: flex;
  gap: 16rpx;
}

.filter-btn {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: space-between;
  height: 76rpx;
  padding: 0 22rpx;
  font-size: 26rpx;
  background: #f3faff;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.filter-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  background: #f3faff;
  border: 1rpx solid #e7ece9;
  border-radius: 12rpx;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-top: 28rpx;
}

.rec-card {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.rec-card.inactive {
  opacity: 0.8;
}

.rec-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.rec-left {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 80rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
  border-radius: 50%;
}

.avatar.muted {
  color: #3f4944;
  background: #d6e5ed;
}

.rec-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.name-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.rec-name {
  font-size: 32rpx;
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

.card-no {
  font-size: 24rpx;
  color: #3f4944;
}

.price {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f7159;
}

.price.muted {
  color: #0f1d23;
}

.rec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx 30rpx;
  padding: 22rpx 0;
  border-top: 1rpx solid #e7ece9;
  border-bottom: 1rpx solid #e7ece9;
}

.grid-item {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.g-label {
  font-size: 22rpx;
  color: #3f4944;
}

.g-value {
  font-size: 26rpx;
  color: #0f1d23;
}

.g-value.accent {
  font-weight: 600;
  color: #1f7159;
}

.rec-actions {
  display: flex;
  gap: 16rpx;
  justify-content: flex-end;
}

.act {
  padding: 10rpx 30rpx;
  font-size: 24rpx;
  border-radius: 8rpx;
}

.act.ghost {
  color: #0f1d23;
  border: 1rpx solid #bec9c3;
}

.act.primary {
  color: #1f7159;
  border: 1rpx solid #1f7159;
}

.act.danger {
  color: #ba1a1a;
  border: 1rpx solid #ba1a1a;
}

.load-more {
  display: flex;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  padding: 18rpx;
  font-size: 26rpx;
  color: #3f4944;
}
</style>
