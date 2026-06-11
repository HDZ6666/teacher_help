<template>
  <div class="app-container schedule-container">
    <!-- 搜索区域 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="教师" prop="teacherId">
        <el-select
          v-model="queryParams.teacherId"
          placeholder="请选择教师"
          clearable
          style="width: 200px"
          @change="handleQuery"
        >
          <el-option
            v-for="teacher in teacherList"
            :key="teacher.id"
            :label="teacher.teacherName"
            :value="teacher.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="学科" prop="subjectCode">
        <el-select
          v-model="queryParams.subjectCode"
          placeholder="请选择学科"
          clearable
          style="width: 200px"
          @change="handleQuery"
        >
          <el-option
            v-for="dict in teach_subjects"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select
          v-model="queryParams.status"
          placeholder="请选择状态"
          clearable
          style="width: 200px"
          @change="handleQuery"
        >
          <el-option label="已安排" value="0" />
          <el-option label="进行中" value="1" />
          <el-option label="已完成" value="2" />
          <el-option label="已取消" value="3" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['teach:schedule:add']"
        >新增排课</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['teach:schedule:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="fetchEvents"></right-toolbar>
    </el-row>

    <!-- FullCalendar 日历组件 -->
    <div class="calendar-wrapper">
      <FullCalendar ref="fullCalendarRef" :options="calendarOptions">
        <template v-slot:eventContent='arg'>
          <div class="fc-event-main-frame">
            <div class="fc-event-time">{{ arg.timeText }}</div>
            <div class="fc-event-title-container">
              <div class="fc-event-title">{{ arg.event.title }}</div>
            </div>
          </div>
        </template>
      </FullCalendar>
    </div>

    <!-- 新增/编辑排课对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="scheduleRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="教师" prop="teacherId">
              <el-select
                v-model="form.teacherId"
                placeholder="请选择教师"
                style="width: 100%"
              >
                <el-option
                  v-for="teacher in teacherList"
                  :key="teacher.id"
                  :label="teacher.teacherName"
                  :value="teacher.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学科" prop="subjectCode">
              <el-select
                v-model="form.subjectCode"
                placeholder="请选择学科"
                style="width: 100%"
              >
                <el-option
                  v-for="dict in teach_subjects"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startTime">
              <el-date-picker
                v-model="form.startTime"
                type="datetime"
                placeholder="选择开始时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endTime">
              <el-date-picker
                v-model="form.endTime"
                type="datetime"
                placeholder="选择结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="学生名单" prop="studentIds">
          <el-select
            v-model="form.studentIds"
            multiple
            placeholder="请选择学生"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="student in studentList"
              :key="student.id"
              :label="student.studentName"
              :value="student.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20" v-if="form.id">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="已安排" value="0" />
                <el-option label="进行中" value="1" />
                <el-option label="已完成" value="2" />
                <el-option label="已取消" value="3" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看排课详情对话框 -->
    <el-dialog title="排课详情" v-model="detailOpen" width="700px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="教师">{{ detailData.teacherName }}</el-descriptions-item>
        <el-descriptions-item label="学科">{{ detailData.subjectName }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ detailData.startTime }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ detailData.endTime }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="detailData.status === '0'" type="info">已安排</el-tag>
          <el-tag v-else-if="detailData.status === '1'" type="warning">进行中</el-tag>
          <el-tag v-else-if="detailData.status === '2'" type="success">已完成</el-tag>
          <el-tag v-else-if="detailData.status === '3'" type="danger">已取消</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailData.createTime }}</el-descriptions-item>
        <el-descriptions-item label="计划人数">{{ detailData.cachedPlanned || 0 }}</el-descriptions-item>
        <el-descriptions-item label="出勤人数">{{ detailData.cachedPresent || 0 }}</el-descriptions-item>
        <el-descriptions-item label="迟到人数">{{ detailData.cachedLate || 0 }}</el-descriptions-item>
        <el-descriptions-item label="请假人数">{{ detailData.cachedExcused || 0 }}</el-descriptions-item>
        <el-descriptions-item label="缺勤人数">{{ detailData.cachedAbsent || 0 }}</el-descriptions-item>
        <el-descriptions-item label="出勤率">{{ detailData.cachedRate || 0 }}%</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailData.remark || '无' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 学生名单 -->
      <el-divider content-position="left">学生名单</el-divider>
      <el-table :data="detailData.students" style="width: 100%" max-height="300">
        <el-table-column prop="studentName" label="学生姓名" width="150" />
        <el-table-column prop="status" label="考勤状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 0" type="info" size="small">未到</el-tag>
            <el-tag v-else-if="scope.row.status === 1" type="success" size="small">出勤</el-tag>
            <el-tag v-else-if="scope.row.status === 2" type="warning" size="small">迟到</el-tag>
            <el-tag v-else-if="scope.row.status === 3" type="primary" size="small">请假</el-tag>
            <el-tag v-else-if="scope.row.status === 4" type="danger" size="small">缺勤</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="checkInTime" label="签到时间" width="180" />
      </el-table>

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="handleEdit(detailData)" v-hasPermi="['teach:schedule:event:edit']">编辑</el-button>
          <el-button type="danger" @click="handleDelete(detailData)" v-hasPermi="['teach:schedule:event:remove']">删除</el-button>
          <el-button @click="detailOpen = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Schedule">
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import {
  listScheduleEvent,
  getScheduleEvent,
  addScheduleEvent,
  updateScheduleEvent,
  delScheduleEvent,
  exportScheduleEvent,
  getCalendarEvents
} from "@/api/teach/schedule"
import { listTeacher } from "@/api/teach/teacher"
import { listStudent } from "@/api/teach/student"

