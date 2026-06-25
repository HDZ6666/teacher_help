<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'MemberCardDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '会员卡详情',
  },
})

const cardId = ref('')
const card = ref({
  name: 'VIP 数学强化卡',
  subtitle: '初中数学专用',
  status: '已启用',
  price: '¥1,200',
  originPrice: '¥1,500',
})

const rights = [
  { label: '适用课程', value: '初中数学' },
  { label: '可使用次数', value: '10次' },
  { label: '有效天数', value: '180天' },
  { label: '生效方式', value: '即时生效' },
  { label: '购买限制', value: '不限', full: true },
]

const note = '仅限本人使用。不可转让，不可与其他优惠叠加使用。过期后卡内剩余次数作废，不予退还。'

function goBack() {
  uni.navigateBack()
}
function onEdit() {
  uni.showToast({ title: '编辑会员卡', icon: 'none' })
}
function onGrant() {
  uni.navigateTo({ url: `/pages/member-card/grant?id=${cardId.value}` })
}
function onDisable() {
  uni.showToast({ title: '已停用此卡', icon: 'none' })
}
function onRecords() {
  uni.navigateTo({ url: '/pages/member-card/grant-record' })
}

onLoad((query) => {
  cardId.value = query?.id || ''
})
</script>

<template>
  <view class="cd-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        会员卡详情
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 卡面预览 -->
    <view class="card-preview">
      <view class="preview-blob" />
      <view class="preview-head">
        <view class="preview-title">
          <text class="pv-name">
            {{ card.name }}
          </text>
          <text class="pv-sub">
            {{ card.subtitle }}
          </text>
        </view>
        <view class="pv-status">
          {{ card.status }}
        </view>
      </view>
      <view class="preview-price">
        <text class="pv-price">
          {{ card.price }}
        </text>
        <text class="pv-origin">
          {{ card.originPrice }}
        </text>
      </view>
    </view>

    <!-- 权益信息 -->
    <view class="card">
      <view class="card-title">
        <uni-icons type="checkbox-filled" size="20" color="#005842" />
        <text>权益信息</text>
      </view>
      <view class="rights-grid">
        <view
          v-for="r in rights"
          :key="r.label"
          class="right-item"
          :class="{ full: r.full }"
        >
          <text class="r-label">
            {{ r.label }}
          </text>
          <text class="r-value">
            {{ r.value }}
          </text>
        </view>
      </view>
      <view class="note-box">
        <text class="note-label">
          使用说明
        </text>
        <text class="note-text">
          {{ note }}
        </text>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-bar">
      <view class="btn-row">
        <button class="ghost-btn" @click="onEdit">
          编辑
        </button>
        <button class="primary-btn" @click="onGrant">
          发放给学员
        </button>
      </view>
      <view class="link-row">
        <view class="link-btn" @click="onDisable">
          <uni-icons type="poweroff" size="16" color="#3f4944" />
          <text>停用此卡</text>
        </view>
        <view class="link-btn" @click="onRecords">
          <uni-icons type="loop" size="16" color="#3f4944" />
          <text>查看发放记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cd-page {
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
  font-size: 36rpx;
  font-weight: 700;
  color: #005842;
}

.card-preview {
  position: relative;
  margin-top: 28rpx;
  padding: 36rpx;
  overflow: hidden;
  color: #ffffff;
  background: #1f7159;
  border-radius: 18rpx;
}

.preview-blob {
  position: absolute;
  top: -60rpx;
  right: -60rpx;
  width: 220rpx;
  height: 220rpx;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.preview-head {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.preview-title {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.pv-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #ffffff;
}

.pv-sub {
  font-size: 24rpx;
  color: #88d6b9;
}

.pv-status {
  padding: 6rpx 22rpx;
  font-size: 24rpx;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.2);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 999rpx;
}

.preview-price {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  margin-top: 56rpx;
}

.pv-price {
  font-size: 56rpx;
  font-weight: 700;
  color: #ffffff;
}

.pv-origin {
  font-size: 24rpx;
  color: #88d6b9;
  text-decoration: line-through;
}

.card {
  margin-top: 24rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.card-title {
  display: flex;
  gap: 10rpx;
  align-items: center;
  padding-bottom: 18rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: #005842;
  border-bottom: 1rpx solid #bec9c3;
}

.rights-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28rpx 16rpx;
  margin-top: 24rpx;
}

.right-item {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.right-item.full {
  grid-column: span 2;
}

.r-label {
  font-size: 22rpx;
  color: #3f4944;
}

.r-value {
  font-size: 28rpx;
  color: #0f1d23;
}

.note-box {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx dashed #bec9c3;
}

.note-label {
  font-size: 22rpx;
  color: #3f4944;
}

.note-text {
  font-size: 24rpx;
  line-height: 1.6;
  color: #0f1d23;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.btn-row {
  display: flex;
  gap: 18rpx;
}

.ghost-btn,
.primary-btn {
  flex: 1;
  height: 88rpx;
  margin: 0;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}

.link-row {
  display: flex;
  justify-content: space-between;
  padding: 0 8rpx;
}

.link-btn {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 24rpx;
  color: #3f4944;
}
</style>
