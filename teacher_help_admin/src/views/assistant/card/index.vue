<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- ======================== 会员卡（卡类型） ======================== -->
      <el-tab-pane label="会员卡" name="card">
        <el-form :model="cardQuery" ref="cardQueryRef" :inline="true" v-show="showSearch" label-width="90px">
          <el-form-item label="搜索会员卡" prop="cardName">
            <el-input v-model="cardQuery.cardName" placeholder="请输入会员卡名称" clearable style="width: 220px" @keyup.enter="handleCardQuery" />
          </el-form-item>
          <el-form-item label="会员卡类型" prop="cardType">
            <el-select v-model="cardQuery.cardType" placeholder="全部" clearable style="width: 160px">
              <el-option v-for="item in cardTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="启用状态" prop="status">
            <el-select v-model="cardQuery.status" placeholder="全部" clearable style="width: 120px">
              <el-option label="启用" :value="1" />
              <el-option label="停用" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleCardQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetCardQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-dropdown v-hasPermi="['teach:card:add']" @command="handleCardAdd">
              <el-button type="primary" plain icon="Plus">新建会员卡<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="course">课程卡</el-dropdown-item>
                  <el-dropdown-item command="venue_discount">场地折扣卡</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-col>
          <el-col :span="1.5">
            <el-button type="danger" plain icon="Delete" :disabled="!cardIds.length" @click="handleCardDelete()" v-hasPermi="['teach:card:remove']">删除</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getCardList" />
        </el-row>

        <el-table v-loading="cardLoading" :data="cardList" border @selection-change="rows => (cardIds = rows.map(item => item.id))">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column label="会员卡名称" prop="cardName" min-width="150" show-overflow-tooltip />
          <el-table-column label="会员卡编号" prop="cardNo" min-width="170" show-overflow-tooltip />
          <el-table-column label="会员卡类型" align="center" width="110">
            <template #default="{ row }">
              <el-tag :type="row.cardType === 'course' ? 'danger' : 'warning'">{{ row.cardTypeName || row.cardType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="初始额度" align="center" width="110">
            <template #default="{ row }">
              <span v-if="row.cardType === 'course'">{{ row.initialCount || 0 }}次</span>
              <span v-else>{{ formatDiscount(row.discountRate) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="有效天数" align="center" width="100">
            <template #default="{ row }">{{ row.validDays ? `${row.validDays}天` : '不限' }}</template>
          </el-table-column>
          <el-table-column label="售价(元)" align="center" prop="price" width="100" />
          <el-table-column label="生效方式" align="center" prop="effectTypeName" width="120" />
          <el-table-column label="适用课程" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.cardType !== 'course'">-</span>
              <span v-else>{{ (row.courses || []).map(item => item.courseName).join('、') || '全部课程' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center" width="90">
            <template #default="{ row }">
              <el-switch
                v-model="row.status"
                :active-value="1"
                :inactive-value="0"
                :disabled="!canEditCard"
                @change="value => handleCardStatus(row, value)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="220" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleCardDetail(row)" v-hasPermi="['teach:card:query']">详情</el-button>
              <el-button link type="primary" @click="handleGrant(row)" v-hasPermi="['teach:card:grant']" :disabled="row.status !== 1">发放</el-button>
              <el-button link type="primary" @click="handleCardEdit(row)" v-hasPermi="['teach:card:edit']">编辑</el-button>
              <el-button link type="danger" @click="handleCardDelete(row)" v-hasPermi="['teach:card:remove']">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <pagination v-show="cardTotal > 0" :total="cardTotal" v-model:page="cardQuery.pageNum" v-model:limit="cardQuery.pageSize" @pagination="getCardList" />
      </el-tab-pane>

      <!-- ======================== 发放记录 ======================== -->
      <el-tab-pane label="发放记录" name="grant">
        <el-form :model="grantQuery" ref="grantQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="学员" prop="studentName">
            <el-input v-model="grantQuery.studentName" placeholder="学员姓名" clearable style="width: 180px" @keyup.enter="handleGrantQuery" />
          </el-form-item>
          <el-form-item label="会员卡" prop="cardName">
            <el-input v-model="grantQuery.cardName" placeholder="会员卡名称" clearable style="width: 180px" @keyup.enter="handleGrantQuery" />
          </el-form-item>
          <el-form-item label="卡状态" prop="grantStatus">
            <el-select v-model="grantQuery.grantStatus" placeholder="全部" clearable style="width: 120px">
              <el-option v-for="(label, value) in grantStatusLabels" :key="value" :label="label" :value="Number(value)" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleGrantQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetGrantQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleGrant()" v-hasPermi="['teach:card:grant']">发放会员卡</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getGrantList" />
        </el-row>

        <el-table v-loading="grantLoading" :data="grantList" border>
          <el-table-column label="卡号" prop="grantNo" min-width="170" show-overflow-tooltip />
          <el-table-column label="会员卡" prop="cardName" min-width="140" show-overflow-tooltip />
          <el-table-column label="类型" align="center" prop="cardTypeName" width="110" />
          <el-table-column label="持卡人" align="center" prop="studentName" width="110" />
          <el-table-column label="状态" align="center" width="90">
            <template #default="{ row }">
              <el-tag :type="grantStatusTag(row.grantStatus)">{{ row.grantStatusName }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="剩余/发放次数" align="center" width="120">
            <template #default="{ row }">
              <span v-if="row.cardType === 'course'">{{ row.remainingCount ?? 0 }} / {{ row.grantCount ?? 0 }}</span>
              <span v-else>{{ formatDiscount(row.discountRate) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="有效期" align="center" min-width="190">
            <template #default="{ row }">{{ formatValidRange(row) }}</template>
          </el-table-column>
          <el-table-column label="发放人" align="center" prop="operatorName" width="100" />
          <el-table-column label="发放时间" align="center" prop="grantTime" width="160" />
          <el-table-column label="操作" align="center" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleGrantLog(row)" v-hasPermi="['teach:card:list']">记录</el-button>
              <el-button
                v-if="row.cardType === 'course'"
                link
                type="primary"
                :disabled="row.grantStatus !== 1"
                @click="handleConsume(row)"
                v-hasPermi="['teach:card:consume']"
              >核销</el-button>
              <el-button link type="danger" :disabled="row.grantStatus === 4" @click="handleVoid(row)" v-hasPermi="['teach:card:grant']">作废</el-button>
            </template>
          </el-table-column>
        </el-table>
        <pagination v-show="grantTotal > 0" :total="grantTotal" v-model:page="grantQuery.pageNum" v-model:limit="grantQuery.pageSize" @pagination="getGrantList" />
      </el-tab-pane>

      <!-- ======================== 操作记录 ======================== -->
      <el-tab-pane label="操作记录" name="log">
        <el-form :model="logQuery" ref="logQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="操作类型" prop="action">
            <el-select v-model="logQuery.action" placeholder="全部" clearable style="width: 140px">
              <el-option v-for="(label, value) in actionLabels" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleLogQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetLogQuery">重置</el-button>
          </el-form-item>
          <el-form-item v-if="logQuery.grantId || logQuery.cardId">
            <el-tag closable @close="clearLogFilter">{{ logFilterLabel }}</el-tag>
          </el-form-item>
        </el-form>
        <card-log-table :loading="logLoading" :rows="logList" />
        <pagination v-show="logTotal > 0" :total="logTotal" v-model:page="logQuery.pageNum" v-model:limit="logQuery.pageSize" @pagination="getLogList" />
      </el-tab-pane>
    </el-tabs>

    <!-- 新建/编辑会员卡 -->
    <el-dialog v-model="cardOpen" :title="cardDialogTitle" width="640px" append-to-body>
      <el-form ref="cardFormRef" :model="cardForm" :rules="cardRules" label-width="110px">
        <el-form-item label="会员卡名称" prop="cardName">
          <el-input v-model="cardForm.cardName" maxlength="100" placeholder="请输入会员卡名称" />
        </el-form-item>
        <el-form-item label="会员卡类型">
          <el-radio-group v-model="cardForm.cardType" :disabled="!!cardForm.id">
            <el-radio v-for="item in cardTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="cardForm.cardType === 'course'">
          <el-form-item label="初始次数" prop="initialCount">
            <el-input-number v-model="cardForm.initialCount" :min="0" :max="99999" controls-position="right" />
            <span class="form-tip">次</span>
          </el-form-item>
          <el-form-item label="适用课程">
            <el-select v-model="cardForm.courseIds" multiple filterable clearable placeholder="不选表示不限课程" style="width: 100%">
              <el-option v-for="course in courseOptions" :key="course.id" :label="course.courseName" :value="course.id" />
            </el-select>
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="折扣" prop="discountRate">
            <el-input-number v-model="cardForm.discountRate" :min="0" :max="10" :precision="2" :step="0.1" controls-position="right" />
            <span class="form-tip">{{ discountTip }}</span>
          </el-form-item>
          <el-form-item label="适用场地">
            <span class="form-tip">当前版本不区分场地，任意场地均可使用（待产品确认）</span>
          </el-form-item>
        </template>
        <el-form-item label="有效天数" prop="validDays">
          <el-input-number v-model="cardForm.validDays" :min="0" :max="36500" controls-position="right" />
          <span class="form-tip">天，0 表示不限</span>
        </el-form-item>
        <el-form-item label="生效方式">
          <el-radio-group v-model="cardForm.effectType">
            <el-radio value="immediate">立即生效</el-radio>
            <el-radio value="first_use">首次使用后生效</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="售价(元)" prop="price">
          <el-input-number v-model="cardForm.price" :min="0" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="卡说明">
          <el-input v-model="cardForm.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-radio-group v-model="cardForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cardOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCard">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 会员卡详情 -->
    <el-dialog v-model="detailOpen" title="会员卡详情" width="760px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="会员卡名称">{{ detail.cardName }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.cardTypeName }}</el-descriptions-item>
        <el-descriptions-item label="编号">{{ detail.cardNo }}</el-descriptions-item>
        <el-descriptions-item label="售价">{{ detail.price }} 元</el-descriptions-item>
        <el-descriptions-item v-if="detail.cardType === 'course'" label="初始次数">{{ detail.initialCount }} 次</el-descriptions-item>
        <el-descriptions-item v-else label="折扣">{{ formatDiscount(detail.discountRate) }}</el-descriptions-item>
        <el-descriptions-item label="有效天数">{{ detail.validDays ? `${detail.validDays} 天` : '不限' }}</el-descriptions-item>
        <el-descriptions-item label="生效方式">{{ detail.effectTypeName }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detail.status === 1 ? '启用' : '停用' }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.cardType === 'course'" label="适用课程" :span="2">
          {{ (detail.courses || []).map(item => item.courseName).join('、') || '不限课程' }}
        </el-descriptions-item>
        <el-descriptions-item label="卡说明" :span="2">{{ detail.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="section-title">操作记录</div>
      <card-log-table :loading="detailLogLoading" :rows="detailLogs" />
    </el-dialog>

    <!-- 发放会员卡 -->
    <el-dialog v-model="grantOpen" title="发放会员卡" width="520px" append-to-body>
      <el-form ref="grantFormRef" :model="grantForm" :rules="grantRules" label-width="100px">
        <el-form-item label="会员卡" prop="cardId">
          <el-select v-model="grantForm.cardId" filterable placeholder="请选择启用中的会员卡" style="width: 100%" @change="handleGrantCardChange">
            <el-option v-for="card in enabledCards" :key="card.id" :label="`${card.cardName}（${card.cardTypeName}）`" :value="card.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学员" prop="studentId">
          <student-select v-model="grantForm.studentId" @change="student => (grantForm.studentName = student?.studentName)" />
        </el-form-item>
        <el-form-item v-if="selectedGrantCard?.cardType === 'course'" label="发放次数">
          <el-input-number v-model="grantForm.grantCount" :min="1" :max="99999" controls-position="right" />
          <span class="form-tip">默认取卡初始次数</span>
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="grantForm.validStartDate" type="date" value-format="YYYY-MM-DD" placeholder="不填按生效方式计算" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="grantForm.remark" type="textarea" :rows="2" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="grantOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitGrant">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 核销 -->
    <el-dialog v-model="consumeOpen" title="会员卡核销" width="480px" append-to-body>
      <el-form ref="consumeFormRef" :model="consumeForm" label-width="100px">
        <el-form-item label="会员卡">{{ consumeRow.cardName }}（{{ consumeRow.grantNo }}）</el-form-item>
        <el-form-item label="持卡人">{{ consumeRow.studentName }}</el-form-item>
        <el-form-item label="剩余次数">{{ consumeRow.remainingCount }}</el-form-item>
        <el-form-item label="上课课程">
          <el-select v-model="consumeForm.courseId" clearable filterable placeholder="选填，用于校验适用课程" style="width: 100%">
            <el-option v-for="course in courseOptions" :key="course.id" :label="course.courseName" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="核销次数">
          <el-input-number v-model="consumeForm.consumeCount" :min="1" :max="consumeRow.remainingCount || 1" controls-position="right" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="consumeForm.remark" type="textarea" :rows="2" maxlength="500" />
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon title="课程卡核销与班级点名扣课相互独立，不会自动联动（待产品确认）" />
      </el-form>
      <template #footer>
        <el-button @click="consumeOpen = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitConsume">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantCard">
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import {
  addCard,
  changeCardStatus,
  consumeCardGrant,
  delCard,
  getCard,
  grantCard,
  listCard,
  listCardGrant,
  listCardLog,
  updateCard,
  voidCardGrant
} from '@/api/teach/card'
import { listCourseOptions } from '@/api/assistant/course'
import StudentSelect from '@/components/StudentSelect'
import CardLogTable from './components/CardLogTable'
import auth from '@/plugins/auth'

const { proxy } = getCurrentInstance()

const cardTypeOptions = [
  { label: '课程卡', value: 'course' },
  { label: '场地折扣卡', value: 'venue_discount' }
]
const grantStatusLabels = { 1: '有效', 2: '过期', 3: '用完', 4: '作废' }
const actionLabels = { grant: '发放', consume: '消耗', void: '作废', expire: '过期' }

const activeTab = ref('card')
const showSearch = ref(true)
const submitting = ref(false)
const courseOptions = ref([])
const canEditCard = computed(() => auth.hasPermi('teach:card:edit'))

// ---------------- 会员卡 ----------------
const cardQuery = ref({ pageNum: 1, pageSize: 10, cardName: undefined, cardType: undefined, status: undefined })
const cardList = ref([])
const cardTotal = ref(0)
const cardLoading = ref(false)
const cardIds = ref([])
const cardOpen = ref(false)
const cardForm = ref({})
const cardDialogTitle = computed(() => `${cardForm.value.id ? '编辑' : '新建'}${cardForm.value.cardType === 'course' ? '课程卡' : '场地折扣卡'}`)
const discountTip = computed(() => {
  const rate = Number(cardForm.value.discountRate || 0)
  if (rate > 0 && rate <= 1) return `按比例：实付 ${Math.round(rate * 100)}%`
  if (rate > 1 && rate <= 10) return `按折数：${rate} 折`
  return '0~1 表示比例（0.8=八折），1~10 表示折数（8=八折）'
})
const cardRules = {
  cardName: [{ required: true, message: '请输入会员卡名称', trigger: 'blur' }],
  discountRate: [
    {
      validator: (rule, value, callback) => (Number(value) > 0 ? callback() : callback(new Error('请输入大于 0 的折扣'))),
      trigger: 'change'
    }
  ]
}

async function getCardList() {
  cardLoading.value = true
  try {
    const res = await listCard(cardQuery.value)
    cardList.value = res.rows || []
    cardTotal.value = res.total || 0
  } finally {
    cardLoading.value = false
  }
}

function handleCardQuery() {
  cardQuery.value.pageNum = 1
  getCardList()
}

function resetCardQuery() {
  proxy.resetForm('cardQueryRef')
  handleCardQuery()
}

function resetCardForm(cardType = 'course') {
  cardForm.value = {
    id: undefined,
    cardName: '',
    cardType,
    initialCount: cardType === 'course' ? 10 : 0,
    discountRate: cardType === 'course' ? 0 : 0.8,
    validDays: 365,
    effectType: 'immediate',
    price: 0,
    description: '',
    status: 1,
    courseIds: []
  }
  proxy.resetForm('cardFormRef')
}

function handleCardAdd(cardType) {
  resetCardForm(cardType)
  cardOpen.value = true
}

async function handleCardEdit(row) {
  const res = await getCard(row.id)
  const data = res.data || {}
  resetCardForm(data.cardType)
  cardForm.value = {
    ...cardForm.value,
    ...data,
    discountRate: Number(data.discountRate || 0),
    price: Number(data.price || 0),
    courseIds: (data.courses || []).map(item => item.courseId)
  }
  cardOpen.value = true
}

function submitCard() {
  proxy.$refs.cardFormRef.validate(async valid => {
    if (!valid) return
    const payload = { ...cardForm.value }
    payload.courses = payload.cardType === 'course'
      ? payload.courseIds.map(courseId => ({
        courseId,
        courseName: courseOptions.value.find(item => item.id === courseId)?.courseName
      }))
      : []
    if (payload.cardType !== 'course') {
      payload.initialCount = 0
    } else {
      payload.discountRate = 0
    }
    delete payload.courseIds
    submitting.value = true
    try {
      if (payload.id) {
        await updateCard(payload)
        proxy.$modal.msgSuccess('修改成功')
      } else {
        await addCard(payload)
        proxy.$modal.msgSuccess('新增成功')
      }
      cardOpen.value = false
      getCardList()
    } finally {
      submitting.value = false
    }
  })
}

async function handleCardStatus(row, value) {
  try {
    await changeCardStatus({ id: row.id, status: value })
    proxy.$modal.msgSuccess(value === 1 ? '已启用' : '已停用')
  } catch (error) {
    row.status = value === 1 ? 0 : 1
  }
}

function handleCardDelete(row) {
  const ids = row ? [row.id] : cardIds.value
  if (!ids.length) return
  proxy.$modal.confirm('确认删除选中的会员卡吗？已发放的记录不受影响。').then(async () => {
    await delCard(ids.join(','))
    proxy.$modal.msgSuccess('删除成功')
    getCardList()
  }).catch(() => {})
}

// 详情
const detailOpen = ref(false)
const detail = ref({})
const detailLogs = ref([])
const detailLogLoading = ref(false)

async function handleCardDetail(row) {
  const res = await getCard(row.id)
  detail.value = res.data || {}
  detailOpen.value = true
  detailLogLoading.value = true
  try {
    const logRes = await listCardLog({ pageNum: 1, pageSize: 50, cardId: row.id })
    detailLogs.value = logRes.rows || []
  } finally {
    detailLogLoading.value = false
  }
}

// ---------------- 发放记录 ----------------
const grantQuery = ref({ pageNum: 1, pageSize: 10, studentName: undefined, cardName: undefined, grantStatus: undefined })
const grantList = ref([])
const grantTotal = ref(0)
const grantLoading = ref(false)
const grantOpen = ref(false)
const grantForm = ref({})
const enabledCards = ref([])
const selectedGrantCard = computed(() => enabledCards.value.find(item => item.id === grantForm.value.cardId))
const grantRules = {
  cardId: [{ required: true, message: '请选择会员卡', trigger: 'change' }],
  studentId: [{ required: true, message: '请选择学员', trigger: 'change' }]
}

async function getGrantList() {
  grantLoading.value = true
  try {
    const res = await listCardGrant(grantQuery.value)
    grantList.value = res.rows || []
    grantTotal.value = res.total || 0
  } finally {
    grantLoading.value = false
  }
}

function handleGrantQuery() {
  grantQuery.value.pageNum = 1
  getGrantList()
}

function resetGrantQuery() {
  proxy.resetForm('grantQueryRef')
  handleGrantQuery()
}

async function handleGrant(row) {
  const res = await listCard({ pageNum: 1, pageSize: 200, status: 1 })
  enabledCards.value = res.rows || []
  grantForm.value = {
    cardId: row?.id,
    studentId: undefined,
    studentName: undefined,
    grantCount: row?.initialCount || undefined,
    validStartDate: undefined,
    remark: ''
  }
  proxy.resetForm('grantFormRef')
  grantOpen.value = true
}

function handleGrantCardChange() {
  grantForm.value.grantCount = selectedGrantCard.value?.initialCount || undefined
}

function submitGrant() {
  proxy.$refs.grantFormRef.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = { ...grantForm.value }
      if (selectedGrantCard.value?.cardType !== 'course') delete payload.grantCount
      await grantCard(payload)
      proxy.$modal.msgSuccess('发放成功')
      grantOpen.value = false
      if (activeTab.value === 'grant') getGrantList()
    } finally {
      submitting.value = false
    }
  })
}

// 核销
const consumeOpen = ref(false)
const consumeRow = ref({})
const consumeForm = ref({})

function handleConsume(row) {
  consumeRow.value = row
  consumeForm.value = { grantId: row.id, studentId: row.studentId, courseId: undefined, consumeCount: 1, remark: '' }
  consumeOpen.value = true
}

async function submitConsume() {
  submitting.value = true
  try {
    const res = await consumeCardGrant(consumeForm.value)
    proxy.$modal.msgSuccess(`核销成功，剩余 ${res.data?.remainingCount ?? '-'} 次`)
    consumeOpen.value = false
    getGrantList()
  } finally {
    submitting.value = false
  }
}

function handleVoid(row) {
  proxy.$modal.prompt(`确认作废「${row.studentName}」的「${row.cardName}」吗？剩余次数将清零，请输入作废原因`).then(async ({ value }) => {
    await voidCardGrant({ id: row.id, remark: value })
    proxy.$modal.msgSuccess('作废成功')
    getGrantList()
  }).catch(() => {})
}

function handleGrantLog(row) {
  logQuery.value = { pageNum: 1, pageSize: 10, action: undefined, grantId: row.id, cardId: undefined }
  logFilterLabel.value = `卡号：${row.grantNo}`
  activeTab.value = 'log'
  getLogList()
}

// ---------------- 操作记录 ----------------
const logQuery = ref({ pageNum: 1, pageSize: 10, action: undefined, grantId: undefined, cardId: undefined })
const logList = ref([])
const logTotal = ref(0)
const logLoading = ref(false)
const logFilterLabel = ref('')

async function getLogList() {
  logLoading.value = true
  try {
    const res = await listCardLog(logQuery.value)
    logList.value = res.rows || []
    logTotal.value = res.total || 0
  } finally {
    logLoading.value = false
  }
}

function handleLogQuery() {
  logQuery.value.pageNum = 1
  getLogList()
}

function resetLogQuery() {
  proxy.resetForm('logQueryRef')
  clearLogFilter()
}

function clearLogFilter() {
  logQuery.value.grantId = undefined
  logQuery.value.cardId = undefined
  logFilterLabel.value = ''
  handleLogQuery()
}

// ---------------- 公共 ----------------
function handleTabChange(name) {
  if (name === 'card') getCardList()
  if (name === 'grant') getGrantList()
  if (name === 'log') getLogList()
}

function formatDiscount(rate) {
  const value = Number(rate || 0)
  if (value > 0 && value <= 1) return `${Number((value * 10).toFixed(2))} 折`
  if (value > 1 && value <= 10) return `${value} 折`
  return '-'
}

function formatValidRange(row) {
  if (!row.validStartDate && !row.validEndDate) return '首次使用后生效 / 不限'
  return `${row.validStartDate || '-'} ~ ${row.validEndDate || '不限'}`
}

function grantStatusTag(status) {
  return { 1: 'success', 2: 'info', 3: 'warning', 4: 'danger' }[status] || 'info'
}

onMounted(async () => {
  getCardList()
  try {
    const res = await listCourseOptions()
    courseOptions.value = res.data || []
  } catch (error) {
    courseOptions.value = []
  }
})
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}

.form-tip {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.section-title {
  margin: 16px 0 8px;
  font-weight: 600;
}
</style>
