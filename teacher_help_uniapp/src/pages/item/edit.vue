<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ItemEdit',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '新增/编辑物品',
  },
})

const form = ref({
  name: '',
  spec: '',
  price: '',
  alert: '',
  enabled: true,
  online: false,
})

const courses = ref(['基础数学'])

function goBack() {
  uni.navigateBack()
}
function addCourse() {
  uni.showToast({ title: '选择课程', icon: 'none' })
}
function removeCourse(idx: number) {
  courses.value.splice(idx, 1)
}
function save(andStockIn = false) {
  if (!form.value.name) {
    uni.showToast({ title: '请输入物品名称', icon: 'none' })
    return
  }
  if (andStockIn) {
    uni.navigateTo({ url: '/pages/item/purchase' })
    return
  }
  uni.showToast({ title: '已保存', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="ie-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        新增物品
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 物品信息 -->
    <view class="card">
      <view class="field">
        <text class="field-label">
          物品名称 <text class="req">*</text>
        </text>
        <input v-model="form.name" class="field-input" placeholder="请输入物品名称">
      </view>
      <view class="field">
        <text class="field-label">
          物品图片
        </text>
        <view class="upload-box" @click="uni.showToast({ title: '上传图片', icon: 'none' })">
          <uni-icons type="image" size="34" color="#6f7974" />
          <text class="upload-tip">
            点击上传图片
          </text>
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          规格
        </text>
        <input v-model="form.spec" class="field-input" placeholder="如：500ml、10个/盒">
      </view>
      <view class="field">
        <text class="field-label">
          销售价格
        </text>
        <view class="prefix-input">
          <text class="prefix">
            ¥
          </text>
          <input v-model="form.price" type="number" class="field-input pl" placeholder="0.00">
        </view>
      </view>
      <view class="field">
        <text class="field-label">
          库存预警值
        </text>
        <input v-model="form.alert" type="number" class="field-input" placeholder="预警阈值数量">
      </view>
    </view>

    <!-- 配置 -->
    <view class="card">
      <view class="field">
        <text class="field-label">
          关联课程
        </text>
        <view class="course-row">
          <view class="add-course" @click="addCourse">
            <uni-icons type="plusempty" size="16" color="#1f7159" />
            <text>添加课程</text>
          </view>
          <view v-for="(c, idx) in courses" :key="c" class="course-chip">
            <text>{{ c }}</text>
            <uni-icons type="closeempty" size="16" color="#3f4944" @click="removeCourse(idx)" />
          </view>
        </view>
      </view>
      <view class="switch-row">
        <text>启用状态</text>
        <switch :checked="form.enabled" color="#1f7159" @change="form.enabled = $event.detail.value" />
      </view>
      <view class="switch-row last">
        <text>线上售卖</text>
        <switch :checked="form.online" color="#1f7159" @change="form.online = $event.detail.value" />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="ghost-btn" @click="save(false)">
        保存
      </button>
      <button class="primary-btn" @click="save(true)">
        保存并入库
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.ie-page {
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

.prefix-input {
  position: relative;
  display: flex;
  align-items: center;
}

.prefix {
  position: absolute;
  left: 24rpx;
  font-size: 28rpx;
  color: #3f4944;
}

.field-input.pl {
  flex: 1;
  padding-left: 56rpx;
}

.upload-box {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  align-items: center;
  justify-content: center;
  height: 220rpx;
  border: 2rpx dashed #bec9c3;
  border-radius: 12rpx;
}

.upload-tip {
  font-size: 24rpx;
  color: #6f7974;
}

.course-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.add-course {
  display: flex;
  gap: 6rpx;
  align-items: center;
  padding: 10rpx 24rpx;
  font-size: 24rpx;
  color: #1f7159;
  background: #ffffff;
  border: 1rpx solid #1f7159;
  border-radius: 999rpx;
}

.course-chip {
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 10rpx 24rpx;
  font-size: 24rpx;
  color: #0f1d23;
  background: #d6e5ed;
  border-radius: 999rpx;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  font-size: 28rpx;
  font-weight: 500;
  border-top: 1rpx solid #bec9c3;
}

.switch-row.last {
  border-bottom: 0;
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
