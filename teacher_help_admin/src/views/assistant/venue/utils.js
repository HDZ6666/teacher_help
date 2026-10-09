// 场地管理页面公共方法（仅用于展示；金额以后端计算为准）

export const WEEK_OPTIONS = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
]

export const BOOKING_STATUS = { 1: '已预订', 2: '已核销', 3: '已取消' }
export const PAY_STATUS = { 0: '未付', 1: '已付', 2: '已退' }

export function weekLabel(day) {
  return WEEK_OPTIONS.find(item => item.value === Number(day))?.label || `星期${day}`
}

export function toMinutes(value) {
  if (!value) return 0
  const [hour, minute] = String(value).split(':')
  return Number(hour) * 60 + Number(minute || 0)
}

export function fromMinutes(minutes) {
  const hour = Math.floor(minutes / 60)
  const minute = minutes % 60
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
}

/**
 * 后端按“每个星期一行”存储时段/价格规则，表单里按“同一时段+价格，多选星期”展示
 * @param {Array} rows 后端行
 * @param {Array} keys 用于合并的字段
 */
export function groupByWeekdays(rows = [], keys = ['startTime', 'endTime']) {
  const map = new Map()
  rows.forEach(row => {
    const key = keys.map(field => String(row[field] ?? '')).join('|')
    if (!map.has(key)) {
      const group = { weekDays: [] }
      keys.forEach(field => {
        group[field] = row[field]
      })
      map.set(key, group)
    }
    map.get(key).weekDays.push(Number(row.weekDay))
  })
  return Array.from(map.values()).map(group => ({ ...group, weekDays: group.weekDays.sort() }))
}

export function expandWeekdays(groups = [], keys = ['startTime', 'endTime']) {
  const rows = []
  groups.forEach(group => {
    ;(group.weekDays || []).forEach(weekDay => {
      const row = { weekDay }
      keys.forEach(field => {
        row[field] = group[field]
      })
      rows.push(row)
    })
  })
  return rows
}

function segmentPrice(halfPrice, hourPrice, minutes) {
  const half = Number(halfPrice || 0)
  const hour = Number(hourPrice || 0)
  if (half > 0) return (half * minutes) / 30
  if (hour > 0) return (hour * minutes) / 60
  return 0
}

/**
 * 估算价格（与后端 TeachVenueService.calc_booking_amount 规则一致，仅用于订场日历展示）
 */
export function estimateAmount(court, rules = [], startTime, endTime) {
  const start = toMinutes(startTime)
  const end = toMinutes(endTime)
  const windows = rules
    .map(rule => ({ rule, s: Math.max(start, toMinutes(rule.startTime)), e: Math.min(end, toMinutes(rule.endTime)) }))
    .filter(item => item.s < item.e)
    .sort((a, b) => a.s - b.s)
  const segments = []
  let cursor = start
  windows.forEach(({ rule, s, e }) => {
    const from = Math.max(s, cursor)
    if (from >= e) return
    if (cursor < from) segments.push([cursor, from, court.pricePerHalfHour, court.pricePerHour])
    segments.push([from, e, rule.pricePerHalfHour, rule.pricePerHour])
    cursor = e
  })
  if (cursor < end) segments.push([cursor, end, court.pricePerHalfHour, court.pricePerHour])
  let amount = segments.reduce((sum, [s, e, half, hour]) => sum + segmentPrice(half, hour, e - s), 0)
  if (segments.length) {
    const last = segments[segments.length - 1]
    const remainder = (end - start) % 30
    if (Number(last[2] || 0) > 0 && remainder) amount += (Number(last[2]) * (30 - remainder)) / 30
  }
  return Math.round(amount * 100) / 100
}
