<template>
  <div>
    <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="80px">
      <el-form-item label="场馆" prop="venueId">
        <el-select v-model="queryParams.venueId" placeholder="全部" clearable style="width: 160px">
          <el-option v-for="venue in venues" :key="venue.id" :label="venue.venueName" :value="venue.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="预订人" prop="customerName">
        <el-input v-model="queryParams.customerName" placeholder="姓名" clearable style="width: 140px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="手机号" prop="customerPhone">
        <el-input v-model="queryParams.customerPhone" placeholder="手机号" clearable style="width: 140px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="单号" prop="bookingNo">
        <el-input v-model="queryParams.bookingNo" placeholder="预订单号" clearable style="width: 180px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="类型" prop="bookingType">
        <el-select v-model="queryParams.bookingType" placeholder="全部" clearable style="width: 110px">
          <el-option label="预订" value="normal" />
          <el-option label="锁场" value="lock" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="bookingStatus">
        <el-select v-model="queryParams.bookingStatus" placeholder="全部" clearable style="width: 110px">
          <el-option v-for="(label, value) in BOOKING_STATUS" :key="value" :label="label" :value="Number(value)" />
        </el-select>
      </el-form-item>
      <el-form-item label="预订日期">
        <el-date-picker v-model="dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="-" start-placeholder="开始" end-placeholder="结束" style="width: 240px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table v-loading="loading" :data="list" border>
      <el-table-column label="单号" prop="bookingNo" min-width="170" show-overflow-tooltip />
      <el-table-column label="类型" prop="bookingTypeName" width="70" align="center" />
      <el-table-column label="场地" prop="courtName" min-width="110" show-overflow-tooltip />
      <el-table-column label="场次" min-width="170" align="center">
        <template #default="{ row }">{{ row.bookingDate }} {{ row.startTime }}-{{ row.endTime }}</template>
      </el-table-column>
      <el-table-column label="预订人" min-width="140" align="center">
        <template #default="{ row }">
          <span v-if="row.bookingType === 'lock'">{{ row.cancelReason || '-' }}</span>
          <span v-else>{{ row.customerName || '-' }} {{ row.customerPhone || '' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="实收(元)" width="100" align="center">
        <template #default="{ row }">{{ row.bookingType === 'lock' ? '-' : (Number(row.amount || 0) - Number(row.discountAmount || 0)).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="支付" prop="payStatusName" width="70" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="{ 1: 'primary', 2: 'success', 3: 'info' }[row.bookingStatus]">{{ row.bookingStatusName }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" prop="originName" width="80" align="center" />
      <el-table-column label="锁场批次" prop="lockGroupNo" min-width="150" show-overflow-tooltip />
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleDetail(row)" v-hasPermi="['teach:venue:query']">详情</el-button>
          <el-button v-if="row.bookingType !== 'lock' && row.bookingStatus === 1" link type="success" @click="handleVerify(row)" v-hasPermi="['teach:venue:edit']">核销</el-button>
          <el-button v-if="row.bookingStatus === 1" link type="danger" @click="handleCancel(row)" v-hasPermi="['teach:venue:edit']">
            {{ row.bookingType === 'lock' ? '解除' : '取消' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <booking-detail-dialog v-model="detailOpen" :booking-id="detailId" @changed="getList" />
    <cancel-booking-dialog v-model="cancelOpen" :booking="cancelRow" @success="getList" />
  </div>
</template>

<script setup>
import { getCurrentInstance, onMounted, ref } from 'vue'
import { listBooking, listVenue, verifyBooking } from '@/api/teach/venue'
import { BOOKING_STATUS } from '../utils'
import BookingDetailDialog from './BookingDetailDialog'
import CancelBookingDialog from './CancelBookingDialog'

const { proxy } = getCurrentInstance()

const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  venueId: undefined,
  customerName: undefined,
  customerPhone: undefined,
  bookingNo: undefined,
  bookingType: undefined,
  bookingStatus: undefined
})
const dateRange = ref([])
const venues = ref([])
const list = ref([])
const total = ref(0)
const loading = ref(false)

async function getList() {
  loading.value = true
  try {
    const [start, end] = dateRange.value || []
    const res = await listBooking({ ...queryParams.value, bookingDateStart: start, bookingDateEnd: end })
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

const detailOpen = ref(false)
const detailId = ref()
const cancelOpen = ref(false)
const cancelRow = ref({})

function handleDetail(row) {
  detailId.value = row.id
  detailOpen.value = true
}

function handleVerify(row) {
  proxy.$modal.confirm(`确认核销 ${row.customerName || ''} ${row.bookingDate} ${row.startTime}-${row.endTime} 的预订吗？`).then(async () => {
    await verifyBooking({ id: row.id })
    proxy.$modal.msgSuccess('核销成功')
    getList()
  }).catch(() => {})
}

function handleCancel(row) {
  cancelRow.value = row
  cancelOpen.value = true
}

function showLocks() {
  queryParams.value.bookingType = 'lock'
  queryParams.value.bookingStatus = 1
  handleQuery()
}

async function loadVenues() {
  const res = await listVenue({ pageNum: 1, pageSize: 100 })
  venues.value = res.rows || []
}

defineExpose({ getList, showLocks, loadVenues })

onMounted(() => {
  loadVenues()
  getList()
})
</script>
