<script lang="ts" setup>
defineOptions({
  name: 'ScheduleConflict',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '排课冲突',
  },
})

const conflicts = [
  {
    type: '老师冲突',
    icon: 'person',
    lesson: '第 3 节课次',
    title: '王老师在 14:00 已有课程',
    desc: '原计划：2023-10-25 14:00 - 15:30 · 高一数学强化班',
    actions: ['更换老师', '修改时间'],
  },
  {
    type: '教室占用',
    icon: 'home',
    lesson: '第 5 节课次',
    title: 'A区201 已被占用',
    desc: '原计划：2023-10-26 10:00 - 11:30 · 物理实验课',
    actions: ['更换教室'],
  },
]

function goBack() {
  uni.navigateBack()
}

function handleAction(label: string) {
  uni.showToast({ title: label, icon: 'none' })
}

function skipConflict() {
  uni.showToast({ title: '已跳过冲突课次', icon: 'none' })
}

function forceSave() {
  uni.showModal({
    title: '仍然保存',
    content: '存在排课冲突，仍然保存可能造成老师或教室占用重叠。确认保存？',
    confirmText: '仍然保存',
    confirmColor: '#1f7159',
  })
}
</script>

<template>
  <view class="conflict-page">
    <view class="topbar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="28" color="#0f1d23" />
      </button>
      <view class="page-title">
        排课冲突
      </view>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="alert-card">
        <uni-icons type="info-filled" size="30" color="#8a671b" />
        <view class="alert-main">
          <view class="alert-title">
            发现 2 个排课冲突
          </view>
          <view class="alert-desc">
            请处理以下冲突以完成排课。您也可以选择跳过这些有冲突的课次。
          </view>
        </view>
      </view>

      <view
        v-for="item in conflicts"
        :key="item.title"
        class="conflict-card"
      >
        <view class="conflict-head">
          <view class="tag-row">
            <view class="conflict-tag">
              <uni-icons :type="item.icon" size="16" color="#8a671b" />
              <text>{{ item.type }}</text>
            </view>
            <text class="lesson-tag">{{ item.lesson }}</text>
          </view>
          <view class="conflict-title">
            {{ item.title }}
          </view>
          <view class="conflict-desc">
            {{ item.desc }}
          </view>
        </view>

        <view class="card-actions">
          <button
            v-for="action in item.actions"
            :key="action"
            class="action-btn"
            @click="handleAction(action)"
          >
            <uni-icons
              :type="action.includes('时间') ? 'calendar' : action.includes('教室') ? 'location' : 'loop'"
              size="22"
              color="#1f7159"
            />
            <text>{{ action }}</text>
          </button>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="skip-btn" @click="skipConflict">
        跳过冲突课次
      </button>
      <button class="save-btn" @click="forceSave">
        仍然保存
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.conflict-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f4f6f5;
}

.topbar {
  display: flex;
  gap: 24rpx;
  align-items: center;
  height: 112rpx;
  padding: 0 28rpx;
  background: #f4f6f5;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 80rpx;
  padding: 0;
  margin: 0;
  background: transparent;
  border-radius: 50%;
}

.page-title {
  flex: 1;
  font-size: 48rpx;
  font-weight: 800;
}

.content-scroll {
  box-sizing: border-box;
  height: calc(100vh - 112rpx);
  padding: 0 28rpx 146rpx;
}

.alert-card {
  display: flex;
  gap: 20rpx;
  align-items: flex-start;
  padding: 28rpx;
  background: #fff5d8;
  border: 1rpx solid rgba(138, 103, 27, 0.24);
  border-radius: 16rpx;
}

.alert-main {
  flex: 1;
  min-width: 0;
}

.alert-title {
  margin-bottom: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #8a671b;
}

.alert-desc {
  font-size: 26rpx;
  line-height: 1.5;
  color: rgba(138, 103, 27, 0.82);
}

.conflict-card {
  margin-top: 24rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 10rpx rgba(15, 29, 35, 0.04);
}

.conflict-head {
  padding: 32rpx;
  background: rgba(243, 250, 255, 0.36);
  border-bottom: 1rpx solid #e7ece9;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  align-items: center;
  margin-bottom: 18rpx;
}

.conflict-tag {
  display: flex;
  gap: 6rpx;
  align-items: center;
  padding: 6rpx 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #8a671b;
  background: #fff5d8;
  border-radius: 999rpx;
}

.lesson-tag {
  font-size: 24rpx;
  color: #3f4944;
}

.conflict-title {
  font-size: 40rpx;
  font-weight: 800;
  line-height: 1.35;
}

.conflict-desc {
  margin-top: 8rpx;
  font-size: 26rpx;
  line-height: 1.5;
  color: #3f4944;
}

.card-actions {
  display: flex;
  gap: 18rpx;
  padding: 28rpx;
}

.action-btn {
  display: flex;
  flex: 1;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 26rpx;
  font-weight: 700;
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
  border-radius: 16rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  display: flex;
  gap: 20rpx;
  padding: 24rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #e7ece9;
}

.skip-btn,
.save-btn {
  flex: 1;
  height: 92rpx;
  padding: 0;
  margin: 0;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 92rpx;
  border-radius: 16rpx;
}

.skip-btn {
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #6f7974;
}

.save-btn {
  color: #ffffff;
  background: #1f7159;
}

.back-btn::after,
.action-btn::after,
.skip-btn::after,
.save-btn::after {
  border: 0;
}
</style>
