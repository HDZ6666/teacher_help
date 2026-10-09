<template>
  <div class="app-container">
    <el-page-header @back="goBack" class="mb16">
      <template #content>老师详情 - {{ teacher.teacherName || '' }}</template>
    </el-page-header>

    <el-descriptions :column="3" border v-loading="loading">
      <el-descriptions-item label="姓名">{{ teacher.teacherName }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ teacher.phone || '-' }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ teacher.statusName || statusLabels[teacher.status] || '-' }}</el-descriptions-item>
      <el-descriptions-item label="教学科目">{{ (teacher.subjects || []).join('、') || '-' }}</el-descriptions-item>
      <el-descriptions-item label="教学经验">{{ teacher.workExperience ?? 0 }} 年</el-descriptions-item>
      <el-descriptions-item label="默认课时费">{{ teacher.hourlyRate ?? 0 }} 元</el-descriptions-item>
      <el-descriptions-item label="个人简介" :span="3">{{ teacher.introduction || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><el-statistic title="授课班级" :value="stats.classCount || 0" /></el-col>
      <el-col :span="6"><el-statistic title="上月课时" :value="stats.lastMonthHours || 0" :suffix="`/ ${stats.lastMonthLessons || 0}次`" /></el-col>
      <el-col :span="6"><el-statistic title="本月课时" :value="stats.thisMonthHours || 0" :suffix="`/ ${stats.thisMonthLessons || 0}次`" /></el-col>
      <el-col :span="6"><el-statistic title="已上课时" :value="stats.totalHours || 0" :suffix="`/ ${stats.totalLessons || 0}次`" /></el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="授课班级" name="class">
        <el-table :data="classes" border v-loading="loading">
          <el-table-column label="班级" min-width="150">
            <template #default="{ row }">
              <el-link type="primary" @click="router.push(`/assistant/class/detail/${row.id}`)">{{ row.className }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="课程" prop="courseName" min-width="140" show-overflow-tooltip />
          <el-table-column label="角色" prop="teacherRole" width="80" align="center" />
          <el-table-column label="在读人数" prop="currentStudents" width="90" align="center" />
          <el-table-column label="已上课次" prop="completedLessons" width="90" align="center" />
          <el-table-column label="已结课时" prop="completedHours" width="90" align="center" />
          <el-table-column label="开课日期" prop="startDate" width="110" align="center" />
          <el-table-column label="结课日期" prop="endDate" width="110" align="center" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="上课记录" name="record">
        <el-form :inline="true" class="mb8">
          <el-form-item label="上课日期">
            <el-date-picker v-model="dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="-" start-placeholder="开始" end-placeholder="结束" style="width: 240px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleRecordQuery">搜索</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="records" border v-loading="recordLoading">
          <el-table-column label="上课时间" prop="classTime" min-width="190" />
          <el-table-column label="班级" prop="className" min-width="140" show-overflow-tooltip />
          <el-table-column label="课程" prop="courseName" min-width="120" show-overflow-tooltip />
          <el-table-column label="课时" prop="lessonHours" width="70" align="center" />
          <el-table-column label="应到/实到" width="100" align="center">
            <template #default="{ row }">{{ row.expectedCount }} / {{ row.actualCount }}</template>
          </el-table-column>
          <el-table-column label="出勤率" width="90" align="center">
            <template #default="{ row }">{{ row.attendanceRate }}%</template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleSignList(row)">签到列表</el-button>
            </template>
          </el-table-column>
        </el-table>
        <pagination v-show="recordTotal > 0" :total="recordTotal" v-model:page="recordQuery.pageNum" v-model:limit="recordQuery.pageSize" @pagination="loadRecords" />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="signOpen" title="签到列表" width="720px" append-to-body>
      <el-table :data="signDetail.details || []" border v-loading="signLoading">
        <el-table-column label="学员" prop="studentName" width="110" align="center" />
        <el-table-column label="手机号" prop="phone" width="130" align="center" />
        <el-table-column label="到课状态" prop="statusName" width="90" align="center" />
        <el-table-column label="扣课" prop="deductQuantity" width="70" align="center" />
        <el-table-column label="消耗方式" prop="consumeType" min-width="160" show-overflow-tooltip />
        <el-table-column label="备注" prop="remark" min-width="120" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantTeacherDetail">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacher, getTeacherOverview, listTeacherRecords } from '@/api/teach/teacher'
import { getAttendanceRecord } from '@/api/assistant/classRecord'

const route = useRoute()
const router = useRouter()
const teacherId = computed(() => Number(route.params.id))
const statusLabels = { 0: '正常', 1: '停用', 2: '已注销' }

const activeTab = ref('class')
const loading = ref(false)
const teacher = ref({})
const stats = ref({})
const classes = ref([])

async function loadOverview() {
  loading.value = true
  try {
    const [teacherRes, overviewRes] = await Promise.all([getTeacher(teacherId.value), getTeacherOverview(teacherId.value)])
    teacher.value = teacherRes.data || {}
    stats.value = overviewRes.data?.stats || {}
    classes.value = overviewRes.data?.classes || []
  } finally {
    loading.value = false
  }
}

const dateRange = ref([])
const recordQuery = ref({ pageNum: 1, pageSize: 10 })
const records = ref([])
const recordTotal = ref(0)
const recordLoading = ref(false)

async function loadRecords() {
  recordLoading.value = true
  try {
    const [beginDate, endDate] = dateRange.value || []
    const res = await listTeacherRecords(teacherId.value, {
      page_num: recordQuery.value.pageNum,
      page_size: recordQuery.value.pageSize,
      begin_date: beginDate,
      end_date: endDate
    })
    records.value = res.rows || []
    recordTotal.value = res.total || 0
  } finally {
    recordLoading.value = false
  }
}

function handleRecordQuery() {
  recordQuery.value.pageNum = 1
  loadRecords()
}

const signOpen = ref(false)
const signLoading = ref(false)
const signDetail = ref({})

async function handleSignList(row) {
  signOpen.value = true
  signLoading.value = true
  signDetail.value = {}
  try {
    const res = await getAttendanceRecord(row.id)
    signDetail.value = res.data || {}
  } finally {
    signLoading.value = false
  }
}

function goBack() {
  router.push('/assistant/teacher')
}

onMounted(() => {
  loadOverview()
  loadRecords()
})
</script>

<style scoped>
.mb8 {
  margin-bottom: 8px;
}

.mb16 {
  margin-bottom: 16px;
}

.stat-row {
  margin: 16px 0;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}
</style>
