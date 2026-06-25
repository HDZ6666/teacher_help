<script lang="ts" setup>
import { ref } from 'vue'

defineOptions({
  name: 'ScheduleComment',
})

definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '课后点评',
  },
})

const summary = ref('')
const homework = ref('')
const parentNote = ref('')
const syncParent = ref(true)
const templates = ['表现积极', '需加强练习', '作业已布置', '专注度高']

function goBack() {
  uni.navigateBack()
}

function appendTemplate(text: string) {
  const prefix = summary.value ? `${summary.value}，` : ''
  summary.value = `${prefix}${text}`
}

function toggleSync() {
  syncParent.value = !syncParent.value
}

function saveDraft() {
  uni.showToast({ title: '已保存草稿', icon: 'none' })
}

function publishComment() {
  uni.showToast({ title: '点评已发布', icon: 'success' })
}
</script>

<template>
  <view class="comment-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="30" color="#34433d" />
      </button>
      <view class="page-title">
        课后点评
      </view>
      <view class="top-placeholder" />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="student-head">
        <view class="avatar">
          李
        </view>
        <view>
          <view class="student-name">
            李明轩
          </view>
          <view class="student-sub">
            钢琴中级班 - 第12节
          </view>
        </view>
      </view>

      <view class="form-card summary-card">
        <view class="field-label">
          课堂表现总结
        </view>
        <textarea
          v-model="summary"
          class="summary-input"
          maxlength="300"
          placeholder="请描述学生本节课的学习状态、掌握情况..."
          placeholder-class="textarea-placeholder"
        />
        <view class="template-row">
          <button
            v-for="item in templates"
            :key="item"
            class="template-chip"
            @click="appendTemplate(item)"
          >
            {{ item }}
          </button>
        </view>
      </view>

      <view class="form-card">
        <view class="field-label">
          作业说明
        </view>
        <textarea
          v-model="homework"
          class="homework-input"
          maxlength="200"
          placeholder="填写课后需要完成的练习或作业内容..."
          placeholder-class="textarea-placeholder"
        />
      </view>

      <view class="form-card">
        <view class="field-label">
          课堂照片 (最多9张)
        </view>
        <view class="photo-grid">
          <button class="upload-box">
            <uni-icons type="plus" size="36" color="#34433d" />
            <text>上传</text>
          </button>
          <view class="photo-item">
            <view class="photo-illustration">
              <view class="photo-face" />
              <view class="photo-piano" />
            </view>
            <button class="remove-photo">
              <uni-icons type="close" size="18" color="#0f1d23" />
            </button>
          </view>
        </view>
      </view>

      <view class="form-card">
        <view class="field-label">
          给家长的备注
        </view>
        <textarea
          v-model="parentNote"
          class="note-input"
          maxlength="160"
          placeholder="仅家长可见，用于沟通注意事项..."
          placeholder-class="textarea-placeholder"
        />
      </view>

      <view class="sync-card" @click="toggleSync">
        <view>
          <view class="sync-title">
            同步给家长
          </view>
          <view class="sync-desc">
            发布后将通过微信通知家长
          </view>
        </view>
        <view class="switch" :class="{ active: syncParent }">
          <view class="switch-dot" />
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="draft-btn" @click="saveDraft">
        保存草稿
      </button>
      <button class="publish-btn" @click="publishComment">
        发布点评
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.comment-page {
  min-height: 100vh;
  color: #0f1d23;
  background: #f3faff;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 88rpx 1fr 88rpx;
  align-items: center;
  height: 104rpx;
  padding: 0 26rpx;
  background: #f3faff;
}

.back-btn,
.template-chip,
.upload-box,
.remove-photo,
.draft-btn,
.publish-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
}

.back-btn::after,
.template-chip::after,
.upload-box::after,
.remove-photo::after,
.draft-btn::after,
.publish-btn::after {
  border: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 72rpx;
  height: 72rpx;
  background: transparent;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  text-align: center;
}

