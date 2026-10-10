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
          <el-button type="warning" plain @click="openEditDialog" v-hasPermi="['teach:classRecord:edit']">编辑</el-button>
          <el-button plain disabled title="系统暂无学习计划数据模型，待产品确认学习计划内容后接入">布置学习计划</el-button>
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
            <el-button
              plain
              :disabled="!classInfo.eventId"
              :title="classInfo.eventId ? '' : '未关联排课课次的点名记录不能添加临时学员'"
              @click="tempDialogVisible = true"
              v-hasPermi="['teach:schedule:event:temp']"
            >添加临时学员</el-button>
            <span class="toolbar-tip">补课学员请在“上课记录-缺课补课”中勾选缺课记录后“开班补课”</span>
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
                <span>
                  {{ row.studentName }}
                  <el-tag v-if="row.isTemp === 1" size="small" type="info">临时</el-tag>
                  <el-tag v-if="row.makeupSourceId" size="small" type="info">补课</el-tag>
                </span>
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
              <el-button
                type="primary"
                link
                :disabled="row.makeupFlag === 1"
                :title="row.makeupFlag === 1 ? '该缺课记录已标记补课，不能修改点名' : ''"
                @click="openDetailDialog(row)"
                v-hasPermi="['teach:classRecord:editDetail']"
              >修改</el-button>
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

    <el-dialog v-model="detailDialogVisible" :title="`修改点名：${detailForm.studentName || ''}`" width="560px" append-to-body>
      <el-form ref="detailFormRef" :model="detailForm" :rules="detailRules" label-width="96px">
        <el-form-item label="当前">
          <span>{{ detailForm.currentText }}</span>
        </el-form-item>
        <el-form-item label="到课状态" prop="status">
          <el-radio-group v-model="detailForm.status" @change="handleDetailStatusChange">
            <el-radio-button :label="1">到课</el-radio-button>
            <el-radio-button :label="2">迟到</el-radio-button>
            <el-radio-button :label="3">请假</el-radio-button>
            <el-radio-button :label="4">未到</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="扣除额度">
          <el-input-number v-model="detailForm.deductQuantity" :min="0" :max="99" :disabled="!detailForm.courseAccountId" />
          <div class="form-tip">按新旧扣课差额自动退回或补扣课时；未到不扣课，请假仅已通过且标记扣课时的请假单扣课（后端判定）。</div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="detailForm.remark" maxlength="300" />
        </el-form-item>
        <el-form-item label="修改原因" prop="reason">
          <el-input v-model="detailForm.reason" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="detailDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitDetail">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑课次" width="620px" append-to-body>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="96px">
        <el-form-item label="上课日期" prop="classDate">
          <el-date-picker v-model="editForm.classDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="上课时间" required>
          <el-time-picker v-model="editForm.startTime" format="HH:mm" value-format="HH:mm" placeholder="开始" style="width: 45%" />
          <span class="range-sep">-</span>
          <el-time-picker v-model="editForm.endTime" format="HH:mm" value-format="HH:mm" placeholder="结束" style="width: 45%" />
        </el-form-item>
        <el-form-item label="上课老师">
          <el-select v-model="editForm.teacherId" filterable clearable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.teacherName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课教室">
          <el-input v-model="editForm.classroom" maxlength="100" />
        </el-form-item>
        <el-form-item label="授课课时" prop="lessonHours">
          <el-input-number v-model="editForm.lessonHours" :min="0.5" :max="99" :step="0.5" :precision="2" />
        </el-form-item>
        <el-form-item label="上课内容">
          <el-input v-model="editForm.content" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" maxlength="500" />
        </el-form-item>
        <div class="form-tip edit-tip">只修改本条上课记录（课时变化会同步班级已结课时），不改学员扣课，也不改排课课次；学员扣课请逐个“修改”。</div>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <TempStudentDialog
      v-model="tempDialogVisible"
      :event-id="classInfo.eventId"
      :attended="true"
      @success="loadDetail"
    />
  </div>
</template>