const { proxy } = getCurrentInstance()
const { teach_subjects } = proxy.useDict('teach_subjects')

// 数据定义
const fullCalendarRef = ref(null)
const teacherList = ref([])
const studentList = ref([])
const open = ref(false)
const detailOpen = ref(false)
const showSearch = ref(true)
const title = ref("")
const detailData = ref({})

const data = reactive({
  form: {},
  queryParams: {
    teacherId: null,
    subjectCode: null,
    status: null
  },
  rules: {
    teacherId: [
      { required: true, message: "请选择教师", trigger: "change" }
    ],
    startTime: [
      { required: true, message: "请选择开始时间", trigger: "change" }
    ],
    endTime: [
      { required: true, message: "请选择结束时间", trigger: "change" }
    ],
    studentIds: [
      { required: true, message: "请选择学生", trigger: "change" }
    ]
  }
})

const { queryParams, form, rules } = toRefs(data)

// FullCalendar 配置
const calendarOptions = reactive({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'timeGridWeek',
  locale: 'zh-cn',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
  },
  buttonText: {
    today: '今天',
    month: '月',
    week: '周',
    day: '日',
    list: '列表'
  },
  slotMinTime: '06:00:00',
  slotMaxTime: '23:00:00',
  allDaySlot: false,
  editable: true,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  navLinks: true,
  events: [],
  eventClick: handleEventClick,
  select: handleDateSelect,
  eventDrop: handleEventDrop,
  eventResize: handleEventResize,
  height: 'auto',
  contentHeight: 650
})

// 获取日历事件数据
async function fetchEvents() {
  try {
    // 获取当前日历视图的时间范围
    const calendarApi = fullCalendarRef.value?.getApi()
    const view = calendarApi?.view

    const params = {
      ...queryParams.value,
      start: view?.activeStart?.toISOString(),
      end: view?.activeEnd?.toISOString()
    }

    const response = await getCalendarEvents(params)
    if (response.code === 200) {
      // API返回的数据已经是FullCalendar格式，直接使用
      calendarOptions.events = response.data.map(item => ({
        ...item,
        backgroundColor: getStatusColor(item.extendedProps?.status),
        borderColor: getStatusColor(item.extendedProps?.status)
      }))
    }
  } catch (error) {
    console.error('获取日历事件失败:', error)
  }
}

// 根据状态获取颜色
function getStatusColor(status) {
  const colorMap = {
    '0': '#909399', // 已安排 - 灰色
    '1': '#E6A23C', // 进行中 - 橙色
    '2': '#67C23A', // 已完成 - 绿色
    '3': '#F56C6C'  // 已取消 - 红色
  }
  return colorMap[status] || '#409EFF'
}

// 点击事件处理
async function handleEventClick(clickInfo) {
  const event = clickInfo.event
  try {
    // 获取完整的事件详情（包含学生名单）
    const response = await getScheduleEvent(event.id)
    if (response.code === 200) {
      detailData.value = {
        ...response.data,
        students: response.data.students || []
      }
      detailOpen.value = true
    }
  } catch (error) {
    console.error('获取事件详情失败:', error)
    proxy.$modal.msgError("获取详情失败")
  }
}

// 选择日期时间处理（用于新增）
function handleDateSelect(selectInfo) {
  reset()
  form.value.startTime = proxy.parseTime(selectInfo.start, '{y}-{m}-{d} {h}:{i}:{s}')
  form.value.endTime = proxy.parseTime(selectInfo.end, '{y}-{m}-{d} {h}:{i}:{s}')
  open.value = true
  title.value = "新增排课"

  // 取消选择
  const calendarApi = selectInfo.view.calendar
  calendarApi.unselect()
}

// 拖拽事件处理
async function handleEventDrop(dropInfo) {
  const event = dropInfo.event
  try {
    await updateScheduleEvent({
      id: event.id,
      startTime: proxy.parseTime(event.start, '{y}-{m}-{d} {h}:{i}:{s}'),
      endTime: proxy.parseTime(event.end, '{y}-{m}-{d} {h}:{i}:{s}')
    })
    proxy.$modal.msgSuccess("排课时间更新成功")
    fetchEvents()
  } catch (error) {
    dropInfo.revert()
    proxy.$modal.msgError("排课时间更新失败")
  }
}

