<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

defineOptions({
  name: 'StudentLeave',
})
definePage({
  style: {
    navigationBarTitleText: '学员请假',
  },
})

const form = ref({
  student: '',
  course: '',
  reason: '',
  startDate: '',
  endDate: '',
})

const leaveTypes = ['事假', '病假', '其他']
const leaveType = ref('事假')

type Mode = 'lesson' | 'range'
const mode = ref<Mode>('lesson')

// 按课次：可选课次
const lessons = ref([
  { id: 1, title: '数学提高A班', time: '06-25 18:30-20:00', checked: true },
  { id: 2, title: '数学提高A班', time: '06-27 18:30-20:00', checked: false },
  { id: 3, title: '数学提高A班', time: '06-30 18:30-20:00', checked: false },
])

const deduct = ref(false)
const images = ref<string[]>([])

function toggleLesson(id: number) {
  const l = lessons.value.find(i => i.id === id)
  if (l)
    l.checked = !l.checked
}

function onStartChange(e: any) {
  form.value.startDate = e.detail.value
}
function onEndChange(e: any) {
  form.value.endDate = e.detail.value
}

function chooseImage() {
  uni.chooseImage({
    count: 3,
    success: (res: any) => {
      images.value = images.value.concat(res.tempFilePaths).slice(0, 3)
    },
  })
}
function removeImage(idx: number) {
  images.value.splice(idx, 1)
}

function submit() {
  if (!form.value.student) {
    uni.showToast({ title: '请选择学员', icon: 'none' })
    return
  }
  uni.showToast({ title: '请假已提交', icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}

onLoad((query) => {
  if (query?.name)
    form.value.student = decodeURIComponent(query.name)
})
</script>

<template>
  <view class="leave-page">
    <view class="form-card">
      <view class="row" @click="form.student = form.student || '李明轩'">
        <text class="row-label req">
          请假学员
        </text>
        <view class="row-value" :class="{ ph: !form.student }">
          {{ form.student || '请选择学员' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
      <view class="row no-border" @click="form.course = '数学提高A班'">
        <text class="row-label">
          关联课程
        </text>
        <view class="row-value" :class="{ ph: !form.course }">
          {{ form.course || '请选择课程' }}
          <uni-icons type="right" size="15" color="#9aa5aa" />
        </view>
      </view>
    </view>

    <!-- 请假类型 -->
    <view class="form-card pad">
      <text class="row-label">
        请假类型
      </text>
      <view class="seg-wrap">
        <view
          v-for="t in leaveTypes"
          :key="t"
          class="seg-item"
          :class="{ on: leaveType === t }"
          @click="leaveType = t"
        >
          {{ t }}
        </view>
      </view>
    </view>

    <!-- 请假方式 -->
    <view class="form-card pad">
      <text class="row-label">
        请假方式
      </text>
      <view class="seg-wrap">
        <view class="seg-item" :class="{ on: mode === 'lesson' }" @click="mode = 'lesson'">
          按课次
        </view>
        <view class="seg-item" :class="{ on: mode === 'range' }" @click="mode = 'range'">
          按时间段
        </view>
      </view>
    </view>

    <!-- 按课次 -->
    <template v-if="mode === 'lesson'">
      <view class="form-card pad">
        <text class="row-label">
          选择课次
        </text>
        <view
          v-for="l in lessons"
          :key="l.id"
          class="lesson-row"
          @click="toggleLesson(l.id)"
        >
          <view class="lesson-main">
            <view class="lesson-title">
              {{ l.title }}
            </view>
            <view class="lesson-time">
              {{ l.time }}
            </view>
          </view>
          <view class="checkbox" :class="{ on: l.checked }">
            <uni-icons v-if="l.checked" type="checkmarkempty" size="15" color="#ffffff" />
          </view>
        </view>
      </view>
    </template>

    <!-- 按时间段 -->
    <template v-else>
      <view class="form-card">
        <picker mode="date" :value="form.startDate" @change="onStartChange">
          <view class="row">
            <text class="row-label">
              开始日期
            </text>
            <view class="row-value" :class="{ ph: !form.startDate }">
              {{ form.startDate || '请选择' }}
              <uni-icons type="right" size="15" color="#9aa5aa" />
            </view>
          </view>
        </picker>
        <picker mode="date" :value="form.endDate" @change="onEndChange">
          <view class="row no-border">
            <text class="row-label">
              结束日期
            </text>
            <view class="row-value" :class="{ ph: !form.endDate }">
              {{ form.endDate || '请选择' }}
              <uni-icons type="right" size="15" color="#9aa5aa" />
            </view>
          </view>
        </picker>
      </view>
    </template>

    <!-- 原因 + 图片 -->
    <view class="form-card pad">
      <text class="row-label">
        请假原因
      </text>
      <textarea v-model="form.reason" class="remark-area" placeholder="请填写请假原因" />
      <view class="img-row">
        <view v-for="(img, idx) in images" :key="idx" class="img-item">
          <image :src="img" mode="aspectFill" class="img-thumb" />
          <view class="img-del" @click="removeImage(idx)">
            <uni-icons type="clear" size="18" color="#ffffff" />
          </view>
        </view>
        <view v-if="images.length < 3" class="img-add" @click="chooseImage">
          <uni-icons type="camera" size="26" color="#9aa5aa" />
        </view>
      </view>
    </view>

    <!-- 是否扣课 -->
    <view class="form-card">
      <view class="row no-border">
        <view>
          <text class="row-label">
            本次请假扣课时
          </text>
          <view class="row-sub">
            关闭则不扣减剩余课时
          </view>
        </view>
        <switch :checked="deduct" color="#1f7159" @change="deduct = $event.detail.value" />
      </view>
    </view>

    <view class="bottom-bar">
      <button class="primary-btn" @click="submit">
        提交请假
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.leave-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.form-card {
  margin-bottom: 16rpx;
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
  font-size: 27rpx;
  color: #4a565c;
}

.row-label.req::before {
  margin-right: 6rpx;
  color: #c0392b;
  content: '*';
}

.row-sub {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #9aa5aa;
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

.seg-wrap {
  display: flex;
  gap: 12rpx;
  margin-top: 18rpx;
}

.seg-item {
  flex: 1;
  font-size: 26rpx;
  line-height: 72rpx;
  color: #67757c;
  text-align: center;
  background: #f1f4f2;
  border: 1rpx solid transparent;
  border-radius: 12rpx;
}

.seg-item.on {
  font-weight: 600;
  color: #1e7259;
  background: #e6f4ee;
  border-color: #b8dccc;
}

.lesson-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.lesson-row:last-child {
  border-bottom: 0;
}

.lesson-title {
  font-size: 27rpx;
  font-weight: 600;
}

.lesson-time {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #839099;
}

.checkbox {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #cfd9d4;
  border-radius: 8rpx;
}

.checkbox.on {
  background: #1f7159;
  border-color: #1f7159;
}

.remark-area {
  width: 100%;
  height: 130rpx;
  margin-top: 16rpx;
  padding: 18rpx 20rpx;
  font-size: 27rpx;
  background: #f6f8f7;
  border-radius: 12rpx;
}

.img-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 20rpx;
}

.img-item {
  position: relative;
  width: 130rpx;
  height: 130rpx;
}

.img-thumb {
  width: 130rpx;
  height: 130rpx;
  border-radius: 12rpx;
}

.img-del {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36rpx;
  height: 36rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
}

.img-add {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 130rpx;
  height: 130rpx;
  background: #f6f8f7;
  border: 1rpx dashed #cfd9d4;
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
