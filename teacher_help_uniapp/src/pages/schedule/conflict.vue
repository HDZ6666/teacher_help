<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ScheduleConflict',
})
definePage({
  style: {
    navigationBarTitleText: '排课冲突',
  },
})

const conflicts = ref([
  {
    id: 1,
    type: '老师时间冲突',
    time: '06月25日 18:30-20:00',
    target: '王老师',
    existing: '英语精读B班',
    tone: 'danger',
  },
  {
    id: 2,
    type: '教室时间冲突',
    time: '06月25日 18:30-20:00',
    target: '301教室',
    existing: '物理基础班',
    tone: 'warn',
  },
])

function backEdit() {
  uni.navigateBack()
}

function changeTeacher() {
  uni.showToast({ title: '选择其他老师', icon: 'none' })
}

function changeRoom() {
  uni.showToast({ title: '选择其他教室', icon: 'none' })
}

function changeTime() {
  uni.showToast({ title: '调整时间', icon: 'none' })
}

function ignoreConflict() {
  uni.showModal({
    title: '忽略冲突继续排课',
    content: '存在 2 个冲突，强行排课可能造成老师/教室占用重叠。确认继续？',
    confirmText: '确认继续',
    confirmColor: '#c0392b',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '已生成排课', icon: 'success' })
        setTimeout(() => uni.navigateBack({ delta: 2 }), 700)
      }
    },
  })
}
</script>

<template>
  <view class="cf-page">
    <view class="alert-bar">
      <uni-icons type="info-filled" size="18" color="#9a3b33" />
      <text>检测到 {{ conflicts.length }} 个排课冲突，请调整后再生成</text>
    </view>

    <view class="summary-row">
      <view class="summary-item">
        <view class="summary-num">
          {{ conflicts.length }}
        </view>
        <view class="summary-label">
          当前冲突
        </view>
      </view>
      <view class="summary-item">
        <view class="summary-num">
          2
        </view>
        <view class="summary-label">
          已有课次
        </view>
      </view>
    </view>

    <view class="conflict-list">
      <view v-for="c in conflicts" :key="c.id" class="conflict-card">
        <view class="cc-head">
          <text class="cc-type" :class="c.tone">
            {{ c.type }}
          </text>
        </view>
        <view class="cc-row">
          <text class="cc-label">
            冲突时间
          </text>
          <text class="cc-value danger-text">
            {{ c.time }}
          </text>
        </view>
        <view class="cc-row">
          <text class="cc-label">
            冲突对象
          </text>
          <text class="cc-value danger-text">
            {{ c.target }}
          </text>
        </view>
        <view class="cc-row">
          <text class="cc-label">
            已存在课程
          </text>
          <text class="cc-value">
            {{ c.existing }}
          </text>
        </view>
      </view>
    </view>

    <view class="fix-grid">
      <button class="fix-btn" @click="changeTeacher">
        换老师
      </button>
      <button class="fix-btn" @click="changeRoom">
        换教室
      </button>
      <button class="fix-btn" @click="changeTime">
        调整时间
      </button>
    </view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="backEdit">
        返回修改
      </button>
      <button class="danger-btn" @click="ignoreConflict">
        忽略冲突继续
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cf-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.alert-bar {
  display: flex;
  gap: 12rpx;
  align-items: center;
  padding: 22rpx 24rpx;
  font-size: 26rpx;
  color: #9a3b33;
  background: #ffeceb;
  border: 1rpx solid #f6d6d2;
  border-radius: 14rpx;
}

.summary-row {
  display: flex;
  gap: 12rpx;
  margin-top: 18rpx;
}

.summary-item {
  flex: 1;
  padding: 24rpx 0;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.summary-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #9a3b33;
}

.summary-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #718088;
}

.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 18rpx;
}

.conflict-card {
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.cc-head {
  margin-bottom: 18rpx;
}

.cc-type {
  padding: 8rpx 18rpx;
  font-size: 23rpx;
  font-weight: 600;
  border-radius: 999rpx;
}

.cc-type.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.cc-type.warn {
  color: #8a671b;
  background: #fff5d8;
}

.cc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
}

.cc-label {
  font-size: 25rpx;
  color: #75838a;
}

.cc-value {
  font-size: 26rpx;
  font-weight: 600;
}

.danger-text {
  color: #c0392b;
}

.fix-grid {
  display: flex;
  gap: 12rpx;
  margin-top: 18rpx;
}

.fix-btn {
  flex: 1;
  margin: 0;
  font-size: 26rpx;
  line-height: 80rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 14rpx;
}

.fix-btn::after {
  border: 0;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 16rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.ghost-btn,
.danger-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  line-height: 90rpx;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #e6f4ee;
}

.danger-btn {
  font-weight: 600;
  color: #ffffff;
  background: #c0392b;
}

.ghost-btn::after,
.danger-btn::after {
  border: 0;
}
</style>
