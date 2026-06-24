<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'StudentAdd',
})
definePage({
  style: {
    navigationBarTitleText: '添加学员',
  },
})

const genderOptions = ['男', '女']
const genderIndex = ref(0)
const gradeOptions = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三', '高一', '高二', '高三']
const gradeIndex = ref(2)
const relationOptions = ['母亲', '父亲', '爷爷', '奶奶', '本人', '其他']
const relationIndex = ref(0)
const sourceOptions = ['到店咨询', '老学员转介绍', '线上推广', '地推活动', '电话邀约', '其他']
const sourceIndex = ref(0)

const form = ref({
  name: '',
  school: '',
  birthday: '',
  phone: '',
  wechat: '',
  intentCourse: '',
  follower: '',
  manager: '',
  remark: '',
})

const tags = ['潜在客户', '已试听', '课时不足', '待跟进', '重点维护']
const selectedTags = ref<string[]>([])

function toggleTag(t: string) {
  const i = selectedTags.value.indexOf(t)
  if (i >= 0)
    selectedTags.value.splice(i, 1)
  else
    selectedTags.value.push(t)
}

function onGenderChange(e: any) {
  genderIndex.value = e.detail.value
}
function onGradeChange(e: any) {
  gradeIndex.value = e.detail.value
}
function onRelationChange(e: any) {
  relationIndex.value = e.detail.value
}
function onSourceChange(e: any) {
  sourceIndex.value = e.detail.value
}
function onBirthdayChange(e: any) {
  form.value.birthday = e.detail.value
}

function save() {
  if (!form.value.name) {
    uni.showToast({ title: '请填写学员姓名', icon: 'none' })
    return
  }
  if (!form.value.phone) {
    uni.showToast({ title: '请填写联系电话', icon: 'none' })
    return
  }
  uni.showToast({ title: '已保存', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="add-page">
    <!-- 基础信息 -->
    <view class="group-title">
      基础信息
    </view>
    <view class="form-card">
      <view class="row">
        <text class="row-label req">
          姓名
        </text>
        <input v-model="form.name" class="row-input" placeholder="请输入学员姓名">
      </view>
      <picker :value="genderIndex" :range="genderOptions" @change="onGenderChange">
        <view class="row">
          <text class="row-label">
            性别
          </text>
          <view class="row-value">
            {{ genderOptions[genderIndex] }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <picker :value="gradeIndex" :range="gradeOptions" @change="onGradeChange">
        <view class="row">
          <text class="row-label">
            年级
          </text>
          <view class="row-value">
            {{ gradeOptions[gradeIndex] }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="row">
        <text class="row-label">
          学校
        </text>
        <input v-model="form.school" class="row-input" placeholder="选填">
      </view>
      <picker mode="date" :value="form.birthday" @change="onBirthdayChange">
        <view class="row no-border">
          <text class="row-label">
            生日
          </text>
          <view class="row-value" :class="{ ph: !form.birthday }">
            {{ form.birthday || '选填' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
    </view>

    <!-- 联系人 -->
    <view class="group-title">
      联系人
    </view>
    <view class="form-card">
      <picker :value="relationIndex" :range="relationOptions" @change="onRelationChange">
        <view class="row">
          <text class="row-label">
            与学员关系
          </text>
          <view class="row-value">
            {{ relationOptions[relationIndex] }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="row">
        <text class="row-label req">
          联系电话
        </text>
        <input v-model="form.phone" type="number" class="row-input" placeholder="请输入手机号">
      </view>
      <view class="row no-border">
        <text class="row-label">
          微信
        </text>
        <input v-model="form.wechat" class="row-input" placeholder="选填">
      </view>
    </view>

    <!-- 报读意向 -->
    <view class="group-title">
      报读意向
    </view>
    <view class="form-card">
      <view class="row" @click="form.intentCourse = '数学提高班'">
        <text class="row-label">
          意向课程
        </text>
        <view class="row-value" :class="{ ph: !form.intentCourse }">
          {{ form.intentCourse || '请选择' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
      <picker :value="sourceIndex" :range="sourceOptions" @change="onSourceChange">
        <view class="row">
          <text class="row-label">
            来源渠道
          </text>
          <view class="row-value">
            {{ sourceOptions[sourceIndex] }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </picker>
      <view class="row" @click="form.follower = '王老师'">
        <text class="row-label">
          跟进人
        </text>
        <view class="row-value" :class="{ ph: !form.follower }">
          {{ form.follower || '请选择' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
      <view class="row no-border" @click="form.manager = '张学管'">
        <text class="row-label">
          学管师
        </text>
        <view class="row-value" :class="{ ph: !form.manager }">
          {{ form.manager || '请选择' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
    </view>

    <!-- 标签 -->
    <view class="group-title">
      标签
    </view>
    <view class="form-card pad">
      <view class="tag-wrap">
        <view
          v-for="t in tags"
          :key="t"
          class="tag-chip"
          :class="{ on: selectedTags.includes(t) }"
          @click="toggleTag(t)"
        >
          {{ t }}
        </view>
      </view>
    </view>

    <!-- 备注 -->
    <view class="form-card pad">
      <text class="row-label">
        备注
      </text>
      <textarea v-model="form.remark" class="remark-area" placeholder="补充说明（选填）" />
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="save">
        保存
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.add-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 8rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.group-title {
  margin: 24rpx 4rpx 14rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #4a565c;
}

.form-card {
  margin-bottom: 4rpx;
  padding: 0 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.form-card.pad {
  padding: 24rpx 26rpx;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 96rpx;
  border-bottom: 1rpx solid #edf1ef;
}

.row.no-border {
  border-bottom: 0;
}

.row-label {
  flex-shrink: 0;
  font-size: 27rpx;
  color: #4a565c;
}

.row-label.req::before {
  margin-right: 6rpx;
  color: #c0392b;
  content: '*';
}

.row-value {
  display: flex;
  gap: 6rpx;
  align-items: center;
  font-size: 27rpx;
}

.row-value.ph {
  color: #9aa5aa;
}

.row-input {
  flex: 1;
  margin-left: 24rpx;
  font-size: 27rpx;
  text-align: right;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.tag-chip {
  padding: 12rpx 24rpx;
  font-size: 24rpx;
  color: #67757c;
  background: #f1f4f2;
  border: 1rpx solid transparent;
  border-radius: 999rpx;
}

.tag-chip.on {
  color: #1e7259;
  background: #e6f4ee;
  border-color: #b8dccc;
}

.remark-area {
  width: 100%;
  height: 140rpx;
  margin-top: 16rpx;
  padding: 18rpx 20rpx;
  font-size: 27rpx;
  background: #f6f8f7;
  border-radius: 12rpx;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.primary-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 90rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 16rpx;
}

.primary-btn::after {
  border: 0;
}
</style>
