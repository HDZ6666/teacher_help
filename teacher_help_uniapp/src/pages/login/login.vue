<script lang="ts" setup>
import type { ICaptcha } from '@/api/types/login'
import { onLoad } from '@dcloudio/uni-app'
import { reactive, ref } from 'vue'
import { getCode } from '@/api/login'
import { useTokenStore } from '@/store/token'
import { tabbarList } from '@/tabbar/config'
import { isPageTabbar } from '@/tabbar/store'
import { ensureDecodeURIComponent } from '@/utils'
import { parseUrlToObj } from '@/utils/index'

definePage({
  style: {
    navigationBarTitleText: '登录',
  },
})

const tokenStore = useTokenStore()
const loading = ref(false)
const captchaLoading = ref(false)
const redirectUrl = ref('')
const captcha = ref<ICaptcha>({
  captchaEnabled: true,
  uuid: '',
  image: '',
})
const form = reactive({
  username: '',
  password: '',
  code: '',
  uuid: '',
})

onLoad((options) => {
  redirectUrl.value = options.redirect ? ensureDecodeURIComponent(options.redirect) : tabbarList[0].pagePath
  loadCaptcha()
})

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const res = await getCode()
    captcha.value = res.data
    form.uuid = res.data.uuid
    form.code = ''
  }
  finally {
    captchaLoading.value = false
  }
}

function validateForm() {
  if (!form.username.trim()) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return false
  }
  if (!form.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return false
  }
  if (captcha.value.captchaEnabled && !form.code.trim()) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return false
  }
  return true
}

function redirectAfterLogin() {
  let path = redirectUrl.value || tabbarList[0].pagePath
  if (!path.startsWith('/')) {
    path = `/${path}`
  }
  const { path: purePath } = parseUrlToObj(path)
  if (isPageTabbar(purePath)) {
    uni.switchTab({ url: purePath })
  }
  else {
    uni.redirectTo({ url: path })
  }
}

async function doLogin() {
  if (tokenStore.hasLogin) {
    redirectAfterLogin()
    return
  }
  if (!validateForm())
    return
  loading.value = true
  try {
    await tokenStore.login({
      username: form.username.trim(),
      password: form.password,
      code: form.code.trim(),
      uuid: form.uuid,
    })
    redirectAfterLogin()
  }
  catch {
    loadCaptcha()
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <view class="login-page">
    <view class="brand-block">
      <view class="brand-mark">
        帮
      </view>
      <view>
        <view class="brand-title">
          老师帮
        </view>
        <view class="brand-sub">
          上课前后，把点名和课时处理干净
        </view>
      </view>
    </view>

    <view class="form-box">
      <view class="field">
        <text class="field-label">手机号</text>
        <input v-model="form.username" class="field-input" placeholder="请输入老师手机号" type="number" confirm-type="next">
      </view>
      <view class="field">
        <text class="field-label">密码</text>
        <input v-model="form.password" class="field-input" placeholder="请输入密码" password confirm-type="done" @confirm="doLogin">
      </view>
      <view v-if="captcha.captchaEnabled" class="field captcha-field">
        <view class="captcha-input">
          <text class="field-label">验证码</text>
          <input v-model="form.code" class="field-input" placeholder="请输入验证码" confirm-type="done" @confirm="doLogin">
        </view>
        <view class="captcha-img" @click="loadCaptcha">
          <image v-if="captcha.image" :src="captcha.image" mode="aspectFit" />
          <text v-else>{{ captchaLoading ? '刷新中' : '刷新' }}</text>
        </view>
      </view>
      <button class="login-btn" :disabled="loading" @click="doLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 96rpx 36rpx 40rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 22rpx;
  margin-bottom: 54rpx;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88rpx;
  height: 88rpx;
  font-size: 38rpx;
  font-weight: 800;
  color: #ffffff;
  background: #193f36;
  border-radius: 20rpx;
}

.brand-title {
  font-size: 44rpx;
  font-weight: 800;
}

.brand-sub {
  margin-top: 8rpx;
  font-size: 25rpx;
  color: #6f7e85;
}

.form-box {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.field {
  padding: 22rpx 24rpx;
  background: #ffffff;
  border: 1rpx solid #e3e9e6;
  border-radius: 16rpx;
}

.field-label {
  display: block;
  margin-bottom: 12rpx;
  font-size: 24rpx;
  color: #65747b;
}

.field-input {
  height: 48rpx;
  font-size: 31rpx;
  color: #1f2d33;
}

.captcha-field {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.captcha-input {
  flex: 1;
  min-width: 0;
}

.captcha-img {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 190rpx;
  height: 74rpx;
  overflow: hidden;
  font-size: 24rpx;
  color: #1f7159;
  background: #edf5f1;
  border-radius: 12rpx;
}

.captcha-img image {
  width: 100%;
  height: 100%;
}

.login-btn {
  height: 92rpx;
  margin-top: 16rpx;
  font-size: 32rpx;
  font-weight: 750;
  line-height: 92rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.login-btn::after {
  border: 0;
}
</style>
