/**
 * 排课模块模拟数据
 * 用于前端开发测试，后端接口开发完成后可删除
 */

// 模拟教师列表
export const mockTeachers = [
  { id: 1, teacherName: '张老师', phone: '13800138001' },
  { id: 2, teacherName: '李老师', phone: '13800138002' },
  { id: 3, teacherName: '王老师', phone: '13800138003' },
  { id: 4, teacherName: '刘老师', phone: '13800138004' },
  { id: 5, teacherName: '陈老师', phone: '13800138005' }
]

// 模拟课程列表
export const mockCourses = [
  { id: 1, courseName: '小学数学', teacherId: 1, subject: '数学' },
  { id: 2, courseName: '初中英语', teacherId: 1, subject: '英语' },
  { id: 3, courseName: '高中物理', teacherId: 2, subject: '物理' },
  { id: 4, courseName: '初中化学', teacherId: 2, subject: '化学' },
  { id: 5, courseName: '小学语文', teacherId: 3, subject: '语文' },
  { id: 6, courseName: '高中数学', teacherId: 3, subject: '数学' },
  { id: 7, courseName: '初中生物', teacherId: 4, subject: '生物' },
  { id: 8, courseName: '小学英语', teacherId: 4, subject: '英语' },
  { id: 9, courseName: '高中历史', teacherId: 5, subject: '历史' },
  { id: 10, courseName: '初中地理', teacherId: 5, subject: '地理' }
]

// 生成模拟排课数据
export function generateMockSchedules() {
  const schedules = []
  const today = new Date()
  const startDate = new Date(today.getFullYear(), today.getMonth(), 1)
  const endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  
  let id = 1
  
  // 为每个教师生成一些课程安排
  mockTeachers.forEach(teacher => {
    const teacherCourses = mockCourses.filter(c => c.teacherId === teacher.id)
    
    // 生成本月的课程安排
    for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1)) {
      const dayOfWeek = date.getDay()
      
      // 周一到周五排课
      if (dayOfWeek >= 1 && dayOfWeek <= 5) {
        teacherCourses.forEach((course, index) => {
          // 每个课程每周上2-3次
          if (dayOfWeek % 2 === index % 2) {
            const hour = 9 + (index * 2) % 12
            const startTime = new Date(date)
            startTime.setHours(hour, 0, 0, 0)
            
            const endTime = new Date(startTime)
            endTime.setHours(hour + 1, 30, 0, 0)
            
            // 确定状态
            let status = 1 // 已安排
            const now = new Date()
            if (startTime < now && endTime > now) {
              status = 2 // 进行中
            } else if (endTime < now) {
              status = 3 // 已完成
            }
            
            schedules.push({
              id: id++,
              teacherId: teacher.id,
              teacherName: teacher.teacherName,
              courseId: course.id,
              courseName: course.courseName,
              startTime: formatDateTime(startTime),
              endTime: formatDateTime(endTime),
              location: `教室${String.fromCharCode(65 + (id % 5))}${101 + (id % 10)}`,
              status: status,
              remark: Math.random() > 0.7 ? '重点课程，需要提前准备教具' : '',
              createTime: formatDateTime(new Date(startTime.getTime() - 7 * 24 * 60 * 60 * 1000))
            })
          }
        })
      }
    }
  })
  
  return schedules
}

// 格式化日期时间
function formatDateTime(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 检查时间冲突
export function checkTimeConflict(schedules, newSchedule) {
  const conflicts = schedules.filter(schedule => {
    // 排除自己（编辑时）
    if (schedule.id === newSchedule.id) {
      return false
    }
    
    // 同一个教师
    if (schedule.teacherId !== newSchedule.teacherId) {
      return false
    }
    
    const scheduleStart = new Date(schedule.startTime)
    const scheduleEnd = new Date(schedule.endTime)
    const newStart = new Date(newSchedule.startTime)
    const newEnd = new Date(newSchedule.endTime)
    
    // 检查时间重叠
    return (newStart < scheduleEnd && newEnd > scheduleStart)
  })
  
  return {
    hasConflict: conflicts.length > 0,
    message: conflicts.length > 0 
      ? `与课程"${conflicts[0].courseName}"时间冲突 (${conflicts[0].startTime} - ${conflicts[0].endTime})`
      : ''
  }
}

// 模拟API响应
export function mockApiResponse(data, delay = 300) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        msg: '操作成功',
        data: data
      })
    }, delay)
  })
}

// 导出模拟数据
export const mockScheduleData = generateMockSchedules()

// 使用示例：
// import { mockTeachers, mockCourses, mockScheduleData, checkTimeConflict } from './mockData'

