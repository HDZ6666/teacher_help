<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'StudentList',
})
definePage({
  style: {
    navigationBarTitleText: '学员',
    enablePullDownRefresh: true,
  },
})

interface StudentItem {
  id: number
  name: string
  grade: string
  school: string
  phone: string
  className: string
  remaining: number
  tags: string[]
  status: 'studying' | 'low' | 'absent' | 'follow' | 'unbound'
}

const keyword = ref('')
const activeFilter = ref('all')

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '在读', value: 'studying' },
  { label: '课时不足', value: 'low' },
  { label: '近期缺勤', value: 'absent' },
  { label: '待跟进', value: 'follow' },
  { label: '未绑定微信', value: 'unbound' },
]

// 静态 mock 数据
const students = ref<StudentItem[]>([
  { id: 1, name: '李明轩', grade: '三年级', school: '实验小学', phone: '138****2046', className: '数学提高A班', remaining: 2, tags: ['课时不足', '待跟进'], status: 'low' },
  { id: 2, name: '王诗涵', grade: '五年级', school: '育才小学', phone: '139****7781', className: '英语精读B班', remaining: 18, tags: ['在读'], status: 'studying' },
  { id: 3, name: '张子墨', grade: '初一', school: '第三中学', phone: '137****5520', className: '物理基础班', remaining: 6, tags: ['近期缺勤'], status: 'absent' },
  { id: 4, name: '陈嘉怡', grade: '四年级', school: '阳光小学', phone: '135****9013', className: '作文兴趣班', remaining: 12, tags: ['未绑定'], status: 'unbound' },
  { id: 5, name: '刘梓萱', grade: '初二', school: '外国语学校', phone: '136****3344', className: '数学冲刺班', remaining: 1, tags: ['课时不足'], status: 'low' },
  { id: 6, name: '赵奕辰', grade: '六年级', school: '中心小学', phone: '188****6677', className: '英语口语班', remaining: 24, tags: ['在读'], status: 'studying' },
])

const filteredStudents = computed(() => {
  return students.value.filter((item) => {
    const matchKeyword = !keyword.value
      || item.name.includes(keyword.value)
      || item.phone.includes(keyword.value)
      || item.className.includes(keyword.value)
    const matchFilter = activeFilter.value === 'all' || item.status === activeFilter.value
    return matchKeyword && matchFilter
  })
})

function tagClass(tag: string) {
  if (tag.includes('不足'))
    return 'warn'
  if (tag.includes('缺勤'))
    return 'danger'
  if (tag.includes('跟进'))
    return 'info'
  if (tag.includes('未绑定'))
    return 'muted'
  return 'success'
}

function openDetail(item: StudentItem) {
  uni.navigateTo({ url: `/pages/student/detail?id=${item.id}` })
}

function contactStudent(item: StudentItem) {
  uni.showToast({ title: `联系 ${item.name} 家长`, icon: 'none' })
}

function openEnroll(item: StudentItem) {
  uni.showToast({ title: `${item.name} 报名续费`, icon: 'none' })
}

function openWrong(item: StudentItem) {
  uni.switchTab({ url: '/pages/wrong-question/index' })
}

function addStudent() {
  uni.showToast({ title: '新增学员', icon: 'none' })
}
</script>