// 调整事件大小处理
async function handleEventResize(resizeInfo) {
  const event = resizeInfo.event
  try {
    await updateScheduleEvent({
      id: event.id,
      startTime: proxy.parseTime(event.start, '{y}-{m}-{d} {h}:{i}:{s}'),
      endTime: proxy.parseTime(event.end, '{y}-{m}-{d} {h}:{i}:{s}')
    })
    proxy.$modal.msgSuccess("排课时间更新成功")
    fetchEvents()
  } catch (error) {
    resizeInfo.revert()
    proxy.$modal.msgError("排课时间更新失败")
  }
}

// 表单重置
function reset() {
  form.value = {
    id: null,
    teacherId: null,
    subjectCode: null,
    startTime: null,
    endTime: null,
    studentIds: [],
    status: '0',
    remark: null
  }
  proxy.resetForm("scheduleRef")
}

// 取消按钮
function cancel() {
  open.value = false
  reset()
}

// 搜索按钮操作
function handleQuery() {
  fetchEvents()
}

// 重置按钮操作
function resetQuery() {
  proxy.resetForm("queryRef")
  handleQuery()
}

// 新增按钮操作
function handleAdd() {
  reset()
  open.value = true
  title.value = "新增排课"
}

// 编辑按钮操作
function handleEdit(row) {
  reset()
  detailOpen.value = false

  getScheduleEvent(row.id).then(response => {
    form.value = {
      ...response.data,
      studentIds: response.data.students?.map(s => s.studentId) || []
    }
    open.value = true
    title.value = "修改排课"
  })
}

// 提交按钮
function submitForm() {
  proxy.$refs["scheduleRef"].validate(async valid => {
    if (valid) {
      saveSchedule()
    }
  })
}

// 保存排课
async function saveSchedule() {
  try {
    if (form.value.id != null) {
      await updateScheduleEvent(form.value)
      proxy.$modal.msgSuccess("修改成功")
    } else {
      await addScheduleEvent(form.value)
      proxy.$modal.msgSuccess("新增成功")
    }
    open.value = false
    fetchEvents()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

// 删除按钮操作
function handleDelete(row) {
  proxy.$modal.confirm('是否确认删除该排课？').then(async () => {
    await delScheduleEvent(row.id)
    proxy.$modal.msgSuccess("删除成功")
    detailOpen.value = false
    fetchEvents()
  }).catch(() => {})
}

// 导出按钮操作
function handleExport() {
  proxy.$modal.confirm("是否确认导出所有排课数据?").then(async () => {
    const response = await exportScheduleEvent(queryParams.value)
    proxy.$download.saveAs(response, `schedule_${new Date().getTime()}.xlsx`)
  })
}

// 加载教师列表
async function loadTeachers() {
  const response = await listTeacher({ pageNum: 1, pageSize: 1000 })
  teacherList.value = response.rows || []
}

// 加载学生列表
async function loadStudents() {
  const response = await listStudent({ pageNum: 1, pageSize: 1000 })
  studentList.value = response.rows || []
}

// 组件挂载时执行
onMounted(() => {
  loadTeachers()
  loadStudents()
  fetchEvents()
})
</script>

<style scoped>
.schedule-container {
  padding: 20px;
}

.calendar-wrapper {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* FullCalendar 样式覆盖 */
:deep(.fc) {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5em;
  font-weight: bold;
  color: #303133;
}

:deep(.fc-button) {
  background-color: #409EFF;
  border-color: #409EFF;
  color: #fff;
  text-transform: capitalize;
  padding: 6px 12px;
  font-size: 14px;
}

:deep(.fc-button:hover) {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

:deep(.fc-button-active) {
  background-color: #337ecc !important;
  border-color: #337ecc !important;
}

:deep(.fc-button:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
}

:deep(.fc-daygrid-day-number) {
  color: #606266;
  font-size: 14px;
  padding: 8px;
}

:deep(.fc-col-header-cell-cushion) {
  color: #303133;
  font-weight: bold;
  padding: 10px 0;
}

:deep(.fc-event) {
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

:deep(.fc-event:hover) {
  opacity: 0.8;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

:deep(.fc-event-main-frame) {
  display: flex;
  flex-direction: column;
}

:deep(.fc-event-time) {
  font-weight: bold;
  margin-bottom: 2px;
}

:deep(.fc-event-title) {
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.fc-timegrid-slot) {
  height: 3em;
}

:deep(.fc-timegrid-slot-label) {
  font-size: 12px;
  color: #909399;
}

:deep(.fc-day-today) {
  background-color: rgba(64, 158, 255, 0.05) !important;
}

:deep(.fc-highlight) {
  background-color: rgba(64, 158, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.fc-toolbar) {
    flex-direction: column;
    gap: 10px;
  }

  :deep(.fc-toolbar-chunk) {
    display: flex;
    justify-content: center;
  }
}
</style>

