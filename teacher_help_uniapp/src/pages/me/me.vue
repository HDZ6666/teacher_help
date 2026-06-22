<script lang="ts" setup>
import { onShow } from '@dcloudio/uni-app'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { LOGIN_PAGE } from '@/router/config'
import { useUserStore } from '@/store'
import { useTokenStore } from '@/store/token'
import type { MobileProfile } from '@/api/teach/mobile'
import { getMobileProfile } from '@/api/teach/mobile'

definePage({
  style: {
    navigationBarTitleText: '我的',
  },
})

const userStore = useUserStore()
const tokenStore = useTokenStore()
const { userInfo } = storeToRefs(userStore)
const mobileProfile = ref<MobileProfile | null>(null)
const profileError = ref('')
const profileLoading = ref(false)

const displayName = computed(() => {
  return mobileProfile.value?.nickname || userInfo.value.nickname || userInfo.value.username || '未登录'
})

const accountText = computed(() => {
  return mobileProfile.value?.phone || mobileProfile.value?.username || userInfo.value.username || '请先登录'
})

const bindText = computed(() => {
  if (!tokenStore.hasLogin) {
    return '未登录'
  }
  if (mobileProfile.value?.isAdmin) {
    return '管理员视角'
  }
  if (mobileProfile.value?.teacherId) {
    return '已关联老师'
  }
  return '未关联老师'
})

const bindClass = computed(() => {
  if (mobileProfile.value?.teacherId || mobileProfile.value?.isAdmin)
    return 'ok'
  return 'warn'
})

const serviceText = computed(() => {
  if (!tokenStore.hasLogin)
    return '未登录'
  if (profileLoading.value)
    return '同步中'
  return profileError.value || '可使用'
})

function handleLogin() {
  uni.navigateTo({ url: LOGIN_PAGE })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定退出当前账号吗？',
    success: async (res) => {
      if (!res.confirm)
        return
      await tokenStore.logout()
      uni.reLaunch({ url: LOGIN_PAGE })
    },
  })
}

function openSchedule() {
  uni.switchTab({ url: '/pages/schedule/index' })
}

async function refreshProfile() {
  if (!tokenStore.hasLogin) {
    mobileProfile.value = null
    profileError.value = ''
    return
  }
  profileLoading.value = true
  try {
    await userStore.fetchUserInfo()
    const res = await getMobileProfile()
    mobileProfile.value = res.data
    profileError.value = ''
  }
  catch (error: any) {
    mobileProfile.value = null
    profileError.value = error?.msg || '资料同步失败'
  }
  finally {
    profileLoading.value = false
  }
}

onShow(() => {
  refreshProfile()
})
</script>

<template>
  <view class="me-page">
    <view class="profile-head">
      <image class="avatar" :src="userInfo.avatar || '/static/images/default-avatar.png'" mode="aspectFill" />
      <view class="profile-main">
        <view class="nickname">
          {{ displayName }}
        </view>
        <view class="account">
          {{ accountText }}
        </view>
      </view>
      <view class="bind-pill" :class="bindClass">
        {{ bindText }}
      </view>
    </view>

    <view class="info-list">
      <view class="info-row">
        <text>账号</text>
        <text>{{ accountText }}</text>
      </view>
      <view class="info-row">
        <text>状态</text>
        <text>{{ serviceText }}</text>
      </view>
    </view>

    <view v-if="tokenStore.hasLogin" class="quick-actions">
      <button class="action-btn primary" @click="openSchedule">
        今日课表
      </button>
      <button class="action-btn secondary" :disabled="profileLoading" @click="refreshProfile">
        {{ profileLoading ? '同步中...' : '刷新资料' }}
      </button>
    </view>

    <button v-if="tokenStore.hasLogin" class="logout-btn" @click="handleLogout">
      退出登录
    </button>
    <button v-else class="login-btn" @click="handleLogin">
      登录
    </button>
  </view>
</template>

<style lang="scss" scoped>
.me-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 28rpx 28rpx 150rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 32rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
}

.avatar {
  width: 104rpx;
  height: 104rpx;
  background: #e6f4ee;
  border: 4rpx solid rgba(255, 255, 255, 0.22);
  border-radius: 50%;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.bind-pill {
  flex-shrink: 0;
  padding: 10rpx 16rpx;
  font-size: 23rpx;
  font-weight: 650;
  border-radius: 999rpx;
}

.bind-pill.ok {
  color: #ffffff;
  background: rgba(42, 157, 115, 0.92);
}

.bind-pill.warn {
  color: #6f5a19;
  background: #fff3c4;
}

.nickname {
  overflow: hidden;
  font-size: 38rpx;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account {
  margin-top: 10rpx;
  font-size: 25rpx;
  color: rgba(255, 255, 255, 0.74);
}

.info-list {
  margin-top: 22rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  min-height: 96rpx;
  padding: 0 26rpx;
  font-size: 28rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.info-row:last-child {
  border-bottom: 0;
}

.info-row text:first-child {
  flex-shrink: 0;
  color: #6f7e85;
}

.info-row text:last-child {
  overflow: hidden;
  font-weight: 650;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 24rpx;
}

.action-btn {
  height: 88rpx;
  padding: 0;
  margin: 0;
  font-size: 29rpx;
  font-weight: 750;
  line-height: 88rpx;
  border-radius: 16rpx;
}

.action-btn::after {
  border: 0;
}

.action-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.action-btn.secondary {
  color: #1f7159;
  background: #e6f4ee;
}

.action-btn[disabled] {
  color: #9aa5aa;
  background: #edf1ef;
}

.logout-btn,
.login-btn {
  height: 90rpx;
  margin-top: 34rpx;
  font-size: 31rpx;
  font-weight: 750;
  line-height: 90rpx;
  border-radius: 16rpx;
}

.logout-btn::after,
.login-btn::after {
  border: 0;
}

.logout-btn {
  color: #a4423a;
  background: #ffeceb;
}

.login-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