<template>
  <view class="student-page">
    <view class="search-bar">
      <view class="search-input">
        <uni-icons type="search" size="18" color="#8a969d" />
        <input v-model="keyword" class="search-field" placeholder="搜索姓名 / 手机号 / 班级" placeholder-class="search-ph">
      </view>
      <button class="add-btn" @click="addStudent">
        <uni-icons type="plusempty" size="18" color="#ffffff" />
      </button>
    </view>

    <scroll-view class="filter-scroll" scroll-x>
      <view class="filter-row">
        <button
          v-for="item in filterOptions"
          :key="item.value"
          class="filter-btn"
          :class="{ active: activeFilter === item.value }"
          @click="activeFilter = item.value"
        >
          {{ item.label }}
        </button>
      </view>
    </scroll-view>

    <view v-if="!filteredStudents.length" class="state-box">
      暂无学员
    </view>
    <view v-else class="student-list">
      <view v-for="item in filteredStudents" :key="item.id" class="student-card" @click="openDetail(item)">
        <view class="card-head">
          <view class="avatar">
            {{ item.name.slice(0, 1) }}
          </view>
          <view class="head-main">
            <view class="name-line">
              <text class="name">
                {{ item.name }}
              </text>
              <text class="meta">
                {{ item.grade }} · {{ item.school }}
              </text>
            </view>
            <view class="sub-line">
              {{ item.className }} · {{ item.phone }}
            </view>
            <view class="tag-line">
              <text v-for="tag in item.tags" :key="tag" class="tag" :class="tagClass(tag)">
                {{ tag }}
              </text>
            </view>
          </view>
          <view class="remaining" :class="{ low: item.remaining <= 3 }">
            <view class="remaining-num">
              {{ item.remaining }}
            </view>
            <view class="remaining-label">
              剩余课时
            </view>
          </view>
        </view>
        <view class="card-actions" @click.stop>
          <button class="act-btn" @click="openDetail(item)">
            详情
          </button>
          <button class="act-btn" @click="contactStudent(item)">
            联系
          </button>
          <button class="act-btn" @click="openEnroll(item)">
            续费
          </button>
          <button class="act-btn" @click="openWrong(item)">
            错题
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
  padding: 24rpx 28rpx 150rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.search-input {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 12rpx;
  height: 76rpx;
  padding: 0 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 999rpx;
}

.search-field {
  flex: 1;
  font-size: 27rpx;
  color: #1f2d33;
}

.search-ph {
  color: #9aa5aa;
}

.add-btn {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  padding: 0;
  margin: 0;
  background: #1f7159;
  border-radius: 50%;
}

.add-btn::after {
  border: 0;
}

.filter-scroll {
  margin: 22rpx -28rpx 18rpx;
  white-space: nowrap;
}

.filter-row {
  display: flex;
  gap: 14rpx;
  padding: 0 28rpx;
}

.filter-btn {
  padding: 16rpx 24rpx;
  margin: 0;
  font-size: 25rpx;
  line-height: 1;
  color: #67757c;
  background: #ffffff;
  border: 1rpx solid #e2e8e5;
  border-radius: 999rpx;
}

.filter-btn::after {
  border: 0;
}

.filter-btn.active {
  color: #1e7259;
  background: #e6f4ee;
  border-color: #b8dccc;
}

.state-box {
  padding: 90rpx 0;
  font-size: 28rpx;
  color: #7a858b;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.student-card {
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.card-head {
  display: flex;
  gap: 20rpx;
  align-items: flex-start;
}

.avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 84rpx;
  height: 84rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 20rpx;
}

.head-main {
  flex: 1;
  min-width: 0;
}

.name-line {
  display: flex;
  align-items: baseline;
  gap: 12rpx;
}

.name {
  font-size: 32rpx;
  font-weight: 700;
}

.meta {
  overflow: hidden;
  font-size: 23rpx;
  color: #839099;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub-line {
  margin-top: 10rpx;
  overflow: hidden;
  font-size: 25rpx;
  color: #75838a;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-line {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 14rpx;
}

.tag {
  padding: 6rpx 14rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.tag.success {
  color: #227253;
  background: #e9f6ef;
}

.tag.warn {
  color: #8a671b;
  background: #fff5d8;
}

.tag.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.tag.info {
  color: #335d9a;
  background: #eaf1ff;
}

.tag.muted {
  color: #5d6a70;
  background: #eef2f0;
}

.remaining {
  flex-shrink: 0;
  min-width: 110rpx;
  padding: 12rpx 0;
  text-align: center;
}

.remaining-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #183a34;
}

.remaining.low .remaining-num {
  color: #c0392b;
}

.remaining-label {
  margin-top: 4rpx;
  font-size: 22rpx;
  color: #718088;
}

.card-actions {
  display: flex;
  gap: 12rpx;
  margin-top: 22rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #edf1ef;
}

.act-btn {
  flex: 1;
  padding: 0;
  margin: 0;
  font-size: 25rpx;
  line-height: 64rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 12rpx;
}

.act-btn::after {
  border: 0;
}
</style>
