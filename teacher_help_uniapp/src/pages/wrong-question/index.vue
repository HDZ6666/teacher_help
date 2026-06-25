<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'WrongQuestion',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '错题本',
  },
})

interface WrongItem {
  id: number
  student: string
  subject: string
  title: string
  status: '已解析' | '分析中'
  mastery: '未掌握' | '部分掌握' | '已掌握'
  thumb: 'phone' | 'board' | 'paper'
}

const keyword = ref('')

const stats = [
  { label: '今日新增', value: '24', tone: 'primary', icon: 'plusempty' },
  { label: '待分析', value: '8', tone: 'plain', icon: 'loop' },
  { label: '已解析', value: '156', tone: 'plain', icon: 'checkmarkempty' },
  { label: '已掌握', value: '89%', tone: 'mint', icon: 'star' },
]

const wrongList = ref<WrongItem[]>([
  {
    id: 1,
    student: '张子涵',
    subject: '数学',
    title: '一元二次方程根的判别式',
    status: '已解析',
    mastery: '未掌握',
    thumb: 'phone',
  },
  {
    id: 2,
    student: '李心怡',
    subject: '物理',
    title: '牛顿第二定律综合应用',
    status: '分析中',
    mastery: '部分掌握',
    thumb: 'board',
  },
  {
    id: 3,
    student: '王宇轩',
    subject: '英语',
    title: '定语从句结构分析',
    status: '已解析',
    mastery: '已掌握',
    thumb: 'paper',
  },
])

function openUpload() {
  uni.navigateTo({ url: '/pages/wrong-question/upload' })
}

function openAlbum() {
  uni.navigateTo({ url: '/pages/wrong-question/upload?source=album' })
}

function openSearch() {
  uni.showToast({ title: '搜索错题', icon: 'none' })
}

function openMenu() {
  uni.showToast({ title: '筛选菜单', icon: 'none' })
}

function openDetail(item: WrongItem) {
  if (item.status === '分析中') {
    uni.navigateTo({ url: '/pages/wrong-question/analyzing' })
    return
  }
  uni.navigateTo({ url: `/pages/wrong-question/detail?id=${item.id}` })
}
</script>

<template>
  <view class="wrong-page">
    <view class="top-bar">
      <button class="icon-btn" @click="openMenu">
        <uni-icons type="list" size="30" color="#005842" />
      </button>
      <view class="page-title">
        错题本
      </view>
      <button class="icon-btn right" @click="openSearch">
        <uni-icons type="search" size="34" color="#005842" />
      </button>
    </view>

    <view class="page-body">
      <view class="search-box">
        <uni-icons type="search" size="32" color="#6f7974" />
        <input
          v-model="keyword"
          class="search-input"
          placeholder="搜索题目、知识点、学员..."
          placeholder-class="search-placeholder"
        >
      </view>

      <view class="stats-grid">
        <view
          v-for="item in stats"
          :key="item.label"
          class="stat-card"
          :class="item.tone"
        >
          <view class="stat-mark">
            <uni-icons
              :type="item.icon"
              size="58"
              :color="item.tone === 'primary' ? '#a4f2d4' : item.tone === 'mint' ? '#466c61' : '#1f7159'"
            />
          </view>
          <view class="stat-label">
            {{ item.label }}
          </view>
          <view class="stat-value">
            {{ item.value }}
          </view>
        </view>
      </view>

      <view class="action-row">
        <button class="upload-btn primary" @click="openUpload">
          <uni-icons type="camera" size="30" color="#ffffff" />
          <text>拍照上传</text>
        </button>
        <button class="upload-btn outline" @click="openAlbum">
          <uni-icons type="image" size="30" color="#1f7159" />
          <text>相册选择</text>
        </button>
      </view>

      <view class="section-title">
        最近错题
      </view>

      <view class="wrong-list">
        <view
          v-for="item in wrongList"
          :key="item.id"
          class="wrong-card"
          @click="openDetail(item)"
        >
          <view class="thumb" :class="item.thumb">
            <view class="phone-shape" />
            <view class="paper-shape" />
            <view class="diagram-shape" />
          </view>
          <view class="wrong-main">
            <view class="card-top">
              <view class="student-name">
                {{ item.student }}
              </view>
              <view class="subject-pill">
                {{ item.subject }}
              </view>
            </view>
            <view class="wrong-title">
              {{ item.title }}
            </view>
            <view class="tag-row">
              <view class="status-pill" :class="{ loading: item.status === '分析中' }">
                <uni-icons
                  :type="item.status === '已解析' ? 'checkbox' : 'loop'"
                  size="16"
                  :color="item.status === '已解析' ? '#005842' : '#6f7974'"
                />
                <text>{{ item.status }}</text>
              </view>
              <view class="mastery-pill" :class="item.mastery === '未掌握' ? 'danger' : item.mastery === '部分掌握' ? 'partial' : 'success'">
                {{ item.mastery }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.wrong-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-bottom: 150rpx;
  color: #0f1d23;
  background: #f3faff;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 96rpx 1fr 96rpx;
  align-items: center;
  height: 100rpx;
  padding: 0 26rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.icon-btn,
.upload-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
}

.icon-btn::after,
.upload-btn::after {
  border: 0;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 72rpx;
  height: 72rpx;
  background: transparent;
}

.icon-btn.right {
  justify-content: flex-end;
  justify-self: end;
}

.page-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #005842;
  text-align: center;
}

