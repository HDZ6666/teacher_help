<script lang="ts" setup>
import type { AttendanceStat, AttendanceStatus } from '@/api/teach/attendance'
import type { ScheduleEvent, ScheduleStudent } from '@/api/teach/schedule'
import { onLoad, onPullDownRefresh } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'
import { batchManualAttendance, getAttendanceStat, manualAttendance } from '@/api/teach/attendance'
import { finishScheduleEvent, getScheduleEvent } from '@/api/teach/schedule'

type StudentFilter = 'all' | 'pending' | 'processed'

definePage({
  style: {
    navigationBarTitleText: '点名',
    enablePullDownRefresh: true,
  },
})

const eventId = ref(0)
const loading = ref(false)
const batchUpdating = ref(false)
const updatingStudentIds = ref<Set<number>>(new Set())
const studentFilter = ref<StudentFilter>('pending')
const eventDetail = ref<ScheduleEvent | null>(null)
const stat = ref<AttendanceStat | null>(null)
const loadError = ref('')

const statusItems: { label: string, value: AttendanceStatus, className: string }[] = [
  { label: '到', value: 1, className: 'present' },
  { label: '迟', value: 2, className: 'late' },
  { label: '假', value: 3, className: 'excused' },
  { label: '缺', value: 4, className: 'absent' },
  { label: '未到', value: 0, className: 'pending' },
]

const students = computed(() => eventDetail.value?.students || [])
const pendingStudents = computed(() => students.value.filter(item => Number(item.status) === 0))
const processedStudents = computed(() => students.value.filter(item => Number(item.status) !== 0))
const visibleStudents = computed(() => {
  if (studentFilter.value === 'pending')
    return pendingStudents.value
  if (studentFilter.value === 'processed')
    return processedStudents.value
  return students.value
})
const courseTitle = computed(() => eventDetail.value?.courseName || eventDetail.value?.subjectName || eventDetail.value?.subjectCode || '课程点名')
const attendanceRate = computed(() => stat.value?.attendanceRate ?? eventDetail.value?.cachedRate ?? 0)
const plannedCount = computed(() => stat.value?.planned ?? eventDetail.value?.cachedPlanned ?? 0)
const arrivedCount = computed(() => {
  const present = stat.value?.present ?? eventDetail.value?.cachedPresent ?? 0
  const late = stat.value?.late ?? eventDetail.value?.cachedLate ?? 0
  return present + late
})
const isFinished = computed(() => String(eventDetail.value?.status || '') === '2')
const isCancelled = computed(() => String(eventDetail.value?.status || '') === '3')
const isClosed = computed(() => isFinished.value || isCancelled.value)
const isBusy = computed(() => batchUpdating.value || updatingStudentIds.value.size > 0)
const canEditAttendance = computed(() => !isClosed.value && !batchUpdating.value)
const studentFilterOptions = computed<Array<{ label: string, value: StudentFilter, count: number }>>(() => [
  { label: '未到', value: 'pending', count: pendingStudents.value.length },
  { label: '全部', value: 'all', count: students.value.length },
  { label: '已处理', value: 'processed', count: processedStudents.value.length },
])
const emptyStudentText = computed(() => {
  if (!students.value.length)
    return '这节课还没有学生'
  if (studentFilter.value === 'pending')
    return '未到学生已处理完'
  if (studentFilter.value === 'processed')
    return '还没有处理过的学生'
  return '暂无学生'
})

function formatTime(value?: string) {
  if (!value)
    return '--:--'
  const date = new Date(value)
  return `${`${date.getHours()}`.padStart(2, '0')}:${`${date.getMinutes()}`.padStart(2, '0')}`
}

