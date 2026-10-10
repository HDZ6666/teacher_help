<template>
  <el-dialog title="缴费收据" v-model="visible" width="760px" append-to-body destroy-on-close>
    <div v-loading="loading" ref="printRef" class="receipt">
      <h2 class="receipt-title">{{ orgTitle }} 收据</h2>
      <div class="receipt-meta">
        <span>收据编号：{{ receipt.orderNo || '-' }}</span>
        <span>经办日期：{{ receipt.enrollDate || '-' }}</span>
      </div>
      <div class="receipt-meta">
        <span>学员：{{ receipt.studentName || '-' }}</span>
        <span>联系电话：{{ receipt.parentPhone || '-' }}</span>
        <span>订单类型：{{ orderTypeName }}</span>
      </div>
      <table class="receipt-table">
        <thead>
          <tr>
            <th>项目</th>
            <th>规格/定价</th>
            <th>数量</th>
            <th>赠送</th>
            <th>单价(元)</th>
            <th>小计(元)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in receipt.items || []" :key="item.id">
            <td>{{ item.itemName }}</td>
            <td>{{ item.specName || item.packageName || '-' }}</td>
            <td>{{ item.quantity }}{{ item.unit || '' }}</td>
            <td>{{ item.giftQuantity || 0 }}{{ item.unit || '' }}</td>
            <td class="num">{{ money(item.unitPrice) }}</td>
            <td class="num">{{ money(item.subtotalPrice) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="receipt-sum">
        <span>订单总额：¥ {{ money(receipt.totalAmount) }}</span>
        <span>优惠：¥ {{ money(receipt.discountAmount) }}</span>
        <span>应收：¥ {{ money(receipt.receivableAmount) }}</span>
        <span>实收：¥ {{ money(receipt.paidAmount) }}</span>
        <span v-if="Number(receipt.debtAmount) > 0" class="debt">欠费：¥ {{ money(receipt.debtAmount) }}</span>
      </div>
      <div class="receipt-meta">
        <span>备注：{{ receipt.remark || '-' }}</span>
      </div>
      <div class="receipt-meta">
        <span>经办人：{{ receipt.createBy || '-' }}</span>
        <span>打印时间：{{ receipt.printTime || '-' }}</span>
        <span>收款方签章：</span>
      </div>
    </div>
    <template #footer>
      <el-button @click="visible = false">关 闭</el-button>
      <el-button type="primary" icon="Printer" :disabled="loading || !receipt.orderNo" @click="print">打 印</el-button>
    </template>
  </el-dialog>
</template>

<script setup name="ReceiptDialog">
import { computed, ref } from 'vue';
import { getOrderReceipt } from '@/api/teach/studentAccount';

const ORDER_TYPES = { enroll: '报名', renew: '续费', transfer: '转课', import: '导入' };
const orgTitle = import.meta.env.VITE_APP_TITLE || '老师帮';
const visible = ref(false);
const loading = ref(false);
const receipt = ref({});
const printRef = ref();
const orderTypeName = computed(() => ORDER_TYPES[receipt.value.orderType] || receipt.value.orderType || '-');

function money(value) {
  return Number(value || 0).toFixed(2);
}

async function open(orderId) {
  visible.value = true;
  loading.value = true;
  receipt.value = {};
  try {
    const res = await getOrderReceipt(orderId);
    receipt.value = res.data || {};
  } finally {
    loading.value = false;
  }
}

function print() {
  const html = printRef.value?.innerHTML || '';
  const win = window.open('', '_blank', 'width=900,height=700');
  if (!win) return;
  win.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>收据</title><style>
    body{font-family:sans-serif;padding:24px;color:#222}
    .receipt-title{text-align:center;margin:0 0 16px}
    .receipt-meta{display:flex;gap:32px;margin:8px 0;font-size:14px}
    .receipt-table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}
    .receipt-table th,.receipt-table td{border:1px solid #999;padding:6px 8px;text-align:left}
    .num{text-align:right}
    .receipt-sum{display:flex;gap:24px;justify-content:flex-end;font-size:14px;margin:8px 0}
    .debt{color:#c00}
  </style></head><body>${html}</body></html>`);
  win.document.close();
  win.focus();
  win.print();
}

defineExpose({ open });
</script>

<style scoped>
.receipt { padding: 8px 16px; color: #303133; }
.receipt-title { text-align: center; margin: 0 0 16px; }
.receipt-meta { display: flex; gap: 32px; margin: 8px 0; font-size: 14px; }
.receipt-table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }
.receipt-table th, .receipt-table td { border: 1px solid #dcdfe6; padding: 6px 8px; text-align: left; }
.receipt-table .num { text-align: right; }
.receipt-sum { display: flex; gap: 24px; justify-content: flex-end; font-size: 14px; margin: 8px 0; }
.receipt-sum .debt { color: #f56c6c; }
</style>
