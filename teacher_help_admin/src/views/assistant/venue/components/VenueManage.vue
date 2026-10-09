<template>
  <div>
    <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="80px">
      <el-form-item label="场馆名称" prop="venueName">
        <el-input v-model="queryParams.venueName" placeholder="请输入场馆名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleVenueAdd" v-hasPermi="['teach:venue:add']">新建场馆</el-button>
      </el-col>
      <right-toolbar :search="false" @queryTable="getList" />
    </el-row>

    <el-table v-loading="loading" :data="venueList" border row-key="id" @expand-change="handleExpand">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="court-panel">
            <div class="court-panel__toolbar">
              <span class="court-panel__title">{{ row.venueName }} 的场地</span>
              <el-button type="primary" link icon="Plus" @click="handleCourtAdd(row)" v-hasPermi="['teach:venue:add']">新增场地</el-button>
            </div>
            <el-table v-loading="courtLoading[row.id]" :data="courtMap[row.id] || []" border size="small">
              <el-table-column label="场地名称" prop="courtName" min-width="120" />
              <el-table-column label="类型" prop="courtType" width="100" align="center" />
              <el-table-column label="默认价格" width="170" align="center">
                <template #default="{ row: court }">{{ formatPrice(court) }}</template>
              </el-table-column>
              <el-table-column label="可约时段" min-width="220" show-overflow-tooltip>
                <template #default="{ row: court }">{{ formatTimes(court.times) }}</template>
              </el-table-column>
              <el-table-column label="分时价格" min-width="220" show-overflow-tooltip>
                <template #default="{ row: court }">{{ formatRules(court.priceRules) }}</template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row: court }">
                  <el-tag :type="court.status === 1 ? 'success' : 'info'">{{ court.status === 1 ? '启用' : '停用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="130" align="center">
                <template #default="{ row: court }">
                  <el-button link type="primary" @click="handleCourtEdit(row, court)" v-hasPermi="['teach:venue:edit']">编辑</el-button>
                  <el-button link type="danger" @click="handleCourtDelete(row, court)" v-hasPermi="['teach:venue:remove']">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="场馆名称" prop="venueName" min-width="150" />
      <el-table-column label="场馆编号" prop="venueNo" min-width="170" show-overflow-tooltip />
      <el-table-column label="地址" prop="address" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.status" :active-value="1" :inactive-value="0" :disabled="!canEdit" @change="value => handleVenueStatus(row, value)" />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" width="160" align="center" />
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleCourtAdd(row)" v-hasPermi="['teach:venue:add']">新增场地</el-button>
          <el-button link type="primary" @click="handleVenueEdit(row)" v-hasPermi="['teach:venue:edit']">编辑</el-button>
          <el-button link type="danger" @click="handleVenueDelete(row)" v-hasPermi="['teach:venue:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <!-- 场馆 -->
    <el-dialog v-model="venueOpen" :title="venueForm.id ? '编辑场馆' : '新建场馆'" width="560px" append-to-body>
      <el-form ref="venueFormRef" :model="venueForm" :rules="venueRules" label-width="90px">
        <el-form-item label="场馆名称" prop="venueName">
          <el-input v-model="venueForm.venueName" maxlength="100" />
        </el-form-item>
        <el-form-item label="场馆编号">
          <el-input v-model="venueForm.venueNo" maxlength="50" placeholder="不填自动生成" />
        </el-form-item>
        <el-form-item label="场馆地址">
          <el-input v-model="venueForm.address" maxlength="255" />
        </el-form-item>
        <el-form-item label="场馆介绍">
          <el-input v-model="venueForm.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="venueForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="venueForm.remark" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="venueOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitVenue">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 场地 -->
    <el-dialog v-model="courtOpen" :title="courtForm.id ? '编辑场地' : '新增场地'" width="860px" append-to-body>
      <el-form ref="courtFormRef" :model="courtForm" :rules="courtRules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="所属场馆" prop="venueId">
              <el-select v-model="courtForm.venueId" style="width: 100%">
                <el-option v-for="venue in venueList" :key="venue.id" :label="venue.venueName" :value="venue.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场地名称" prop="courtName">
              <el-input v-model="courtForm.courtName" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场地类型">
              <el-input v-model="courtForm.courtType" maxlength="50" placeholder="如 篮球 / 羽毛球" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="courtForm.status">
                <el-radio :value="1">启用</el-radio>
                <el-radio :value="0">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认小时价">
              <el-input-number v-model="courtForm.pricePerHour" :min="0" :precision="2" controls-position="right" />
              <span class="form-tip">元/小时</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认半小时价">
              <el-input-number v-model="courtForm.pricePerHalfHour" :min="0" :precision="2" controls-position="right" />
              <span class="form-tip">元/半小时，填写后优先按半小时计费</span>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="section-title">
          可约时段
          <el-button link type="primary" icon="Plus" @click="courtForm.timeGroups.push({ weekDays: [1, 2, 3, 4, 5, 6, 7], startTime: '08:00', endTime: '22:00' })">添加时段</el-button>
        </div>
        <el-table :data="courtForm.timeGroups" border size="small" empty-text="未设置时段：订场日历中所有时间均显示为可约">
          <el-table-column label="星期" min-width="300">
            <template #default="{ row }">
              <el-checkbox-group v-model="row.weekDays">
                <el-checkbox v-for="week in WEEK_OPTIONS" :key="week.value" :value="week.value">{{ week.label }}</el-checkbox>
              </el-checkbox-group>
            </template>
          </el-table-column>
          <el-table-column label="开始" width="130">
            <template #default="{ row }">
              <el-time-select v-model="row.startTime" start="00:00" step="00:30" end="23:30" :clearable="false" style="width: 110px" />
            </template>
          </el-table-column>
          <el-table-column label="结束" width="130">
            <template #default="{ row }">
              <el-time-select v-model="row.endTime" start="00:30" step="00:30" end="24:00" :clearable="false" style="width: 110px" />
            </template>
          </el-table-column>
          <el-table-column label="" width="60" align="center">
            <template #default="{ $index }">
              <el-button link type="danger" icon="Delete" @click="courtForm.timeGroups.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">
          分时价格
          <el-button link type="primary" icon="Plus" @click="courtForm.ruleGroups.push({ weekDays: [6, 7], startTime: '18:00', endTime: '22:00', pricePerHour: courtForm.pricePerHour, pricePerHalfHour: 0 })">添加价格规则</el-button>
          <span class="form-tip">规则覆盖的时段按规则价格计费，未覆盖的时段按默认价格；同一星期的规则时段不能重叠</span>
        </div>
        <el-table :data="courtForm.ruleGroups" border size="small" empty-text="未设置分时价格：全天按默认价格">
          <el-table-column label="星期" min-width="300">
            <template #default="{ row }">
              <el-checkbox-group v-model="row.weekDays">
                <el-checkbox v-for="week in WEEK_OPTIONS" :key="week.value" :value="week.value">{{ week.label }}</el-checkbox>
              </el-checkbox-group>
            </template>
          </el-table-column>
          <el-table-column label="开始" width="120">
            <template #default="{ row }">
              <el-time-select v-model="row.startTime" start="00:00" step="00:30" end="23:30" :clearable="false" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="结束" width="120">
            <template #default="{ row }">
              <el-time-select v-model="row.endTime" start="00:30" step="00:30" end="24:00" :clearable="false" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="元/小时" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.pricePerHour" :min="0" :precision="2" :controls="false" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="元/半小时" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.pricePerHalfHour" :min="0" :precision="2" :controls="false" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="" width="60" align="center">
            <template #default="{ $index }">
              <el-button link type="danger" icon="Delete" @click="courtForm.ruleGroups.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>

        <el-form-item label="备注" class="mt16">
          <el-input v-model="courtForm.remark" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="courtOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCourt">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, getCurrentInstance, onMounted, reactive, ref } from 'vue'
import {
  addCourt,
  addVenue,
  changeVenueStatus,
  delCourt,
  delVenue,
  getCourt,
  listCourt,
  listVenue,
  updateCourt,
  updateVenue
} from '@/api/teach/venue'
import auth from '@/plugins/auth'
import { WEEK_OPTIONS, expandWeekdays, groupByWeekdays, weekLabel } from '../utils'

const emit = defineEmits(['changed'])
const { proxy } = getCurrentInstance()
const canEdit = computed(() => auth.hasPermi('teach:venue:edit'))

const RULE_KEYS = ['startTime', 'endTime', 'pricePerHour', 'pricePerHalfHour']

const queryParams = ref({ pageNum: 1, pageSize: 10, venueName: undefined, status: undefined })
const venueList = ref([])
const total = ref(0)
const loading = ref(false)
const courtMap = reactive({})
const courtLoading = reactive({})
const submitting = ref(false)

async function getList() {
  loading.value = true
  try {
    const res = await listVenue(queryParams.value)
    venueList.value = res.rows || []
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
  handleQuery()
}

async function loadCourts(venueId) {
  courtLoading[venueId] = true
  try {
    const res = await listCourt({ venueId })
    courtMap[venueId] = res.data || []
  } finally {
    courtLoading[venueId] = false
  }
}

function handleExpand(row, expandedRows) {
  if (expandedRows.some(item => item.id === row.id)) loadCourts(row.id)
}

// ---------------- 场馆 ----------------
const venueOpen = ref(false)
const venueForm = ref({})
const venueRules = { venueName: [{ required: true, message: '请输入场馆名称', trigger: 'blur' }] }

function handleVenueAdd() {
  venueForm.value = { venueName: '', venueNo: '', address: '', description: '', status: 1, remark: '' }
  proxy.resetForm('venueFormRef')
  venueOpen.value = true
}

function handleVenueEdit(row) {
  venueForm.value = { ...row }
  venueOpen.value = true
}

function submitVenue() {
  proxy.$refs.venueFormRef.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      if (venueForm.value.id) {
        await updateVenue(venueForm.value)
        proxy.$modal.msgSuccess('修改成功')
      } else {
        await addVenue(venueForm.value)
        proxy.$modal.msgSuccess('新增成功')
      }
      venueOpen.value = false
      getList()
      emit('changed')
    } finally {
      submitting.value = false
    }
  })
}

