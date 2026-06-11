<template>
  <div class="app-container">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" class="mb20">
      <template #content>
        <span class="text-large font-600 mr-3">点名详情</span>
      </template>
    </el-page-header>

    <!-- 课程基本信息 -->
    <el-card class="mb20">
      <div class="course-header">
        <h2>{{ classInfo.className }} {{ classInfo.startTime }}~{{ classInfo.endTime }}</h2>
        <div class="action-buttons">
          <el-button type="warning" plain>编辑</el-button>
          <el-button type="primary" plain>拓展学习计划</el-button>
          <el-button type="success" plain>课堂点评</el-button>
        </div>
      </div>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课班级：</span>
            <span>{{ classInfo.className }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课时间：</span>
            <span>{{ classInfo.classDate }} {{ classInfo.startTime }}~{{ classInfo.endTime }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课老师：</span>
            <span>{{ classInfo.teacherName }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课班型：</span>
            <span>{{ classInfo.classType }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课教室：</span>
            <span>{{ classInfo.classroom }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课内容：</span>
            <span>{{ classInfo.content }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="course-info">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">学员可见文件：</span>
            <span>共0个文件</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">点名老师：</span>
            <span>{{ classInfo.attendanceTeacher }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">点名时间：</span>
            <span>{{ classInfo.attendanceTime }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab">
      <el-tab-pane label="学员名单" name="students">
        <!-- 搜索栏 -->
        <el-form :inline="true" class="mb20">
          <el-form-item>
            <el-input
              v-model="searchKeyword"
              placeholder="请输入学员姓名"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search">搜索</el-button>
          </el-form-item>
        </el-form>

        <!-- 统计信息 -->
        <div class="stats-bar mb20">
          <el-button type="text">添加到到课学员</el-button>
          <el-button type="text">添加未到课学员</el-button>
          <span class="stats-text">只看到到课学员</span>
        </div>

        <!-- 学员列表 -->
        <el-table :data="filteredStudents" border>
          <el-table-column label="姓名" align="center" width="150">
            <template #default="scope">
              <div class="student-info">
                <div class="name-with-tags">
                  <span>{{ scope.row.studentName }}</span>
                  <el-tag
                    v-for="tag in scope.row.tags"
                    :key="tag"
                    type="success"
                    size="small"
                    class="ml5"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                <div class="phone">{{ scope.row.phone }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="消耗方式" align="center" prop="consumeType" />
          <el-table-column label="到课状态" align="center" width="180">
            <template #default="scope">
              <div v-if="scope.row.editing" class="edit-status">
                <el-button
                  :type="scope.row.editStatus === '到课' ? 'warning' : ''"
                  size="small"
                  @click="scope.row.editStatus = '到课'"
                >
                  到课
                </el-button>
                <el-button
                  :type="scope.row.editStatus === '迟到' ? 'warning' : ''"
                  size="small"
                  @click="scope.row.editStatus = '迟到'"
                >
                  迟到
                </el-button>
                <el-button
                  :type="scope.row.editStatus === '请假' ? 'warning' : ''"
                  size="small"
                  @click="scope.row.editStatus = '请假'"
                >
                  请假
                </el-button>
                <el-button
                  :type="scope.row.editStatus === '未到' ? 'warning' : ''"
                  size="small"
                  @click="scope.row.editStatus = '未到'"
                >
                  未到
                </el-button>
              </div>
              <div v-else>
                <el-tag v-if="scope.row.status === '到课'" type="success">{{ scope.row.status }}</el-tag>
                <el-tag v-else-if="scope.row.status === '未到'" type="danger">{{ scope.row.status }}</el-tag>
                <el-tag v-else-if="scope.row.status === '请假'" type="info">{{ scope.row.status }}</el-tag>
                <el-tag v-else type="warning">{{ scope.row.status }}</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="补课状态" align="center" prop="makeupStatus" />
          <el-table-column label="扣课额度数" align="center" width="120">
            <template #default="scope">
              <el-input
                v-if="scope.row.editing"
                v-model="scope.row.editQuota"
                size="small"
                type="number"
                style="width: 80px"
              />
              <span v-else>{{ scope.row.quota }}</span>
            </template>
          </el-table-column>
          <el-table-column label="备注" align="center" width="150">
            <template #default="scope">
              <el-input
                v-if="scope.row.editing"
                v-model="scope.row.editRemark"
                size="small"
                placeholder="请输入备注"
              />
              <span v-else>{{ scope.row.remark || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="scope">
              <div v-if="scope.row.editing">
                <el-button type="warning" link size="small" @click="handleSave(scope.row)">保存</el-button>
                <el-button type="info" link size="small" @click="handleCancel(scope.row)">取消</el-button>
              </div>
              <el-button v-else type="primary" link size="small" @click="handleModify(scope.row)">修改</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="修改记录" name="history">
        <el-table :data="changeHistory" border v-if="changeHistory.length > 0">
          <el-table-column label="操作时间" align="center" prop="operateTime" width="180" />
          <el-table-column label="操作人" align="center" prop="operator" width="120" />
          <el-table-column label="账号" align="center" prop="account" width="150" />
          <el-table-column label="操作类型" align="center" prop="operateType" width="120" />
          <el-table-column label="修改内容" align="center" prop="changeContent" min-width="300" />
        </el-table>
        <el-empty v-else description="暂无修改记录" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup name="ClassRecordDetail">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 当前激活的tab
const activeTab = ref('students')

// 搜索关键词
const searchKeyword = ref('')

// 课程基本信息
const classInfo = ref({
  className: '托展训练班',
  classDate: '2025-11-03',
  startTime: '9:00',
  endTime: '10:00',
  teacherName: '叶老师',
  classType: '1课时',
  classroom: '1课时',
  content: '',
  attendanceTeacher: '黄老师',
  attendanceTime: '2025-11-05 14:53'
})

// 学员列表
const studentList = ref([
  {
    id: 1,
    studentName: '方泽南',
    phone: '158****8261',
    consumeType: '课程【托展训练】',
    status: '到课',
    makeupStatus: '-',
    quota: '1课时',
    remark: '',
    tags: ['满课'],
    editing: false,
    editStatus: '到课',
    editQuota: '1课时',
    editRemark: ''
  },
  {
    id: 2,
    studentName: '黄韵涵',
    phone: '164****4465',
    consumeType: '课程【托展训练】',
    status: '请假',
    makeupStatus: '待补课',
    quota: '0课时',
    remark: '',
    tags: ['满课'],
    editing: false,
    editStatus: '请假',
    editQuota: '0课时',
    editRemark: ''
  },
  {
    id: 3,
    studentName: '黄子馨',
    phone: '134****9512',
    consumeType: '课程【托展训练】',
    status: '请假',
    makeupStatus: '待补课',
    quota: '0课时',
    remark: '',
    tags: ['满课'],
    editing: false,
    editStatus: '请假',
    editQuota: '0课时',
    editRemark: ''
  },
  {
    id: 4,
    studentName: '林曼',
    phone: '188****9695',
    consumeType: '课程【托展训练】',
    status: '未到',
    makeupStatus: '待补课',
    quota: '0课时',
    remark: '',
    tags: [],
    editing: false,
    editStatus: '未到',
    editQuota: '0课时',
    editRemark: ''
  },
  {
    id: 5,
    studentName: '刘少明',
    phone: '152****9134',
    consumeType: '课程【托展训练】',
    status: '到课',
    makeupStatus: '-',
    quota: '1课时',
    remark: '',
    tags: [],
    editing: false,
    editStatus: '到课',
    editQuota: '1课时',
    editRemark: ''
  }
])

// 修改记录列表
const changeHistory = ref([
  {
    operateTime: '2025-11-07 16:45',
    operator: 'HDZ',
    account: '130****2483',
    operateType: '修改学员到课信息',
    changeContent:
      '原到课状态: "学员名称：方瑶南，方瑶南：到课，到课状态：1.00，课时金额：100，课时金额：1.04.21" 调整为 "学员名称：方瑶南，到课状态：到课，到课状态：2.00，课时金额：2.00，课时金额：208.42"'
  }
])

// 过滤后的学员列表
const filteredStudents = computed(() => {
  if (!searchKeyword.value) {
    return studentList.value
  }
  return studentList.value.filter(student =>
    student.studentName.includes(searchKeyword.value)
  )
})

// 返回上一页
function goBack() {
  router.back()
}

// 修改学员信息
function handleModify(row) {
  // 进入编辑模式
  row.editing = true
  // 初始化编辑值
  row.editStatus = row.status
  row.editQuota = row.quota
  row.editRemark = row.remark
}

// 保存修改
function handleSave(row) {
  // 构建修改内容描述
  const changes = []
  if (row.editStatus !== row.status) {
    changes.push(`到课状态：${row.status} → ${row.editStatus}`)
  }
  if (row.editQuota !== row.quota) {
    changes.push(`扣课额度数：${row.quota} → ${row.editQuota}`)
  }
  if (row.editRemark !== row.remark) {
    changes.push(`备注：${row.remark || '无'} → ${row.editRemark || '无'}`)
  }

  if (changes.length === 0) {
    ElMessage.warning('未检测到任何修改')
    row.editing = false
    return
  }

  // 保存修改
  row.status = row.editStatus
  row.quota = row.editQuota
  row.remark = row.editRemark
  row.editing = false

  // 添加修改记录
  const now = new Date()
  const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  changeHistory.value.unshift({
    operateTime: timeStr,
    operator: 'HDZ',
    account: '130****2483',
    operateType: '修改学员到课信息',
    changeContent: `学员名称：${row.studentName}，${changes.join('，')}`
  })

  ElMessage.success('修改成功')
}

// 取消修改
function handleCancel(row) {
  row.editing = false
  // 恢复原始值
  row.editStatus = row.status
  row.editQuota = row.quota
  row.editRemark = row.remark
}

// 组件挂载时获取详情数据
onMounted(() => {
  const recordId = route.params.id
  console.log('点名记录ID:', recordId)
  // TODO: 根据ID获取详情数据
})
</script>

<style scoped lang="scss">
.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;

  h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }

  .action-buttons {
    display: flex;
    gap: 10px;
  }
}

.course-info {
  margin-bottom: 15px;

  .info-item {
    line-height: 32px;

    .label {
      color: #909399;
      margin-right: 8px;
    }
  }
}

.stats-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;

  .stats-text {
    color: #606266;
    font-size: 14px;
  }
}

.student-info {
  .name-with-tags {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
  }

  .phone {
    color: #909399;
    font-size: 12px;
    margin-top: 4px;
  }
}

.ml5 {
  margin-left: 5px;
}

.mb20 {
  margin-bottom: 20px;
}

// 编辑状态样式
.edit-status {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  justify-content: center;

  :deep(.el-button) {
    margin: 0;
    padding: 5px 10px;
    font-size: 12px;

    &.el-button--warning {
      background-color: #e6a23c;
      border-color: #e6a23c;
      color: #fff;
    }
  }
}
</style>

