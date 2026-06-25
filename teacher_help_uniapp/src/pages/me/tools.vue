<script lang="ts" setup>
defineOptions({
  name: 'MoreTools',
})
definePage({
  style: {
    navigationStyle: 'custom',
    navigationBarTitleText: '更多工具',
  },
})

interface Tool {
  key: string
  title: string
  desc: string
  icon: string
  route?: string
  tab?: boolean
}

// 高频工具（主色图标）
const frequentTools: Tool[] = [
  { key: 'schedule', title: '排课管理', desc: '智能编排课程计划', icon: 'calendar-filled', route: '/pages/schedule/create' },
  { key: 'attendance', title: '点名记录', desc: '课堂考勤快速登记', icon: 'list', route: '/pages/schedule/index', tab: true },
  { key: 'leave', title: '学员请假', desc: '请假审批与补课', icon: 'flag-filled', route: '/pages/student/leave' },
  { key: 'wrong', title: '错题分析记录', desc: '学情诊断与提分', icon: 'help-filled', route: '/pages/wrong-question/index', tab: true },
]

// 教务管理（次色图标）
const teachingTools: Tool[] = [
  { key: 'course', title: '课程管理', desc: '课程体系与大纲', icon: 'font', route: '/pages/course/index' },
  { key: 'class', title: '班级管理', desc: '班级编排与升班', icon: 'staff', route: '/pages/class/index' },
  { key: 'teacher', title: '老师管理', desc: '教师档案与排期', icon: 'person', route: '/pages/teacher/index' },
  { key: 'room', title: '教室/场地', desc: '场地资源与调配', icon: 'location', route: '/pages/venue/index' },
]

// 经营管理（次色图标）
const businessTools: Tool[] = [
  { key: 'item', title: '物品费用', desc: '教材杂费管理', icon: 'cart', route: '/pages/item/index' },
  { key: 'card', title: '会员卡', desc: '储值卡与计次卡', icon: 'wallet', route: '/pages/member-card/index' },
  { key: 'bill', title: '收费记录', desc: '流水账单查询', icon: 'paperplane' },
  { key: 'data', title: '数据概览', desc: '核心运营指标', icon: 'eye', route: '/pages/me/business' },
]

function goBack() {
  uni.navigateBack()
}

function onTool(tool: Tool) {
  if (!tool.route) {
    uni.showToast({ title: `${tool.title}（待开发）`, icon: 'none' })
    return
  }
  if (tool.tab)
    uni.switchTab({ url: tool.route })
  else
    uni.navigateTo({ url: tool.route })
}
</script>

<template>
  <view class="tools-page">
    <view class="top-bar">
      <button class="back-btn" @click="goBack">
        <uni-icons type="left" size="26" color="#00684f" />
      </button>
      <text class="nav-title">
        更多工具
      </text>
      <view class="nav-space" />
    </view>

    <view class="section">
      <text class="section-title">
        高频工具
      </text>
      <view class="tool-grid">
        <view v-for="t in frequentTools" :key="t.key" class="tool-card" @click="onTool(t)">
          <view class="tool-icon primary">
            <uni-icons :type="t.icon" size="20" color="#1f7159" />
          </view>
          <text class="tool-name">
            {{ t.title }}
          </text>
          <text class="tool-desc">
            {{ t.desc }}
          </text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">
        教务管理
      </text>
      <view class="tool-grid">
        <view v-for="t in teachingTools" :key="t.key" class="tool-card" @click="onTool(t)">
          <view class="tool-icon">
            <uni-icons :type="t.icon" size="20" color="#40655b" />
          </view>
          <text class="tool-name">
            {{ t.title }}
          </text>
          <text class="tool-desc">
            {{ t.desc }}
          </text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">
        经营管理
      </text>
      <view class="tool-grid">
        <view v-for="t in businessTools" :key="t.key" class="tool-card" @click="onTool(t)">
          <view class="tool-icon">
            <uni-icons :type="t.icon" size="20" color="#40655b" />
          </view>
          <text class="tool-name">
            {{ t.title }}
          </text>
          <text class="tool-desc">
            {{ t.desc }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.tools-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0 28rpx 40rpx;
  color: #0f1d23;
  background: #f4f6f5;
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
  padding: 0 28rpx;
  background: #f3faff;
}

.back-btn,
.nav-space {
  width: 64rpx;
  height: 64rpx;
  padding: 0;
  margin: 0;
  background: transparent;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #00684f;
}

.section {
  margin-top: 36rpx;
}

.section-title {
  display: block;
  margin: 0 0 18rpx 4rpx;
  font-size: 27rpx;
  font-weight: 600;
  color: #3f4944;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22rpx;
}

.tool-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 26rpx 24rpx;
  background: #ffffff;
  border: 1rpx solid #bec9c3;
  border-radius: 16rpx;
}

.tool-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  margin-bottom: 18rpx;
  background: #e7f6fe;
  border-radius: 50%;
}

.tool-icon.primary {
  background: #e6f4ee;
}

.tool-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #0f1d23;
}

.tool-desc {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #6f7974;
}
</style>
