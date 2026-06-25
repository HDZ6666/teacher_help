<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'VenueIndex',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '场地管理',
  },
})

interface DateItem {
  week: string
  day: number
}
interface Venue {
  id: number
  name: string
  campus: string
  icon: string
  status: '空闲' | '已预约' | '已锁定'
  capacity: number
  occupancy: number
  bookedRange?: string
  reason?: string
}

const dates = ref<DateItem[]>([
  { week: '周一', day: 12 },
  { week: '周二', day: 13 },
  { week: '周三', day: 14 },
  { week: '周四', day: 15 },
  { week: '周五', day: 16 },
  { week: '周六', day: 17 },
  { week: '周日', day: 18 },
])
const activeDay = ref(14)

const stats = ref([
  { key: 'today', label: '今日预约', value: 12, icon: 'calendar', trend: '+2', highlight: true },
  { key: 'free', label: '可订时段', value: 24, icon: 'checkmarkempty', color: '#1f7159' },
  { key: 'pending', label: '待核销', value: 5, icon: 'loop', color: '#8a671b' },
  { key: 'locked', label: '已锁场地', value: 2, icon: 'locked', color: '#ba1a1a' },
])

const venues = ref<Venue[]>([
  { id: 1, name: 'A101 教室', campus: '北校区', icon: 'home', status: '空闲', capacity: 40, occupancy: 25 },
  { id: 2, name: '多功能厅', campus: '南校区', icon: 'shop', status: '已预约', capacity: 250, occupancy: 80, bookedRange: '已约 (10:00 - 14:00)' },
  { id: 3, name: 'B302 实验室', campus: '北校区', icon: 'gear', status: '已锁定', capacity: 0, occupancy: 0, reason: '设备维护中' },
])

function goBack() {
  uni.navigateBack()
}
function onAdd() {
  uni.showToast({ title: '新增场地', icon: 'none' })
}
function onBook(v: Venue) {
  uni.navigateTo({ url: `/pages/venue/schedule?id=${v.id}&name=${encodeURIComponent(v.name)}` })
}
function onLock(v: Venue) {
  uni.navigateTo({ url: `/pages/venue/lock?id=${v.id}&name=${encodeURIComponent(v.name)}` })
}
function onUnlock() {
  uni.showToast({ title: '已解锁', icon: 'success' })
}
function onDetail(v: Venue) {
  uni.navigateTo({ url: `/pages/venue/booking-detail?id=${v.id}` })
}
</script>

<template>
  <view class="venue-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        场地管理
      </text>
      <button class="icon-btn" @click="onAdd">
        <uni-icons type="plusempty" size="26" color="#005842" />
      </button>
    </view>

    <!-- 日期选择 -->
    <scroll-view class="date-scroll" scroll-x>
      <view class="date-row">
        <view
          v-for="d in dates"
          :key="d.day"
          class="date-cell"
          :class="{ on: activeDay === d.day }"
          @click="activeDay = d.day"
        >
          <text class="date-week">
            {{ d.week }}
          </text>
          <text class="date-day">
            {{ d.day }}
          </text>
        </view>
      </view>
    </scroll-view>

    <!-- 统计卡片 -->
    <view class="stats-grid">
      <view
        v-for="s in stats"
        :key="s.key"
        class="stat-card"
        :class="{ highlight: s.highlight }"
      >
        <view class="stat-top">
          <uni-icons :type="s.icon" size="22" :color="s.highlight ? '#8cf7c7' : s.color" />
          <view v-if="s.trend" class="trend">
            {{ s.trend }}
          </view>
        </view>
        <view class="stat-bottom">
          <text class="stat-value" :class="{ light: s.highlight }">
            {{ s.value }}
          </text>
          <text class="stat-label" :class="{ light: s.highlight }">
            {{ s.label }}
          </text>
        </view>
      </view>
    </view>

    <!-- 场地列表 -->
    <view class="section-title">
      场地
    </view>
    <view class="list">
      <view
        v-for="v in venues"
        :key="v.id"
        class="venue-card"
        :class="{ locked: v.status === '已锁定' }"
      >
        <view class="card-head">
          <view class="head-left">
            <view class="v-icon" :class="{ danger: v.status === '已锁定' }">
              <uni-icons :type="v.icon" size="24" :color="v.status === '已锁定' ? '#ba1a1a' : '#005842'" />
            </view>
            <view>
              <text class="v-name" :class="{ strike: v.status === '已锁定' }">
                {{ v.name }}
              </text>
              <view class="v-sub" :class="{ danger: v.status === '已锁定' }">
                <uni-icons :type="v.status === '已锁定' ? 'info' : 'location'" size="14" :color="v.status === '已锁定' ? '#ba1a1a' : '#3f4944'" />
                <text>{{ v.status === '已锁定' ? v.reason : v.campus }}</text>
              </view>
            </view>
          </view>
          <view
            class="status-chip"
            :class="{
              ok: v.status === '空闲',
              booked: v.status === '已预约',
              locked: v.status === '已锁定',
            }"
          >
            <uni-icons
              v-if="v.status !== '空闲'"
              :type="v.status === '已锁定' ? 'locked' : 'loop'"
              size="12"
              :color="v.status === '已锁定' ? '#93000a' : '#3f4944'"
            />
            <text>{{ v.status }}</text>
          </view>
        </view>

        <view v-if="v.status !== '已锁定'" class="metric-box">
          <view class="metric">
            <text class="metric-label">
              容量
            </text>
            <view class="metric-value">
              <uni-icons type="staff" size="16" color="#0f1d23" />
              <text>{{ v.capacity }} 人</text>
            </view>
          </view>
          <view class="metric">
            <text class="metric-label">
              今日占用
            </text>
            <view class="bar-row">
              <view class="bar-track">
                <view
                  class="bar-fill"
                  :class="{ warn: v.occupancy >= 80 }"
                  :style="{ width: `${v.occupancy}%` }"
                />
              </view>
              <text class="bar-pct">
                {{ v.occupancy }}%
              </text>
            </view>
          </view>
        </view>

        <view class="card-actions">
          <template v-if="v.status === '空闲'">
            <button class="act-btn primary" @click="onBook(v)">
              预约
            </button>
            <button class="act-btn ghost" @click="onLock(v)">
              锁场
            </button>
            <button class="act-btn square" @click="onDetail(v)">
              <uni-icons type="more-filled" size="20" color="#0f1d23" />
            </button>
          </template>
          <template v-else-if="v.status === '已预约'">
            <button class="act-btn disabled" @click="onDetail(v)">
              {{ v.bookedRange }}
            </button>
            <button class="act-btn square" @click="onDetail(v)">
              <uni-icons type="more-filled" size="20" color="#0f1d23" />
            </button>
          </template>
          <template v-else>
            <button class="act-btn ghost" @click="onUnlock">
              解锁
            </button>
            <button class="act-btn square" @click="onDetail(v)">
              <uni-icons type="more-filled" size="20" color="#0f1d23" />
            </button>
          </template>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.venue-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 60rpx;
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
  background: #ffffff;
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
  color: #005842;
}

