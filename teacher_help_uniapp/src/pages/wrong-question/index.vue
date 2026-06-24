<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'WrongQuestion',
})
definePage({
  style: {
    navigationBarTitleText: '错题本',
    enablePullDownRefresh: true,
  },
})

interface WrongItem {
  id: number
  student: string
  subject: string
  point: string
  mastery: '未掌握' | '已了解' | '已掌握'
  aiStatus: 'analyzing' | 'pending' | 'done' | 'failed'
  updateTime: string
}

const keyword = ref('')
const activeFilter = ref('all')

const stats = [
  { key: 'pending-ai', label: '待解析', value: 3, tone: 'warn' },
  { key: 'pending', label: '待确认', value: 5, tone: 'info' },
  { key: 'unmastered', label: '未掌握', value: 12, tone: 'danger' },
  { key: 'mastered', label: '已掌握', value: 48, tone: 'success' },
]

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '待解析', value: 'analyzing' },
  { label: '待确认', value: 'pending' },
  { label: '未掌握', value: 'unmastered' },
  { label: '已掌握', value: 'mastered' },
  { label: '本周新增', value: 'week' },
]

const aiStatusMap = {
  analyzing: { text: '识别中', cls: 'info' },
  pending: { text: '待确认', cls: 'warn' },
  done: { text: '已完成', cls: 'success' },
  failed: { text: '识别失败', cls: 'danger' },
}

const list = ref<WrongItem[]>([
  { id: 1, student: '李明轩', subject: '数学', point: '分数应用题', mastery: '未掌握', aiStatus: 'done', updateTime: '10分钟前' },
  { id: 2, student: '王诗涵', subject: '英语', point: '现在完成时', mastery: '已了解', aiStatus: 'pending', updateTime: '1小时前' },
  { id: 3, student: '张子墨', subject: '物理', point: '受力分析', mastery: '未掌握', aiStatus: 'analyzing', updateTime: '刚刚' },
  { id: 4, student: '陈嘉怡', subject: '语文', point: '修辞手法', mastery: '已掌握', aiStatus: 'done', updateTime: '昨天' },
  { id: 5, student: '刘梓萱', subject: '数学', point: '二次函数', mastery: '未掌握', aiStatus: 'failed', updateTime: '昨天' },
])

const filteredList = computed(() => {
  return list.value.filter((item) => {
    const matchKeyword = !keyword.value
      || item.student.includes(keyword.value)
      || item.subject.includes(keyword.value)
      || item.point.includes(keyword.value)
    let matchFilter = true
    if (activeFilter.value === 'analyzing')
      matchFilter = item.aiStatus === 'analyzing'
    else if (activeFilter.value === 'pending')
      matchFilter = item.aiStatus === 'pending'
    else if (activeFilter.value === 'unmastered')
      matchFilter = item.mastery === '未掌握'
    else if (activeFilter.value === 'mastered')
      matchFilter = item.mastery === '已掌握'
    return matchKeyword && matchFilter
  })
})

function masteryClass(m: string) {
  if (m === '未掌握')
    return 'danger'
  if (m === '已了解')
    return 'warn'
  return 'success'
}

function openUpload() {
  uni.navigateTo({ url: '/pages/wrong-question/upload' })
}

function openDetail(item: WrongItem) {
  if (item.aiStatus === 'analyzing') {
    uni.navigateTo({ url: '/pages/wrong-question/analyzing' })
    return
  }
  uni.navigateTo({ url: `/pages/wrong-question/detail?id=${item.id}` })
}
</script>

<template>
  <view class="wq-page">
    <view class="search-bar">
      <view class="search-input">
        <uni-icons type="search" size="18" color="#8a969d" />
        <input v-model="keyword" class="search-field" placeholder="搜索学生 / 题目 / 知识点" placeholder-class="search-ph">
      </view>
      <button class="cam-btn" @click="openUpload">
        <uni-icons type="camera" size="20" color="#ffffff" />
      </button>
    </view>

    <view class="stat-grid">
      <view v-for="s in stats" :key="s.key" class="stat-item">
        <view class="stat-value" :class="s.tone">
          {{ s.value }}
        </view>
        <view class="stat-label">
          {{ s.label }}
        </view>
      </view>
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

    <view v-if="!filteredList.length" class="state-box">
      暂无错题
    </view>
    <view v-else class="wq-list">
      <view v-for="item in filteredList" :key="item.id" class="wq-card" @click="openDetail(item)">
        <view class="wq-thumb">
          <uni-icons type="image" size="28" color="#9aa5aa" />
        </view>
        <view class="wq-main">
          <view class="wq-title-line">
            <text class="wq-title">
              {{ item.subject }} · {{ item.point }}
            </text>
            <text class="ai-pill" :class="aiStatusMap[item.aiStatus].cls">
              {{ aiStatusMap[item.aiStatus].text }}
            </text>
          </view>
          <view class="wq-sub">
            {{ item.student }} · {{ item.updateTime }}
          </view>
          <view class="wq-foot">
            <text class="mastery" :class="masteryClass(item.mastery)">
              {{ item.mastery }}
            </text>
          </view>
        </view>
      </view>
    </view>

    <view class="float-btn" @click="openUpload">
      <uni-icons type="camera-filled" size="24" color="#ffffff" />
      <text>拍错题</text>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.wq-page {
  position: relative;
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

.cam-btn {
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

.cam-btn::after {
  border: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.stat-item {
  padding: 22rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.stat-value {
  font-size: 38rpx;
  font-weight: 700;
}

.stat-value.warn {
  color: #8a671b;
}

.stat-value.info {
  color: #335d9a;
}

.stat-value.danger {
  color: #9a3b33;
}

.stat-value.success {
  color: #227253;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #718088;
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

.wq-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.wq-card {
  display: flex;
  gap: 22rpx;
  padding: 22rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.wq-thumb {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  background: #f1f4f2;
  border-radius: 14rpx;
}

.wq-main {
  flex: 1;
  min-width: 0;
}

.wq-title-line {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.wq-title {
  flex: 1;
  overflow: hidden;
  font-size: 30rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-pill {
  flex-shrink: 0;
  padding: 6rpx 14rpx;
  font-size: 21rpx;
  border-radius: 999rpx;
}

.ai-pill.info {
  color: #335d9a;
  background: #eaf1ff;
}

.ai-pill.warn {
  color: #8a671b;
  background: #fff5d8;
}

.ai-pill.success {
  color: #227253;
  background: #e9f6ef;
}

.ai-pill.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.wq-sub {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #75838a;
}

.wq-foot {
  margin-top: 16rpx;
}

.mastery {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.mastery.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.mastery.warn {
  color: #8a671b;
  background: #fff5d8;
}

.mastery.success {
  color: #227253;
  background: #e9f6ef;
}

.float-btn {
  position: fixed;
  right: 36rpx;
  bottom: 180rpx;
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  font-size: 20rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 50%;
  box-shadow: 0 12rpx 30rpx rgba(31, 113, 89, 0.36);
}
</style>
