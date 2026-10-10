<template>
  <div>
    <el-row :gutter="10" class="mb8" align="middle">
      <el-col :span="6">
        <el-select v-model="venueId" placeholder="请选择场馆" style="width: 100%" @change="loadAll">
          <el-option v-for="venue in venues" :key="venue.id" :label="venue.venueName" :value="venue.id" />
        </el-select>
      </el-col>
      <el-col :span="18">
        <el-radio-group v-model="bookingDate" @change="loadAll">
          <el-radio-button v-for="day in weekDates" :key="day.value" :value="day.value">
            {{ day.label }} {{ day.value.slice(5) }}
          </el-radio-button>
        </el-radio-group>
        <el-date-picker v-model="bookingDate" type="date" value-format="YYYY-MM-DD" :clearable="false" class="ml8" style="width: 150px" @change="loadAll" />
        <el-select v-model="step" class="ml8" style="width: 110px" @change="clearSelection">
          <el-option label="每格1小时" :value="60" />
          <el-option label="每格半小时" :value="30" />
        </el-select>
      </el-col>
    </el-row>

    <div class="legend">
      <span><i class="legend__dot is-available" />可约</span>
      <span><i class="legend__dot is-booked" />已预订</span>
      <span><i class="legend__dot is-locked" />已锁场</span>
      <span><i class="legend__dot is-closed" />不可约</span>
      <span><i class="legend__dot is-selected" />已选中</span>
      <span class="legend__tip">价格为按场地价格/分时规则的估算，下单金额以后端计算为准</span>
    </div>

    <el-empty v-if="!venueId" description="请先在“场地管理”中新建场馆和场地" />
    <div v-else v-loading="loading" class="grid-wrapper">
      <table class="booking-grid">
        <thead>
          <tr>
            <th class="court-col">场地</th>
            <th v-for="cell in timeCells" :key="cell.start">{{ cell.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!courtRows.length">
            <td :colspan="timeCells.length + 1" class="empty">该场馆下暂无启用的场地</td>
          </tr>
          <tr v-for="court in courtRows" :key="court.id">
            <td class="court-col">{{ court.courtName }}</td>
            <td
              v-for="cell in court.cells"
              :key="cell.start"
              :class="['cell', `is-${cell.state}`, { 'is-selected': isSelected(court.id, cell.start) }]"
              :title="cell.title"
              @click="handleCellClick(court, cell)"
            >
              <template v-if="cell.state === 'available'">¥{{ cell.amount }}</template>
              <template v-else-if="cell.state === 'booked'">{{ cell.booking.customerName || '已预订' }}</template>
              <template v-else-if="cell.state === 'locked'">已锁场</template>
              <template v-else>不可约</template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="grid-footer">
      <el-button @click="emit('show-locks')">查看锁场记录</el-button>
      <div>
        <span class="selected-tip">已选择 {{ selected.length }} 个场次</span>
        <el-button type="primary" :disabled="!selected.length" @click="openBooking" v-hasPermi="['teach:venue:add']">代预订</el-button>
        <el-button type="warning" @click="openLock" v-hasPermi="['teach:venue:add']">锁场</el-button>
      </div>
    </div>

    <booking-dialog v-model="bookingOpen" :courts="grid.courts || []" :preset="preset" @success="loadAll" />
    <lock-dialog v-model="lockOpen" :courts="grid.courts || []" :preset="preset" @success="loadAll" />
    <booking-detail-dialog v-model="detailOpen" :booking-id="detailId" @changed="loadAll" />
  </div>
</template>

<script setup>
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { getBookingGrid, listBooking, listCourt, listVenue } from '@/api/teach/venue'
import { estimateAmount, fromMinutes, toMinutes, weekLabel } from '../utils'
import BookingDialog from './BookingDialog'
import LockDialog from './LockDialog'
import BookingDetailDialog from './BookingDetailDialog'

const emit = defineEmits(['show-locks'])
const { proxy } = getCurrentInstance()

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const venues = ref([])
const venueId = ref()
const bookingDate = ref(formatDate(new Date()))
const step = ref(60)
const loading = ref(false)
const grid = ref({ courts: [] })
const courtDetails = ref([])
const bookings = ref([])
const selected = ref([])

const weekDates = computed(() => {
  const today = new Date()
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today)
    date.setDate(today.getDate() + index)
    const weekDay = date.getDay() === 0 ? 7 : date.getDay()
    return { value: formatDate(date), label: index === 0 ? '今天' : weekLabel(weekDay) }
  })
})

