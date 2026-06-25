<script lang="ts" setup>
defineOptions({
  name: 'Mine',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '我的',
  },
})

const quickEntries = [
  { label: '课程', value: '12', icon: 'calendar-filled' },
  { label: '班级', value: '8', icon: 'staff-filled' },
  { label: '课时', value: '86', icon: 'flag-filled' },
  { label: '消息', value: '3', icon: 'notification-filled', badge: true },
]

const menuList = [
  { label: '更多工具', icon: 'list', value: '', route: '/pages/me/tools' },
  { label: '切换校区', icon: 'shop', value: '杭州总校区' },
  { label: '账号安全', icon: 'locked', value: '' },
  { label: '通知设置', icon: 'notification', value: '', route: '/pages/me/settings' },
  { label: '数据同步', icon: 'loop', value: '刚刚' },
  { label: '帮助与反馈', icon: 'help', value: '' },
  { label: '关于老师帮', icon: 'info', value: '' },
]

function openMenu(item: { label: string, route?: string }) {
  if (item.route) {
    uni.navigateTo({ url: item.route })
    return
  }
  uni.showToast({ title: item.label, icon: 'none' })
}

function logout() {
  uni.showModal({
    title: '退出登录',
    content: '确定退出当前账号吗？',
    confirmText: '退出',
    confirmColor: '#ba1a1a',
  })
}
</script>

<template>
  <view class="me-page">
    <scroll-view class="content-scroll" scroll-y>
      <view class="profile-card">
        <view class="profile-head">
          <image class="avatar" src="/static/images/default-avatar.png" mode="aspectFill" />
          <view class="profile-main">
            <view class="name">
              林老师
            </view>
            <view class="account">
              138****6699
            </view>
            <view class="tag-row">
              <text>高级老师</text>
              <text>杭州总校区</text>
            </view>
          </view>
        </view>

        <view class="profile-stats">
          <view>
            <view class="stat-label">
              本月课时
            </view>
            <view class="stat-value">
              86<text>节</text>
            </view>
          </view>
          <view class="right-stat">
            <view class="stat-label">
              综合评级
            </view>
            <view class="rank">
              S+
            </view>
          </view>
        </view>
      </view>

      <view class="quick-grid">
        <button
          v-for="item in quickEntries"
          :key="item.label"
          class="quick-item"
        >
          <view class="quick-icon">
            <uni-icons :type="item.icon" size="28" color="#1f7159" />
            <view v-if="item.badge" class="badge" />
          </view>
          <view class="quick-value">
            {{ item.value }}
          </view>
          <view class="quick-label">
            {{ item.label }}
          </view>
        </button>
      </view>

      <view class="menu-card">
        <button
          v-for="item in menuList"
          :key="item.label"
          class="menu-row"
          @click="openMenu(item)"
        >
          <view class="menu-left">
            <uni-icons :type="item.icon" size="24" color="#6f7974" />
            <text>{{ item.label }}</text>
          </view>
          <view class="menu-right">
            <text v-if="item.value">{{ item.value }}</text>
            <uni-icons type="right" size="18" color="#6f7974" />
          </view>
        </button>
      </view>

      <button class="logout-btn" @click="logout">
        <uni-icons type="closeempty" size="24" color="#ba1a1a" />
        <text>退出登录</text>
      </button>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.me-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f4f6f5;
}

.content-scroll {
  box-sizing: border-box;
  height: 100vh;
  padding: 32rpx 28rpx 170rpx;
}

.profile-card {
  padding: 32rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 18rpx rgba(31, 113, 89, 0.15);
}

.profile-head {
  display: flex;
  gap: 24rpx;
  align-items: center;
}

.avatar {
  width: 128rpx;
  height: 128rpx;
  overflow: hidden;
  background: #d6e5ed;
  border: 4rpx solid rgba(255, 255, 255, 0.45);
  border-radius: 50%;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.name {
  font-size: 40rpx;
  font-weight: 800;
}

.account {
  margin-top: 8rpx;
  font-size: 25rpx;
  color: rgba(255, 255, 255, 0.78);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 18rpx;
}

.tag-row text {
  padding: 6rpx 14rpx;
  font-size: 22rpx;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.16);
  border-radius: 999rpx;
}

.profile-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 30rpx;
  margin-top: 30rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.18);
}

.stat-label {
  margin-bottom: 8rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.78);
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
}

.stat-value text {
  margin-left: 4rpx;
  font-size: 22rpx;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.78);
}

.right-stat {
  text-align: right;
}

.rank {
  font-size: 34rpx;
  font-weight: 800;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-top: 24rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
  padding: 24rpx 8rpx;
  margin: 0;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.quick-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56rpx;
  height: 56rpx;
}

.badge {
  position: absolute;
  top: 2rpx;
  right: 2rpx;
  width: 14rpx;
  height: 14rpx;
  background: #ba1a1a;
  border: 2rpx solid #ffffff;
  border-radius: 50%;
}

.quick-value {
  margin-top: 10rpx;
  font-size: 32rpx;
  font-weight: 800;
  color: #0f1d23;
}

.quick-label {
  margin-top: 2rpx;
  font-size: 22rpx;
  color: #3f4944;
}

.menu-card {
  margin-top: 28rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.menu-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 104rpx;
  padding: 0 28rpx;
  margin: 0;
  background: #ffffff;
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.38);
  border-radius: 0;
}

.menu-row:last-child {
  border-bottom: 0;
}

.menu-left,
.menu-right {
  display: flex;
  align-items: center;
}

.menu-left {
  gap: 20rpx;
  font-size: 30rpx;
  color: #0f1d23;
}

.menu-right {
  gap: 8rpx;
  font-size: 24rpx;
  color: #6f7974;
}

.logout-btn {
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 92rpx;
  padding: 0;
  margin: 32rpx 0 0;
  font-size: 30rpx;
  color: #ba1a1a;
  background: transparent;
  border: 1rpx solid #ba1a1a;
  border-radius: 16rpx;
}

.quick-item::after,
.menu-row::after,
.logout-btn::after {
  border: 0;
}
</style>
