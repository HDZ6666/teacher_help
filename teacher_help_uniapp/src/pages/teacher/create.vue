<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'TeacherCreate',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '新增/编辑老师',
  },
})

const isEdit = ref(false)
const navTitle = ref('新增老师')

const form = ref({
  name: '',
  phone: '',
  gender: 'male',
  role: '',
  attendanceGroup: '',
  allowLogin: true,
  remark: '',
})

const subjects = ref<string[]>(['数学'])
const subjectInput = ref('')

const roleOptions = ['班主任', '任课教师', '教务']
const roleIndex = ref(-1)
const groupOptions = ['早班组', '晚班组', '全职组']
const groupIndex = ref(-1)

function goBack() {
  uni.navigateBack()
}
function addSubject() {
  const v = subjectInput.value.trim()
  if (v && !subjects.value.includes(v)) {
    subjects.value.push(v)
    subjectInput.value = ''
  }
}
function removeSubject(s: string) {
  subjects.value = subjects.value.filter(item => item !== s)
}
function onRoleChange(e: any) {
  roleIndex.value = e.detail.value
  form.value.role = roleOptions[e.detail.value]
}
function onGroupChange(e: any) {
  groupIndex.value = e.detail.value
  form.value.attendanceGroup = groupOptions[e.detail.value]
}
function save() {
  if (!form.value.name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' })
    return
  }
  uni.showToast({ title: '已保存', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.id) {
    isEdit.value = true
    navTitle.value = '编辑老师'
  }
})
</script>

<template>
  <view class="tc-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        {{ navTitle }}
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 基本信息 -->
    <view class="card">
      <view class="field">
        <text class="field-label">
          姓名 <text class="req">*</text>
        </text>
        <input v-model="form.name" class="field-input" placeholder="请输入姓名">
      </view>
      <view class="field">
        <text class="field-label">
          联系电话
        </text>
        <input v-model="form.phone" type="tel" class="field-input" placeholder="请输入手机号码">
      </view>
      <view class="field">
        <text class="field-label">
          性别
        </text>
        <view class="radio-row">
          <view
            class="radio"
            :class="{ on: form.gender === 'male' }"
            @click="form.gender = 'male'"
          >
            男
          </view>
          <view
            class="radio"
            :class="{ on: form.gender === 'female' }"
            @click="form.gender = 'female'"
          >
            女
          </view>
        </view>
      </view>
    </view>

    <!-- 专业信息 -->
    <view class="card">
      <view class="field">
        <text class="field-label">
          擅长科目
        </text>
        <view class="tag-input">
          <view
            v-for="s in subjects"
            :key="s"
            class="subject-chip"
          >
            {{ s }}
            <uni-icons type="closeempty" size="14" color="#1f7159" @click="removeSubject(s)" />
          </view>
          <input
            v-model="subjectInput"
            class="tag-field"
            placeholder="添加科目..."
            confirm-type="done"
            @confirm="addSubject"
          >
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          角色
        </text>
        <picker mode="selector" :range="roleOptions" :value="roleIndex" @change="onRoleChange">
          <view class="picker-box">
            <text :class="{ ph: !form.role }">
              {{ form.role || '选择角色' }}
            </text>
            <uni-icons type="bottom" size="16" color="#3f4944" />
          </view>
        </picker>
      </view>
      <view class="field">
        <text class="field-label">
          考勤组
        </text>
        <picker mode="selector" :range="groupOptions" :value="groupIndex" @change="onGroupChange">
          <view class="picker-box">
            <text :class="{ ph: !form.attendanceGroup }">
              {{ form.attendanceGroup || '选择考勤组' }}
            </text>
            <uni-icons type="bottom" size="16" color="#3f4944" />
          </view>
        </picker>
      </view>
    </view>

    <!-- 设置与备注 -->
    <view class="card">
      <view class="switch-row">
        <view class="switch-info">
          <text class="switch-title">
            允许登录
          </text>
          <text class="switch-desc">
            开启后该老师可登录系统
          </text>
        </view>
        <switch :checked="form.allowLogin" color="#1f7159" @change="form.allowLogin = $event.detail.value" />
      </view>
      <view class="field pt">
        <text class="field-label">
          备注
        </text>
        <textarea v-model="form.remark" class="field-area" placeholder="请输入备注信息..." />
      </view>
    </view>

    <!-- 权限提示 -->
    <view class="hint-box">
      <uni-icons type="info" size="18" color="#1f7159" />
      <text class="hint-text">
        权限配置请到 PC 后台完成
      </text>
    </view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="goBack">
        取消
      </button>
      <button class="primary-btn" @click="save">
        保存
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.tc-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 170rpx;
  color: #0f1d23;
  background: #f3faff;
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
  padding: 0 20rpx;
  background: #f3faff;
  border-bottom: 1rpx solid #bec9c3;
}

.icon-btn {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #005842;
}

.card {
  margin-top: 22rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 14rpx;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-top: 24rpx;
}

.card .field:first-child {
  margin-top: 0;
}

.field.pt {
  padding-top: 8rpx;
}

.field-label {
  font-size: 24rpx;
  color: #3f4944;
}

.req {
  color: #ba1a1a;
}

.field-input {
  box-sizing: border-box;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 10rpx;
}

.field-area {
  box-sizing: border-box;
  width: 100%;
  height: 150rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 10rpx;
}

.radio-row {
  display: flex;
  gap: 16rpx;
}

.radio {
  padding: 14rpx 44rpx;
  font-size: 26rpx;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 999rpx;
}

.radio.on {
  color: #1f7159;
  background: #e7f6fe;
  border-color: #1f7159;
}

.tag-input {
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  align-items: center;
  min-height: 84rpx;
  padding: 12rpx 16rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 10rpx;
}

.subject-chip {
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 8rpx 18rpx;
  font-size: 25rpx;
  color: #1f7159;
  background: #e7f6fe;
  border: 1rpx solid #88d6b9;
  border-radius: 999rpx;
}

.tag-field {
  flex: 1;
  min-width: 160rpx;
  height: 56rpx;
  font-size: 26rpx;
}

.picker-box {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 84rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 10rpx;
}

.ph {
  color: #9aa5aa;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 22rpx;
  border-bottom: 1rpx solid #bec9c3;
}

.switch-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.switch-title {
  font-size: 28rpx;
}

.switch-desc {
  font-size: 22rpx;
  color: #3f4944;
}

.hint-box {
  display: flex;
  gap: 12rpx;
  align-items: center;
  margin-top: 22rpx;
  padding: 22rpx;
  background: #e7f6fe;
  border: 1rpx solid #d6e5ed;
  border-radius: 14rpx;
}

.hint-text {
  font-size: 25rpx;
  color: #3f4944;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 18rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.ghost-btn,
.primary-btn {
  flex: 1;
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