async function handleVenueStatus(row, value) {
  try {
    await changeVenueStatus({ id: row.id, status: value })
    proxy.$modal.msgSuccess(value === 1 ? '已启用' : '已停用')
    emit('changed')
  } catch (error) {
    row.status = value === 1 ? 0 : 1
  }
}

function handleVenueDelete(row) {
  proxy.$modal.confirm(`确认删除场馆「${row.venueName}」吗？场馆下有场地时不能删除。`).then(async () => {
    await delVenue(row.id)
    proxy.$modal.msgSuccess('删除成功')
    getList()
    emit('changed')
  }).catch(() => {})
}

// ---------------- 场地 ----------------
const courtOpen = ref(false)
const courtForm = ref({ timeGroups: [], ruleGroups: [] })
const courtRules = {
  venueId: [{ required: true, message: '请选择场馆', trigger: 'change' }],
  courtName: [{ required: true, message: '请输入场地名称', trigger: 'blur' }]
}

function handleCourtAdd(venue) {
  courtForm.value = {
    venueId: venue.id,
    courtName: '',
    courtType: '',
    pricePerHour: 0,
    pricePerHalfHour: 0,
    status: 1,
    remark: '',
    timeGroups: [{ weekDays: [1, 2, 3, 4, 5, 6, 7], startTime: '08:00', endTime: '22:00' }],
    ruleGroups: []
  }
  proxy.resetForm('courtFormRef')
  courtOpen.value = true
}

