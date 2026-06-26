<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'StudentAdd',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '添加学生',
  },
})

interface Candidate {
  id: number
  name: string
  phone: string
  checked: boolean
  avatar?: string
}

const keyword = ref('')
const candidates = ref<Candidate[]>([
  { id: 1, name: '张伟', phone: '138 0000 0001', checked: true, avatar: '/static/images/avatar.jpg' },
  { id: 2, name: '王芳', phone: '139 1234 5678', checked: false, avatar: '/static/images/default-avatar.png' },
  { id: 3, name: '李娜', phone: '137 9876 5432', checked: true },
  { id: 4, name: '赵强', phone: '136 1111 2222', checked: false },
  { id: 5, name: '陈明', phone: '135 5555 6666', checked: true, avatar: '/static/images/avatar.jpg' },
])

const filteredCandidates = computed(() => {
  return candidates.value.filter(item => !keyword.value || item.name.includes(keyword.value) || item.phone.includes(keyword.value))
})

const selectedCount = computed(() => candidates.value.filter(item => item.checked).length)

function toggle(item: Candidate) {
  item.checked = !item.checked
}

function goBack() {
  uni.navigateBack()
}

function createAndJoin() {
  uni.showToast({ title: '打开新增学员表单', icon: 'none' })
}

function confirmAdd() {
  uni.showToast({ title: `已添加 ${selectedCount.value} 人`, icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="add-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#34433d" />
      </button>
      <text class="nav-title">
        添加学生
      </text>
      <view class="nav-space" />
    </view>

    <view class="search-box">
      <uni-icons type="search" size="26" color="#6f7974" />
      <input v-model="keyword" class="search-input" placeholder="搜索姓名或手机号" placeholder-class="placeholder">
    </view>

    <view class="candidate-list">
      <view v-for="item in filteredCandidates" :key="item.id" class="candidate-card" @click="toggle(item)">
        <image v-if="item.avatar" :src="item.avatar" mode="aspectFill" class="candidate-avatar" />
        <view v-else class="candidate-letter">
          {{ item.name.slice(0, 1) }}
        </view>
        <view class="candidate-main">
          <view class="candidate-name">
            {{ item.name }}
          </view>
          <view class="candidate-phone">
            {{ item.phone }}
          </view>
        </view>
        <view class="check-box" :class="{ checked: item.checked }">
          <uni-icons v-if="item.checked" type="checkmarkempty" size="18" color="#ffffff" />
        </view>
      </view>
    </view>

    <view class="bottom-bar">
      <view class="selected">
        <uni-icons type="checkbox-filled" size="20" color="#00684f" />
        <text>已选 {{ selectedCount }} 人</text>
      </view>
      <button class="outline-btn" @click="createAndJoin">
        新增学员并加入
      </button>
      <button class="primary-btn" @click="confirmAdd">
        确认添加
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.add-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 150rpx;
  color: #101f26;
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
  padding: 0 28rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #b8c6c0;
}

.back-btn,
.nav-space {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #00684f;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 22rpx;
  height: 78rpx;
  margin-top: 30rpx;
  padding: 0 28rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
}

.search-input {
  flex: 1;
  font-size: 30rpx;
}

.placeholder {
  color: #9aa5aa;
}

.candidate-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
  margin-top: 28rpx;
}

.candidate-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  min-height: 118rpx;
  padding: 18rpx 24rpx;
  background: #ffffff;
  border: 1rpx solid #b8c6c0;
  border-radius: 14rpx;
}

.candidate-avatar,
.candidate-letter {
  width: 68rpx;
  height: 68rpx;
  border-radius: 50%;
}

.candidate-avatar {
  border: 1rpx solid #c9d5d0;
}

.candidate-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #1f7159;
  background: #c2ebde;
}

.candidate-main {
  flex: 1;
}

.candidate-name {
  font-size: 34rpx;
  font-weight: 800;
}

.candidate-phone {
  margin-top: 8rpx;
  font-size: 28rpx;
  color: #34433d;
}

.check-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32rpx;
  height: 32rpx;
  border: 2rpx solid #5d6a70;
  border-radius: 2rpx;
}

.check-box.checked {
  background: #005842;
  border-color: #005842;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: grid;
  grid-template-columns: auto 1.2fr 1fr;
  gap: 14rpx;
  align-items: center;
  padding: 24rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #b8c6c0;
}

.selected {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 26rpx;
  font-weight: 800;
  color: #00684f;
  white-space: nowrap;
}

.outline-btn,
.primary-btn {
  height: 76rpx;
  padding: 0;
  margin: 0;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 76rpx;
  border-radius: 12rpx;
}

.outline-btn {
  color: #00684f;
  background: #ffffff;
  border: 2rpx solid #00684f;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