function formatDate(value?: string) {
  if (!value)
    return ''
  const date = new Date(value)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function statusText(status: number) {
  return ['未到', '出勤', '迟到', '请假', '缺勤'][Number(status)] || '未知'
}

function statusClass(status: number) {
  return ['pending', 'present', 'late', 'excused', 'absent'][Number(status)] || 'pending'
}

function studentNote(student: ScheduleStudent) {
  const checkText = student.checkInTime ? `签到 ${formatTime(student.checkInTime)}` : '待确认'
  const noteText = (student.notes || '').trim()
  const prefix = noteText ? `${noteText} · ` : ''
  if (student.remainingCount == null)
    return `${prefix}${checkText} · 无课时账户`
  return `${prefix}${checkText} · 剩余 ${student.remainingCount} 课时`
}

function isLowRemaining(student: ScheduleStudent) {
  return !!student.lowRemaining
}

async function loadDetail() {
  if (!eventId.value) {
    loadError.value = '课次信息不完整'
    return
  }
  loading.value = true
  loadError.value = ''
  try {
    const detailRes = await getScheduleEvent(eventId.value)
    eventDetail.value = detailRes.data
    try {
      const statRes = await getAttendanceStat(eventId.value)
      stat.value = statRes.data
    }
    catch {
      stat.value = null
    }
  }
  catch (error: any) {
    if (!eventDetail.value)
      loadError.value = error?.msg || '加载失败，请重试'
  }
  finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

function setStudentStatusLocal(studentIds: number[], status: AttendanceStatus, notes?: string) {
  if (!eventDetail.value?.students)
    return
  const checkInTime = status === 1 || status === 2 ? new Date().toISOString() : undefined
  eventDetail.value.students = eventDetail.value.students.map((item) => {
    if (!studentIds.includes(item.studentId))
      return item
    return {
      ...item,
      status,
      checkInTime,
      notes: notes ?? item.notes,
    }
  })
}

function setStudentUpdating(studentId: number, value: boolean) {
  const next = new Set(updatingStudentIds.value)
  if (value) {
    next.add(studentId)
  }
  else {
    next.delete(studentId)
  }
  updatingStudentIds.value = next
}

function isStudentUpdating(studentId: number) {
  return updatingStudentIds.value.has(studentId)
}

function setStudentFilter(value: StudentFilter) {
  studentFilter.value = value
}

function getReasonOptions(status: AttendanceStatus) {
  if (status === 3)
    return ['家长请假', '病假', '事假', '不填原因']
  if (status === 4)
    return ['无故缺勤', '临时缺席', '联系不上', '不填原因']
  return []
}

function chooseAttendanceNote(status: AttendanceStatus) {
  const itemList = getReasonOptions(status)
  if (!itemList.length)
    return Promise.resolve('')
  return new Promise<string | null>((resolve) => {
    uni.showActionSheet({
      itemList,
      success: (res) => {
        const selected = itemList[res.tapIndex]
        resolve(selected === '不填原因' ? '' : selected)
      },
      fail: () => resolve(null),
    })
  })
}

async function updateStudentStatus(student: ScheduleStudent, status: AttendanceStatus, quiet = false) {
  if (!eventId.value || !canEditAttendance.value || isStudentUpdating(student.studentId))
    return
  if (Number(student.status) === status)
    return
  const nextNotes = await chooseAttendanceNote(status)
  if (nextNotes === null)
    return
  const previousStatus = Number(student.status) as AttendanceStatus
  const previousCheckInTime = student.checkInTime
  const previousNotes = student.notes
  setStudentUpdating(student.studentId, true)
  setStudentStatusLocal([student.studentId], status, nextNotes)
  try {
    await manualAttendance({
      eventId: eventId.value,
      studentId: student.studentId,
      status,
      notes: nextNotes,
    })
    if (!quiet) {
      uni.showToast({
        title: '已更新',
        icon: 'success',
      })
    }
    await loadDetail()
  }
  catch (error) {
    if (eventDetail.value?.students) {
      eventDetail.value.students = eventDetail.value.students.map((item) => {
        if (item.studentId !== student.studentId)
          return item
        return {
          ...item,
          status: previousStatus,
          checkInTime: previousCheckInTime,
          notes: previousNotes,
        }
      })
    }
  }
  finally {
    setStudentUpdating(student.studentId, false)
  }
}

function runBatch(title: string, targets: ScheduleStudent[], status: AttendanceStatus, notes = '') {
  if (isClosed.value) {
    uni.showToast({
      title: isCancelled.value ? '课次已取消' : '课次已完成',
      icon: 'none',
    })
    return
  }
  if (!targets.length) {
    uni.showToast({
      title: '没有需要处理的学生',
      icon: 'none',
    })
    return
  }
  uni.showModal({
    title,
    content: `将处理 ${targets.length} 名学生`,
    success: async (res) => {
      if (!res.confirm)
        return
      batchUpdating.value = true
      try {
        const res = await batchManualAttendance({
          eventId: eventId.value,
          studentIds: targets.map(item => item.studentId),
          status,
          notes,
        })
        setStudentStatusLocal(targets.map(item => item.studentId), status, notes)
        uni.showToast({
          title: res.msg || `已处理${targets.length}人`,
          icon: 'success',
        })
        await loadDetail()
      }
      finally {
        batchUpdating.value = false
      }
    },
  })
}

function markPendingPresent() {
  runBatch('未到全到', pendingStudents.value, 1, '')
}

function markPendingAbsent() {
  runBatch('未到记缺勤', pendingStudents.value, 4, '未到记缺勤')
}

function finishAttendance() {
  if (!eventId.value || isBusy.value || isClosed.value)
    return
  const pending = pendingStudents.value.length
  const finishConfirmContent = pending
    ? `还有 ${pending} 名学生未到，将自动记为缺勤并完成。`
    : '确认将本节课标记为已完成？'
  uni.showModal({
    title: '完成点名',
    content: finishConfirmContent,
    success: async (res) => {
      if (!res.confirm)
        return
      batchUpdating.value = true
      try {
        if (pendingStudents.value.length) {
          const pendingIds = pendingStudents.value.map(item => item.studentId)
          await batchManualAttendance({
            eventId: eventId.value,
            studentIds: pendingIds,
            status: 4,
            notes: '完成点名自动记缺勤',
          })
          setStudentStatusLocal(pendingIds, 4, '完成点名自动记缺勤')
        }
        await finishScheduleEvent(eventId.value)
        if (eventDetail.value) {
          eventDetail.value.status = '2'
          eventDetail.value.statusName = '已完成'
        }
        uni.showToast({
          title: '已完成',
          icon: 'success',
        })
        await loadDetail()
      }
      catch {
        await loadDetail()
      }
      finally {
        batchUpdating.value = false
      }
    },
  })
}

onLoad((options) => {
  eventId.value = Number(options.id || 0)
  loadDetail()
})

onPullDownRefresh(() => {
  loadDetail()
})
</script>

<template>
  <view class="detail-page">
    <view v-if="loading && !eventDetail" class="state-box">
      加载中...
    </view>
    <view v-else-if="loadError && !eventDetail" class="state-box">
      <view>{{ loadError }}</view>
      <button class="state-action" @click="loadDetail">
        重试
      </button>
    </view>
    <template v-else-if="eventDetail">
      <view class="course-head">
        <view class="head-title">
          {{ courseTitle }}
        </view>
        <view class="head-meta">
          {{ formatDate(eventDetail.startTime) }} {{ formatTime(eventDetail.startTime) }}-{{ formatTime(eventDetail.endTime) }}
        </view>
        <view class="head-meta">
          {{ eventDetail.teacherName || '未分配老师' }}
        </view>
      </view>

      <view class="stat-grid">
        <view class="stat-item">
          <view class="stat-value">
            {{ plannedCount }}
          </view>
          <view class="stat-label">
            应到
          </view>
        </view>
        <view class="stat-item">
          <view class="stat-value">
            {{ arrivedCount }}
          </view>
          <view class="stat-label">
            已到
          </view>
        </view>
        <view class="stat-item">
          <view class="stat-value">
            {{ pendingStudents.length }}
          </view>
          <view class="stat-label">
            未到
          </view>
        </view>
        <view class="stat-item">
          <view class="stat-value">
            {{ attendanceRate }}%
          </view>
          <view class="stat-label">
            出勤率
          </view>
        </view>
      </view>

      <view class="section-title">
        <text>学生名单</text>
        <text class="section-count">
          剩余 {{ pendingStudents.length }} 人
        </text>
      </view>

      <view v-if="isClosed" class="finished-notice" :class="{ cancelled: isCancelled }">
        {{ isCancelled ? '本节课已取消，不能点名。' : '本节课已完成，考勤已锁定。需要更正时请到 PC 管理端处理。' }}
      </view>

      <scroll-view v-if="students.length" class="student-filter-scroll" scroll-x>
        <view class="student-filter-row">
          <button
            v-for="item in studentFilterOptions"
            :key="item.value"
            class="student-filter-btn"
            :class="{ active: studentFilter === item.value }"
            @click="setStudentFilter(item.value)"
          >
            {{ item.label }} {{ item.count }}
          </button>
        </view>
      </scroll-view>

      <view v-if="!visibleStudents.length" class="state-box">
        {{ emptyStudentText }}
      </view>
      <view v-else class="student-list">
        <view v-for="student in visibleStudents" :key="student.studentId" class="student-row">
          <view class="student-head">
            <view class="avatar">
              {{ (student.studentName || '?').slice(0, 1) }}
            </view>
            <view class="student-info">
              <view class="student-name">
                {{ student.studentName }}
              </view>
              <view class="student-note" :class="{ low: isLowRemaining(student) }">
                {{ studentNote(student) }}
              </view>
            </view>
            <view class="status-tag" :class="statusClass(student.status)">
              {{ statusText(student.status) }}
            </view>
          </view>
          <view class="status-actions">
            <button
              v-for="item in statusItems"
              :key="item.value"
              class="status-btn"
              :class="[item.className, { active: Number(student.status) === item.value }]"
              :disabled="isClosed || batchUpdating || isStudentUpdating(student.studentId)"
              @click="updateStudentStatus(student, item.value)"
            >
              <text v-if="isStudentUpdating(student.studentId)">...</text>
              <text v-else>{{ item.label }}</text>
            </button>
          </view>
        </view>
      </view>

      <view class="bottom-actions">
        <button class="batch-btn secondary" :disabled="isBusy || isClosed" @click="markPendingAbsent">
          未到记缺
        </button>
        <button class="batch-btn secondary" :disabled="isBusy || isClosed" @click="markPendingPresent">
          未到全到
        </button>
        <button class="batch-btn primary" :disabled="isBusy || isClosed" @click="finishAttendance">
          {{ batchUpdating ? '处理中...' : isCancelled ? '已取消' : isFinished ? '已完成' : '完成点名' }}
        </button>
      </view>
    </template>
    <view v-else class="state-box">
      没找到这节课
    </view>
  </view>
</template>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 28rpx 170rpx;
  color: #1f2d33;
  background: #f4f6f5;
}

.course-head {
  padding: 32rpx;
  color: #ffffff;
  background: #193f36;
  border-radius: 18rpx;
}

.head-title {
  overflow: hidden;
  font-size: 42rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.head-meta {
  margin-top: 12rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.76);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 18rpx;
}

.stat-item {
  padding: 22rpx 8rpx;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.stat-value {
  font-size: 34rpx;
  font-weight: 700;
  color: #173a33;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #74828a;
}

.section-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 20rpx;
  margin-top: 34rpx;
  margin-bottom: 16rpx;
  font-size: 32rpx;
  font-weight: 700;
}

.section-count {
  flex-shrink: 0;
  font-size: 24rpx;
  font-weight: 500;
  color: #74828a;
}

.finished-notice {
  margin-bottom: 16rpx;
  padding: 18rpx 22rpx;
  font-size: 25rpx;
  line-height: 1.5;
  color: #6f5a19;
  background: #fff7dd;
  border: 1rpx solid #f2dfaa;
  border-radius: 14rpx;
}

.finished-notice.cancelled {
  color: #9a3b33;
  background: #ffeceb;
  border-color: #f3c4bf;
}

.student-filter-scroll {
  margin: 0 -28rpx 18rpx;
  white-space: nowrap;
}

.student-filter-row {
  display: flex;
  gap: 12rpx;
  padding: 0 28rpx;
}

.student-filter-btn {
  padding: 16rpx 22rpx;
  margin: 0;
  font-size: 25rpx;
  line-height: 1;
  color: #607077;
  background: #ffffff;
  border: 1rpx solid #e1e8e4;
  border-radius: 999rpx;
}

.student-filter-btn::after {
  border: 0;
}

.student-filter-btn.active {
  color: #1f7159;
  background: #e6f4ee;
  border-color: #badfce;
}

.state-box {
  padding: 80rpx 0;
  font-size: 28rpx;
  color: #7a858b;
  text-align: center;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 14rpx;
}

.state-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 160rpx;
  height: 64rpx;
  padding: 0;
  margin: 24rpx auto 0;
  font-size: 26rpx;
  line-height: 64rpx;
  color: #ffffff;
  background: #1f7159;
  border-radius: 12rpx;
}

