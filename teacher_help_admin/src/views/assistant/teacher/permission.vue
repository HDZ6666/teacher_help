<template>
  <div class="app-container">
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="mb12"
      title="为系统角色勾选“老师帮业务权限”下的页面与按钮（如给“老师”角色只开放课表、点名、点评）。只修改业务权限，角色在系统管理等其他菜单上的授权不变；新建角色、给员工分配角色请到“系统管理-角色管理/用户管理”。保存后该角色用户下次请求即按新权限校验。"
    />
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" header="角色">
          <el-table
            v-loading="roleLoading"
            :data="roleList"
            highlight-current-row
            border
            @current-change="handleSelectRole"
          >
            <el-table-column label="角色名称" prop="roleName" min-width="110" />
            <el-table-column label="权限字符" prop="roleKey" min-width="100" show-overflow-tooltip />
            <el-table-column label="业务按钮" width="100" align="center">
              <template #default="{ row }">{{ row.grantedCount }}/{{ row.totalCount }}</template>
            </el-table-column>
            <el-table-column label="状态" width="70" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === '0' ? 'success' : 'info'" size="small">{{ row.status === '0' ? '正常' : '停用' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>{{ currentRole ? `业务权限：${currentRole.roleName}` : '请选择左侧角色' }}</span>
              <div v-if="currentRole">
                <el-checkbox v-model="expandAll" @change="toggleExpand">展开/折叠</el-checkbox>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving"
                  :disabled="currentRole.isAdmin"
                  :title="currentRole.isAdmin ? '超级管理员拥有全部权限' : ''"
                  @click="handleSave"
                  v-hasPermi="['teach:teacher:permission']"
                >保存</el-button>
              </div>
            </div>
          </template>
          <div v-loading="treeLoading" class="tree-wrapper">
            <el-empty v-if="!currentRole" description="请选择角色" />
            <template v-else>
              <el-alert v-if="currentRole.isAdmin" type="warning" :closable="false" title="超级管理员拥有全部权限，不可修改" class="mb12" />
              <el-tree
                ref="treeRef"
                :data="menuTree"
                node-key="id"
                show-checkbox
                :default-expand-all="expandAll"
                :props="{ label: 'label', children: 'children', disabled: () => currentRole.isAdmin }"
              >
                <template #default="{ data }">
                  <span>{{ data.label }}</span>
                  <span v-if="data.perms" class="perms">{{ data.perms }}</span>
                </template>
              </el-tree>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="AssistantTeacherPermission">
import { getCurrentInstance, nextTick, onMounted, ref } from 'vue'
import { getRolePermission, listPermissionRoles, saveRolePermission } from '@/api/teach/teacherPermission'

const { proxy } = getCurrentInstance()
const roleLoading = ref(false)
const treeLoading = ref(false)
const saving = ref(false)
const roleList = ref([])
const currentRole = ref(null)
const menuTree = ref([])
const treeRef = ref(null)
const expandAll = ref(true)

async function loadRoles() {
  roleLoading.value = true
  try {
    const response = await listPermissionRoles()
    roleList.value = response.data || []
  } finally {
    roleLoading.value = false
  }
}

async function handleSelectRole(role) {
  if (!role) return
  currentRole.value = role
  treeLoading.value = true
  try {
    const response = await getRolePermission(role.roleId)
    const data = response.data || {}
    menuTree.value = data.menus || []
    await nextTick()
    treeRef.value?.setCheckedKeys(data.checkedKeys || [])
  } finally {
    treeLoading.value = false
  }
}

function toggleExpand(value) {
  const nodes = treeRef.value?.store?.nodesMap || {}
  Object.values(nodes).forEach(node => {
    node.expanded = value
  })
}

async function handleSave() {
  const menuIds = [...treeRef.value.getCheckedKeys(), ...treeRef.value.getHalfCheckedKeys()]
  saving.value = true
  try {
    const response = await saveRolePermission({ roleId: currentRole.value.roleId, menuIds })
    proxy.$modal.msgSuccess(response.msg || '保存成功')
    const roleId = currentRole.value.roleId
    await loadRoles()
    currentRole.value = roleList.value.find(item => item.roleId === roleId) || currentRole.value
  } finally {
    saving.value = false
  }
}

onMounted(loadRoles)
</script>

<style scoped>
.mb12 {
  margin-bottom: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header > div {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tree-wrapper {
  min-height: 300px;
  max-height: calc(100vh - 320px);
  overflow: auto;
}

.perms {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
