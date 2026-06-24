<script lang="ts" setup>
import { computed, ref } from 'vue'

defineOptions({
  name: 'ScheduleCreate',
})
definePage({
  style: {
    navigationBarTitleText: '新增排课',
  },
})

type Mode = 'single' | 'rule' | 'calendar'
const step = ref<'mode' | 'form'>('mode')
const mode = ref<Mode>('single')

const modeCards = [
  { key: 'single' as Mode, title: '单次排课', desc: '只生成一节课', scene: '临时课 / 补课 / 体验课', icon: 'calendar' },
  { key: 'rule' as Mode, title: '规则排课', desc: '按每天/隔天/每周/隔周批量生成', scene: '常规班级课', icon: 'loop' },
  { key: 'calendar' as Mode, title: '日历排课', desc: '在月历上多选日期', scene: '不规则但已确定日期', icon: 'calendar-filled' },
]

const commonTimes = ['08:00-09:00', '10:00-11:30', '14:00-15:30', '18:30-20:00']

// 公共字段
const form = ref({
  course: '',
  className: '',
  teacher: '',
  room: '',
  date: '',
  start: '',
  end: '',
  content: '',
  remark: '',
})

// 规则排课
const repeatOptions = ['每天重复', '隔天重复', '每周重复', '隔周重复']
const repeatIndex = ref(2)
const ruleStartDate = ref('')
const ruleSlots = ref<{ week: string, time: string }[]>([
  { week: '周一', time: '18:30-20:00' },
  { week: '周三', time: '18:30-20:00' },
])
const endTypeOptions = ['按次数结束', '按日期结束']
const endTypeIndex = ref(0)
const ruleCount = ref(12)

// 日历排课
const calendarDays = Array.from({ length: 30 }, (_, i) => i + 1)
const selectedDays = ref<number[]>([3, 5, 10, 12])
const todayDay = 24

const ruleSelected = computed(() => mode.value === 'rule')
const estimateCount = computed(() => {
  if (mode.value === 'rule')
    return endTypeIndex.value === 0 ? ruleCount.value : ruleSlots.value.length * 4
  if (mode.value === 'calendar')
    return selectedDays.value.length
  return 1
})

function chooseMode(m: Mode) {
  mode.value = m
}

function goForm() {
  step.value = 'form'
}

function backMode() {
  step.value = 'mode'
}

function applyCommonTime(t: string) {
  const [s, e] = t.split('-')
  form.value.start = s
  form.value.end = e
}

function onDateChange(e: any) {
  form.value.date = e.detail.value
}

function onRuleStartChange(e: any) {
  ruleStartDate.value = e.detail.value
}

function onRepeatChange(e: any) {
  repeatIndex.value = e.detail.value
}

function onEndTypeChange(e: any) {
  endTypeIndex.value = e.detail.value
}

function addSlot() {
  ruleSlots.value.push({ week: '周五', time: '18:30-20:00' })
}

function removeSlot(idx: number) {
  ruleSlots.value.splice(idx, 1)
}

function toggleDay(d: number) {
  const i = selectedDays.value.indexOf(d)
  if (i >= 0)
    selectedDays.value.splice(i, 1)
  else
    selectedDays.value.push(d)
}

function clearDays() {
  selectedDays.value = []
}

function checkConflict() {
  uni.navigateTo({ url: '/pages/schedule/conflict' })
}

function save() {
  uni.showToast({ title: `已生成 ${estimateCount.value} 节课`, icon: 'success' })
  setTimeout(() => uni.navigateBack(), 700)
}
</script>

