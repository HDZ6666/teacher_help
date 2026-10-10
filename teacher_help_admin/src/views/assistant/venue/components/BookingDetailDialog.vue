<template>
  <el-dialog :model-value="modelValue" title="预订详情" width="640px" append-to-body @update:model-value="val => emit('update:modelValue', val)" @open="loadDetail">
    <div v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号" :span="2">{{ detail.bookingNo }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.bookingTypeName }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTag(detail.bookingStatus)">{{ detail.bookingStatusName }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="场地">{{ detail.courtName }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ detail.bookingDate }} {{ detail.startTime }}-{{ detail.endTime }}</el-descriptions-item>
        <template v-if="detail.bookingType !== 'lock'">
          <el-descriptions-item label="预订人">{{ detail.customerName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detail.customerPhone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="应收金额">{{ detail.amount }} 元</el-descriptions-item>
          <el-descriptions-item label="优惠金额">{{ detail.discountAmount }} 元</el-descriptions-item>
          <el-descriptions-item label="实收金额">{{ paidAmount }} 元</el-descriptions-item>
          <el-descriptions-item label="支付状态">{{ detail.payStatusName }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ detail.originName }}</el-descriptions-item>
          <el-descriptions-item label="会员卡">{{ detail.cardGrantId ? `发放记录 #${detail.cardGrantId}` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="核销时间">{{ detail.verifyTime || '-' }}</el-descriptions-item>
          <el-descriptions-item label="退款金额">{{ detail.refundAmount }} 元</el-descriptions-item>
        </template>
        <template v-else>
          <el-descriptions-item label="锁场批次" :span="2">{{ detail.lockGroupNo || '单次锁场' }}</el-descriptions-item>
        </template>
        <el-descriptions-item :label="detail.bookingType === 'lock' ? '锁场/解除原因' : '取消原因'" :span="2">{{ detail.cancelReason || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ detail.operatorName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.createTime }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </div>
    <template #footer>
      <el-button
        v-if="detail.bookingType !== 'lock' && detail.bookingStatus === 1"
        type="success"
        @click="handleVerify"
        v-hasPermi="['teach:venue:edit']"
      >核销</el-button>
      <el-button v-if="detail.bookingStatus === 1" type="danger" @click="handleCancel" v-hasPermi="['teach:venue:edit']">
        {{ detail.bookingType === 'lock' ? '解除锁场' : '取消预订' }}
      </el-button>
      <el-button
        v-if="detail.bookingType === 'lock' && detail.lockGroupNo && detail.bookingStatus === 1"
        type="danger"
        plain
        @click="handleCancelGroup"
        v-hasPermi="['teach:venue:edit']"
      >解除整个批次</el-button>
      <el-button @click="emit('update:modelValue', false)">关 闭</el-button>
    </template>

    <cancel-booking-dialog v-model="cancelOpen" :booking="detail" @success="handleChanged" />
  </el-dialog>
</template>

<script setup>
import { computed, getCurrentInstance, ref } from 'vue'
import { cancelLockGroup, getBooking, verifyBooking } from '@/api/teach/venue'
import CancelBookingDialog from './CancelBookingDialog'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  bookingId: { type: [Number, String], default: undefined }
})
const emit = defineEmits(['update:modelValue', 'changed'])
const { proxy } = getCurrentInstance()

const detail = ref({})
const loading = ref(false)
const cancelOpen = ref(false)
const paidAmount = computed(() => (Number(detail.value.amount || 0) - Number(detail.value.discountAmount || 0)).toFixed(2))

async function loadDetail() {
  if (!props.bookingId) return
  loading.value = true
  try {
    const res = await getBooking(props.bookingId)
    detail.value = res.data || {}
  } finally {
    loading.value = false
  }
}

function statusTag(status) {
  return { 1: 'primary', 2: 'success', 3: 'info' }[status] || 'info'
}

function handleVerify() {
  proxy.$modal.confirm('确认核销该预订吗？核销后不能取消。').then(async () => {
    await verifyBooking({ id: detail.value.id })
    proxy.$modal.msgSuccess('核销成功')
    handleChanged()
  }).catch(() => {})
}

function handleCancel() {
  cancelOpen.value = true
}

function handleCancelGroup() {
  proxy.$modal
    .confirm(`确认解除批次 ${detail.value.lockGroupNo} 中自 ${detail.value.bookingDate} 起所有未取消的锁场吗？`)
    .then(async () => {
      const res = await cancelLockGroup({ lockGroupNo: detail.value.lockGroupNo, fromDate: detail.value.bookingDate, cancelReason: '解除锁场' })
      proxy.$modal.msgSuccess(res.msg || '解除成功')
      handleChanged()
    })
    .catch(() => {})
}

function handleChanged() {
  loadDetail()
  emit('changed')
}
</script>
