<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'StudentList',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '学员',
    enablePullDownRefresh: true,
  },
})

interface StudentItem {
  id: number
  name: string
  gender: 'male' | 'female'
  age: string
  grade: string
  className: string
  remaining: number
  lastLesson: string
  status: 'studying' | 'renew' | 'stopped' | 'today' | 'leave'
  avatar?: string
}

const keyword = ref('')
const activeFilter = ref('all')

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '在读', value: 'studying' },
  { label: '待续费', value: 'renew' },
  { label: '已停课', value: 'stopped' },
  { label: '今日有课', value: 'today' },
  { label: '请假中', value: 'leave' },
]

const students = ref<StudentItem[]>([
  { id: 1, name: '张小明', gender: 'male', age: '12岁', grade: '初一', className: '英语进阶班', remaining: 24, lastLesson: '2023-10-27', status: 'studying' },
  { id: 2, name: '李思思', gender: 'female', age: '10岁', grade: '小学四年级', className: '数学思维班', remaining: 2, lastLesson: '2023-10-25', status: 'renew', avatar: '/static/images/avatar.jpg' },
  { id: 3, name: '王强', gender: 'male', age: '15岁', grade: '高一', className: '物理集训营', remaining: 12, lastLesson: '2023-09-10', status: 'stopped' },
])

const filteredStudents = computed(() => {
  return students.value.filter((item) => {
    const matchKeyword = !keyword.value
      || item.name.includes(keyword.value)
      || item.className.includes(keyword.value)
      || item.grade.includes(keyword.value)
    const matchFilter = activeFilter.value === 'all' || item.status === activeFilter.value
    return matchKeyword && matchFilter
  })
})

function statusText(status: StudentItem['status']) {
  const map = {
    studying: '在读',
    renew: '待续费',
    stopped: '已停课',
    today: '今日有课',
    leave: '请假中',
  }
  return map[status]
}

function openDetail(item: StudentItem) {
  uni.navigateTo({ url: `/pages/student/detail?id=${item.id}` })
}

function openLeave(item: StudentItem) {
  uni.navigateTo({ url: `/pages/student/leave?name=${encodeURIComponent(item.name)}` })
}

function contactStudent(item: StudentItem) {
  uni.showActionSheet({
    itemList: ['打电话', '复制手机号', '发消息', '添加跟进记录'],
    success: () => uni.showToast({ title: `联系 ${item.name}`, icon: 'none' }),
  })
}

function addStudent() {
  uni.navigateTo({ url: '/pages/student/add' })
}
</script>

<template>
  <view class="student-page">
    <view class="top-bar">
      <view class="brand">
        <image src="/static/images/avatar.jpg" mode="aspectFill" class="teacher-avatar" />
        <text class="brand-text">
          老师帮
        </text>
      </view>
      <button class="campus-btn">
        切换校区
      </button>
    </view>

    <view class="title-row">
      <text class="page-title">
        学员
      </text>
      <button class="add-round" @click="addStudent">
        <uni-icons type="personadd" size="24" color="#00684f" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="23" color="#34433d" />
      <input v-model="keyword" class="search-input" placeholder="搜索姓名、手机号、班级" placeholder-class="placeholder">
    </view>

    <scroll-view class="filter-scroll" scroll-x>
      <view class="filter-row">
        <button
          v-for="item in filterOptions"
          :key="item.value"
          class="filter-chip"
          :class="{ active: activeFilter === item.value }"
          @click="activeFilter = item.value"
        >
          {{ item.label }}
        </button>
      </view>
    </scroll-view>

    <view class="student-list">
      <view
        v-for="item in filteredStudents"
        :key="item.id"
        class="student-card"
        :class="{ disabled: item.status === 'stopped' }"
        @click="openDetail(item)"
      >
        <view class="card-head">
          <image v-if="item.avatar" :src="item.avatar" mode="aspectFill" class="avatar-img" />
          <view v-else class="avatar-text">
            {{ item.name.slice(0, 1) }}
          </view>
          <view class="student-main">
            <view class="name-line">
              <text class="student-name">
                {{ item.name }}
              </text>
              <text class="gender" :class="item.gender">
                {{ item.gender === 'male' ? '♂' : '♀' }}
              </text>
            </view>
            <view class="student-meta">
              {{ item.age }} · {{ item.grade }} · {{ item.className }}
            </view>
          </view>
          <text class="status-pill" :class="item.status">
            {{ statusText(item.status) }}
          </text>
        </view>

        <view class="stat-panel">
          <view class="stat-block">
            <text class="stat-label">
              剩余课时
            </text>
            <view class="stat-value" :class="{ danger: item.remaining <= 3 }">
              {{ item.remaining }} <text>节</text>
            </view>
          </view>
          <view class="stat-divider" />
          <view class="stat-block">
            <text class="stat-label">
              最近上课
            </text>
            <view class="stat-date">
              {{ item.lastLesson }}
            </view>
          </view>
        </view>

        <view class="card-actions" @click.stop>
          <button class="action-btn" @click="contactStudent(item)">
            <uni-icons type="phone" size="18" color="#00684f" />
            <text>联系</text>
          </button>
          <button class="action-btn" :disabled="item.status === 'stopped'" @click="openLeave(item)">
            <uni-icons type="calendar" size="18" color="#00684f" />
            <text>请假</text>
          </button>
          <button class="action-btn" @click="openDetail(item)">
            <uni-icons type="eye" size="18" color="#00684f" />
            <text>详情</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.student-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 160rpx;
  color: #101f26;
  background: #f4f6f5;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 104rpx;
  margin: 0 -28rpx;
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #c9d5d0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.teacher-avatar {
  width: 58rpx;
  height: 58rpx;
  border: 2rpx solid #76988b;
  border-radius: 50%;
}