<script setup name="ClassRecordDetail">
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { parseTime } from '@/utils/ruoyi'
import { editAttendanceDetail, editAttendanceRecord, getAttendanceRecord } from '@/api/assistant/classRecord'
import { listTeacher } from '@/api/teach/teacher'
import TempStudentDialog from '@/components/TempStudentDialog/index.vue'

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
const submitting = ref(false)
const tempDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailFormRef = ref(null)
const detailForm = ref({})
const detailRules = {
  status: [{ required: true, message: '请选择到课状态', trigger: 'change' }],
  reason: [{ required: true, message: '请填写修改原因', trigger: 'blur' }]
}
const editDialogVisible = ref(false)
const editFormRef = ref(null)
const editForm = ref({})
const editRules = {
  classDate: [{ required: true, message: '请选择上课日期', trigger: 'change' }],
  lessonHours: [{ required: true, message: '请填写授课课时', trigger: 'change' }]
}
const teacherOptions = ref([])
const STATUS_TEXT = { 1: '到课', 2: '迟到', 3: '请假', 4: '未到' }

// 修改记录：后端在点名明细备注中追加“MM-DD HH:mm 操作人 修改点名：原→新，原因”
function buildChangeHistory(details) {
  const history = []
  details.forEach(item => {
    String(item.remark || '').split('；').forEach(segment => {
      const match = segment.match(/^(\d{2}-\d{2} \d{2}:\d{2}) (\S+) 修改点名：(.*)$/)
      if (match) {
        history.push({
          operateTime: match[1],
          operator: match[2],
          operateType: `修改点名（${item.studentName}）`,
          changeContent: match[3]
        })
      }
    })
  })
  return history.sort((a, b) => (a.operateTime < b.operateTime ? 1 : -1))
}

function openDetailDialog(row) {
  detailForm.value = {
    detailId: row.id,
    studentName: row.studentName,
    courseAccountId: row.courseAccountId,
    currentText: `${STATUS_TEXT[row.status] || '-'}，扣${row.deductQuantity || 0}`,
    status: row.status,
    deductQuantity: row.deductQuantity || 0,
    remark: '',
    reason: ''
  }
  detailDialogVisible.value = true
}

function handleDetailStatusChange(status) {
  if (status === 4) {
    detailForm.value.deductQuantity = 0
  } else if ([1, 2].includes(status) && !detailForm.value.deductQuantity && detailForm.value.courseAccountId) {
    detailForm.value.deductQuantity = 1
  }
}

function submitDetail() {
  detailFormRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      const form = detailForm.value
      const response = await editAttendanceDetail({
        detailId: form.detailId,
        status: form.status,
        deductQuantity: form.deductQuantity || 0,
        remark: form.remark || undefined,
        reason: form.reason
      })
      proxy.$modal.msgSuccess(response.msg || '修改成功')
      detailDialogVisible.value = false
      await loadDetail()
    } finally {
      submitting.value = false
    }
  })
}

async function openEditDialog() {
  const info = classInfo.value
  editForm.value = {
    id: info.id,
    classDate: info.classDate,
    startTime: info.startTime,
    endTime: info.endTime,
    teacherId: info.teacherId,
    classroom: info.classroom,
    lessonHours: Number(info.lessonHours || 1),
    content: info.content,
    remark: info.remark
  }
  editDialogVisible.value = true
  if (!teacherOptions.value.length) {
    const response = await listTeacher({ pageNum: 1, pageSize: 200 })
    teacherOptions.value = response.rows || []
  }
}

function submitEdit() {
  editFormRef.value.validate(async valid => {
    if (!valid) return
    const form = editForm.value
    if (!form.startTime || !form.endTime || form.endTime <= form.startTime) {
      proxy.$modal.msgWarning('请正确选择上课时间')
      return
    }
    submitting.value = true
    try {
      await editAttendanceRecord(form)
      proxy.$modal.msgSuccess('修改成功')
      editDialogVisible.value = false
      await loadDetail()
    } finally {
      submitting.value = false
    }
  })
}

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
    changeHistory.value = buildChangeHistory(data.details || [])
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function handleComment() {
  router.push({
    name: 'CommentDetail',
    params: { id: route.params.id }
  })
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
.toolbar-tip,
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
  line-height: 18px;
}

.edit-tip {
  padding-left: 86px;
}

.range-sep {
  margin: 0 6px;
}
</style>
