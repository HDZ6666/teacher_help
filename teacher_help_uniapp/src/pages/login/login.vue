<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'Login',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '登录',
  },
})

const campus = ref('杭州总校区')
const phone = ref('')
const password = ref('')
const remember = ref(true)
const showPassword = ref(false)

function chooseCampus() {
  uni.showActionSheet({
    itemList: ['杭州总校区', '滨江校区', '西湖校区'],
    success: (res) => {
      campus.value = ['杭州总校区', '滨江校区', '西湖校区'][res.tapIndex]
    },
  })
}

function login() {
  uni.showToast({ title: '登录成功', icon: 'success' })
  setTimeout(() => {
    uni.switchTab({ url: '/pages/index/index' })
  }, 500)
}

function smsLogin() {
  uni.showToast({ title: '验证码登录', icon: 'none' })
}

function forgotPassword() {
  uni.showToast({ title: '忘记密码', icon: 'none' })
}
</script>

<template>
  <view class="login-page">
    <view class="top-glow" />

    <view class="login-wrap">
      <view class="brand">
        <view class="brand-title">
          老师帮
        </view>
        <view class="brand-subtitle">
          让上课、点名、排课更快一点
        </view>
      </view>

      <view class="login-card">
        <button class="campus-row" @click="chooseCampus">
          <text>选择校区</text>
          <view class="campus-value">
            <text>{{ campus }}</text>
            <uni-icons type="right" size="18" color="#6f7974" />
          </view>
        </button>

        <view class="input-wrap">
          <uni-icons type="phone" size="22" color="#6f7974" />
          <input
            v-model="phone"
            class="field-input"
            placeholder="请输入手机号"
            placeholder-class="placeholder"
            type="number"
          >
        </view>

        <view class="input-wrap">
          <uni-icons type="locked" size="22" color="#6f7974" />
          <input
            v-model="password"
            class="field-input"
            placeholder="请输入密码"
            placeholder-class="placeholder"
            :password="!showPassword"
          >
          <button class="eye-btn" @click="showPassword = !showPassword">
            <uni-icons :type="showPassword ? 'eye-filled' : 'eye-slash-filled'" size="22" color="#6f7974" />
          </button>
        </view>

        <view class="option-row">
          <view class="remember" @click="remember = !remember">
            <view class="check-box" :class="{ active: remember }">
              <uni-icons v-if="remember" type="checkmarkempty" size="16" color="#ffffff" />
            </view>
            <text>记住登录</text>
          </view>
          <button class="link-btn" @click="forgotPassword">
            忘记密码?
          </button>
        </view>

        <button class="login-btn" @click="login">
          登录
        </button>
        <button class="sms-btn" @click="smsLogin">
          验证码登录
        </button>
      </view>

      <view class="footer">
        <view class="agreement">
          登录即代表同意 <text>《用户服务协议》</text> 和 <text>《隐私政策》</text>
        </view>
        <view class="version">
          v1.2.0
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: #0f1d23;
  background: #f4f6f5;
}

.top-glow {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 260rpx;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(164, 242, 212, 0.28), rgba(244, 246, 245, 0));
}

.login-wrap {
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100vh;
  padding: 96rpx 28rpx 56rpx;
}

.brand {
  margin: 40rpx 0 80rpx;
  text-align: center;
}

.brand-title {
  margin-bottom: 16rpx;
  font-size: 48rpx;
  font-weight: 800;
  color: #1f7159;
}

.brand-subtitle {
  font-size: 28rpx;
  line-height: 1.45;
  color: #3f4944;
}

.login-card {
  padding: 48rpx;
  background: #ffffff;
  border: 1rpx solid rgba(190, 201, 195, 0.7);
  border-radius: 24rpx;
  box-shadow: 0 8rpx 22rpx rgba(15, 29, 35, 0.04);
}

.campus-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 0 24rpx;
  margin: 0 0 28rpx;
  font-size: 28rpx;
  color: #0f1d23;
  background: transparent;
  border-bottom: 1rpx solid rgba(190, 201, 195, 0.55);
}

.campus-value {
  display: flex;
  gap: 4rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.input-wrap {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 22rpx;
  margin-top: 24rpx;
  background: #f3faff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.field-input {
  flex: 1;
  height: 88rpx;
  padding-left: 16rpx;
  font-size: 28rpx;
  color: #0f1d23;
}

.placeholder {
  color: #6f7974;
}

.eye-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48rpx;
  height: 48rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.option-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 0 20rpx;
}

.remember {
  display: flex;
  gap: 12rpx;
  align-items: center;
  font-size: 25rpx;
  color: #3f4944;
}

.check-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32rpx;
  height: 32rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 8rpx;
}

.check-box.active {
  background: #1f7159;
  border-color: #1f7159;
}

.link-btn {
  padding: 0;
  margin: 0;
  font-size: 25rpx;
  color: #1f7159;
  background: transparent;
}

.login-btn,
.sms-btn {
  width: 100%;
  height: 92rpx;
  padding: 0;
  margin: 16rpx 0 0;
  font-size: 34rpx;
  font-weight: 700;
  border-radius: 16rpx;
}

.login-btn {
  color: #ffffff;
  background: #1f7159;
  box-shadow: 0 6rpx 16rpx rgba(31, 113, 89, 0.16);
}

.sms-btn {
  color: #1f7159;
  background: transparent;
  border: 2rpx solid #1f7159;
}

.footer {
  margin-top: auto;
  padding-top: 64rpx;
  text-align: center;
}

.agreement {
  max-width: 560rpx;
  margin: 0 auto;
  font-size: 22rpx;
  line-height: 1.6;
  color: rgba(63, 73, 68, 0.7);
}

.agreement text {
  color: #1f7159;
}

.version {
  margin-top: 14rpx;
  font-size: 22rpx;
  color: #6f7974;
}

.campus-row::after,
.eye-btn::after,
.link-btn::after,
.login-btn::after,
.sms-btn::after {
  border: 0;
}
</style>
