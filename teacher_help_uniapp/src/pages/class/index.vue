<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ClassList',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '班级',
  },
})

interface ClassItem {
  id: number
  name: string
  course: string
  type: 'group' | 'one'
  teacher: string
  room: string
  students: string
  schedule: string
  status: 'active' | 'pending' | 'done'
}

const keyword = ref('')
const activeFilter = ref('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '班课', value: 'group' },
  { label: '一对一', value: 'one' },
  { label: '今日有课', value: 'today' },
  { label: '待排课', value: 'pending' },
  { label: '已结业', value: 'done' },
]

const classes = ref<ClassItem[]>([
  {
    id: 1,
    name: '春季初二数学强化班',
    course: '初中数学',
    type: 'group',
    teacher: '张老师',
    room: '教室 A102',
    students: '12/15 人',
    schedule: '每周 2 节课，已上 10/20',
    status: 'active',
  },
  {
    id: 2,
    name: '高中英语VIP(李华)',
    course: '高中英语',
    type: 'one',
    teacher: '王老师',
    room: 'VIP 3室',
    students: '1/1 人',
    schedule: '课时包，剩余 15 课时',
    status: 'pending',
  },
  {
    id: 3,
    name: '秋季物理实验营',
    course: '物理实验',
    type: 'group',
    teacher: '陈老师',
    room: '实验室 B201',
    students: '9/12 人',
    schedule: '周六 14:00-16:00',
    status: 'done',
  },
])

const filteredClasses = computed(() => {
  return classes.value.filter((item) => {
    const matchKeyword = !keyword.value || item.name.includes(keyword.value) || item.course.includes(keyword.value) || item.teacher.includes(keyword.value)
    const matchFilter = activeFilter.value === 'all'
      || activeFilter.value === item.type
      || activeFilter.value === item.status
      || (activeFilter.value === 'today' && item.id === 1)
    return matchKeyword && matchFilter
  })
})

function goBack() {
  uni.navigateBack()
}

function createClass() {
  uni.navigateTo({ url: '/pages/class/create' })
}

function openDetail(item: ClassItem) {
  uni.navigateTo({ url: `/pages/class/detail?id=${item.id}` })
}

function addStudent() {
  uni.navigateTo({ url: '/pages/student/add' })
}

function createSchedule() {
  uni.navigateTo({ url: '/pages/schedule/create' })
}

function checkin() {
  uni.navigateTo({ url: '/pages/schedule/detail' })
}

function statusText(status: ClassItem['status']) {
  const map = {
    active: '开班中',
    pending: '待排课',
    done: '已结业',
  }
  return map[status]
}
</script>

