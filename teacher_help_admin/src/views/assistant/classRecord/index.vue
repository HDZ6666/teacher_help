<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="点名记录" name="attendance">
        <el-form v-show="showSearch" ref="queryRef" :model="queryParams" :inline="true" label-width="80px">
          <el-form-item label="上课日期">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select v-model="queryParams.classId" placeholder="请选择班级" clearable style="width: 200px">
              <el-option v-for="item in classList" :key="item.id" :label="item.className" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="授课课程" prop="courseId">
            <el-select v-model="queryParams.courseId" placeholder="请选择课程" clearable style="width: 200px">
              <el-option v-for="item in courseList" :key="item.id" :label="item.courseName" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="上课老师" prop="teacherId">
            <el-select v-model="queryParams.teacherId" placeholder="请选择老师" clearable style="width: 200px">
              <el-option v-for="item in teacherList" :key="item.id" :label="item.teacherName" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleExport">导出</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
        </el-row>

        <el-table v-loading="loading" :data="recordList" border>
          <el-table-column label="点名时间" align="center" prop="attendanceTime" width="170">
            <template #default="{ row }">
              <span>{{ parseTime(row.attendanceTime, '{y}-{m}-{d} {h}:{i}') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="班级名称" align="center" prop="className" min-width="150" show-overflow-tooltip />
          <el-table-column label="授课课程" align="center" prop="courseName" min-width="140" show-overflow-tooltip />
          <el-table-column label="上课时间" align="center" min-width="180">
            <template #default="{ row }">
              <span>{{ row.classDate }} {{ row.startTime }}~{{ row.endTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课老师" align="center" prop="teacherName" width="110" />
          <el-table-column label="授课课时" align="center" prop="lessonHoursText" width="100" />
          <el-table-column label="实到人数" align="center" width="100">
            <template #default="{ row }">
              <el-tag :type="row.actualCount < row.expectedCount ? 'warning' : 'success'">
                {{ row.actualCount }}/{{ row.expectedCount }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="扣课合计" align="center" prop="deductedQuantity" width="100" />
          <el-table-column label="上课教室" align="center" prop="classroom" min-width="120" show-overflow-tooltip />
          <el-table-column label="上课内容" align="center" prop="content" min-width="160" show-overflow-tooltip />
          <el-table-column label="状态" align="center" prop="statusName" width="90" />
          <el-table-column label="操作" align="center" width="190" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
              <el-button type="warning" link @click="handleComment(row)">课后点评</el-button>
              <el-button type="danger" link @click="handleDelete(row)">撤销</el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="total > 0"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          :total="total"
          @pagination="getList"
        />
      </el-tab-pane>

      <el-tab-pane label="超时未点" name="overtime">
        <el-form ref="overtimeQueryRef" :model="overtimeQueryParams" :inline="true" label-width="80px">
          <el-form-item label="上课日期">
            <el-date-picker
              v-model="overtimeDateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select v-model="overtimeQueryParams.classId" placeholder="请选择班级" clearable style="width: 200px">
              <el-option v-for="item in classList" :key="item.id" :label="item.className" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="上课老师" prop="teacherId">
            <el-select v-model="overtimeQueryParams.teacherId" placeholder="请选择老师" clearable style="width: 200px">
              <el-option v-for="item in teacherList" :key="item.id" :label="item.teacherName" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleOvertimeQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetOvertimeQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Bell" @click="handleBatchRemind">批量提醒</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleOvertimeExport">导出</el-button>
          </el-col>
        </el-row>

        <el-table v-loading="overtimeLoading" :data="overtimeList" border>
          <el-table-column label="上课时间" align="center" width="180">
            <template #default="{ row }">
              <span>{{ row.classDate }} {{ row.classTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="班级名称" align="center" prop="className" min-width="150" show-overflow-tooltip />
          <el-table-column label="上课老师" align="center" prop="teacherName" width="110" />
          <el-table-column label="授课课程" align="center" prop="courseName" min-width="140" show-overflow-tooltip />
          <el-table-column label="上课教室" align="center" prop="classroom" min-width="120" show-overflow-tooltip />
          <el-table-column label="上课内容" align="center" prop="classContent" min-width="180" show-overflow-tooltip />
          <el-table-column label="状态" align="center" prop="statusName" width="100" />
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="warning" link @click="handleRemind(row)">去点名</el-button>
              <el-button type="primary" link @click="handleOvertimeDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="overtimeTotal > 0"
          v-model:page="overtimeQueryParams.pageNum"
          v-model:limit="overtimeQueryParams.pageSize"
          :total="overtimeTotal"
          @pagination="getOvertimeList"
        />
      </el-tab-pane>

      <el-tab-pane label="缺课补课" name="makeup">
        <el-form ref="makeupQueryRef" :model="makeupQueryParams" :inline="true" label-width="90px">
          <el-form-item label="搜索学员">
            <el-input
              v-model="makeupQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 220px"
              @keyup.enter="handleMakeupQuery"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select v-model="makeupQueryParams.classId" placeholder="请选择班级" clearable style="width: 200px">
              <el-option v-for="item in classList" :key="item.id" :label="item.className" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="上课日期">
            <el-date-picker
              v-model="makeupDateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleMakeupQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetMakeupQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Bell" @click="handleBatchNotify">开班补课</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleMakeupExport">导出</el-button>
          </el-col>
        </el-row>

        <el-table v-loading="makeupLoading" :data="makeupList" border>
          <el-table-column label="学员姓名" align="center" prop="studentName" width="120" />
          <el-table-column label="手机号" align="center" prop="phone" width="130" />
          <el-table-column label="班级名称" align="center" prop="className" min-width="160" show-overflow-tooltip />
          <el-table-column label="上课时间" align="center" width="180">
            <template #default="{ row }">
              <span>{{ row.classDate }} {{ row.classTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课老师" align="center" prop="teacherName" width="110" />
          <el-table-column label="课程" align="center" prop="courseName" width="130" />
          <el-table-column label="缺课状态" align="center" prop="makeupStatus" width="110">
            <template #default="{ row }">
              <el-tag :type="getMakeupStatusType(row.makeupStatus)">{{ row.makeupStatus }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="消耗方式" align="center" prop="consumeType" min-width="160" show-overflow-tooltip />
          <el-table-column label="应扣额度" align="center" prop="shouldDeduct" width="100" />
          <el-table-column label="实扣额度" align="center" prop="actualDeduct" width="100" />
          <el-table-column label="补课状态" align="center" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.madeupStatus" type="success">已补课</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="上课内容" align="center" prop="classContent" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" align="center" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="warning" link @click="handleNotifyMakeup(row)">提醒补课</el-button>
              <el-button type="primary" link @click="handleMarkMadeup(row)">标记已补</el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="makeupTotal > 0"
          v-model:page="makeupQueryParams.pageNum"
          v-model:limit="makeupQueryParams.pageSize"
          :total="makeupTotal"
          @pagination="getMakeupList"
        />
      </el-tab-pane>

      <el-tab-pane label="缺课提醒" name="absence">
        <el-alert
          title="列表根据已点名记录中的未到/请假数据汇总，提醒设置与不提醒名单后续接入。"
          type="warning"
          :closable="false"
          show-icon
          class="mb8"
        />
        <el-form ref="absenceQueryRef" :model="absenceQueryParams" :inline="true" label-width="90px">
          <el-form-item label="搜索学员">
            <el-input
              v-model="absenceQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 220px"
              @keyup.enter="handleAbsenceQuery"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select v-model="absenceQueryParams.classId" placeholder="请选择班级" clearable style="width: 200px">
              <el-option v-for="item in classList" :key="item.id" :label="item.className" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="未到次数">
            <el-input v-model="absenceQueryParams.minAbsences" placeholder="最小值" clearable style="width: 100px" />
            <span class="range-split">-</span>
            <el-input v-model="absenceQueryParams.maxAbsences" placeholder="最大值" clearable style="width: 100px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleAbsenceQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetAbsenceQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Bell" @click="handleBatchRemindAbsence">提醒</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleAbsenceExport">导出</el-button>
          </el-col>
          <right-toolbar @queryTable="getAbsenceList" />
        </el-row>

        <el-table v-loading="absenceLoading" :data="absenceList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="学员" align="center" prop="studentName" width="120" />
          <el-table-column label="手机号" align="center" prop="phone" width="130" />
          <el-table-column label="所在班级" align="center" prop="className" min-width="160" show-overflow-tooltip />
          <el-table-column label="未到次数" align="center" prop="absenceCount" width="100" />
          <el-table-column label="请假次数" align="center" prop="leaveCount" width="100" />
          <el-table-column label="缺课合计" align="center" prop="missedCount" width="100" />
          <el-table-column label="未上课天数" align="center" prop="missedClasses" width="110" />
          <el-table-column label="上次上课日期" align="center" prop="lastClassDate" width="130" />
          <el-table-column label="上次提醒时间" align="center" prop="lastRemindTime" width="150">
            <template #default="{ row }">
              <span>{{ row.lastRemindTime || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="warning" link @click="handleRemindAbsence(row)">提醒</el-button>
              <el-button type="primary" link @click="handleMarkReminded(row)">不再提醒</el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="absenceTotal > 0"
          v-model:page="absenceQueryParams.pageNum"
          v-model:limit="absenceQueryParams.pageSize"
          :total="absenceTotal"
          @pagination="getAbsenceList"
        />
      </el-tab-pane>

      <el-tab-pane label="请假申请" name="leave">
        <el-empty description="请假申请审批流程后续接入" />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="detailDialogVisible" title="超时未点详情" width="520px" append-to-body>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="班级">{{ currentRecord.className || '-' }}</el-descriptions-item>
        <el-descriptions-item label="课程">{{ currentRecord.courseName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="上课时间">
          {{ currentRecord.classDate || '-' }} {{ currentRecord.classTime || '' }}
        </el-descriptions-item>
        <el-descriptions-item label="上课老师">{{ currentRecord.teacherName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="上课教室">{{ currentRecord.classroom || '-' }}</el-descriptions-item>
        <el-descriptions-item label="上课内容">{{ currentRecord.classContent || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup name="ClassRecord">
import { getCurrentInstance, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { parseTime } from '@/utils/ruoyi'
import { listClassOptions } from '@/api/assistant/class'
import { listCourseOptions } from '@/api/assistant/course'
import { listTeacher } from '@/api/teach/teacher'
import {
  listAbsenceReminder,
  listAttendanceRecord,
  listMakeupRecord,
  listOvertimeRecord
} from '@/api/assistant/classRecord'

const { proxy } = getCurrentInstance()
const router = useRouter()

const activeTab = ref('attendance')
const loading = ref(false)
const showSearch = ref(true)
const recordList = ref([])
const total = ref(0)
const dateRange = ref([])
const detailDialogVisible = ref(false)
const currentRecord = ref({})

const overtimeLoading = ref(false)
const overtimeList = ref([])
const overtimeTotal = ref(0)
const overtimeDateRange = ref([])
const overtimeQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  classId: '',
  teacherId: ''
})

const makeupLoading = ref(false)
const makeupList = ref([])
const makeupTotal = ref(0)
const makeupDateRange = ref([])
const makeupQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  classId: ''
})

const absenceLoading = ref(false)
const absenceList = ref([])
const absenceTotal = ref(0)
const absenceQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  classId: '',
  minAbsences: '',
  maxAbsences: ''
})

const classList = ref([])
const courseList = ref([])
const teacherList = ref([])

const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  classId: '',
  courseId: '',
  teacherId: '',
  status: ''
})

function buildDateRangeParams(source, range) {
  const params = { ...source }
  if (range && range.length === 2) {
    params.beginTime = range[0]
    params.endTime = range[1]
  }
  return cleanParams(params)
}

function cleanParams(params) {
  return Object.keys(params).reduce((result, key) => {
    if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
      result[key] = params[key]
    }
    return result
  }, {})
}

async function getList() {
  loading.value = true
  try {
    const response = await listAttendanceRecord(buildDateRangeParams(queryParams.value, dateRange.value))
    recordList.value = response.rows || []
    total.value = response.total || 0
  } finally {
    loading.value = false
  }
}

function handleTabClick(tab) {
  if (tab.props.name === 'attendance') {
    getList()
  } else if (tab.props.name === 'overtime') {
    getOvertimeList()
  } else if (tab.props.name === 'makeup') {
    getMakeupList()
  } else if (tab.props.name === 'absence') {
    getAbsenceList()
  }
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  dateRange.value = []
  queryParams.value = {
    pageNum: 1,
    pageSize: 10,
    classId: '',
    courseId: '',
    teacherId: '',
    status: ''
  }
  getList()
}

function handleExport() {
  proxy.$modal.msgInfo('导出功能后续接入')
}

function handleDetail(row) {
  router.push({
    name: 'ClassRecordDetail',
    params: { id: row.id }
  })
}

function handleComment(row) {
  router.push({
    name: 'CommentDetail',
    params: { id: row.id }
  })
}

function handleDelete() {
  proxy.$modal.msgInfo('撤销点名记录后续接入')
}

async function initSelectOptions() {
  const [classRes, courseRes, teacherRes] = await Promise.all([
    listClassOptions(),
    listCourseOptions(),
    listTeacher({ pageNum: 1, pageSize: 500 })
  ])
  classList.value = classRes.data || []
  courseList.value = courseRes.data || []
  teacherList.value = teacherRes.rows || []
}

async function getOvertimeList() {
  overtimeLoading.value = true
  try {
    const response = await listOvertimeRecord(
      buildDateRangeParams(overtimeQueryParams.value, overtimeDateRange.value)
    )
    overtimeList.value = response.rows || []
    overtimeTotal.value = response.total || 0
  } finally {
    overtimeLoading.value = false
  }
}

function handleOvertimeQuery() {
  overtimeQueryParams.value.pageNum = 1
  getOvertimeList()
}

function resetOvertimeQuery() {
  overtimeDateRange.value = []
  overtimeQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    classId: '',
    teacherId: ''
  }
  getOvertimeList()
}

function handleBatchRemind() {
  proxy.$modal.msgInfo('批量提醒功能后续接入')
}

function handleOvertimeExport() {
  proxy.$modal.msgInfo('导出功能后续接入')
}

function handleRemind(row) {
  if (row.classId) {
    router.push({
      name: 'ClassAttendance',
      params: { id: row.classId },
      query: row.id ? { eventId: row.id } : {}
    })
  } else {
    proxy.$modal.msgError('无法获取班级信息')
  }
}

function handleOvertimeDetail(row) {
  currentRecord.value = { ...row }
  detailDialogVisible.value = true
}

async function getMakeupList() {
  makeupLoading.value = true
  try {
    const response = await listMakeupRecord(buildDateRangeParams(makeupQueryParams.value, makeupDateRange.value))
    makeupList.value = response.rows || []
    makeupTotal.value = response.total || 0
  } finally {
    makeupLoading.value = false
  }
}

function handleMakeupQuery() {
  makeupQueryParams.value.pageNum = 1
  getMakeupList()
}

function resetMakeupQuery() {
  makeupDateRange.value = []
  makeupQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    studentKeyword: '',
    classId: ''
  }
  getMakeupList()
}

function getMakeupStatusType(status) {
  const typeMap = {
    未到: 'danger',
    请假: 'warning'
  }
  return typeMap[status] || 'info'
}

function handleNotifyMakeup(row) {
  proxy.$modal.msgInfo(`${row.studentName || ''} 的补课提醒后续接入`)
}

function handleBatchNotify() {
  proxy.$modal.msgInfo('开班补课功能后续接入')
}

function handleMarkMadeup(row) {
  proxy.$modal.msgInfo(`${row.studentName || ''} 的标记已补后续接入`)
}

function handleMakeupExport() {
  proxy.$modal.msgInfo('导出功能后续接入')
}

async function getAbsenceList() {
  absenceLoading.value = true
  try {
    const response = await listAbsenceReminder(cleanParams(absenceQueryParams.value))
    absenceList.value = response.rows || []
    absenceTotal.value = response.total || 0
  } finally {
    absenceLoading.value = false
  }
}

function handleAbsenceQuery() {
  absenceQueryParams.value.pageNum = 1
  getAbsenceList()
}

function resetAbsenceQuery() {
  absenceQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    studentKeyword: '',
    classId: '',
    minAbsences: '',
    maxAbsences: ''
  }
  getAbsenceList()
}

function handleRemindAbsence(row) {
  proxy.$modal.msgInfo(`${row.studentName || ''} 的缺课提醒后续接入`)
}

function handleBatchRemindAbsence() {
  proxy.$modal.msgInfo('批量提醒功能后续接入')
}

function handleMarkReminded(row) {
  proxy.$modal.msgInfo(`${row.studentName || ''} 的不再提醒后续接入`)
}

function handleAbsenceExport() {
  proxy.$modal.msgInfo('导出功能后续接入')
}

onMounted(() => {
  initSelectOptions()
  getList()
})
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}

.range-split {
  display: inline-block;
  width: 24px;
  text-align: center;
  color: #909399;
}
</style>
