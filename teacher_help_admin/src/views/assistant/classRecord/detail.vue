<template>
  <div class="app-container">
    <el-page-header class="mb20" @back="goBack">
      <template #content>
        <span class="page-title">点名详情</span>
      </template>
    </el-page-header>

    <el-card v-loading="loading" shadow="never" class="mb20">
      <div class="course-header">
        <h2>{{ classInfo.className || '-' }} {{ classInfo.startTime || '' }}~{{ classInfo.endTime || '' }}</h2>
        <div class="action-buttons">
          <el-button type="warning" plain @click="handleEditLesson">编辑</el-button>
          <el-button plain @click="handleLearningPlan">布置学习计划</el-button>
          <el-button type="success" plain @click="handleComment">课后点评</el-button>
        </div>
      </div>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课班级：</span>
            <span>{{ classInfo.className || '-' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课时间：</span>
            <span>{{ classInfo.classDate || '-' }} {{ classInfo.startTime || '' }}~{{ classInfo.endTime || '' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课老师：</span>
            <span>{{ classInfo.teacherName || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课课程：</span>
            <span>{{ classInfo.courseName || '-' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课课时：</span>
            <span>{{ classInfo.lessonHoursText || '-' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课教室：</span>
            <span>{{ classInfo.classroom || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">学员可见文件：</span>
            <span>共0个文件</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">点名老师：</span>
            <span>{{ classInfo.createBy || classInfo.teacherName || '-' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">点名时间：</span>
            <span>{{ parseTime(classInfo.attendanceTime, '{y}-{m}-{d} {h}:{i}') || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="course-info">
        <el-col :span="24">
          <div class="info-item">
            <span class="label">上课内容：</span>
            <span>{{ classInfo.content || '-' }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="学员名单" name="students">
        <div class="table-toolbar">
          <div>
            <el-button plain @click="handleAddTempStudent">添加临时学员</el-button>
            <el-button plain @click="handleAddMakeupStudent">添加补课学员</el-button>
          </div>
          <div class="table-search">
            <el-checkbox v-model="onlyAbsent">只看未到学员</el-checkbox>
            <el-input
              v-model="searchKeyword"
              placeholder="学员姓名/手机号"
              clearable
              style="width: 220px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <el-table :data="filteredStudents" border>
          <el-table-column label="姓名" min-width="150">
            <template #default="{ row }">
              <div class="student-info">
                <span>{{ row.studentName }}</span>
                <span class="phone">{{ row.phone || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="消耗方式" align="center" prop="consumeType" min-width="180" show-overflow-tooltip />
          <el-table-column label="到课状态" align="center" width="110">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.statusName)">{{ row.statusName || '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="补课状态" align="center" prop="makeupStatus" width="100" />
          <el-table-column label="扣除额度" align="center" prop="quota" width="110" />
          <el-table-column label="备注" align="center" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ row.remark || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="110" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleModify(row)">修改</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="修改记录" name="history">
        <el-table v-if="changeHistory.length > 0" :data="changeHistory" border>
          <el-table-column label="操作时间" align="center" prop="operateTime" width="180" />
          <el-table-column label="操作人" align="center" prop="operator" width="120" />
          <el-table-column label="操作类型" align="center" prop="operateType" width="160" />
          <el-table-column label="修改内容" align="center" prop="changeContent" min-width="300" />
        </el-table>
        <el-empty v-else description="暂无修改记录" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup name="ClassRecordDetail">
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { parseTime } from '@/utils/ruoyi'
import { getAttendanceRecord } from '@/api/assistant/classRecord'

const { proxy } = getCurrentInstance()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const activeTab = ref('students')
const searchKeyword = ref('')
const onlyAbsent = ref(false)
const classInfo = ref({})
const studentList = ref([])
const changeHistory = ref([])

const filteredStudents = computed(() => {
  const keyword = searchKeyword.value.trim()
  return studentList.value.filter(student => {
    const matchKeyword = !keyword || (student.studentName || '').includes(keyword) || (student.phone || '').includes(keyword)
    const matchAbsent = !onlyAbsent.value || [3, 4].includes(Number(student.status))
    return matchKeyword && matchAbsent
  })
})

function getStatusTagType(statusName) {
  const typeMap = {
    到课: 'success',
    迟到: 'warning',
    请假: 'info',
    未到: 'danger'
  }
  return typeMap[statusName] || 'info'
}

async function loadDetail() {
  loading.value = true
  try {
    const response = await getAttendanceRecord(route.params.id)
    const data = response.data || {}
    classInfo.value = data
    studentList.value = (data.details || []).map(item => ({
      ...item,
      consumeType: item.consumeType || item.consumeMethod || '-',
      statusName: item.statusName || '-',
      makeupStatus: item.makeupStatus || '-',
      quota: item.quota || `${item.deductQuantity || 0}课时`
    }))
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function handleEditLesson() {
  proxy.$modal.msgInfo('编辑课次功能后续接入')
}

function handleLearningPlan() {
  proxy.$modal.msgInfo('布置学习计划功能后续接入')
}

function handleComment() {
  router.push({
    name: 'CommentDetail',
    params: { id: route.params.id }
  })
}

function handleAddTempStudent() {
  proxy.$modal.msgInfo('添加临时学员功能后续接入')
}

function handleAddMakeupStudent() {
  proxy.$modal.msgInfo('添加补课学员功能后续接入')
}

function handleModify(row) {
  proxy.$modal.msgInfo(`${row.studentName || ''} 的点名修改功能后续接入`)
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped lang="scss">
.page-title {
  font-size: 18px;
  font-weight: 600;
}

.course-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 18px;
  margin-bottom: 18px;
  border-bottom: 1px solid #ebeef5;

  h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }

  .action-buttons {
    display: flex;
    gap: 10px;
  }
}

.course-info {
  margin-bottom: 14px;

  .info-item {
    line-height: 28px;

    .label {
      margin-right: 8px;
      color: #909399;
    }
  }
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  .table-search {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.student-info {
  display: flex;
  flex-direction: column;
  line-height: 20px;

  .phone {
    color: #909399;
    font-size: 12px;
  }
}

.mb20 {
  margin-bottom: 20px;
}
</style>
