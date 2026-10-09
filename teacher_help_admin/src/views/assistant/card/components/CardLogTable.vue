<template>
  <el-table v-loading="loading" :data="rows" border>
    <el-table-column label="操作时间" prop="createTime" width="170" align="center" />
    <el-table-column label="操作" prop="actionName" width="90" align="center" />
    <el-table-column label="变动次数" prop="changeCount" width="90" align="center" />
    <el-table-column label="变动前" prop="beforeCount" width="80" align="center" />
    <el-table-column label="变动后" prop="afterCount" width="80" align="center" />
    <el-table-column label="备注" prop="remark" min-width="160" show-overflow-tooltip />
    <el-table-column label="操作人" prop="operatorName" width="100" align="center" />
  </el-table>
</template>

<script setup>
defineProps({
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})
</script>