.state-action::after {
  border: 0;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.student-row {
  padding: 24rpx;
  background: #ffffff;
  border: 1rpx solid #e7ece9;
  border-radius: 16rpx;
}

.student-head {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #1f7159;
  background: #e6f4ee;
  border-radius: 50%;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  overflow: hidden;
  font-size: 31rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-note {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #7b8990;
}

.student-note.low {
  color: #a15b15;
}

.status-tag {
  flex-shrink: 0;
  padding: 8rpx 16rpx;
  font-size: 23rpx;
  border-radius: 999rpx;
}

.status-actions {
  display: grid;
  grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
  gap: 8rpx;
  margin-top: 22rpx;
}

.status-btn,
.batch-btn {
  padding: 0;
  margin: 0;
  line-height: 1;
}

.status-btn::after,
.batch-btn::after {
  border: 0;
}

.status-btn {
  height: 64rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #56646b;
  background: #f3f6f5;
  border-radius: 12rpx;
}

.status-btn.active {
  color: #ffffff;
}

.pending,
.status-btn.pending.active {
  color: #6a7379;
  background: #edf0f2;
}

.present,
.status-btn.present.active {
  color: #1f7159;
  background: #e8f5ef;
}

.late,
.status-btn.late.active {
  color: #8a671b;
  background: #fff5d8;
}

.excused,
.status-btn.excused.active {
  color: #335d9a;
  background: #eaf1ff;
}

.absent,
.status-btn.absent.active {
  color: #9a3b33;
  background: #ffeceb;
}

.status-btn.present.active,
.status-btn.pending.active,
.status-btn.late.active,
.status-btn.excused.active,
.status-btn.absent.active {
  color: #ffffff;
}

.status-btn.pending.active {
  background: #68757c;
}

.status-btn.present.active {
  background: #21845f;
}

.status-btn.late.active {
  background: #b98519;
}

.status-btn.excused.active {
  background: #3e6fb0;
}

.status-btn.absent.active {
  background: #b94c43;
}

.bottom-actions {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16rpx;
  padding: 20rpx 28rpx calc(20rpx + env(safe-area-inset-bottom));
  background: rgba(244, 246, 245, 0.96);
  border-top: 1rpx solid #e1e8e4;
}

.batch-btn {
  height: 88rpx;
  font-size: 28rpx;
  font-weight: 700;
  border-radius: 14rpx;
}

.batch-btn.primary {
  color: #ffffff;
  background: #1f7159;
}

.batch-btn.secondary {
  color: #1f7159;
  background: #e6f4ee;
}

.status-btn[disabled],
.batch-btn[disabled] {
  color: #9aa5aa;
  background: #edf1ef;
}

.status-btn.active[disabled] {
  color: #9aa5aa;
  background: #edf1ef;
}
</style>