<template>
  <view class="class-page">
    <view class="topbar">
      <button class="nav-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#1f7159" />
      </button>
      <text class="page-title">
        班级
      </text>
      <button class="nav-btn" @click="createClass">
        <uni-icons type="plus" size="24" color="#1f7159" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="22" color="#6f7974" />
      <input v-model="keyword" class="search-input" placeholder="搜索班级/课程/老师" placeholder-class="placeholder">
    </view>

    <scroll-view class="filter-scroll" scroll-x>
      <view class="filter-row">
        <button
          v-for="item in filters"
          :key="item.value"
          class="filter-chip"
          :class="{ active: activeFilter === item.value }"
          @click="activeFilter = item.value"
        >
          {{ item.label }}
        </button>
      </view>
    </scroll-view>

    <view class="class-list">
      <view v-for="item in filteredClasses" :key="item.id" class="class-card">
        <view class="card-head" @click="openDetail(item)">
          <text class="class-name">
            {{ item.name }}
          </text>
          <text class="status-pill" :class="item.status">
            {{ statusText(item.status) }}
          </text>
        </view>

        <view class="info-grid" @click="openDetail(item)">
          <view class="info-line">
            <uni-icons type="paperclip" size="16" color="#6f7974" />
            <text>{{ item.course }}</text>
            <text class="type-tag">
              {{ item.type === 'group' ? '班课' : '一对一' }}
            </text>
          </view>
          <view class="info-line">
            <uni-icons type="person" size="16" color="#6f7974" />
            <text>{{ item.teacher }}</text>
          </view>
          <view class="info-line">
            <uni-icons type="home" size="16" color="#6f7974" />
            <text>{{ item.room }}</text>
          </view>
          <view class="info-line">
            <uni-icons type="staff" size="16" color="#6f7974" />
            <text>{{ item.students }}</text>
          </view>
          <view class="info-line wide">
            <uni-icons type="calendar" size="16" color="#6f7974" />
            <text>{{ item.schedule }}</text>
          </view>
        </view>

        <view class="actions">
          <button class="action-btn" @click="addStudent">
            <uni-icons type="personadd" size="18" color="#1f7159" />
            <text>学员</text>
          </button>
          <button class="action-btn" @click="createSchedule">
            <uni-icons type="calendar" size="18" color="#1f7159" />
            <text>排课</text>
          </button>
          <button class="action-btn" @click="checkin">
            <uni-icons type="checkbox-filled" size="18" color="#1f7159" />
            <text>点名</text>
          </button>
          <button class="action-btn" @click="openDetail(item)">
            <uni-icons type="eye" size="18" color="#1f7159" />
            <text>详情</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.class-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 60rpx;
  color: #0f1d23;
  background: #f4f6f5;
}

button::after {
  border: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 112rpx;
  margin: 0 -28rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #e1e8e4;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1f7159;
}

.search-box {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 22rpx;
  margin-top: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.search-input {
  flex: 1;
  height: 88rpx;
  padding-left: 14rpx;
  font-size: 28rpx;
}

.placeholder {
  color: #8a9690;
}

.filter-scroll {
  margin: 24rpx -28rpx 0;
  white-space: nowrap;
}

.filter-row {
  display: inline-flex;
  gap: 16rpx;
  padding: 0 28rpx 4rpx;
}

.filter-chip {
  height: 58rpx;
  padding: 0 24rpx;
  margin: 0;
  font-size: 24rpx;
  font-weight: 600;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 999rpx;
}

.filter-chip.active {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.class-list {
  margin-top: 24rpx;
}

.class-card {
  padding: 28rpx;
  margin-bottom: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
  box-shadow: 0 6rpx 18rpx rgba(15, 29, 35, 0.04);
}

.card-head {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
  justify-content: space-between;
}

.class-name {
  flex: 1;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.35;
}

.status-pill {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
  border-radius: 999rpx;
}

.status-pill.active {
  color: #227253;
  background: #e9f6ef;
}

.status-pill.pending {
  color: #8a671b;
  background: #fff5d8;
}

.status-pill.done {
  color: #5d6a70;
  background: #eef2f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx 14rpx;
  margin-top: 22rpx;
}

.info-line {
  display: flex;
  gap: 8rpx;
  align-items: center;
  min-width: 0;
  font-size: 25rpx;
  color: #5f6d66;
}

.info-line text:not(.type-tag) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-line.wide {
  grid-column: span 2;
}

.type-tag {
  flex: none;
  padding: 2rpx 10rpx;
  font-size: 20rpx;
  color: #40655b;
  background: #e7f6fe;
  border-radius: 6rpx;
}

.actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding-top: 20rpx;
  margin-top: 24rpx;
  border-top: 1rpx solid #edf1ef;
}

.action-btn {
  display: flex;
  gap: 6rpx;
  align-items: center;
  justify-content: center;
  min-height: 54rpx;
  padding: 0;
  margin: 0;
  font-size: 24rpx;
  font-weight: 600;
  color: #1f7159;
  background: transparent;
  border-right: 1rpx solid #edf1ef;
  border-radius: 0;
}

.action-btn:last-child {
  border-right: 0;
}
</style>