.date-scroll {
  margin: 20rpx -28rpx 0;
  white-space: nowrap;
}

.date-row {
  display: flex;
  gap: 16rpx;
  padding: 8rpx 28rpx;
}

.date-cell {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  width: 110rpx;
  height: 130rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.date-cell.on {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.date-week {
  font-size: 22rpx;
  color: #3f4944;
}

.date-day {
  font-size: 34rpx;
  font-weight: 600;
}

.date-cell.on .date-week,
.date-cell.on .date-day {
  color: #ffffff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-top: 24rpx;
}

.stat-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 180rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.stat-card.highlight {
  background: #193f36;
  border: 0;
}

.stat-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.trend {
  display: flex;
  align-items: center;
  padding: 4rpx 14rpx;
  font-size: 20rpx;
  color: #e9f6ef;
  background: #227253;
  border-radius: 999rpx;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 700;
}

.stat-value.light {
  color: #ffffff;
}

.stat-label {
  display: block;
  margin-top: 4rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.stat-label.light {
  color: #a4f2d4;
}

.section-title {
  margin-top: 32rpx;
  font-size: 36rpx;
  font-weight: 600;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-top: 20rpx;
}

.venue-card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.venue-card.locked {
  opacity: 0.85;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.head-left {
  display: flex;
  gap: 18rpx;
}

.v-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88rpx;
  height: 88rpx;
  background: #e1f0f8;
  border-radius: 14rpx;
}

.v-icon.danger {
  background: #ffdad6;
}

.v-name {
  font-size: 32rpx;
  font-weight: 600;
}

.v-name.strike {
  text-decoration: line-through;
}

.v-sub {
  display: flex;
  gap: 6rpx;
  align-items: center;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #3f4944;
}

.v-sub.danger {
  color: #ba1a1a;
}

.status-chip {
  display: flex;
  gap: 6rpx;
  align-items: center;
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.status-chip.ok {
  color: #227253;
  background: #e9f6ef;
}

.status-chip.booked {
  color: #3f4944;
  background: #dbebf3;
}

.status-chip.locked {
  color: #93000a;
  background: #ffdad6;
}

.metric-box {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28rpx;
  padding: 22rpx;
  background: #f3faff;
  border: 1rpx solid #d6e5ed;
  border-radius: 12rpx;
}

.metric-label {
  font-size: 22rpx;
  color: #3f4944;
}

.metric-value {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 10rpx;
  font-size: 26rpx;
  font-weight: 500;
}

.bar-row {
  display: flex;
  gap: 12rpx;
  align-items: center;
  margin-top: 14rpx;
}

.bar-track {
  flex: 1;
  height: 12rpx;
  overflow: hidden;
  background: #d6e5ed;
  border-radius: 999rpx;
}

.bar-fill {
  height: 100%;
  background: #1f7159;
}

.bar-fill.warn {
  background: #d97706;
}

.bar-pct {
  font-size: 22rpx;
  font-weight: 500;
}

.card-actions {
  display: flex;
  gap: 16rpx;
}

.act-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80rpx;
  margin: 0;
  font-size: 26rpx;
  font-weight: 600;
  line-height: 80rpx;
  border-radius: 12rpx;
}

.act-btn.primary {
  flex: 1;
  color: #ffffff;
  background: #1f7159;
}

.act-btn.ghost {
  flex: 1;
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.act-btn.disabled {
  flex: 1;
  color: #3f4944;
  background: transparent;
  border: 1rpx solid #d6e5ed;
  opacity: 0.6;
}

.act-btn.square {
  width: 80rpx;
  background: #e1f0f8;
  border: 1rpx solid #d6e5ed;
}
</style>
