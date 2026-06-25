<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'CoursePackage',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '套餐',
  },
})

const packages = ref([
  {
    id: 1,
    name: '思维+编程启蒙包',
    status: '已售罄',
    price: 3200,
    courseCount: 2,
    itemCount: 0,
    expanded: false,
  },
  {
    id: 2,
    name: '英语+美术暑期联报包',
    status: '可售',
    price: 4800,
    courseCount: 2,
    itemCount: 2,
    courses: ['少儿英语', '创意美术'],
    items: ['教材包', '建档费'],
    origin: 5600,
    discount: 800,
    expanded: true,
  },
])

function goBack() {
  uni.navigateBack()
}
function toggle(p: any) {
  p.expanded = !p.expanded
}
function onShare() {
  uni.showToast({ title: '分享海报', icon: 'none' })
}
function onApply() {
  uni.showToast({ title: '立即办理', icon: 'none' })
}
</script>

<template>
  <view class="pkg-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        套餐
      </text>
      <view class="icon-btn" />
    </view>

    <view class="head-row">
      <text class="head-title">
        特惠套餐
      </text>
      <uni-icons type="bars" size="22" color="#3f4944" />
    </view>

    <view
      v-for="p in packages"
      :key="p.id"
      class="pkg-card"
      :class="{ active: p.expanded }"
      @click="toggle(p)"
    >
      <view v-if="p.expanded" class="accent" />
      <view class="pkg-head" :class="{ pl: p.expanded }">
        <text class="pkg-name">
          {{ p.name }}
        </text>
        <text class="pkg-tag" :class="p.status === '可售' ? 'ok' : 'muted'">
          {{ p.status }}
        </text>
      </view>
      <text class="pkg-price" :class="{ big: p.expanded, pl: p.expanded }">
        ￥{{ p.price }}
      </text>

      <!-- 收起态摘要 -->
      <view v-if="!p.expanded" class="pkg-meta">
        <view class="meta-item">
          <uni-icons type="bars" size="15" color="#3f4944" />
          <text>课程 {{ p.courseCount }} 门</text>
        </view>
        <view class="meta-item">
          <uni-icons type="cart" size="15" color="#3f4944" />
          <text>物品 {{ p.itemCount }} 个</text>
        </view>
      </view>

      <!-- 展开态详情 -->
      <template v-else>
        <view class="divider" />
        <view class="detail-sec">
          <view class="sec-label">
            <uni-icons type="star" size="15" color="#3f4944" />
            <text>包含课程 ({{ p.courseCount }})</text>
          </view>
          <view class="chip-wrap">
            <text v-for="c in p.courses" :key="c" class="d-chip">
              {{ c }}
            </text>
          </view>
        </view>
        <view class="detail-sec">
          <view class="sec-label">
            <uni-icons type="cart" size="15" color="#3f4944" />
            <text>物品及费用 ({{ p.itemCount }})</text>
          </view>
          <view class="chip-wrap">
            <text v-for="i in p.items" :key="i" class="d-chip">
              {{ i }}
            </text>
          </view>
        </view>
        <view class="price-box">
          <view class="pb-row">
            <text>原价合计</text>
            <text class="strike">￥{{ p.origin }}</text>
          </view>
          <view class="pb-row err">
            <text>套餐优惠</text>
            <text>- ￥{{ p.discount }}</text>
          </view>
          <view class="pb-divider" />
          <view class="pb-row total">
            <text>应收金额</text>
            <text class="total-num">￥{{ p.price }}</text>
          </view>
        </view>
        <view class="pkg-actions" @click.stop>
          <button class="ghost-btn" @click="onShare">
            分享海报
          </button>
          <button class="primary-btn" @click="onApply">
            立即办理
          </button>
        </view>
      </template>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.pkg-page {
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
  font-size: 34rpx;
  font-weight: 700;
}

.head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 28rpx 0 18rpx;
}

.head-title {
  font-size: 38rpx;
  font-weight: 700;
}

.pkg-card {
  position: relative;
  margin-bottom: 22rpx;
  padding: 24rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.pkg-card.active {
  border-color: #1f7159;
}

.accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 8rpx;
  height: 100%;
  background: #1f7159;
}

.pkg-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.pkg-head.pl,
.pkg-price.pl {
  padding-left: 14rpx;
}

.pkg-name {
  font-size: 32rpx;
  font-weight: 700;
}

.pkg-tag {
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.pkg-tag.ok {
  color: #284d44;
  background: #c2ebde;
}

.pkg-tag.muted {
  color: #3f4944;
  background: #dbebf3;
}

.pkg-price {
  display: block;
  margin-top: 12rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #3f4944;
}

.pkg-price.big {
  font-size: 52rpx;
  color: #1f7159;
}

.pkg-meta {
  display: flex;
  gap: 32rpx;
  margin-top: 14rpx;
}

.meta-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.divider {
  margin: 22rpx 0;
  border-top: 1rpx solid #bec9c3;
}

.detail-sec {
  padding-left: 14rpx;
  margin-bottom: 22rpx;
}

.sec-label {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-bottom: 14rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.d-chip {
  padding: 12rpx 22rpx;
  font-size: 25rpx;
  background: #e1f0f8;
  border: 1rpx solid #bec9c3;
  border-radius: 8rpx;
}

.price-box {
  margin: 0 0 22rpx 14rpx;
  padding: 22rpx;
  background: #e7f6fe;
  border-radius: 12rpx;
}

.pb-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 25rpx;
  color: #3f4944;
}

.pb-row + .pb-row {
  margin-top: 12rpx;
}

.pb-row.err {
  color: #ba1a1a;
}

.strike {
  text-decoration: line-through;
}

.pb-divider {
  margin: 14rpx 0;
  border-top: 1rpx dashed #bec9c3;
}

.pb-row.total {
  font-size: 28rpx;
  font-weight: 600;
  color: #0f1d23;
}

.total-num {
  font-weight: 700;
  color: #1f7159;
}

.pkg-actions {
  display: flex;
  gap: 18rpx;
  padding-left: 14rpx;
}

.ghost-btn,
.primary-btn {
  height: 84rpx;
  margin: 0;
  font-size: 27rpx;
  font-weight: 600;
  line-height: 84rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  flex: 1;
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  flex: 2;
  color: #ffffff;
  background: #1f7159;
}
</style>
