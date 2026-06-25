<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'TeacherIndex',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '老师',
  },
})

interface Teacher {
  id: number
  name: string
  avatarText: string
  subject: string
  phone: string
  status: '启用' | '停用'
  todayCount: number
  weekHours: number
}

const keyword = ref('')
const filters = ['全部', '今日有课', '本周有课', '启用', '停用']
const activeFilter = ref('全部')

const teachers = ref<Teacher[]>([
  { id: 1, name: '李明', avatarText: '李', subject: '初中数学', phone: '138 0000 0001', status: '启用', todayCount: 2, weekHours: 12 },
  { id: 2, name: '张芳', avatarText: '张', subject: '高中英语', phone: '139 1234 5678', status: '启用', todayCount: 4, weekHours: 20 },
  { id: 3, name: '王强', avatarText: '王', subject: '小学语文', phone: '137 9876 5432', status: '停用', todayCount: 0, weekHours: 0 },
])

const filteredTeachers = computed(() => {
  return teachers.value.filter((t) => {
    if (keyword.value && !t.name.includes(keyword.value) && !t.phone.includes(keyword.value) && !t.subject.includes(keyword.value))
      return false
    if (activeFilter.value === '全部')
      return true
    if (activeFilter.value === '今日有课')
      return t.todayCount > 0
    if (activeFilter.value === '本周有课')
      return t.weekHours > 0
    if (activeFilter.value === '启用' || activeFilter.value === '停用')
      return t.status === activeFilter.value
    return true
  })
})

function goBack() {
  uni.navigateBack()
}
function onAdd() {
  uni.navigateTo({ url: '/pages/teacher/create' })
}
function onDetail(t: Teacher) {
  uni.navigateTo({ url: `/pages/teacher/detail?id=${t.id}` })
}
function onSchedule(t: Teacher) {
  uni.navigateTo({ url: `/pages/teacher/schedule?id=${t.id}` })
}
function onContact(t: Teacher) {
  uni.makePhoneCall({ phoneNumber: t.phone.replace(/\s/g, '') })
}
</script>

<template>
  <view class="teacher-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        老师
      </text>
      <button class="icon-btn" @click="onAdd">
        <uni-icons type="plusempty" size="26" color="#005842" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="24" color="#3f4944" />
      <input v-model="keyword" class="search-input" placeholder="搜索姓名/手机号/学科" placeholder-class="ph">
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
        v-for="t in filteredTeachers"
        :key="t.id"
        class="teacher-card"
        :class="{ disabled: t.status === '停用' }"
      >
        <view class="card-head">
          <view class="head-left">
            <view class="avatar" :class="{ off: t.status === '停用' }">
              {{ t.avatarText }}
            </view>
            <view class="head-info">
              <view class="name-row">
                <text class="teacher-name">
                  {{ t.name }}
                </text>
                <text class="subject-tag">
                  {{ t.subject }}
                </text>
              </view>
              <text class="phone">
                {{ t.phone }}
              </text>
            </view>
          </view>
          <view class="status" :class="t.status === '启用' ? 'ok' : 'muted'">
            <view class="status-dot" />
            {{ t.status }}
          </view>
        </view>

        <view class="divider" />

        <view class="stats">
          <view class="stat-item">
            <text class="stat-label">
              今日课程
            </text>
            <text class="stat-value">
              {{ t.todayCount }} <text class="stat-unit">节</text>
            </text>
          </view>
          <view class="stat-item line">
            <text class="stat-label">
              本周课时
            </text>
            <text class="stat-value">
              {{ t.weekHours }} <text class="stat-unit">时</text>
            </text>
          </view>
        </view>

        <view class="card-actions">
          <button v-if="t.status === '启用'" class="act primary" @click="onSchedule(t)">
            课表
          </button>
          <button v-else class="act disabled-btn">
            课表
          </button>
          <button v-if="t.status === '启用'" class="act outline" @click="onContact(t)">
            <uni-icons type="phone" size="16" color="#1f7159" />联系
          </button>
          <button class="act ghost" @click="onDetail(t)">
            详情
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.teacher-page {
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
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
}

.ph {
  color: #9aa5aa;
}

.chip-scroll {
  margin: 20rpx -28rpx 0;
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

.teacher-card {
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.teacher-card.disabled {
  opacity: 0.75;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.head-left {
  display: flex;
  gap: 20rpx;
  align-items: center;
}

.avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 88rpx;
  height: 88rpx;
  font-size: 34rpx;
  font-weight: 600;
  color: #1f7159;
  background: #dbebf3;
  border-radius: 50%;
}

.avatar.off {
  color: #3f4944;
  background: #d6e5ed;
}

.head-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.name-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.teacher-name {
  font-size: 32rpx;
  font-weight: 600;
}

.subject-tag {
  padding: 4rpx 14rpx;
  font-size: 22rpx;
  color: #3f4944;
  background: #e1f0f8;
  border-radius: 6rpx;
}

.phone {
  font-size: 25rpx;
  color: #3f4944;
}

.status {
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 6rpx 18rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.status.ok {
  color: #227253;
  background: #e9f6ef;
}

.status.muted {
  color: #3f4944;
  background: #d6e5ed;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  background: currentColor;
  border-radius: 50%;
}

.divider {
  height: 1rpx;
  margin: 22rpx 0;
  background: #e7ece9;
}

.stats {
  display: flex;
  gap: 32rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.stat-item.line {
  padding-left: 32rpx;
  border-left: 1rpx solid #e7ece9;
}

.stat-label {
  font-size: 22rpx;
  color: #3f4944;
}

.stat-value {
  font-size: 32rpx;
  font-weight: 600;
}

.stat-unit {
  font-size: 24rpx;
  font-weight: 400;
  color: #3f4944;
}

.card-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 24rpx;
}

.act {
  flex: 1;
  display: flex;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  height: 76rpx;
  margin: 0;
  font-size: 26rpx;
  line-height: 76rpx;
  border-radius: 10rpx;
}

.act.primary {
  color: #ffffff;
  background: #1f7159;
}

.act.outline {
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
}

.act.ghost {
  color: #0f1d23;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
}

.act.disabled-btn {
  color: #9aa5aa;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
}
</style>
