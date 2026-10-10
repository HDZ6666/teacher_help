<template>
  <el-dialog :title="title" :model-value="modelValue" width="640px" append-to-body destroy-on-close @close="close">
    <el-alert type="info" :closable="false" show-icon class="mb8">
      <template #title>
        <div v-for="tip in tips" :key="tip">{{ tip }}</div>
      </template>
    </el-alert>
    <div class="import-actions">
      <el-button type="primary" link icon="Download" @click="downloadTemplate">下载导入模板</el-button>
    </div>
    <el-upload
      ref="uploadRef"
      drag
      :limit="1"
      accept=".xlsx,.xls"
      :auto-upload="false"
      :on-change="handleChange"
      :on-remove="() => (file = null)"
      :on-exceed="() => proxy.$modal.msgWarning('一次只能上传一个文件，请先移除已选文件')"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">将文件拖到此处，或<em>点击选择</em></div>
      <template #tip>
        <div class="el-upload__tip">仅支持 xls/xlsx，不超过 5MB；整表校验通过才会导入，任何一行有错都不会写入。</div>
      </template>
    </el-upload>

    <div v-if="result" class="import-result">
      <el-alert
        :type="result.success ? 'success' : 'error'"
        :closable="false"
        show-icon
        :title="result.success ? `导入成功：共 ${result.successCount} 行` : `校验未通过：${result.errorCount} 行有误，未导入任何数据`"
      />
      <el-table v-if="result.errors && result.errors.length" :data="result.errors" border max-height="260" class="mt8">
        <el-table-column label="Excel 行号" prop="row" width="100" align="center" />
        <el-table-column label="错误原因" prop="message" min-width="300" show-overflow-tooltip />
      </el-table>
    </div>

    <template #footer>
      <el-button @click="close">关 闭</el-button>
      <el-button type="primary" :loading="uploading" :disabled="!file" @click="submit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup name="ExcelImportDialog">
import { getCurrentInstance, ref, watch } from 'vue';
import { UploadFilled } from '@element-plus/icons-vue';
import { uploadImportFile } from '@/api/teach/studentAccount';

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '导入' },
  templateUrl: { type: String, required: true },
  templateName: { type: String, default: '导入模板.xlsx' },
  uploadUrl: { type: String, required: true },
  tips: { type: Array, default: () => [] }
});
const emit = defineEmits(['update:modelValue', 'success']);
const { proxy } = getCurrentInstance();

const file = ref(null);
const uploading = ref(false);
const result = ref(null);
const uploadRef = ref();

watch(() => props.modelValue, (visible) => {
  if (visible) {
    file.value = null;
    result.value = null;
  }
});

function close() {
  emit('update:modelValue', false);
}

function downloadTemplate() {
  proxy.download(props.templateUrl, {}, props.templateName);
}

function handleChange(uploadFile) {
  file.value = uploadFile.raw;
  result.value = null;
}

async function submit() {
  if (!file.value) return;
  uploading.value = true;
  try {
    const res = await uploadImportFile(props.uploadUrl, file.value);
    result.value = res.data || null;
    if (result.value && result.value.success) {
      proxy.$modal.msgSuccess(res.msg || '导入成功');
      uploadRef.value?.clearFiles();
      file.value = null;
      emit('success', result.value);
    } else {
      proxy.$modal.msgError(res.msg || '校验未通过，请按错误行修改后重新上传');
    }
  } finally {
    uploading.value = false;
  }
}
</script>

<style scoped>
.import-actions { margin: 8px 0; }
.import-result { margin-top: 12px; }
.mt8 { margin-top: 8px; }
</style>
