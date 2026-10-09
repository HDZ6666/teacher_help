<template>
  <el-dialog :model-value="modelValue" title="代预订" width="560px" append-to-body @update:model-value="val => emit('update:modelValue', val)" @open="init">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="场地" prop="courtId">
        <el-select v-model="form.courtId" style="width: 100%" @change="refreshQuote">
          <el-option v-for="court in courts" :key="court.courtId" :label="court.courtName" :value="court.courtId" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期" prop="bookingDate">
        <el-date-picker v-model="form.bookingDate" type="date" value-format="YYYY-MM-DD" :clearable="false" style="width: 100%" @change="refreshQuote" />
      </el-form-item>
      <el-form-item label="时间" required>
        <el-time-select v-model="form.startTime" start="00:00" step="00:30" end="23:30" :clearable="false" style="width: 120px" @change="refreshQuote" />
        <span class="range-sep">至</span>
        <el-time-select v-model="form.endTime" start="00:30" step="00:30" end="24:00" :clearable="false" style="width: 120px" @change="refreshQuote" />
      </el-form-item>
      <el-form-item label="预订人类型">
        <el-radio-group v-model="customerType" @change="handleCustomerTypeChange">
          <el-radio value="student">学员</el-radio>
          <el-radio value="guest">非学员</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="customerType === 'student'" label="学员" prop="customerId">
        <student-select v-model="form.customerId" @change="handleStudentChange" />
      </el-form-item>
      <el-form-item label="姓名" prop="customerName">
        <el-input v-model="form.customerName" maxlength="50" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.customerPhone" maxlength="20" />
      </el-form-item>
      <el-form-item v-if="customerType === 'student'" label="场地折扣卡">
        <el-select v-model="form.cardGrantId" clearable placeholder="不使用" style="width: 100%" :disabled="!discountCards.length">
          <el-option
            v-for="card in discountCards"
            :key="card.id"
            :label="`${card.cardName}（${formatDiscount(card.discountRate)}，有效期至 ${card.validEndDate || '不限'}）`"
            :value="card.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="减免金额">
        <el-input-number v-model="form.discountAmount" :min="0" :max="quote.amount || 0" :precision="2" controls-position="right" />
        <span class="form-tip">人工减免，不含会员卡折扣</span>
      </el-form-item>
      <el-form-item label="支付状态">
        <el-radio-group v-model="form.payStatus">
          <el-radio :value="0">未付</el-radio>
          <el-radio :value="1">已付</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="500" />
      </el-form-item>
      <el-form-item label="应收金额">
        <span v-loading="quoteLoading" class="amount">¥ {{ quote.amount ?? '-' }}</span>
        <span v-if="quote.segments && quote.segments.length > 1" class="form-tip">
          {{ quote.segments.map(seg => `${seg.startTime}-${seg.endTime}${seg.priceRuleId ? '（分时价）' : ''}`).join('，') }}
        </span>
        <el-tag v-if="quote.available === false" type="danger" class="ml8">该时段已被占用</el-tag>
        <div class="form-tip block">金额由后端按场地价格计算；使用折扣卡时按（应收-减免）× 折扣计算优惠，以提交结果为准</div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取 消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确认预订</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { getCurrentInstance, ref } from 'vue'
import { addBooking, getBookingQuote } from '@/api/teach/venue'
import { listStudentCards } from '@/api/teach/card'
import StudentSelect from '@/components/StudentSelect'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  courts: { type: Array, default: () => [] },
  preset: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const form = ref({})
const customerType = ref('student')
const discountCards = ref([])
const quote = ref({})
const quoteLoading = ref(false)
const submitting = ref(false)
const rules = {
  courtId: [{ required: true, message: '请选择场地', trigger: 'change' }],
  bookingDate: [{ required: true, message: '请选择日期', trigger: 'change' }],
  customerId: [{ required: true, message: '请选择学员', trigger: 'change' }],
  customerName: [{ required: true, message: '请输入预订人姓名', trigger: 'blur' }]
}

function init() {
  form.value = {
    courtId: props.preset.courtId,
    bookingDate: props.preset.bookingDate,
    startTime: props.preset.startTime || '09:00',
    endTime: props.preset.endTime || '10:00',
    customerId: undefined,
    customerName: '',
    customerPhone: '',
    cardGrantId: undefined,
    discountAmount: 0,
    payStatus: 0,
    remark: ''
  }
  customerType.value = 'student'
  discountCards.value = []
  quote.value = {}
  proxy.resetForm('formRef')
  refreshQuote()
}

async function refreshQuote() {
  const { courtId, bookingDate, startTime, endTime } = form.value
  if (!courtId || !bookingDate || !startTime || !endTime || startTime >= endTime) {
    quote.value = {}
    return
  }
  quoteLoading.value = true
  try {
    const res = await getBookingQuote({ courtId, bookingDate, startTime, endTime })
    quote.value = res.data || {}
  } catch (error) {
    quote.value = {}
  } finally {
    quoteLoading.value = false
  }
}

function handleCustomerTypeChange() {
  form.value.customerId = undefined
  form.value.cardGrantId = undefined
  discountCards.value = []
}

async function handleStudentChange(student) {
  form.value.cardGrantId = undefined
  discountCards.value = []
  if (!student) return
  form.value.customerName = student.studentName
  form.value.customerPhone = student.parentPhone || form.value.customerPhone
  try {
    const res = await listStudentCards(student.id)
    discountCards.value = (res.data || []).filter(card => card.cardType === 'venue_discount' && card.grantStatus === 1)
  } catch (error) {
    discountCards.value = []
  }
}

function formatDiscount(rate) {
  const value = Number(rate || 0)
  if (value > 0 && value <= 1) return `${Number((value * 10).toFixed(2))}折`
  if (value > 1 && value <= 10) return `${value}折`
  return '-'
}

function submit() {
  proxy.$refs.formRef.validate(async valid => {
    if (!valid) return
    if (form.value.startTime >= form.value.endTime) {
      proxy.$modal.msgError('结束时间必须晚于开始时间')
      return
    }
    submitting.value = true
    try {
      const payload = { ...form.value, bookingType: 'normal', origin: 'admin' }
      if (customerType.value !== 'student') {
        payload.customerId = undefined
        payload.cardGrantId = undefined
      }
      const res = await addBooking(payload)
      const data = res.data || {}
      const paid = (Number(data.amount || 0) - Number(data.discountAmount || 0)).toFixed(2)
      proxy.$modal.msgSuccess(`预订成功：应收 ${data.amount} 元，优惠 ${data.discountAmount} 元，实收 ${paid} 元`)
      emit('update:modelValue', false)
      emit('success')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.range-sep {
  margin: 0 8px;
}

.amount {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-danger);
}

.form-tip {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.form-tip.block {
  display: block;
  margin-left: 0;
  line-height: 18px;
}

.ml8 {
  margin-left: 8px;
}
</style>
