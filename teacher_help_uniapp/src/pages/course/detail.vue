<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'CourseDetail',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '课程详情',
  },
})

const courseId = ref('')
const course = ref({
  name: '少儿英语进阶',
  type: '一对多',
  enabled: true,
  sellable: true,
  total: 2400,
  unit: 200,
  count: 12,
})

const tabs = ['价格', '班级', '套餐', '规则']
const activeTab = ref('价格')

const rules = [
  { label: '请假扣课', value: '提前2小时可退' },
  { label: '课时消耗', value: '每节课消耗1课时' },
  { label: '有效期', value: '自报读起1年有效' },
]

function goBack() {
  uni.navigateBack()
}
function onEdit() {
  uni.navigateTo({ url: `/pages/course/create?id=${courseId.value}` })
}

onLoad((query) => {
  courseId.value = query?.id || ''
})
</script>

<template>
  <view class="cd-page">
    <view class="top-bar">
      <button class="icon-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#005842" />
      </button>
      <text class="nav-title">
        课程详情
      </text>
      <view class="icon-btn" />
    </view>

    <!-- 封面 -->
    <view class="cover">
      <view class="cover-tag">
        <view class="cover-dot" />
        {{ course.type }}
      </view>
    </view>

    <!-- 标题卡 -->
    <view class="title-card">
      <view class="accent" />
      <text class="course-name">
        {{ course.name }}
      </text>
      <view class="title-tags">
        <view class="t-tag primary">
          <uni-icons type="checkmarkempty" size="13" color="#00513d" />启用中
        </view>
        <view v-if="course.sellable" class="t-tag">
          <uni-icons type="shop" size="13" color="#3f4944" />可售
        </view>
      </view>
    </view>

    <!-- 分段 -->
    <view class="seg">
      <view
        v-for="t in tabs"
        :key="t"
        class="seg-item"
        :class="{ on: activeTab === t }"
        @click="activeTab = t"
      >
        {{ t }}
      </view>
    </view>

    <template v-if="activeTab === '价格'">
      <!-- 标准收费 -->
      <view class="card">
        <view class="card-title">
          <uni-icons type="wallet" size="18" color="#1f7159" />
          <text>标准收费</text>
        </view>
        <view class="total-box">
          <text class="total-label">
            总价
          </text>
          <text class="total-value">
            <text class="cny">￥</text>{{ course.total }}
          </text>
        </view>
        <view class="mini-grid">
          <view class="mini-item">
            <text class="mini-label">
              单价
            </text>
            <text class="mini-value">
              ￥{{ course.unit }}
            </text>
          </view>
          <view class="mini-item">
            <text class="mini-label">
              数量
            </text>
            <text class="mini-value">
              {{ course.count }} 节
            </text>
          </view>
        </view>
      </view>

      <!-- 规则详情 -->
      <view class="card no-pad">
        <view class="rule-head">
          <uni-icons type="info" size="17" color="#40655b" />
          <text>规则详情</text>
        </view>
        <view v-for="(r, idx) in rules" :key="r.label" class="rule-row" :class="{ last: idx === rules.length - 1 }">
          <view class="rule-label">
            <view class="rule-dot" />
            <text>{{ r.label }}</text>
          </view>
          <text class="rule-value">
            {{ r.value }}
          </text>
        </view>
      </view>
    </template>

    <view v-else class="empty">
      {{ activeTab }}内容待完善
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="onEdit">
        <uni-icons type="compose" size="19" color="#ffffff" />
        <text>编辑课程</text>
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.cd-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 160rpx;
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
  font-size: 32rpx;
  font-weight: 600;
}

.cover {
  position: relative;
  height: 280rpx;
  margin-top: 20rpx;
  background: linear-gradient(135deg, #2a9d73, #1f7159);
  border-radius: 18rpx;
}

.cover-tag {
  position: absolute;
  bottom: 22rpx;
  left: 22rpx;
  display: flex;
  gap: 8rpx;
  align-items: center;
  padding: 8rpx 20rpx;
  font-size: 22rpx;
  color: #1f7159;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999rpx;
}

.cover-dot {
  width: 14rpx;
  height: 14rpx;
  background: #007351;
  border-radius: 50%;
}

.title-card {
  position: relative;
  margin-top: 22rpx;
  padding: 24rpx 24rpx 24rpx 30rpx;
  overflow: hidden;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 18rpx;
}

.accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 8rpx;
  height: 100%;
  background: #007351;
}

.course-name {
  font-size: 40rpx;
  font-weight: 700;
}

.title-tags {
  display: flex;
  gap: 12rpx;
  margin-top: 18rpx;
}

.t-tag {
  display: flex;
  gap: 4rpx;
  align-items: center;
  padding: 6rpx 18rpx;
  font-size: 23rpx;
  color: #3f4944;
  background: #dbebf3;
  border-radius: 999rpx;
}

.t-tag.primary {
  color: #00513d;
  background: #a4f2d4;
}

.seg {
  display: flex;
  gap: 6rpx;
  margin-top: 24rpx;
  padding: 8rpx;
  background: #e7f6fe;
  border-radius: 14rpx;
}

.seg-item {
  flex: 1;
  font-size: 25rpx;
  line-height: 60rpx;
  color: #3f4944;
  text-align: center;
  border-radius: 10rpx;
}

.seg-item.on {
  font-weight: 700;
  color: #1f7159;
  background: #ffffff;
}

.card {
  margin-top: 22rpx;
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 18rpx;
}

.card.no-pad {
  padding: 0;
  overflow: hidden;
}

.card-title {
  display: flex;
  gap: 10rpx;
  align-items: center;
  margin-bottom: 22rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.total-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28rpx;
  background: #e7f6fe;
  border-radius: 14rpx;
}

.total-label {
  font-size: 22rpx;
  color: #3f4944;
}

.total-value {
  margin-top: 8rpx;
  font-size: 56rpx;
  font-weight: 700;
  color: #1f7159;
}

.cny {
  font-size: 30rpx;
}

.mini-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
  margin-top: 14rpx;
}

.mini-item {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  padding: 20rpx;
  background: #f3faff;
  border: 1rpx solid #bec9c3;
  border-radius: 12rpx;
}

.mini-label {
  font-size: 22rpx;
  color: #6f7974;
}

.mini-value {
  font-size: 30rpx;
  font-weight: 600;
}

.rule-head {
  display: flex;
  gap: 10rpx;
  align-items: center;
  padding: 22rpx 24rpx;
  font-size: 26rpx;
  font-weight: 600;
  background: #e7f6fe;
  border-bottom: 1rpx solid #bec9c3;
}

.rule-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 26rpx 24rpx;
  border-bottom: 1rpx solid #eef2f0;
}

.rule-row.last {
  border-bottom: 0;
}

.rule-label {
  display: flex;
  gap: 12rpx;
  align-items: center;
  font-size: 27rpx;
  color: #3f4944;
}

.rule-dot {
  width: 12rpx;
  height: 12rpx;
  background: #a7cfc2;
  border-radius: 50%;
}

.rule-value {
  font-size: 27rpx;
  font-weight: 500;
}

.empty {
  margin-top: 60rpx;
  font-size: 26rpx;
  color: #9aa5aa;
  text-align: center;
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #bec9c3;
}

.primary-btn {
  display: flex;
  gap: 10rpx;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 90rpx;
  margin: 0;
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
  border-radius: 14rpx;
}
</style>
