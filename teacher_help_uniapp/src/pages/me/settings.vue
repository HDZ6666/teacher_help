<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'MeSettings',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '设置',
  },
})

interface SettingRow {
  key: string
  title: string
  icon: string
  value?: string
  type?: 'link' | 'switch' | 'text'
}

// 账号分组
const accountRows = ref<SettingRow[]>([
  { key: 'profile', title: '个人资料', icon: 'person', type: 'link' },
  { key: 'password', title: '修改密码', icon: 'locked', type: 'link' },
  { key: 'phone', title: '手机号绑定', icon: 'phone', value: '138****5678', type: 'link' },
])

// 通知开关
const notifyOn = ref(true)

// 偏好分组
const prefRows = ref<SettingRow[]>([
  { key: 'privacy', title: '隐私与权限', icon: 'eye', type: 'link' },
  { key: 'cache', title: '清理缓存', icon: 'trash', value: '128 MB', type: 'text' },
  { key: 'about', title: '关于版本', icon: 'info', value: 'v2.4.1', type: 'link' },
])

function goBack() {
  uni.navigateBack()
}

function onRow(row: SettingRow) {
  if (row.key === 'cache') {
    uni.showToast({ title: '已清理缓存', icon: 'success' })
    return
  }
  uni.showToast({ title: row.title, icon: 'none' })
}

function onToggleNotify(e: any) {
  notifyOn.value = e.detail.value
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
  <view class="settings-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        设置
      </text>
      <view class="nav-space" />
    </view>

    <view class="page-body">
      <!-- 账号分组 -->
      <view class="group-card">
        <view
          v-for="row in accountRows"
          :key="row.key"
          class="setting-row"
          @click="onRow(row)"
        >
          <view class="row-left">
            <view class="row-icon">
              <uni-icons :type="row.icon" size="20" color="#1f7159" />
            </view>
            <text class="row-title">
              {{ row.title }}
            </text>
          </view>
          <view class="row-right">
            <text v-if="row.value" class="row-value">
              {{ row.value }}
            </text>
            <uni-icons type="right" size="18" color="#bec9c3" />
          </view>
        </view>
      </view>

      <!-- 偏好分组 -->
      <view class="group-card">
        <!-- 消息通知（开关） -->
        <view class="setting-row">
          <view class="row-left">
            <view class="row-icon">
              <uni-icons type="notification" size="20" color="#1f7159" />
            </view>
            <text class="row-title">
              消息通知
            </text>
          </view>
          <switch
            :checked="notifyOn"
            color="#1f7159"
            style="transform: scale(0.85);"
            @change="onToggleNotify"
          />
        </view>

        <view
          v-for="row in prefRows"
          :key="row.key"
          class="setting-row"
          @click="onRow(row)"
        >
          <view class="row-left">
            <view class="row-icon">
              <uni-icons :type="row.icon" size="20" color="#1f7159" />
            </view>
            <text class="row-title">
              {{ row.title }}
            </text>
          </view>
          <view class="row-right">
            <text v-if="row.value" class="row-value">
              {{ row.value }}
            </text>
            <uni-icons v-if="row.type !== 'text'" type="right" size="18" color="#bec9c3" />
          </view>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="logout-wrap">
        <button class="logout-btn" @click="logout">
          退出登录
        </button>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.settings-page {
  min-height: 100vh;
  box-sizing: border-box;
  color: #0f1d23;
  background: #f3faff;
}

button::after {
  border: 0;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 102rpx;
  padding: 0 26rpx;
  background: #f3faff;
}

.back-btn,
.nav-space {
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.nav-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #005842;
}

.page-body {
  padding: 16rpx 28rpx 40rpx;
}

.group-card {
  margin-bottom: 36rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 108rpx;
  padding: 0 28rpx;
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.32);
}

.setting-row:last-child {
  border-bottom: 0;
}

.row-left {
  display: flex;
  gap: 22rpx;
  align-items: center;
}

.row-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60rpx;
  height: 60rpx;
  background: #e6f4ee;
  border-radius: 50%;
}

.row-title {
  font-size: 32rpx;
  color: #0f1d23;
}

.row-right {
  display: flex;
  gap: 10rpx;
  align-items: center;
}

.row-value {
  font-size: 26rpx;
  color: #6f7974;
}

.logout-wrap {
  padding-top: 16rpx;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 92rpx;
  margin: 0;
  font-size: 32rpx;
  font-weight: 700;
  color: #93000a;
  background: #ffdad6;
  border: 0;
  border-radius: 16rpx;
}
</style>
