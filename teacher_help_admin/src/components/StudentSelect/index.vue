<template>
  <el-select
    :model-value="modelValue"
    filterable
    remote
    clearable
    reserve-keyword
    :remote-method="remoteSearch"
    :loading="loading"
    :placeholder="placeholder"
    :disabled="disabled"
    :style="{ width }"
    @update:model-value="handleChange"
    @visible-change="handleVisible"
  >
    <el-option v-for="item in options" :key="item.id" :label="item.studentName" :value="item.id">
      <span>{{ item.studentName }}</span>
      <span class="student-select__extra">{{ item.parentPhone || item.parentName || '' }}</span>
    </el-option>
  </el-select>
</template>

<script setup name="StudentSelect">
/**
 * 学员远程搜索下拉：按姓名调用 /teach/student/list，返回真实学员数据
 * v-model 为学员ID；change 事件额外返回学员对象（含 studentName / parentPhone）
 */
import { listStudent } from '@/api/teach/student'

const props = defineProps({
  modelValue: { type: [Number, String], default: undefined },
  // 编辑回显时传入当前学员姓名，避免下拉只显示ID
  initialLabel: { type: String, default: '' },
  placeholder: { type: String, default: '输入学员姓名搜索' },
  disabled: { type: Boolean, default: false },
  width: { type: String, default: '100%' }
})
const emit = defineEmits(['update:modelValue', 'change'])

const options = ref([])
const loading = ref(false)

watch(
  () => [props.modelValue, props.initialLabel],
  ([value, label]) => {
    if (value && label && !options.value.some(item => item.id === value)) {
      options.value = [{ id: value, studentName: label }, ...options.value]
    }
  },
  { immediate: true }
)

async function remoteSearch(keyword) {
  loading.value = true
  try {
    const res = await listStudent({ pageNum: 1, pageSize: 20, studentName: keyword || undefined })
    const rows = res.rows || []
    const current = options.value.find(item => item.id === props.modelValue)
    options.value = current && !rows.some(item => item.id === current.id) ? [current, ...rows] : rows
  } finally {
    loading.value = false
  }
}

function handleVisible(visible) {
  if (visible && options.value.length <= 1) {
    remoteSearch('')
  }
}

function handleChange(value) {
  emit('update:modelValue', value)
  emit('change', options.value.find(item => item.id === value) || null)
}
</script>

<style scoped>
.student-select__extra {
  float: right;
  margin-left: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