.page-body {
  padding: 18rpx 26rpx 0;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 18rpx;
  height: 78rpx;
  padding: 0 24rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 14rpx;
}

.search-input {
  flex: 1;
  height: 76rpx;
  font-size: 29rpx;
  color: #0f1d23;
}

.search-placeholder {
  color: #6f7974;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
  margin-top: 44rpx;
}

.stat-card {
  position: relative;
  min-height: 158rpx;
  box-sizing: border-box;
  padding: 28rpx 30rpx;
  overflow: hidden;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 14rpx;
  box-shadow: 0 4rpx 10rpx rgba(31, 45, 51, 0.05);
}

.stat-card.primary {
  color: #a4f2d4;
  background: #1f7159;
  border-color: #1f7159;
}

.stat-card.mint {
  color: #466c61;
  background: #c2ebde;
  border-color: #c2ebde;
}

.stat-mark {
  position: absolute;
  top: -8rpx;
  right: -6rpx;
  line-height: 1;
  opacity: 0.2;
}

.stat-label {
  position: relative;
  z-index: 1;
  font-size: 25rpx;
  font-weight: 700;
  color: inherit;
  opacity: 0.82;
}

.stat-card.plain .stat-label {
  color: #3f4944;
}

.stat-value {
  position: relative;
  z-index: 1;
  margin-top: 26rpx;
  font-size: 40rpx;
  font-weight: 800;
  color: #0f1d23;
}

.stat-card.primary .stat-value,
.stat-card.mint .stat-value {
  color: inherit;
}

.action-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22rpx;
  margin-top: 44rpx;
}

.upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  height: 80rpx;
  font-size: 29rpx;
  font-weight: 700;
  border-radius: 14rpx;
}

.upload-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.upload-btn.outline {
  color: #1f7159;
  background: transparent;
  border: 2rpx solid #1f7159;
}

.section-title {
  margin-top: 50rpx;
  margin-bottom: 28rpx;
  font-size: 34rpx;
  font-weight: 800;
}

.wrong-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.wrong-card {
  display: flex;
  gap: 22rpx;
  padding: 26rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 14rpx;
}

.thumb {
  position: relative;
  flex-shrink: 0;
  width: 144rpx;
  height: 144rpx;
  overflow: hidden;
  background: #d6e5ed;
  border-radius: 8rpx;
}

.thumb.phone {
  background: linear-gradient(145deg, #193f36, #2f5d53);
}

.thumb.board {
  background: linear-gradient(145deg, #d9f0ef, #eef7f2);
}

.thumb.paper {
  background: linear-gradient(145deg, #edf7f4, #ffffff);
}

.phone-shape {
  position: absolute;
  top: 28rpx;
  left: 46rpx;
  width: 48rpx;
  height: 88rpx;
  background: #0f1d23;
  border: 4rpx solid #4c8c7a;
  border-radius: 10rpx;
  transform: rotate(-14deg);
}

.phone-shape::after {
  position: absolute;
  top: 14rpx;
  left: 8rpx;
  width: 28rpx;
  height: 46rpx;
  background: #ffffff;
  border-radius: 3rpx;
  content: '';
}

.paper-shape {
  position: absolute;
  right: 28rpx;
  bottom: 24rpx;
  width: 64rpx;
  height: 82rpx;
  background: #ffffff;
  border-radius: 4rpx;
  box-shadow: 0 12rpx 20rpx rgba(15, 29, 35, 0.18);
  transform: rotate(-8deg);
}

.paper-shape::before,
.paper-shape::after {
  position: absolute;
  left: 12rpx;
  width: 40rpx;
  height: 4rpx;
  background: #c2ebde;
  border-radius: 999rpx;
  content: '';
}

.paper-shape::before {
  top: 20rpx;
}

.paper-shape::after {
  top: 34rpx;
}

.diagram-shape {
  position: absolute;
  top: 38rpx;
  left: 32rpx;
  width: 82rpx;
  height: 62rpx;
  border: 4rpx solid #ffffff;
  border-left-color: #8ebbb0;
  border-bottom-color: #8ebbb0;
}

.thumb.phone .paper-shape,
.thumb.phone .diagram-shape,
.thumb.board .phone-shape,
.thumb.board .paper-shape,
.thumb.paper .phone-shape,
.thumb.paper .diagram-shape {
  display: none;
}

.wrong-main {
  flex: 1;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14rpx;
}

.student-name {
  overflow: hidden;
  font-size: 30rpx;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-pill {
  flex-shrink: 0;
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #00583d;
  background: rgba(194, 235, 222, 0.82);
  border-radius: 999rpx;
}

.wrong-title {
  overflow: hidden;
  margin-top: 18rpx;
  font-size: 28rpx;
  line-height: 1.35;
  color: #0f1d23;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 24rpx;
}

.status-pill,
.mastery-pill {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  min-height: 40rpx;
  padding: 0 16rpx;
  font-size: 23rpx;
  color: #005842;
  background: rgba(194, 235, 222, 0.5);
  border-radius: 999rpx;
}

.status-pill.loading {
  color: #6f7974;
  background: #d6e5ed;
}

.mastery-pill.danger {
  color: #ba1a1a;
  background: rgba(255, 218, 214, 0.6);
}

.mastery-pill.partial,
.mastery-pill.success {
  color: #00583d;
  background: rgba(194, 235, 222, 0.72);
}
</style>