<template>
  <view class="sc-page">
    <!-- 模式选择 -->
    <template v-if="step === 'mode'">
      <view class="mode-list">
        <view
          v-for="m in modeCards"
          :key="m.key"
          class="mode-card"
          :class="{ active: mode === m.key }"
          @click="chooseMode(m.key)"
        >
          <view class="mode-icon">
            <uni-icons :type="m.icon" size="24" :color="mode === m.key ? '#1f7159' : '#8a969d'" />
          </view>
          <view class="mode-main">
            <view class="mode-title">
              {{ m.title }}
            </view>
            <view class="mode-desc">
              {{ m.desc }}
            </view>
            <view class="mode-scene">
              {{ m.scene }}
            </view>
          </view>
          <view class="mode-radio" :class="{ on: mode === m.key }">
            <uni-icons v-if="mode === m.key" type="checkmarkempty" size="16" color="#ffffff" />
          </view>
        </view>
      </view>
      <view class="bottom-bar">
        <button class="primary-btn" @click="goForm">
          下一步
        </button>
      </view>
    </template>

    <!-- 表单 -->
    <template v-else>
      <view class="mode-tip">
        <text>{{ modeCards.find(m => m.key === mode)?.title }}</text>
        <text class="mode-tip-link" @click="backMode">
          切换模式
        </text>
      </view>

      <!-- 公共：课程/班级 -->
      <view class="form-card">
        <view class="row" @click="form.course = '数学提高'">
          <text class="row-label">
            课程
          </text>
          <view class="row-value" :class="{ ph: !form.course }">
            {{ form.course || '请选择课程' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
        <view class="row no-border" @click="form.className = 'A班'">
          <text class="row-label">
            班级
          </text>
          <view class="row-value" :class="{ ph: !form.className }">
            {{ form.className || '请选择班级' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
      </view>

      <!-- 单次排课 -->
      <template v-if="mode === 'single'">
        <view class="form-card">
          <picker mode="date" :value="form.date" @change="onDateChange">
            <view class="row">
              <text class="row-label">
                日期
              </text>
              <view class="row-value" :class="{ ph: !form.date }">
                {{ form.date || '请选择日期' }}
                <uni-icons type="right" size="15" color="#9aa5aa" />
              </view>
            </view>
          </picker>
          <view class="row no-border">
            <text class="row-label">
              时间
            </text>
            <view class="row-value" :class="{ ph: !form.start }">
              {{ form.start && form.end ? `${form.start} - ${form.end}` : '选择常用时间段' }}
            </view>
          </view>
          <view class="time-chips">
            <view
              v-for="t in commonTimes"
              :key="t"
              class="time-chip"
              :class="{ active: `${form.start}-${form.end}` === t }"
              @click="applyCommonTime(t)"
            >
              {{ t }}
            </view>
          </view>
        </view>
      </template>

      <!-- 规则排课 -->
      <template v-else-if="mode === 'rule'">
        <view class="form-card">
          <picker mode="date" :value="ruleStartDate" @change="onRuleStartChange">
            <view class="row">
              <text class="row-label">
                开始日期
              </text>
              <view class="row-value" :class="{ ph: !ruleStartDate }">
                {{ ruleStartDate || '请选择' }}
                <uni-icons type="right" size="15" color="#9aa5aa" />
              </view>
            </view>
          </picker>
          <picker :value="repeatIndex" :range="repeatOptions" @change="onRepeatChange">
            <view class="row no-border">
              <text class="row-label">
                重复方式
              </text>
              <view class="row-value">
                {{ repeatOptions[repeatIndex] }}
                <uni-icons type="right" size="15" color="#9aa5aa" />
              </view>
            </view>
          </picker>
        </view>

        <view class="form-card">
          <view class="card-head-row">
            <text class="row-label">
              星期 + 时间段
            </text>
            <text class="add-link" @click="addSlot">
              + 添加时间段
            </text>
          </view>
          <view v-for="(slot, idx) in ruleSlots" :key="idx" class="slot-row">
            <text class="slot-week">
              {{ slot.week }}
            </text>
            <text class="slot-time">
              {{ slot.time }}
            </text>
            <uni-icons type="trash" size="18" color="#c0392b" @click="removeSlot(idx)" />
          </view>
        </view>

        <view class="form-card">
          <picker :value="endTypeIndex" :range="endTypeOptions" @change="onEndTypeChange">
            <view class="row" :class="{ 'no-border': endTypeIndex !== 0 }">
              <text class="row-label">
                结束方式
              </text>
              <view class="row-value">
                {{ endTypeOptions[endTypeIndex] }}
                <uni-icons type="right" size="15" color="#9aa5aa" />
              </view>
            </view>
          </picker>
          <view v-if="endTypeIndex === 0" class="row no-border">
            <text class="row-label">
              排课次数
            </text>
            <input v-model.number="ruleCount" type="number" class="row-input" placeholder="12">
          </view>
        </view>
      </template>

      <!-- 日历排课 -->
      <template v-else>
        <view class="form-card">
          <view class="cal-head">
            <uni-icons type="left" size="16" color="#74828a" />
            <text>2026年6月</text>
            <uni-icons type="right" size="16" color="#74828a" />
          </view>
          <view class="cal-week">
            <text v-for="w in ['日', '一', '二', '三', '四', '五', '六']" :key="w">{{ w }}</text>
          </view>
          <view class="cal-grid">
            <view
              v-for="d in calendarDays"
              :key="d"
              class="cal-day"
              :class="{ on: selectedDays.includes(d), today: d === todayDay }"
              @click="toggleDay(d)"
            >
              {{ d }}
            </view>
          </view>
        </view>
        <view class="form-card">
          <view class="card-head-row">
            <text class="row-label">
              已选 {{ selectedDays.length }} 天
            </text>
            <text class="add-link danger" @click="clearDays">
              清空
            </text>
          </view>
          <view class="day-chips">
            <view v-for="d in selectedDays" :key="d" class="day-chip">
              6月{{ d }}日
            </view>
          </view>
        </view>
      </template>

      <!-- 公共：老师/教室/内容 -->
      <view class="form-card">
        <view class="row" @click="form.teacher = '王老师'">
          <text class="row-label">
            上课老师
          </text>
          <view class="row-value" :class="{ ph: !form.teacher }">
            {{ form.teacher || '请选择' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
        <view class="row" @click="form.room = '301教室'">
          <text class="row-label">
            上课教室
          </text>
          <view class="row-value" :class="{ ph: !form.room }">
            {{ form.room || '请选择' }}
            <uni-icons type="right" size="15" color="#9aa5aa" />
          </view>
        </view>
        <view class="row no-border column">
          <text class="row-label">
            上课内容
          </text>
          <input v-model="form.content" class="full-input" placeholder="本节课内容（可选）">
        </view>
      </view>

      <!-- 预览 -->
      <view v-if="mode !== 'single'" class="preview-card">
        <view class="preview-num">
          预计生成 <text class="num">{{ estimateCount }}</text> 节课
        </view>
        <view class="preview-list">
          <text>· 06月25日 18:30-20:00</text>
          <text>· 06月27日 18:30-20:00</text>
          <text>· 06月30日 18:30-20:00</text>
        </view>
        <text class="preview-all">
          查看全部预览
        </text>
      </view>

      <view class="bottom-bar two">
        <button class="ghost-btn" @click="checkConflict">
          检查冲突
        </button>
        <button class="primary-btn" @click="save">
          {{ mode === 'single' ? '保存排课' : '生成排课' }}
        </button>
      </view>
    </template>
  </view>
</template>

<style lang="scss" scoped>
.sc-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 180rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

/* 模式卡 */
.mode-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.mode-card {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 28rpx;
  background: #ffffff;
  border: 2rpx solid #e7ece9;
  border-radius: 16rpx;
}

.mode-card.active {
  border-color: #1f7159;
  background: #f3faf7;
}

.mode-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 84rpx;
  height: 84rpx;
  background: #eef2f0;
  border-radius: 20rpx;
}

.mode-card.active .mode-icon {
  background: #e6f4ee;
}

.mode-main {
  flex: 1;
  min-width: 0;
}

.mode-title {
  font-size: 31rpx;
  font-weight: 700;
}

.mode-desc {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #75838a;
}

.mode-scene {
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #9aa5aa;
}

.mode-radio {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #cfd9d4;
  border-radius: 50%;
}

.mode-radio.on {
  background: #1f7159;
  border-color: #1f7159;
}

/* 表单 */
.mode-tip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
  font-size: 27rpx;
  font-weight: 700;
}

.mode-tip-link {
  font-size: 25rpx;
  font-weight: 400;
  color: #1d8b69;
}

.form-card {
  margin-bottom: 16rpx;
  padding: 0 26rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
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

.row.column {
  display: block;
  padding: 22rpx 0;
}

.row-label {
  font-size: 27rpx;
  color: #4a565c;
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
  font-size: 27rpx;
  text-align: right;
}

.full-input {
  width: 100%;
  margin-top: 16rpx;
  padding: 18rpx 20rpx;
  font-size: 27rpx;
  background: #f6f8f7;
  border-radius: 12rpx;
}

.time-chips,
.day-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  padding: 0 0 24rpx;
}

.time-chip {
  padding: 12rpx 22rpx;
  font-size: 24rpx;
  color: #67757c;
  background: #f1f4f2;
  border-radius: 999rpx;
}

.time-chip.active {
  color: #ffffff;
  background: #1f7159;
}

.card-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0 16rpx;
}

.add-link {
  font-size: 25rpx;
  color: #1d8b69;
}

.add-link.danger {
  color: #c0392b;
}

.slot-row {
  display: flex;
  gap: 18rpx;
  align-items: center;
  padding: 18rpx 0;
  border-top: 1rpx solid #edf1ef;
}

.slot-week {
  flex-shrink: 0;
  width: 90rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.slot-time {
  flex: 1;
  font-size: 26rpx;
  color: #4a565c;
}

.day-chip {
  padding: 10rpx 18rpx;
  font-size: 23rpx;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 999rpx;
}

/* 日历 */
.cal-head {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40rpx;
  padding: 24rpx 0 18rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.cal-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding-bottom: 12rpx;
  font-size: 22rpx;
  color: #9aa5aa;
  text-align: center;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8rpx;
  padding-bottom: 22rpx;
}

.cal-day {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 72rpx;
  font-size: 26rpx;
  color: #3d484e;
  border-radius: 50%;
}

.cal-day.today {
  border: 2rpx solid #2a9d73;
}

.cal-day.on {
  color: #ffffff;
  background: #1f7159;
}

/* 预览 */
.preview-card {
  margin-bottom: 16rpx;
  padding: 26rpx;
  background: #f3faf7;
  border: 1rpx solid #c7e6d8;
  border-radius: 16rpx;
}

.preview-num {
  font-size: 27rpx;
  color: #2d4a42;
}

.preview-num .num {
  font-size: 36rpx;
  font-weight: 700;
  color: #1f7159;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #5a6a64;
}

.preview-all {
  display: inline-block;
  margin-top: 16rpx;
  font-size: 25rpx;
  color: #1d8b69;
}

/* 底部 */
.bottom-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 16rpx;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1rpx solid #eef1ef;
}

.ghost-btn,
.primary-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  line-height: 90rpx;
  border-radius: 16rpx;
}

.ghost-btn {
  color: #1f7159;
  background: #e6f4ee;
}

.primary-btn {
  font-weight: 600;
  color: #ffffff;
  background: #1f7159;
}

.ghost-btn::after,
.primary-btn::after {
  border: 0;
}
</style>