const weekDay = computed(() => {
  const date = new Date(`${bookingDate.value}T00:00:00`)
  return date.getDay() === 0 ? 7 : date.getDay()
})

// 时间轴：取当天所有场地可约时段的最早开始与最晚结束；均未配置时默认 08:00-22:00
const timeCells = computed(() => {
  let start = Infinity
  let end = -Infinity
  ;(grid.value.courts || []).forEach(court => {
    ;(court.slots || []).forEach(slot => {
      start = Math.min(start, toMinutes(slot.startTime))
      end = Math.max(end, toMinutes(slot.endTime))
    })
  })
  if (!Number.isFinite(start)) {
    start = 8 * 60
    end = 22 * 60
  }
  start = Math.floor(start / step.value) * step.value
  const cells = []
  for (let minute = start; minute < end; minute += step.value) {
    cells.push({ start: minute, end: Math.min(minute + step.value, 24 * 60), label: fromMinutes(minute) })
  }
  return cells
})

const courtRows = computed(() => {
  const detailMap = new Map(courtDetails.value.map(court => [court.id, court]))
  return (grid.value.courts || []).map(court => {
    const detail = detailMap.get(court.courtId) || {}
    const hasTimes = (detail.times || []).length > 0
    const openSlots = (court.slots || []).map(slot => [toMinutes(slot.startTime), toMinutes(slot.endTime)])
    const courtBookings = bookings.value.filter(item => item.courtId === court.courtId)
    const cells = timeCells.value.map(cell => {
      const booking = courtBookings.find(item => toMinutes(item.startTime) < cell.end && toMinutes(item.endTime) > cell.start)
      if (booking) {
        const state = booking.bookingType === 'lock' ? 'locked' : 'booked'
        return { ...cell, state, booking, title: `${booking.startTime}-${booking.endTime} ${booking.bookingTypeName || ''} ${booking.customerName || ''}` }
      }
      const open = !hasTimes || openSlots.some(([s, e]) => s <= cell.start && e >= cell.end)
      if (!open) return { ...cell, state: 'closed', title: '不在可约时段内' }
      const amount = estimateAmount(court, court.priceRules || [], fromMinutes(cell.start), fromMinutes(cell.end))
      return { ...cell, state: 'available', amount, title: `${fromMinutes(cell.start)}-${fromMinutes(cell.end)} 约 ¥${amount}` }
    })
    return { id: court.courtId, courtName: court.courtName, cells }
  })
})

async function loadVenues() {
  const res = await listVenue({ pageNum: 1, pageSize: 100, status: 1 })
  venues.value = res.rows || []
  if (!venues.value.some(item => item.id === venueId.value)) {
    venueId.value = venues.value[0]?.id
  }
}

async function loadAll() {
  clearSelection()
  if (!venueId.value) return
  loading.value = true
  try {
    const [gridRes, courtRes, bookingRes] = await Promise.all([
      getBookingGrid({ venueId: venueId.value, date: bookingDate.value }),
      listCourt({ venueId: venueId.value, status: 1 }),
      listBooking({ pageNum: 1, pageSize: 1000, venueId: venueId.value, bookingDate: bookingDate.value })
    ])
    grid.value = gridRes.data || { courts: [] }
    courtDetails.value = courtRes.data || []
    bookings.value = (bookingRes.rows || []).filter(item => [1, 2].includes(item.bookingStatus))
  } finally {
    loading.value = false
  }
}

function clearSelection() {
  selected.value = []
}

