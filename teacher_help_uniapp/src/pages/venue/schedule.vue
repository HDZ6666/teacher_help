<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'VenueSchedule',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '订场时间表',
  },
})

type SlotStatus = 'available' | 'booked' | 'locked' | 'unavailable'
interface SlotItem {
  start: string
  end: string
  status: SlotStatus
  title: string
  desc: string
}

const venueId = ref('')
const venueName = ref('A101')
const dateText = ref('2023年10月24日')
const campus = ref('总校区')

const tabs = ref(['A101', 'A102', 'B205', 'C310', '实验室1'])
const activeTab = ref('A101')

const slots = ref<SlotItem[]>([
  { start: '08:00', end: '09:00', status: 'available', title: '空闲', desc: '点击代预约' },
  { start: '09:00', end: '10:00', status: 'booked', title: '已预约', desc: '王老师 · 生物入门' },
  { start: '10:00', end: '11:00', status: 'locked', title: '已锁定', desc: '设备维护时段' },
  { start: '11:00', end: '12:00', status: 'unavailable', title: '不可用', desc: '已过去的时段' },
  { start: '12:00', end: '13:00', status: 'available', title: '空闲', desc: '点击代预约' },
  { start: '13:00', end: '14:00', status: 'available', title: '空闲', desc: '点击代预约' },
])

function goBack() {
  uni.navigateBack()
}
function onCalendar() {
  uni.showToast({ title: '选择日期', icon: 'none' })
}
function onSlot(s: SlotItem) {
  if (s.status === 'available') {
    uni.navigateTo({
      url: `/pages/venue/proxy-booking?venue=${encodeURIComponent(venueName.value)}&start=${s.start}&end=${s.end}`,
    })
  }
  else if (s.status === 'booked') {
    uni.navigateTo({ url: `/pages/venue/booking-detail?slot=${s.start}` })
  }
}

onLoad((query) => {
  venueId.value = query?.id || ''
  if (query?.name) {
    venueName.value = decodeURIComponent(query.name)
    activeTab.value = venueName.value
    if (!tabs.value.includes(venueName.value))
      tabs.value.unshift(venueName.value)
  }
})
</script>

<template>
  <view class="vs-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        订场时间表
      </text>
      <button class="icon-btn" @click="onCalendar">
        <uni-icons type="calendar" size="24" color="#3f4944" />
      </button>
    </view>

    <!-- 日期 / 校区选择 -->
    <view class="sub-head">
      <view class="sub-col">
        <text class="sub-label">
          日期
        </text>
        <view class="sub-value" @click="onCalendar">
          <text>{{ dateText }}</text>
          <uni-icons type="bottom" size="16" color="#005842" />
        </view>
      </view>
      <view class="sub-col end">
        <text class="sub-label">
          校区
        </text>
        <view class="sub-value">
          <text>{{ campus }}</text>
          <uni-icons type="bottom" size="16" color="#005842" />
        </view>
      </view>
    </view>

    <!-- 场地切换 -->
    <scroll-view class="tab-scroll" scroll-x>
      <view class="tab-row">
        <view
          v-for="t in tabs"
          :key="t"
          class="tab"
          :class="{ on: activeTab === t }"
          @click="activeTab = t"
        >
          {{ t }}
        </view>
      </view>
    </scroll-view>

    <!-- 时段表 -->
    <view class="timeline">
      <view
        v-for="(s, idx) in slots"
        :key="idx"
        class="slot-row"
        :class="{ dim: s.status === 'locked', faded: s.status === 'unavailable' }"
        @click="onSlot(s)"
      >
        <view class="time-col">
          <text class="time-start">
            {{ s.start }}
          </text>
          <text class="time-end">
            {{ s.end }}
          </text>
        </view>
        <view class="line-col">
          <view class="line" />
          <view
            class="node"
            :class="{
              filled: s.status === 'booked',
              outline: s.status === 'available',
              gray: s.status === 'locked',
              ghost: s.status === 'unavailable',
            }"
          />
        </view>
        <view
          class="slot-card"
          :class="{
            available: s.status === 'available',
            booked: s.status === 'booked',
            locked: s.status === 'locked',
            unavailable: s.status === 'unavailable',
          }"
        >
          <view v-if="s.status === 'unavailable'" class="hatch" />
          <view class="slot-text">
            <view class="slot-title-row">
              <text
                class="slot-title"
                :class="{
                  available: s.status === 'available',
                  booked: s.status === 'booked',
                }"
              >
                {{ s.title }}
              </text>
              <uni-icons v-if="s.status === 'locked'" type="locked" size="16" color="#3f4944" />
            </view>
            <text class="slot-desc" :class="{ booked: s.status === 'booked' }">
              {{ s.desc }}
            </text>
          </view>
          <uni-icons
            v-if="s.status === 'available'"
            type="plus-filled"
            size="22"
            color="#1f7159"
          />
          <uni-icons
            v-else-if="s.status === 'booked'"
            type="right"
            size="20"
            color="#ffffff"
          />
          <uni-icons
            v-else-if="s.status === 'unavailable'"
            type="minus-filled"
            size="20"
            color="#6f7974"
          />
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.vs-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-bottom: 60rpx;
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
  font-weight: 600;
  color: #005842;
}

