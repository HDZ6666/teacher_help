<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'CourseIndex',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '课程',
  },
})

interface Course {
  id: number
  name: string
  color: string
  status: '启用' | '停用'
  online: boolean
  type: string
  charge: string
  price: string
  classCount: number
}

const keyword = ref('')
const filters = ['全部', '一对多', '一对一', '启用', '停用', '可售卖']
const activeFilter = ref('全部')

const courses = ref<Course[]>([
  { id: 1, name: '少儿英语进阶', color: '#5c9ce6', status: '启用', online: true, type: '一对多', charge: '按课时', price: '￥2400 / 12节', classCount: 3 },
  { id: 2, name: '钢琴一对一VIP', color: '#e68a5c', status: '启用', online: false, type: '一对一', charge: '按期', price: '￥5800 / 期', classCount: 12 },
  { id: 3, name: '硬笔书法基础', color: '#9ca3af', status: '停用', online: false, type: '一对多', charge: '按课时', price: '￥1200 / 16节', classCount: 0 },
])

const filteredCourses = computed(() => {
  return courses.value.filter((c) => {
    if (keyword.value && !c.name.includes(keyword.value))
      return false
    if (activeFilter.value === '全部')
      return true
    if (activeFilter.value === '可售卖')
      return c.online
    if (activeFilter.value === '启用' || activeFilter.value === '停用')
      return c.status === activeFilter.value
    return c.type === activeFilter.value
  })
})

function goBack() {
  uni.navigateBack()
}
function onAdd() {
  uni.navigateTo({ url: '/pages/course/create' })
}
function onView(c: Course) {
  uni.navigateTo({ url: `/pages/course/detail?id=${c.id}` })
}
function onEdit(c: Course) {
  uni.navigateTo({ url: `/pages/course/create?id=${c.id}` })
}
function onSchedule() {
  uni.showToast({ title: '前往排课', icon: 'none' })
}
function onEnable() {
  uni.showToast({ title: '已启用', icon: 'success' })
}
</script>

<template>
  <view class="course-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        课程
      </text>
      <button class="icon-btn" @click="onAdd">
        <uni-icons type="plusempty" size="26" color="#005842" />
      </button>
    </view>

    <view class="search-box">
      <uni-icons type="search" size="24" color="#3f4944" />
      <input v-model="keyword" class="search-input" placeholder="搜索课程名称" placeholder-class="ph">
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
        v-for="c in filteredCourses"
        :key="c.id"
        class="course-card"
        :class="{ disabled: c.status === '停用' }"
      >
        <view class="card-head">
          <view class="head-left">
            <view class="dot" :style="{ background: c.color }" />
            <text class="course-name">
              {{ c.name }}
            </text>
          </view>
          <view class="tags">
            <text class="tag" :class="c.status === '启用' ? 'ok' : 'muted'">
              {{ c.status }}
            </text>
            <text v-if="c.online" class="tag online">
              线上售卖
            </text>
          </view>
        </view>
        <view class="info-grid">
          <view class="info-item">
            <uni-icons type="bars" size="15" color="#3f4944" />
            <text>类型: {{ c.type }}</text>
          </view>
          <view class="info-item">
            <uni-icons type="wallet" size="15" color="#3f4944" />
            <text>收费: {{ c.charge }}</text>
          </view>
          <view class="info-item full price">
            <uni-icons type="tag" size="15" color="#0f1d23" />
            <text>{{ c.price }}</text>
          </view>
          <view class="info-item full muted-text">
            <uni-icons type="staff" size="15" color="#74828a" />
            <text>关联班级: {{ c.classCount }}个</text>
          </view>
        </view>
        <view class="card-actions">
          <text class="act" @click="onView(c)">
            查看
          </text>
          <text v-if="c.status === '启用'" class="act" @click="onEdit(c)">
            编辑
          </text>
          <text v-if="c.status === '启用'" class="act primary" @click="onSchedule">
            排课
          </text>
          <text v-else class="act primary" @click="onEnable">
            启用
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.course-page {
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
}

.search-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
  height: 80rpx;
  margin-top: 24rpx;
  padding: 0 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
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
  border: 1rpx solid #e7ece9;
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

.course-card {
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.course-card.disabled {
  opacity: 0.75;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.head-left {
  display: flex;
  gap: 14rpx;
  align-items: center;
}

.dot {
  flex-shrink: 0;
  width: 24rpx;
  height: 24rpx;
  border-radius: 6rpx;
}

.course-name {
  font-size: 32rpx;
  font-weight: 600;
}

.tags {
  display: flex;
  gap: 8rpx;
}

.tag {
  padding: 4rpx 14rpx;
  font-size: 22rpx;
  border-radius: 6rpx;
}

.tag.ok {
  color: #227253;
  background: #e9f6ef;
}

.tag.muted {
  color: #3f4944;
  background: #d6e5ed;
}

.tag.online {
  color: #1f7159;
  background: #e7f6fe;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx 20rpx;
  margin-top: 22rpx;
}

.info-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.info-item.full {
  grid-column: span 2;
}

.info-item.price {
  font-weight: 500;
  color: #0f1d23;
}

.info-item.muted-text {
  color: #74828a;
}

.card-actions {
  display: flex;
  gap: 30rpx;
  justify-content: flex-end;
  margin-top: 22rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #e7ece9;
}

.act {
  font-size: 26rpx;
  color: #3f4944;
}

.act.primary {
  color: #1f7159;
}
</style>