async function handleCourtEdit(venue, court) {
  const res = await getCourt(court.id)
  const data = res.data || {}
  courtForm.value = {
    ...data,
    pricePerHour: Number(data.pricePerHour || 0),
    pricePerHalfHour: Number(data.pricePerHalfHour || 0),
    timeGroups: groupByWeekdays(data.times || []),
    ruleGroups: groupByWeekdays(
      (data.priceRules || []).map(rule => ({
        ...rule,
        pricePerHour: Number(rule.pricePerHour || 0),
        pricePerHalfHour: Number(rule.pricePerHalfHour || 0)
      })),
      RULE_KEYS
    )
  }
  courtOpen.value = true
}

function validateGroups(groups, name) {
  for (const group of groups) {
    if (!group.weekDays?.length) return `${name}请至少选择一个星期`
    if (!group.startTime || !group.endTime || group.startTime >= group.endTime) return `${name}的结束时间必须晚于开始时间`
  }
  return ''
}

function submitCourt() {
  proxy.$refs.courtFormRef.validate(async valid => {
    if (!valid) return
    const error = validateGroups(courtForm.value.timeGroups, '可约时段') || validateGroups(courtForm.value.ruleGroups, '价格规则')
    if (error) {
      proxy.$modal.msgError(error)
      return
    }
    const payload = { ...courtForm.value }
    payload.times = expandWeekdays(payload.timeGroups)
    payload.priceRules = expandWeekdays(payload.ruleGroups, RULE_KEYS)
    delete payload.timeGroups
    delete payload.ruleGroups
    submitting.value = true
    try {
      if (payload.id) {
        await updateCourt(payload)
        proxy.$modal.msgSuccess('修改成功')
      } else {
        await addCourt(payload)
        proxy.$modal.msgSuccess('新增成功')
      }
      courtOpen.value = false
      loadCourts(payload.venueId)
      emit('changed')
    } finally {
      submitting.value = false
    }
  })
}

