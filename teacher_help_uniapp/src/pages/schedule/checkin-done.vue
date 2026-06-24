<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'CheckinDone',
})
definePage({
  style: {
    navigationBarTitleText: '点名完成',
  },
})

const result = ref({
  rate: 88,
  planned: 8,
  present: 6,
  late: 1,
  excused: 0,
  absent: 1,
  deducted: 7,
})

const lowStudents = ref([
  { id: 1, name: '李明轩', remaining: 1 },
  { id: 5, name: '刘梓萱', remaining: 0 },
])

const hasNext = ref(true)

function writeComment() {
  uni.navigateTo({ url: '/pages/schedule/comment?id=1' })
}

function viewDetail() {
  uni.navigateBack()
}

function nextCheckin() {
  uni.redirectTo({ url: '/pages/schedule/detail?id=2' })
}

function backToday() {
  uni.switchTab({ url: '/pages/index/index' })
}

onLoad(() => {})
</script>

<template>
  <view class="done-page">
    <view class="success-card">
      <view class="success-icon">
        <uni-icons type="checkmarkempty" size="46" color="#ffffff" />
      </view>
      <view class="success-title">
        点名完成
      </view>
      <view class="success-rate">
        出勤率 <text class="rate-num">{{ result.rate }}%</text>
      </view>
    </view>

    <view class="stat-grid">
      <view class="stat-item">
        <view class="stat-num">
          {{ result.planned }}
        </view>
        <view class="stat-label">
          应到
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num present">
          {{ result.present }}
        </view>
        <view class="stat-label">
          到课
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num late">
          {{ result.late }}
        </view>
        <view class="stat-label">
          迟到
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num info">
          {{ result.excused }}
        </view>
        <view class="stat-label">
          请假
        </view>
      </view>
      <view class="stat-item">
        <view class="stat-num absent">
          {{ result.absent }}
        </view>
        <view class="stat-label">
          缺勤
        </view>
      </view>
    </view>

    <view class="deduct-card">
      <uni-icons type="wallet" size="18" color="#1f7159" />
      <text>本次共扣减 <text class="deduct-num">{{ result.deducted }}</text> 课时</text>
    </view>

    <view v-if="lowStudents.length" class="low-card">
      <view class="low-title">
        <uni-icons type="info" size="16" color="#c0392b" />
        <text>课时不足学生</text>
      </view>
      <view v-for="s in lowStudents" :key="s.id" class="low-row">
        <text>{{ s.name }}</text>
        <text class="low-remain">剩余 {{ s.remaining }} 课时</text>
      </view>
    </view>

    <view class="action-grid">
      <button class="grid-btn primary" @click="writeComment">
        写课后点评
      </button>
      <button class="grid-btn" @click="viewDetail">
        查看点名详情
      </button>
      <button v-if="hasNext" class="grid-btn" @click="nextCheckin">
        继续点下一节
      </button>
      <button class="grid-btn" @click="backToday">
        返回今日
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.done-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 40rpx 28rpx 60rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.success-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50rpx 30rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  background: #2a9d73;
  border-radius: 50%;
}

.success-title {
  margin-top: 26rpx;
  font-size: 38rpx;
  font-weight: 700;
}

.success-rate {
  margin-top: 14rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.78);
}

.rate-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #a4f2d4;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10rpx;
  margin-top: 22rpx;
}

.stat-item {
  padding: 22rpx 4rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.stat-num {
  font-size: 34rpx;
  font-weight: 700;
  color: #183a34;
}

.stat-num.present {
  color: #227253;
}

.stat-num.late {
  color: #8a671b;
}

.stat-num.info {
  color: #335d9a;
}

.stat-num.absent {
  color: #9a3b33;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 21rpx;
  color: #718088;
}

.deduct-card {
  display: flex;
  gap: 12rpx;
  align-items: center;
  margin-top: 16rpx;
  padding: 24rpx 26rpx;
  font-size: 27rpx;
  color: #2d4a42;
  background: #f3faf7;
  border: 1rpx solid #c7e6d8;
  border-radius: 14rpx;
}

.deduct-num {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f7159;
}

.low-card {
  margin-top: 16rpx;
  padding: 26rpx;
  background: #fff5f4;
  border: 1rpx solid #f6d6d2;
  border-radius: 14rpx;
}

.low-title {
  display: flex;
  gap: 8rpx;
  align-items: center;
  font-size: 26rpx;
  font-weight: 700;
  color: #9a3b33;
}

.low-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #8a4a44;
}

.low-remain {
  font-size: 24rpx;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12rpx;
  margin-top: 26rpx;
}

.grid-btn {
  margin: 0;
  font-size: 27rpx;
  line-height: 86rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 14rpx;
}

.grid-btn.primary {
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
}

.grid-btn::after {
  border: 0;
}
</style>
