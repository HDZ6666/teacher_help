<template>
  <div class="attendance-container">
    <!-- 返回按钮 -->
    <div class="page-header">
      <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
      <span class="page-title">班级点名</span>
    </div>

    <!-- 课程信息卡片 -->
    <el-card class="course-info-card mb20">
      <div class="course-title">{{ courseInfo.courseName }}</div>
      <el-row :gutter="20" class="course-details">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课日期：</span>
            <el-date-picker
              v-model="courseInfo.classDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 200px"
            />
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课时间：</span>
            <el-time-picker
              v-model="courseInfo.startTime"
              placeholder="开始时间"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 100px"
            />
            <span style="margin: 0 5px">-</span>
            <el-time-picker
              v-model="courseInfo.endTime"
              placeholder="结束时间"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 100px"
            />
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课课程：</span>
            <el-select v-model="courseInfo.courseType" placeholder="请选择" style="width: 200px">
              <el-option label="齐" value="齐" />
              <el-option label="其他课程" value="其他" />
            </el-select>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" class="course-details">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课课时：</span>
            <el-input-number v-model="courseInfo.classHours" :min="1" style="width: 200px" />
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课教室：</span>
            <el-select v-model="courseInfo.classroom" placeholder="请选择" style="width: 200px">
              <el-option label="教室1" value="教室1" />
              <el-option label="教室2" value="教室2" />
            </el-select>
          </div>
        </el-col>
      </el-row>
      <div class="info-item">
        <span class="label">上课内容：</span>
        <el-input v-model="courseInfo.classContent" placeholder="请输入上课内容" style="width: 100%" />
      </div>
      <div class="info-item">
        <span class="label">学员可见文件：</span>
        <span>其它文字</span>
      </div>
    </el-card>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab">
      <!-- 添加时学员Tab -->
      <el-tab-pane label="添加时学员" name="addStudent">
        <div class="tab-toolbar">
          <el-button type="primary" @click="showAddTempStudentDialog">添加临时学员</el-button>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索学员姓名/手机号"
            clearable
            style="width: 300px; margin-left: 10px"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 学员列表表格 -->
        <el-table :data="filteredStudentList" border>
          <el-table-column label="姓名" align="center" width="200">
            <template #default="scope">
              <div class="student-info">
                <el-avatar :size="32" :src="scope.row.avatar">{{ scope.row.studentName.charAt(0) }}</el-avatar>
                <div class="student-detail">
                  <div class="name">{{ scope.row.studentName }}</div>
                  <div class="phone">{{ scope.row.phone }}</div>
                </div>
                <el-tag v-if="scope.row.tag" size="small" type="warning">{{ scope.row.tag }}</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="消耗方式" align="center" prop="consumeType" width="150" />
          <el-table-column label="到课状态" align="center" width="200">
            <template #default="scope">
              <div class="attendance-status">
                <el-button
                  :type="scope.row.attendanceStatus === '到课' ? 'success' : ''"
                  size="small"
                  @click="setAttendanceStatus(scope.row, '到课')"
                >到课</el-button>
                <el-button
                  :type="scope.row.attendanceStatus === '迟到' ? 'warning' : ''"
                  size="small"
                  @click="setAttendanceStatus(scope.row, '迟到')"
                >迟到</el-button>
                <el-button
                  :type="scope.row.attendanceStatus === '请假' ? 'info' : ''"
                  size="small"
                  @click="setAttendanceStatus(scope.row, '请假')"
                >请假</el-button>
                <el-button
                  :type="scope.row.attendanceStatus === '未到' ? 'danger' : ''"
                  size="small"
                  @click="setAttendanceStatus(scope.row, '未到')"
                >未到</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="补课状态" align="center" prop="makeupStatus" width="120" />
          <el-table-column label="配置额度数" align="center" width="150">
            <template #default="scope">
              <el-input-number v-model="scope.row.quota" :min="0" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="备注" align="center" min-width="150">
            <template #default="scope">
              <span>{{ scope.row.remark || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="100">
            <template #default="scope">
              <el-button type="primary" link size="small">修改</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 添加课学员Tab -->
      <el-tab-pane label="添加课学员" name="addCourseStudent">
        <el-empty description="暂无数据" />
      </el-tab-pane>
    </el-tabs>

    <!-- 底部统计和操作按钮 -->
    <div class="footer-section">
      <div class="statistics">
        <span class="stat-item">到课{{ arrivedCount }}人</span>
        <span class="stat-item">迟到{{ lateCount }}人</span>
        <span class="stat-item">请假{{ leaveCount }}人</span>
        <span class="stat-item">未到{{ absentCount }}人</span>
      </div>
      <div class="footer-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="danger" @click="handleSave">完成点名</el-button>
      </div>
    </div>

    <!-- 添加临时学员弹窗 -->
    <el-dialog
      v-model="tempStudentDialogVisible"
      title="添加临时学员"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="tempStudentTab">
        <!-- 关联课程学员Tab -->
        <el-tab-pane label="关联课程学员" name="relatedStudent">
          <div class="dialog-search">
            <el-input
              v-model="tempStudentSearch.keyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 200px"
            />
            <el-select
              v-model="tempStudentSearch.course"
              placeholder="请选择课程"
              clearable
              style="width: 150px; margin-left: 10px"
            >
              <el-option label="全部课程" value="" />
              <el-option label="蓝球课" value="蓝球课" />
              <el-option label="舞蹈课" value="舞蹈课" />
            </el-select>
            <el-select
              v-model="tempStudentSearch.class"
              placeholder="所在班级"
              clearable
              style="width: 150px; margin-left: 10px"
            >
              <el-option label="全部班级" value="" />
              <el-option label="A班" value="A班" />
              <el-option label="B班" value="B班" />
            </el-select>
            <el-button type="primary" style="margin-left: 10px">
              <el-icon><Search /></el-icon>
            </el-button>
          </div>

          <el-table :data="relatedStudentList" border max-height="400" style="margin-top: 20px">
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="姓名" prop="studentName" align="center" width="120" />
            <el-table-column label="手机号" prop="phone" align="center" width="150" />
            <el-table-column label="性别" prop="gender" align="center" width="80" />
            <el-table-column label="报名课程" prop="enrolledCourse" align="center" width="150" />
            <el-table-column label="剩余课时/天数" prop="remainingHours" align="center" width="150" />
            <el-table-column label="报名课程课次" prop="courseCount" align="center" width="120">
              <template #default="scope">
                <span :class="scope.row.courseCount === '不够次' ? 'text-danger' : ''">
                  {{ scope.row.courseCount }}
                </span>
              </template>
            </el-table-column>
          </el-table>

          <div class="dialog-footer">
            <span class="selected-count">已选择：{{ selectedRelatedStudents }}人</span>
          </div>
        </el-tab-pane>

        <!-- 会员卡学员Tab -->
        <el-tab-pane label="会员卡学员" name="memberStudent">
          <el-empty description="暂无数据" />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="tempStudentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddTempStudent">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="ClassAttendance">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 当前激活的Tab
const activeTab = ref('addStudent')

// 搜索关键词
const searchKeyword = ref('')

// 临时学员弹窗相关
const tempStudentDialogVisible = ref(false)
const tempStudentTab = ref('relatedStudent')
const selectedRelatedStudents = ref(0)

// 临时学员搜索条件
const tempStudentSearch = ref({
  keyword: '',
  course: '',
  class: ''
})

// 关联课程学员列表
const relatedStudentList = ref([
  {
    studentName: '张三',
    phone: '152****6231',
    gender: '男',
    enrolledCourse: '架子鼓',
    remainingHours: '30课时',
    courseCount: '不够次'
  }
])

// 课程信息
const courseInfo = ref({
  courseName: '测2',
  classDate: '2025-11-07',
  startTime: '14:40',
  endTime: '19:45',
  courseType: '齐',
  classHours: 1,
  classroom: '教室1',
  classContent: '其它文字',
  visibleFiles: '其它文字'
})

// 学员列表
const studentList = ref([
  {
    id: 1,
    studentName: '二分',
    phone: '123****8855',
    avatar: '',
    tag: '满课',
    consumeType: '课程【蓝球课7】',
    attendanceStatus: '到课',
    makeupStatus: '',
    quota: 1,
    remark: '测时'
  },
  {
    id: 2,
    studentName: '宁宁',
    phone: '187****5892',
    avatar: '',
    tag: '满课',
    consumeType: '课程【蓝球课7】',
    attendanceStatus: '迟到',
    makeupStatus: '请假',
    quota: 1,
    remark: '测时'
  },
  {
    id: 3,
    studentName: '张婷悦',
    phone: '186****5632',
    avatar: '',
    tag: '',
    consumeType: '课程【学子班】',
    attendanceStatus: '请假',
    makeupStatus: '请假',
    quota: 28,
    remark: '测时'
  }
])

// 过滤后的学员列表
const filteredStudentList = computed(() => {
  if (!searchKeyword.value) {
    return studentList.value
  }
  return studentList.value.filter(student =>
    student.studentName.includes(searchKeyword.value) ||
    student.phone.includes(searchKeyword.value)
  )
})

// 底部统计数据
const arrivedCount = computed(() => {
  return studentList.value.filter(s => s.attendanceStatus === '到课').length
})

const lateCount = computed(() => {
  return studentList.value.filter(s => s.attendanceStatus === '迟到').length
})

const leaveCount = computed(() => {
  return studentList.value.filter(s => s.attendanceStatus === '请假').length
})

const absentCount = computed(() => {
  return studentList.value.filter(s => s.attendanceStatus === '未到').length
})

// 搜索学员
function handleSearch() {
  // 搜索逻辑已在computed中处理
}

// 显示添加临时学员弹窗
function showAddTempStudentDialog() {
  tempStudentDialogVisible.value = true
}

// 添加临时学员
function handleAddTempStudent() {
  ElMessage.success('添加临时学员成功')
  tempStudentDialogVisible.value = false
}

// 设置到课状态
function setAttendanceStatus(row, status) {
  row.attendanceStatus = status
  ElMessage.success(`已将${row.studentName}的到课状态设置为：${status}`)
}

// 返回上一页
function goBack() {
  router.back()
}

// 取消
function handleCancel() {
  router.back()
}

// 送达人
function handleSendToParent() {
  const arrivedCount = studentList.value.filter(s => s.attendanceStatus === '到课').length
  ElMessage.success(`已送达${arrivedCount}人`)
}

// 确认人
function handleConfirmAttendance() {
  const confirmedCount = studentList.value.filter(s => s.attendanceStatus === '到课' || s.attendanceStatus === '迟到').length
  ElMessage.success(`已确认${confirmedCount}人`)
}

// 未到人
function handleAddStudent() {
  const absentCount = studentList.value.filter(s => s.attendanceStatus === '未到').length
  ElMessage.info(`未到${absentCount}人`)
}

// 完成点名
function handleSave() {
  ElMessage.success('点名完成！')
  setTimeout(() => {
    router.back()
  }, 1000)
}

// 组件挂载时获取数据
onMounted(() => {
  const classId = route.params.id
  console.log('班级ID:', classId)
  // TODO: 根据ID获取班级点名数据
})
</script>

<style scoped lang="scss">
.attendance-container {
  padding: 20px;

  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      font-size: 18px;
      font-weight: bold;
      margin-left: 10px;
    }
  }

  .course-info-card {
    .course-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 20px;
    }

    .course-details {
      margin-bottom: 15px;
    }

    .info-item {
      display: flex;
      align-items: center;
      margin-bottom: 15px;

      .label {
        min-width: 100px;
        color: #606266;
      }
    }
  }

  .tab-toolbar {
    margin-bottom: 20px;
  }

  .student-info {
    display: flex;
    align-items: center;
    gap: 10px;

    .student-detail {
      flex: 1;
      text-align: left;

      .name {
        font-weight: bold;
      }

      .phone {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .attendance-status {
    display: flex;
    gap: 5px;
    justify-content: center;
  }

  .footer-section {
    margin-top: 20px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 4px;

    .statistics {
      display: flex;
      gap: 30px;
      margin-bottom: 15px;
      padding-bottom: 15px;
      border-bottom: 1px solid #e4e7ed;

      .stat-item {
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }
    }

    .footer-actions {
      text-align: right;
    }
  }

  .dialog-search {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }

  .dialog-footer {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e4e7ed;
    text-align: left;

    .selected-count {
      font-size: 14px;
      color: #606266;
    }
  }

  .text-danger {
    color: #f56c6c;
  }
}
</style>