.top-placeholder {
  width: 72rpx;
}

.content-scroll {
  height: calc(100vh - 104rpx);
  box-sizing: border-box;
  padding: 0 26rpx 170rpx;
}

.student-head {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-top: 4rpx;
  margin-bottom: 44rpx;
}

.avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 86rpx;
  height: 86rpx;
  font-size: 36rpx;
  color: #1f7159;
  background: #c2ebde;
  border-radius: 50%;
}

.student-name {
  font-size: 34rpx;
  font-weight: 700;
}

.student-sub {
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #3f4944;
}

.form-card,
.sync-card {
  box-sizing: border-box;
  margin-bottom: 44rpx;
  padding: 28rpx;
  background: #ffffff;
  border: 2rpx solid #bec9c3;
  border-radius: 14rpx;
  box-shadow: 0 4rpx 10rpx rgba(31, 45, 51, 0.05);
}

.summary-card {
  min-height: 360rpx;
}

.field-label {
  margin-bottom: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #34433d;
}

.summary-input,
.homework-input,
.note-input {
  width: 100%;
  min-height: 152rpx;
  padding: 0;
  font-size: 30rpx;
  line-height: 1.55;
  color: #0f1d23;
  background: transparent;
  border: 0;
}

.summary-input {
  min-height: 180rpx;
}

.homework-input {
  min-height: 140rpx;
}

.note-input {
  min-height: 116rpx;
}

.textarea-placeholder {
  color: #6f7974;
}

.template-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-top: 24rpx;
}

.template-chip {
  height: 46rpx;
  padding: 0 24rpx;
  font-size: 24rpx;
  color: #34433d;
  background: #e7f6fe;
  border-radius: 999rpx;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18rpx;
}

.upload-box,
.photo-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: 12rpx;
}

.upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  font-size: 22rpx;
  color: #34433d;
  background: #ffffff;
  border: 2rpx dashed #bec9c3;
}

.photo-item {
  border: 2rpx solid #bec9c3;
}

.photo-illustration {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f8d9a7 0%, #f3faff 46%, #193f36 100%);
}

.photo-face {
  position: absolute;
  top: 18rpx;
  left: 28rpx;
  width: 34rpx;
  height: 34rpx;
  background: #8c4f2b;
  border-radius: 50%;
}

.photo-piano {
  position: absolute;
  right: 12rpx;
  bottom: 16rpx;
  width: 72rpx;
  height: 28rpx;
  background: #101f26;
  border-radius: 6rpx;
}

.remove-photo {
  position: absolute;
  top: 4rpx;
  right: 4rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42rpx;
  height: 42rpx;
  background: rgba(255, 255, 255, 0.86);
  border-radius: 50%;
}

.sync-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28rpx;
}

.sync-title {
  font-size: 30rpx;
  color: #0f1d23;
}

.sync-desc {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #3f4944;
}

.switch {
  position: relative;
  flex-shrink: 0;
  width: 88rpx;
  height: 48rpx;
  background: #d6e5ed;
  border-radius: 999rpx;
  transition: background 0.2s ease;
}

.switch.active {
  background: #1f7159;
}

.switch-dot {
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  width: 40rpx;
  height: 40rpx;
  background: #ffffff;
  border-radius: 50%;
  transition: transform 0.2s ease;
}

.switch.active .switch-dot {
  transform: translateX(40rpx);
}

.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 22rpx;
  padding: 26rpx 26rpx calc(26rpx + env(safe-area-inset-bottom));
  background: #f3faff;
  border-top: 1rpx solid #bec9c3;
}

.draft-btn,
.publish-btn {
  height: 78rpx;
  font-size: 28rpx;
  font-weight: 700;
  border-radius: 12rpx;
}

.draft-btn {
  color: #1f7159;
  background: #f3faff;
  border: 2rpx solid #1f7159;
}

.publish-btn {
  color: #ffffff;
  background: #1f7159;
}
</style>