function handleCourtDelete(venue, court) {
  proxy.$modal.confirm(`确认删除场地「${court.courtName}」吗？`).then(async () => {
    await delCourt(court.id)
    proxy.$modal.msgSuccess('删除成功')
    loadCourts(venue.id)
    emit('changed')
  }).catch(() => {})
}

// ---------------- 展示 ----------------
function formatPrice(court) {
  const parts = []
  if (Number(court.pricePerHalfHour) > 0) parts.push(`${court.pricePerHalfHour}元/半小时`)
  if (Number(court.pricePerHour) > 0) parts.push(`${court.pricePerHour}元/小时`)
  return parts.join('；') || '免费'
}

function formatWeekDays(days) {
  if (days.length === 7) return '每天'
  return days.map(weekLabel).join('、')
}

function formatTimes(times = []) {
  if (!times.length) return '未设置（不限）'
  return groupByWeekdays(times).map(group => `${formatWeekDays(group.weekDays)} ${group.startTime}-${group.endTime}`).join('；')
}

function formatRules(rules = []) {
  if (!rules.length) return '-'
  return groupByWeekdays(rules, RULE_KEYS)
    .map(group => {
      const price = Number(group.pricePerHalfHour) > 0 ? `${group.pricePerHalfHour}元/半小时` : `${group.pricePerHour}元/小时`
      return `${formatWeekDays(group.weekDays)} ${group.startTime}-${group.endTime} ${price}`
    })
    .join('；')
}

defineExpose({ getList })

onMounted(getList)
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}

.mt16 {
  margin-top: 16px;
}

.court-panel {
  padding: 8px 48px 12px;
}

.court-panel__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.court-panel__title,
.section-title {
  font-weight: 600;
}

.section-title {
  margin: 16px 0 8px;
}

.form-tip {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  font-weight: normal;
}
</style>
