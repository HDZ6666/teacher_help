<script lang="ts" setup>
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

defineOptions({
  name: 'StudentDetail',
})
definePage({
  style: {
    navigationBarTitleText: '学员详情',
  },
})

const studentId = ref('')

// 静态 mock：实际应按 id 拉取，这里固定一份
const student = ref({
  name: '李明轩',
  grade: '三年级',
  school: '实验小学',
  phone: '138****2046',
  relation: '母亲',
  tags: ['课时不足', '待跟进'],
  follower: '王老师',
  manager: '张学管',
  remaining: 2,
  consumed: 38,
  absent: 1,
  wrongCount: 12,
})

const quickActions = [
  { key: 'contact', label: '联系家长', icon: 'phone' },
  { key: 'enroll', label: '报名续费', icon: 'wallet' },
  { key: 'leave', label: '请假', icon: 'calendar' },
  { key: 'reschedule', label: '调课', icon: 'loop' },
  { key: 'wrong', label: '拍错题', icon: 'camera' },
]

const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'courses', label: '报读课程' },
  { key: 'records', label: '上课记录' },
  { key: 'wrong', label: '错题' },
  { key: 'consume', label: '消费' },
]
const activeTab = ref('overview')

const courses = ref([
  { id: 1, name: '数学提高A班', remaining: 2, consumed: 38, expire: '2026-09-30', status: '在读', className: '数学提高A班' },
  { id: 2, name: '英语精读B班', remaining: 0, consumed: 24, expire: '2026-06-15', status: '已结课', className: '英语精读B班' },
])

const records = ref([
  { id: 1, date: '06-23', course: '数学提高A班', status: '到课', statusClass: 'present' },
  { id: 2, date: '06-20', course: '数学提高A班', status: '迟到', statusClass: 'late' },
  { id: 3, date: '06-18', course: '数学提高A班', status: '缺勤', statusClass: 'absent' },
  { id: 4, date: '06-16', course: '数学提高A班', status: '请假', statusClass: 'leave' },
])

const wrongList = ref([
  { id: 1, subject: '数学', point: '分数应用题', mastery: '未掌握', masteryClass: 'danger', date: '06-23' },
  { id: 2, subject: '数学', point: '面积计算', mastery: '已了解', masteryClass: 'warn', date: '06-20' },
])

const consumes = ref([
  { id: 1, title: '数学提高A班 · 续费', amount: -1980, date: '2026-05-12', type: '报名' },
  { id: 2, title: '数学提高A班 · 课消', amount: -1, date: '2026-06-23', type: '课消', unit: '课时' },
])

const riskTips = computed(() => {
  const tips: string[] = []
  if (student.value.remaining <= 3)
    tips.push('剩余课时不足，建议尽快续费')
  if (student.value.absent > 0)
    tips.push('近期有缺勤，需关注补课')
  return tips
})

function onAction(key: string) {
  const map: Record<string, string> = {
    contact: '联系家长',
    enroll: '报名续费',
    leave: '请假',
    reschedule: '调课',
    wrong: '拍错题',
  }
  uni.showToast({ title: map[key] || key, icon: 'none' })
}

onLoad((query) => {
  studentId.value = query?.id || ''
})
</script>