.sub-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 28rpx;
  background: #ffffff;
  border-bottom: 1rpx solid #bec9c3;
}

.sub-col {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.sub-col.end {
  align-items: flex-end;
}

.sub-label {
  font-size: 22rpx;
  letter-spacing: 2rpx;
  color: #3f4944;
}

.sub-value {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 32rpx;
  font-weight: 600;
  color: #005842;
}

.tab-scroll {
  white-space: nowrap;
  background: #ffffff;
  border-bottom: 1rpx solid #bec9c3;
}

.tab-row {
  display: flex;
  gap: 24rpx;
  padding: 12rpx 28rpx;
}

.tab {
  flex-shrink: 0;
  padding: 12rpx 18rpx;
  font-size: 26rpx;
  color: #3f4944;
  border-bottom: 4rpx solid transparent;
}

.tab.on {
  font-weight: 600;
  color: #005842;
  border-bottom-color: #1f7159;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 28rpx;
}

.slot-row {
  display: flex;
  gap: 16rpx;
  align-items: stretch;
}

.slot-row.dim,
.slot-row.faded {
  opacity: 0.7;
}

.time-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  width: 90rpx;
  padding-top: 10rpx;
}

.time-start {
  font-size: 24rpx;
  font-weight: 600;
  color: #3f4944;
}

.time-end {
  font-size: 22rpx;
  color: #6f7974;
}

.line-col {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24rpx;
}

.line {
  position: absolute;
  top: 0;
  width: 3rpx;
  height: 100%;
  background: #d6e5ed;
}

.node {
  z-index: 1;
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
}

.node.filled {
  background: #1f7159;
}

.node.outline {
  background: #f3faff;
  border: 3rpx solid #1f7159;
}

.node.gray {
  background: #d6e5ed;
}

.node.ghost {
  background: #f3faff;
  border: 3rpx solid #bec9c3;
}

.slot-card {
  position: relative;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: space-between;
  padding: 22rpx;
  overflow: hidden;
  border-radius: 14rpx;
}

.slot-card.available {
  background: #ffffff;
  border: 1rpx solid #1f7159;
}

.slot-card.booked {
  background: #1f7159;
}

.slot-card.locked {
  background: #d6e5ed;
}

.slot-card.unavailable {
  background: #ffffff;
  border: 1rpx solid #bec9c3;
}

.hatch {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 20rpx, #0f1d23 20rpx, #0f1d23 24rpx);
}

.slot-text {
  z-index: 1;
}

.slot-title-row {
  display: flex;
  gap: 8rpx;
  align-items: center;
}

.slot-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #3f4944;
}

.slot-title.available {
  color: #1f7159;
}

.slot-title.booked {
  color: #ffffff;
}

.slot-desc {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.slot-desc.booked {
  color: rgba(255, 255, 255, 0.9);
}
</style>
