<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'CourseCreate',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '新增/编辑课程',
  },
})

const form = ref({
  name: '',
  type: '一对多',
  color: '#E57373',
  priceName: '',
  count: '',
  unit: '',
  total: '',
  enabled: true,
  online: false,
  remark: '',
})

const colors = ['#E57373', '#81C784', '#64B5F6', '#FFB74D', '#BA68C8']
const billing = ref('按课时')
const billingOptions = ['按课时', '按月', '按次']

function goBack() {
  uni.navigateBack()
}
function save(andClass = false) {
  if (!form.value.name) {
    uni.showToast({ title: '请输入课程名称', icon: 'none' })
    return
  }
  uni.showToast({ title: andClass ? '已保存并建班' : '已保存', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="cc-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        新增/编辑课程
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 基本信息 -->
    <view class="card">
      <text class="card-title">
        基本信息
      </text>
      <view class="field">
        <text class="field-label">
          课程名称 <text class="req">*</text>
        </text>
        <input v-model="form.name" class="field-input" placeholder="请输入课程名称">
      </view>
      <view class="field">
        <text class="field-label">
          课程类型 <text class="req">*</text>
        </text>
        <view class="radio-row">
          <view
            v-for="t in ['一对多', '一对一']"
            :key="t"
            class="radio"
            :class="{ on: form.type === t }"
            @click="form.type = t"
          >
            {{ t }}
          </view>
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          展示颜色
        </text>
        <view class="color-row">
          <view
            v-for="c in colors"
            :key="c"
            class="color-dot"
            :class="{ on: form.color === c }"
            :style="{ background: c }"
            @click="form.color = c"
          >
            <uni-icons v-if="form.color === c" type="checkmarkempty" size="16" color="#ffffff" />
          </view>
        </view>
      </view>
    </view>

    <!-- 收费标准 -->
    <view class="card">
      <view class="card-title-row">
        <text class="card-title">
          收费标准
        </text>
        <text class="add-link">
          + 添加标准
        </text>
      </view>
      <view class="charge-box">
        <view class="field">
          <text class="field-label">
            收费方式
          </text>
          <view class="radio-row">
            <view
              v-for="b in billingOptions"
              :key="b"
              class="radio sm"
              :class="{ on: billing === b }"
              @click="billing = b"
            >
              {{ b }}
            </view>
          </view>
        </view>
        <view class="field">
          <text class="field-label">
            价格名称
          </text>
          <input v-model="form.priceName" class="field-input" placeholder="如：春季常规班">
        </view>
        <view class="two-col">
          <view class="field">
            <text class="field-label">
              包含课时
            </text>
            <input v-model="form.count" type="number" class="field-input" placeholder="0">
          </view>
          <view class="field">
            <text class="field-label">
              单价
            </text>
            <input v-model="form.unit" type="number" class="field-input" placeholder="0.00">
          </view>
        </view>
        <view class="field">
          <text class="field-label">
            总价
          </text>
          <input v-model="form.total" type="number" class="field-input total" placeholder="0.00">
        </view>
      </view>
    </view>

    <!-- 设置与备注 -->
    <view class="card">
      <text class="card-title">
        设置与备注
      </text>
      <view class="switch-row">
        <text>是否启用</text>
        <switch :checked="form.enabled" color="#1f7159" @change="form.enabled = $event.detail.value" />
      </view>
      <view class="switch-row">
        <text>是否线上售卖</text>
        <switch :checked="form.online" color="#1f7159" @change="form.online = $event.detail.value" />
      </view>
      <view class="field pt">
        <text class="field-label">
          备注
        </text>
        <textarea v-model="form.remark" class="field-area" placeholder="添加课程备注信息..." />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="save(false)">
        保存
      </button>
      <button class="primary-btn" @click="save(true)">
        保存并建班
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cc-page {
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

.card-title {
  font-size: 30rpx;
  font-weight: 600;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.add-link {
  font-size: 24rpx;
  color: #1f7159;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-top: 24rpx;
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

.field-input.total {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f7159;
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
  padding: 14rpx 32rpx;
  font-size: 26rpx;
  color: #3f4944;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 999rpx;
}

.radio.sm {
  padding: 10rpx 26rpx;
  font-size: 25rpx;
}

.radio.on {
  color: #1f7159;
  background: #e7f6fe;
  border-color: #1f7159;
}

.color-row {
  display: flex;
  gap: 24rpx;
}

.color-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
}

.color-dot.on {
  box-shadow: 0 0 0 4rpx #ffffff, 0 0 0 7rpx currentColor;
}

.charge-box {
  margin-top: 18rpx;
  padding: 22rpx;
  background: #f3faff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.charge-box .field:first-child {
  margin-top: 0;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22rpx 0;
  font-size: 28rpx;
  border-bottom: 1rpx solid #bec9c3;
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
  height: 88rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
  border-radius: 12rpx;
}

.ghost-btn {
  flex: 1;
  color: #1f7159;
  background: transparent;
  border: 1rpx solid #1f7159;
}

.primary-btn {
  flex: 2;
  color: #ffffff;
  background: #1f7159;
}
</style>