<template>
  <view class="detail-page">
    <view class="hero-card">
      <view class="hero-top">
        <view class="hero-avatar">
          {{ student.name.slice(0, 1) }}
        </view>
        <view class="hero-main">
          <view class="hero-name">
            {{ student.name }}
          </view>
          <view class="hero-meta">
            {{ student.grade }} · {{ student.school }}
          </view>
          <view class="hero-meta">
            {{ student.relation }} · {{ student.phone }}
          </view>
        </view>
      </view>
      <view class="hero-tags">
        <text v-for="tag in student.tags" :key="tag" class="hero-tag">
          {{ tag }}
        </text>
      </view>
      <view class="hero-foot">
        <text>跟进人：{{ student.follower }}</text>
        <text>学管师：{{ student.manager }}</text>
      </view>
    </view>

    <view class="quick-row">
      <view v-for="act in quickActions" :key="act.key" class="quick-item" @click="onAction(act.key)">
        <view class="quick-icon">
          <uni-icons :type="act.icon" size="20" color="#1f7159" />
        </view>
        <text class="quick-label">
          {{ act.label }}
        </text>
      </view>
    </view>

    <view class="metric-grid">
      <view class="metric-item">
        <view class="metric-value" :class="{ low: student.remaining <= 3 }">
          {{ student.remaining }}
        </view>
        <view class="metric-label">
          剩余课时
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ student.consumed }}
        </view>
        <view class="metric-label">
          已消耗
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ student.absent }}
        </view>
        <view class="metric-label">
          缺勤次数
        </view>
      </view>
      <view class="metric-item">
        <view class="metric-value">
          {{ student.wrongCount }}
        </view>
        <view class="metric-label">
          错题数量
        </view>
      </view>
    </view>

    <scroll-view class="tab-scroll" scroll-x>
      <view class="tab-row">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </view>
      </view>
    </scroll-view>

    <!-- 概览 -->
    <view v-if="activeTab === 'overview'" class="tab-pane">
      <view v-if="riskTips.length" class="risk-card">
        <view class="risk-title">
          风险提醒
        </view>
        <view v-for="tip in riskTips" :key="tip" class="risk-item">
          <uni-icons type="info" size="15" color="#c0392b" />
          <text>{{ tip }}</text>
        </view>
      </view>
      <view class="info-card">
        <view class="card-title">
          最近上课
        </view>
        <view class="info-line">
          06-23 数学提高A班 · <text class="state present">到课</text>
        </view>
        <view class="card-title mt">
          最近错题
        </view>
        <view class="info-line">
          数学 · 分数应用题 · <text class="state danger">未掌握</text>
        </view>
        <view class="card-title mt">
          最近跟进
        </view>
        <view class="info-line">
          05-28 已电联家长，提醒续费
        </view>
      </view>
    </view>

    <!-- 报读课程 -->
    <view v-else-if="activeTab === 'courses'" class="tab-pane">
      <view v-for="c in courses" :key="c.id" class="course-card">
        <view class="course-head">
          <text class="course-name">
            {{ c.name }}
          </text>
          <text class="course-status" :class="c.status === '在读' ? 'present' : 'muted'">
            {{ c.status }}
          </text>
        </view>
        <view class="course-grid">
          <view><text class="cg-num" :class="{ low: c.remaining <= 3 }">{{ c.remaining }}</text><text class="cg-label">剩余课时</text></view>
          <view><text class="cg-num">{{ c.consumed }}</text><text class="cg-label">已消耗</text></view>
          <view><text class="cg-num sm">{{ c.expire }}</text><text class="cg-label">有效期</text></view>
        </view>
        <view class="course-actions">
          <button class="mini-btn primary" @click="onAction('enroll')">
            续费
          </button>
          <button class="mini-btn" @click="onAction('transfer')">
            转课
          </button>
          <button class="mini-btn" @click="onAction('detail')">
            课时明细
          </button>
        </view>
      </view>
    </view>

    <!-- 上课记录 -->
    <view v-else-if="activeTab === 'records'" class="tab-pane">
      <view class="list-card">
        <view v-for="r in records" :key="r.id" class="list-row">
          <text class="row-date">
            {{ r.date }}
          </text>
          <text class="row-main">
            {{ r.course }}
          </text>
          <text class="state" :class="r.statusClass">
            {{ r.status }}
          </text>
        </view>
      </view>
    </view>

    <!-- 错题 -->
    <view v-else-if="activeTab === 'wrong'" class="tab-pane">
      <view v-for="w in wrongList" :key="w.id" class="wrong-card">
        <view class="wrong-thumb">
          <uni-icons type="image" size="24" color="#9aa5aa" />
        </view>
        <view class="wrong-main">
          <view class="wrong-title">
            {{ w.subject }} · {{ w.point }}
          </view>
          <view class="wrong-sub">
            {{ w.date }} 更新
          </view>
        </view>
        <text class="state" :class="w.masteryClass">
          {{ w.mastery }}
        </text>
      </view>
    </view>

    <!-- 消费 -->
    <view v-else class="tab-pane">
      <view class="list-card">
        <view v-for="item in consumes" :key="item.id" class="consume-row">
          <view>
            <view class="consume-title">
              {{ item.title }}
            </view>
            <view class="consume-date">
              {{ item.date }} · {{ item.type }}
            </view>
          </view>
          <text class="consume-amount">
            {{ item.unit ? `${item.amount} ${item.unit}` : `¥${Math.abs(item.amount)}` }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 60rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.hero-card {
  padding: 30rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
  box-shadow: 0 18rpx 38rpx rgba(25, 63, 54, 0.16);
}

.hero-top {
  display: flex;
  gap: 22rpx;
  align-items: center;
}

.hero-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.16);
  border-radius: 22rpx;
}

.hero-name {
  font-size: 40rpx;
  font-weight: 700;
}

.hero-meta {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.74);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 22rpx;
}

