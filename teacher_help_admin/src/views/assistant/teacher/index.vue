<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="70px">
      <el-form-item label="老师" prop="teacherName">
        <el-input v-model="queryParams.teacherName" placeholder="老师姓名" clearable style="width: 180px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="queryParams.phone" placeholder="手机号" clearable style="width: 160px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 120px">
          <el-option v-for="(label, value) in statusLabels" :key="value" :label="label" :value="value" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['teach:teacher:add']">新增老师</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="warning" plain icon="Download" @click="handleExport" v-hasPermi="['teach:teacher:export']">导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="teacherList" border>
      <el-table-column label="老师" min-width="110">
        <template #default="{ row }">
          <el-link type="primary" @click="handleDetail(row)">{{ row.teacherName }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="手机号" prop="phone" width="130" align="center" />
      <el-table-column label="科目" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ (row.subjects || []).join('、') || '-' }}</template>
      </el-table-column>
      <el-table-column label="授课班级" width="90" align="center">
        <template #default="{ row }">{{ statOf(row).classCount ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="上月课时" width="110" align="center">
        <template #default="{ row }">{{ formatStat(statOf(row).lastMonthHours, statOf(row).lastMonthLessons) }}</template>
      </el-table-column>
      <el-table-column label="本月课时" width="110" align="center">
        <template #default="{ row }">{{ formatStat(statOf(row).thisMonthHours, statOf(row).thisMonthLessons) }}</template>
      </el-table-column>
      <el-table-column label="已上课时" width="110" align="center">
        <template #default="{ row }">{{ formatStat(statOf(row).totalHours, statOf(row).totalLessons) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="String(row.status) === '0' ? 'success' : 'info'">{{ statusLabels[row.status] || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" width="160" align="center" />
      <el-table-column label="操作" width="180" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleDetail(row)" v-hasPermi="['teach:teacher:query']">详情</el-button>
          <el-button link type="primary" @click="handleEdit(row)" v-hasPermi="['teach:teacher:edit']">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)" v-hasPermi="['teach:teacher:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <el-dialog v-model="open" :title="form.id ? '编辑老师' : '新增老师'" width="560px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="老师姓名" prop="teacherName">
          <el-input v-model="form.teacherName" maxlength="50" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" maxlength="11" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item v-if="!form.id" label="登录密码" prop="password">
          <el-input v-model="form.password" type="password" show-password maxlength="20" placeholder="6-20位，老师端登录使用" />
        </el-form-item>
        <el-form-item label="教学经验">
          <el-input-number v-model="form.workExperience" :min="0" :max="60" controls-position="right" />
          <span class="form-tip">年</span>
        </el-form-item>
        <el-form-item label="默认课时费">
          <el-input-number v-model="form.hourlyRate" :min="0" :precision="2" controls-position="right" />
          <span class="form-tip">元</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio v-for="(label, value) in statusLabels" :key="value" :value="value">{{ label }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="form.introduction" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="open = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantTeacher">
import { getCurrentInstance, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { addTeacher, delTeacher, getTeacher, getTeacherStats, listTeacher, updateTeacher } from '@/api/teach/teacher'

const { proxy } = getCurrentInstance()
const router = useRouter()

const statusLabels = { 0: '正常', 1: '停用', 2: '已注销' }

const queryParams = ref({ pageNum: 1, pageSize: 10, teacherName: undefined, phone: undefined, status: undefined })
const showSearch = ref(true)
const teacherList = ref([])
const statMap = ref({})
const total = ref(0)
const loading = ref(false)

async function getList() {
  loading.value = true
  try {
    const res = await listTeacher(queryParams.value)
    teacherList.value = res.rows || []
    total.value = res.total || 0
    statMap.value = {}
    const ids = teacherList.value.map(item => item.id).filter(Boolean)
    if (ids.length) {
      const statRes = await getTeacherStats(ids)
      statMap.value = Object.fromEntries((statRes.data || []).map(item => [item.teacherId, item]))
    }
  } finally {
    loading.value = false
  }
}

function statOf(row) {
  return statMap.value[row.id] || {}
}

function formatStat(hours, lessons) {
  if (hours === undefined) return '-'
  return `${hours}课时/${lessons}次`
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  proxy.resetForm('queryRef')
  handleQuery()
}

function handleDetail(row) {
  router.push(`/assistant/teacher/detail/${row.id}`)
}

// ---------------- 新增/编辑 ----------------
const open = ref(false)
const form = ref({})
const submitting = ref(false)
const rules = {
  teacherName: [{ required: true, message: '请输入老师姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入11位手机号', trigger: 'blur' }
  ],
  password: [{ required: true, min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }]
}

function handleAdd() {
  form.value = { teacherName: '', phone: '', password: '', workExperience: 0, hourlyRate: 0, status: '0', introduction: '', remark: '' }
  proxy.resetForm('formRef')
  open.value = true
}

async function handleEdit(row) {
  const res = await getTeacher(row.id)
  const data = res.data || {}
  form.value = {
    id: data.id,
    teacherName: data.teacherName,
    phone: data.phone || row.phone,
    workExperience: Number(data.workExperience || 0),
    hourlyRate: Number(data.hourlyRate || 0),
    status: data.status === undefined || data.status === null ? '0' : String(data.status),
    introduction: data.introduction || '',
    remark: data.remark || ''
  }
  open.value = true
}

function submitForm() {
  proxy.$refs.formRef.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      if (form.value.id) {
        const payload = { ...form.value }
        delete payload.phone
        await updateTeacher(payload)
        proxy.$modal.msgSuccess('修改成功')
      } else {
        await addTeacher(form.value)
        proxy.$modal.msgSuccess('新增成功')
      }
      open.value = false
      getList()
    } finally {
      submitting.value = false
    }
  })
}

function handleDelete(row) {
  proxy.$modal.confirm(`确认删除老师「${row.teacherName}」吗？`).then(async () => {
    await delTeacher(row.id)
    proxy.$modal.msgSuccess('删除成功')
    getList()
  }).catch(() => {})
}

function handleExport() {
  proxy.download('teach/teacher/export', { ...queryParams.value }, `teacher_${new Date().getTime()}.xlsx`)
}

onMounted(getList)
</script>

<style scoped>
.mb8 {
  margin-bottom: 8px;
}

.form-tip {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