function isSelected(courtId, start) {
  return selected.value.some(item => item.courtId === courtId && item.start === start)
}

function handleCellClick(court, cell) {
  if (cell.state === 'booked' || cell.state === 'locked') {
    detailId.value = cell.booking.id
    detailOpen.value = true
    return
  }
  if (cell.state !== 'available') return
  const index = selected.value.findIndex(item => item.courtId === court.id && item.start === cell.start)
  if (index >= 0) {
    selected.value.splice(index, 1)
  } else {
    selected.value.push({ courtId: court.id, start: cell.start, end: cell.end })
  }
}

const bookingOpen = ref(false)
const lockOpen = ref(false)
const detailOpen = ref(false)
const detailId = ref()
const preset = ref({})

function selectionRange() {
  const start = Math.min(...selected.value.map(item => item.start))
  const end = Math.max(...selected.value.map(item => item.end))
  return { startTime: fromMinutes(start), endTime: fromMinutes(end) }
}

function openBooking() {
  const courtIds = [...new Set(selected.value.map(item => item.courtId))]
  if (courtIds.length !== 1) {
    proxy.$modal.msgWarning('代预订一次只能选择同一场地的场次')
    return
  }
  const starts = selected.value.map(item => item.start).sort((a, b) => a - b)
  const contiguous = starts.every((value, index) => index === 0 || value - starts[index - 1] === step.value)
  if (!contiguous) {
    proxy.$modal.msgWarning('请选择连续的时间段')
    return
  }
  preset.value = { courtId: courtIds[0], bookingDate: bookingDate.value, ...selectionRange() }
  bookingOpen.value = true
}

function openLock() {
  preset.value = selected.value.length
    ? { courtIds: [...new Set(selected.value.map(item => item.courtId))], bookingDate: bookingDate.value, ...selectionRange() }
    : { courtIds: [], bookingDate: bookingDate.value }
  lockOpen.value = true
}

async function reload() {
  await loadVenues()
  await loadAll()
}

defineExpose({ reload })

onMounted(reload)
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}

.ml8 {
  margin-left: 8px;
}

.legend {
  display: flex;
  gap: 16px;
  align-items: center;
  margin: 8px 0;
  font-size: 12px;
  color: var(--el-text-color-regular);

  &__dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    margin-right: 4px;
    vertical-align: -2px;
    border: 1px solid var(--el-border-color);

    &.is-available { background: var(--el-bg-color); }
    &.is-booked { background: var(--el-color-primary-light-8); }
    &.is-locked { background: var(--el-color-info-light-5); }
    &.is-closed { background: var(--el-fill-color); }
    &.is-selected { background: var(--el-color-warning); }
  }

  &__tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
  }
}

.grid-wrapper {
  overflow-x: auto;
}

.booking-grid {
  border-collapse: collapse;
  min-width: 100%;
  font-size: 12px;

  th,
  td {
    min-width: 72px;
    height: 44px;
    padding: 0 4px;
    text-align: center;
    border: 1px solid var(--el-border-color-lighter);
    white-space: nowrap;
  }

  th {
    background: var(--el-fill-color-light);
    font-weight: 500;
  }

  .court-col {
    position: sticky;
    left: 0;
    min-width: 110px;
    background: var(--el-bg-color);
    font-weight: 500;
    z-index: 1;
  }

  .empty {
    color: var(--el-text-color-secondary);
  }

  .cell {
    cursor: default;

    &.is-available {
      cursor: pointer;

      &:hover { background: var(--el-color-warning-light-9); }
    }

    &.is-booked {
      cursor: pointer;
      background: var(--el-color-primary-light-8);
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 72px;
    }

    &.is-locked {
      cursor: pointer;
      background: var(--el-color-info-light-5);
      color: var(--el-color-white);
    }

    &.is-closed {
      background: var(--el-fill-color);
      color: var(--el-text-color-placeholder);
    }

    &.is-selected {
      background: var(--el-color-warning);
      color: var(--el-color-white);
    }
  }
}

.grid-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.selected-tip {
  margin-right: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
