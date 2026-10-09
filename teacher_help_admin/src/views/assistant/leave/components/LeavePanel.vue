<template>
  <div>
    <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="80px">
      <el-form-item label="学员" prop="studentKeyword">
        <el-input v-model="queryParams.studentKeyword" placeholder="学员姓名" clearable style="width: 160px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="请假类型" prop="leaveType">
        <el-select v-model="queryParams.leaveType" placeholder="全部" clearable style="width: 110px">
          <el-option label="事假" :value="1" />
          <el-option label="病假" :value="2" />
          <el-option label="其他" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="leaveStatus">
        <el-select v-model="queryParams.leaveStatus" placeholder="全部" clearable style="width: 110px">
          <el-option label="待审批" :value="1" />
          <el-option label="已通过" :value="2" />
          <el-option label="已拒绝" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="请假日期">
        <el-date-picker v-model="dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="-" start-placeholder="开始" end-placeholder="结束" style="width: 240px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="applyOpen = true" v-hasPermi="['teach:leave:add']">给学员请假</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="RefreshLeft" :disabled="!selectedIds.length" @click="handleRevoke()" v-hasPermi="['teach:leave:remove']">撤销</el-button>
      </el-col>
      <right-toolbar :search="false" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="list" border @selection-change="rows => (selectedIds = rows.map(item => item.id))">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="学员" prop="studentName" width="100" align="center" />
      <el-table-column label="班级" prop="className" min-width="140" show-overflow-tooltip />
      <el-table-column label="课程" prop="courseName" min-width="120" show-overflow-tooltip />
      <el-table-column label="请假日期" prop="leaveDate" width="110" align="center" />
      <el-table-column label="类型" prop="leaveTypeName" width="70" align="center" />
      <el-table-column label="扣课" prop="isDeductName" width="60" align="center" />
      <el-table-column label="事由" prop="leaveReason" min-width="160" show-overflow-tooltip />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="{ 1: 'warning', 2: 'success', 3: 'info' }[row.leaveStatus]">{{ row.leaveStatusName }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="申请人" prop="applicantName" width="90" align="center" />
      <el-table-column label="申请时间" prop="applyTime" width="160" align="center" />
      <el-table-column label="审批" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.leaveStatus === 1">-</span>
          <span v-else>{{ row.approverName }} {{ row.approveTime }} {{ row.approveRemark || '' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.leaveStatus === 1" link type="primary" @click="handleApprove(row)" v-hasPermi="['teach:leave:edit']">审批</el-button>
          <el-button link type="danger" @click="handleRevoke(row)" v-hasPermi="['teach:leave:remove']">撤销</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <leave-apply-dialog v-model="applyOpen" @success="getList" />

    <el-dialog v-model="approveOpen" title="请假审批" width="480px" append-to-body>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="学员">{{ approveRow.studentName }}</el-descriptions-item>
        <el-descriptions-item label="班级/课程">{{ approveRow.className || '-' }} / {{ approveRow.courseName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="请假日期">{{ approveRow.leaveDate }}（{{ approveRow.leaveTypeName }}，{{ approveRow.isDeduct === 1 ? '扣课时' : '不扣课时' }}）</el-descriptions-item>
        <el-descriptions-item label="事由">{{ approveRow.leaveReason }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="approveForm" label-width="80px" class="mt16">
        <el-form-item label="审批结果">
          <el-radio-group v-model="approveForm.leaveStatus">
            <el-radio :value="2">通过</el-radio>
            <el-radio :value="3">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批备注">
          <el-input v-model="approveForm.approveRemark" type="textarea" :rows="2" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitApprove">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { getCurrentInstance, onMounted, ref } from 'vue'
import { approveLeaveApplication, delLeaveApplication, listLeaveApplication } from '@/api/assistant/classRecord'
import LeaveApplyDialog from './LeaveApplyDialog'

const { proxy } = getCurrentInstance()

const queryParams = ref({ pageNum: 1, pageSize: 10, studentKeyword: undefined, leaveType: undefined, leaveStatus: undefined })
const dateRange = ref([])
const list = ref([])
const total = ref(0)
const loading = ref(false)
const selectedIds = ref([])
const applyOpen = ref(false)
const submitting = ref(false)

async function getList() {
  loading.value = true
  try {
    const [beginTime, endTime] = dateRange.value || []
    const res = await listLeaveApplication({ ...queryParams.value, beginTime, endTime })
    list.value = res.rows || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryRef')
  dateRange.value = []
  handleQuery()
}

const approveOpen = ref(false)
const approveRow = ref({})
const approveForm = ref({ leaveStatus: 2, approveRemark: '' })

function handleApprove(row) {
  approveRow.value = row
  approveForm.value = { id: row.id, leaveStatus: 2, approveRemark: '' }
  approveOpen.value = true
}

async function submitApprove() {
  submitting.value = true
  try {
    const res = await approveLeaveApplication(approveForm.value)
    proxy.$modal.msgSuccess(res.msg || '审批完成')
    approveOpen.value = false
    getList()
  } finally {
    submitting.value = false
  }
}

function handleRevoke(row) {
  const ids = row ? [row.id] : selectedIds.value
  if (!ids.length) return
  proxy.$modal
    .confirm('确认撤销选中的请假申请吗？已通过且课次未点名的，课表考勤会恢复为“未到”；已点名的保留点名结果。')
    .then(async () => {
      await delLeaveApplication(ids.join(','))
      proxy.$modal.msgSuccess('撤销成功')
      getList()
    })
    .catch(() => {})
}

defineExpose({ getList })

onMounted(getList)
</script>

<style scoped>
.mb8 {
  margin-bottom: 8px;
}

.mt16 {
  margin-top: 16px;
}
</style>