.hero-tag {
  padding: 6rpx 16rpx;
  font-size: 22rpx;
  color: #a4f2d4;
  background: rgba(42, 157, 115, 0.28);
  border-radius: 999rpx;
}

.hero-foot {
  display: flex;
  gap: 30rpx;
  margin-top: 22rpx;
  font-size: 23rpx;
  color: rgba(255, 255, 255, 0.7);
}

.quick-row {
  display: flex;
  justify-content: space-between;
  margin-top: 22rpx;
  padding: 26rpx 16rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.quick-item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.quick-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 80rpx;
  background: #e6f4ee;
  border-radius: 22rpx;
}

.quick-label {
  font-size: 22rpx;
  color: #5d6a70;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.metric-item {
  padding: 22rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.metric-value {
  font-size: 38rpx;
  font-weight: 700;
  color: #183a34;
}

.metric-value.low {
  color: #c0392b;
}

.metric-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #718088;
}

.tab-scroll {
  margin: 26rpx -28rpx 18rpx;
  white-space: nowrap;
}

.tab-row {
  display: flex;
  gap: 30rpx;
  padding: 0 28rpx;
}

.tab-item {
  position: relative;
  padding: 12rpx 0;
  font-size: 28rpx;
  color: #67757c;
}

.tab-item.active {
  font-weight: 700;
  color: #1f7159;
}

.tab-item.active::after {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 40rpx;
  height: 6rpx;
  content: '';
  background: #1f7159;
  border-radius: 999rpx;
  transform: translateX(-50%);
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.risk-card {
  padding: 24rpx;
  background: #fff5f4;
  border: 1rpx solid #f6d6d2;
  border-radius: 14rpx;
}

.risk-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #9a3b33;
}

.risk-item {
  display: flex;
  gap: 8rpx;
  align-items: center;
  margin-top: 12rpx;
  font-size: 25rpx;
  color: #8a4a44;
}

.info-card,
.list-card {
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.card-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #1f2d33;
}

.card-title.mt {
  margin-top: 24rpx;
}

.info-line {
  margin-top: 12rpx;
  font-size: 25rpx;
  color: #75838a;
}

.state {
  padding: 5rpx 14rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.state.present {
  color: #227253;
  background: #e9f6ef;
}

.state.late {
  color: #8a671b;
  background: #fff5d8;
}

.state.absent,
.state.danger {
  color: #9a3b33;
  background: #ffeceb;
}

.state.leave,
.state.info {
  color: #335d9a;
  background: #eaf1ff;
}

.state.warn {
  color: #8a671b;
  background: #fff5d8;
}

.state.muted {
  color: #5d6a70;
  background: #eef2f0;
}

.course-card {
  padding: 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.course-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.course-name {
  font-size: 30rpx;
  font-weight: 700;
}

.course-status {
  padding: 5rpx 14rpx;
  font-size: 22rpx;
  border-radius: 999rpx;
}

.course-status.present {
  color: #227253;
  background: #e9f6ef;
}

.course-status.muted {
  color: #5d6a70;
  background: #eef2f0;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  margin-top: 22rpx;
  text-align: center;
}

.cg-num {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #183a34;
}

.cg-num.sm {
  font-size: 24rpx;
}

.cg-num.low {
  color: #c0392b;
}

.cg-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #718088;
}

.course-actions {
  display: flex;
  gap: 12rpx;
  margin-top: 24rpx;
  padding-top: 22rpx;
  border-top: 1rpx solid #edf1ef;
}

.mini-btn {
  flex: 1;
  padding: 0;
  margin: 0;
  font-size: 25rpx;
  line-height: 64rpx;
  color: #1f7159;
  background: #eef2f0;
  border-radius: 12rpx;
}

.mini-btn::after {
  border: 0;
}

.mini-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.list-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.list-row:last-child {
  border-bottom: 0;
}

.row-date {
  flex-shrink: 0;
  width: 90rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #1d463d;
}

.row-main {
  flex: 1;
  font-size: 26rpx;
  color: #4a565c;
}

.wrong-card {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 22rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.wrong-thumb {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  background: #f1f4f2;
  border-radius: 12rpx;
}

.wrong-main {
  flex: 1;
  min-width: 0;
}

.wrong-title {
  font-size: 28rpx;
  font-weight: 600;
}

.wrong-sub {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #839099;
}

.consume-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.consume-row:last-child {
  border-bottom: 0;
}

.consume-title {
  font-size: 27rpx;
  font-weight: 600;
}

.consume-date {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #839099;
}

.consume-amount {
  font-size: 28rpx;
  font-weight: 700;
  color: #c0392b;
}
</style>