.brand-text {
  font-size: 34rpx;
  font-weight: 800;
  color: #00684f;
}

.campus-btn {
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 56rpx;
  color: #00684f;
  background: transparent;
}

.campus-btn::after,
.add-round::after,
.filter-chip::after,
.action-btn::after {
  border: 0;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 50rpx;
}

.page-title {
  font-size: 48rpx;
  font-weight: 800;
  color: #101f26;
}

.add-round {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 74rpx;
  height: 74rpx;
  padding: 0;
  margin: 0;
  background: #e1f0f8;
  border-radius: 50%;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 18rpx;
  height: 82rpx;
  margin-top: 38rpx;
  padding: 0 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
  box-shadow: 0 2rpx 4rpx rgba(16, 31, 38, 0.06);
}

.search-input {
  flex: 1;
  font-size: 28rpx;
}

.placeholder {
  color: #8a969d;
}

.filter-scroll {
  margin: 32rpx -28rpx 26rpx;
  white-space: nowrap;
}

.filter-row {
  display: flex;
  gap: 16rpx;
  padding: 0 28rpx;
}

.filter-chip {
  height: 58rpx;
  padding: 0 30rpx;
  margin: 0;
  font-size: 28rpx;
  line-height: 58rpx;
  color: #34433d;
  background: #e7f6fe;
  border: 1rpx solid #b8c6c0;
  border-radius: 999rpx;
}

.filter-chip.active {
  color: #ffffff;
  background: #1f7159;
  border-color: #1f7159;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.student-card {
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #c9d5d0;
  border-radius: 16rpx;
}

.student-card.disabled {
  opacity: 0.68;
}

.card-head {
  display: flex;
  align-items: flex-start;
  gap: 22rpx;
}

.avatar-img,
.avatar-text {
  width: 74rpx;
  height: 74rpx;
  border-radius: 50%;
}

.avatar-img {
  border: 1rpx solid #c9d5d0;
}

.avatar-text {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 800;
  color: #1f7159;
  background: #c2ebde;
}

.student-main {
  flex: 1;
  min-width: 0;
}

.name-line {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.student-name {
  font-size: 31rpx;
  font-weight: 800;
}

.gender {
  font-size: 26rpx;
  font-weight: 700;
}

.gender.male {
  color: #00684f;
}

.gender.female {
  color: #cc1b1b;
}

.student-meta {
  margin-top: 8rpx;
  font-size: 26rpx;
  line-height: 38rpx;
  color: #27343b;
}

.status-pill {
  flex-shrink: 0;
  padding: 10rpx 18rpx;
  font-size: 27rpx;
  font-weight: 800;
  border-radius: 8rpx;
}

.status-pill.studying,
.status-pill.today,
.status-pill.leave {
  color: #1f7159;
  background: #dff4ec;
  border: 1rpx solid #aadac9;
}

.status-pill.renew {
  color: #ffffff;
  background: #007f5f;
}

.status-pill.stopped {
  color: #5d6a70;
  background: #eef2f0;
  border: 1rpx solid #c9d5d0;
}

.stat-panel {
  display: flex;
  align-items: center;
  margin: 28rpx 0;
  padding: 24rpx;
  background: #e7f6fe;
  border: 1rpx solid #cce3ec;
  border-radius: 10rpx;
}

.stat-block {
  flex: 1;
}

.stat-label {
  font-size: 24rpx;
  color: #5d6a70;
}

.stat-value,
.stat-date {
  margin-top: 12rpx;
  font-size: 32rpx;
  font-weight: 800;
  color: #101f26;
}

.stat-value {
  color: #00684f;
}

.stat-value.danger {
  color: #ba1a1a;
}

.stat-value text {
  font-size: 24rpx;
  font-weight: 500;
}

.stat-divider {
  width: 1rpx;
  height: 58rpx;
  margin: 0 36rpx;
  background: #c9d5d0;
}

.card-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #c9d5d0;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  height: 62rpx;
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 62rpx;
  color: #00684f;
  background: #e7f6fe;
  border-radius: 10rpx;
}

.action-btn[disabled] {
  color: #5d6a70;
  background: #eef2f0;
}
</style>
