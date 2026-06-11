<template>
  <div class="app-container schedule-container">
    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="schedule-tabs">
      <el-tab-pane label="时间课表" name="time"></el-tab-pane>
      <el-tab-pane label="老师课表" name="teacher"></el-tab-pane>
      <el-tab-pane label="教室课表" name="classroom"></el-tab-pane>
      <el-tab-pane label="班级课表" name="class"></el-tab-pane>
    </el-tabs>

    <!-- 时间课表内容 -->
    <div v-show="activeTab === 'time'" class="time-schedule">
      <!-- 筛选条件 -->
      <div class="filter-bar">
        <div class="filter-left">
          <span class="filter-label">所属课程：</span>
          <el-select v-model="queryParams.courseId" placeholder="请选择课程" clearable style="width: 150px;" @change="handleQuery">
            <el-option
              v-for="course in courseList"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>

          <span class="filter-label" style="margin-left: 20px;">上课班级：</span>
          <el-select v-model="queryParams.classId" placeholder="请选择班级" clearable style="width: 150px;" @change="handleQuery">
            <el-option
              v-for="cls in classList"
              :key="cls.id"
              :label="cls.name"
              :value="cls.id"
            />
          </el-select>

          <span class="filter-label" style="margin-left: 20px;">上课老师：</span>
          <el-select v-model="queryParams.teacherId" placeholder="请选择老师" clearable style="width: 150px;" @change="handleQuery">
            <el-option
              v-for="teacher in teacherList"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            />
          </el-select>
        </div>

        <div class="filter-right">
          <el-button type="warning" plain @click="handleAddSchedule">新增排课</el-button>
          <el-button type="primary" plain @click="handleBooking">约课</el-button>
          <el-dropdown @command="handleMoreAction">
            <el-button>
              更多操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="export">导出课表</el-dropdown-item>
                <el-dropdown-item command="print">打印课表</el-dropdown-item>
                <el-dropdown-item command="settings">课表设置</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 视图切换和日期导航 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="viewType" size="small" @change="handleViewChange">
            <el-radio-button label="day">日</el-radio-button>
            <el-radio-button label="week">周</el-radio-button>
            <el-radio-button label="month">月</el-radio-button>
          </el-radio-group>
        </div>

        <div class="toolbar-center">
          <el-button size="small" icon="ArrowLeft" @click="handlePrevious" />
          <span class="date-range">{{ dateRangeText }}</span>
          <el-button size="small" @click="handleNext">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>

        <div class="toolbar-right">
          <el-button size="small" icon="Bell" @click="handleReminder">活动提醒</el-button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="statistics">
        <span>共 <strong>{{ totalCount }}</strong> 节课，未点名 <strong>{{ unattendedCount }}</strong> 节课</span>
      </div>

      <!-- 课程表视图 -->
      <div class="schedule-wrapper">
        <CourseSchedule
          :courses="scheduleCourses"
          :view-mode="viewType"
          :dates="computedDates"
          :month="computedMonth"
          :cell-height="60"
          height="calc(100vh - 400px)"
          @view-detail="handleCourseDetail"
          @reschedule="handleCourseReschedule"
          @delete="handleCourseDelete"
        />
      </div>
    </div>

    <!-- 老师课表内容 -->
    <div v-show="activeTab === 'teacher'" class="teacher-schedule">
      <div class="teacher-schedule-layout">
        <!-- 左侧老师列表 -->
        <div class="teacher-list-panel">
          <div class="panel-header">
            <span class="panel-title">老师列表</span>
            <span class="teacher-count">共 {{ teacherList.length }} 位</span>
          </div>
          <div class="search-box">
            <el-input
              v-model="teacherSearchKeyword"
              placeholder="搜索老师姓名"
              clearable
              prefix-icon="Search"
              size="small"
            />
          </div>
          <div class="teacher-list">
            <div
              v-for="teacher in filteredTeacherList"
              :key="teacher.id"
              class="teacher-item"
              :class="{ active: selectedTeacherId === teacher.id }"
              @click="handleSelectTeacher(teacher.id)"
            >
              <div class="teacher-avatar">
                <el-avatar :size="40" :src="teacher.avatar">
                  {{ teacher.name.charAt(0) }}
                </el-avatar>
              </div>
              <div class="teacher-info">
                <div class="teacher-name">{{ teacher.name }}</div>
                <div class="teacher-meta">
                  <span class="course-count">{{ teacher.courseCount || 0 }}节课</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧课程表 -->
        <div class="schedule-panel">
          <!-- 工具栏 -->
          <div class="schedule-toolbar">
            <div class="toolbar-left">
              <el-radio-group v-model="teacherViewType" size="small" @change="handleTeacherViewChange">
                <el-radio-button label="week">周视图</el-radio-button>
                <el-radio-button label="month">月视图</el-radio-button>
              </el-radio-group>
            </div>

            <div class="toolbar-center">
              <el-button size="small" icon="ArrowLeft" @click="handleTeacherPrevious" />
              <span class="date-range">{{ teacherDateRangeText }}</span>
              <el-button size="small" @click="handleTeacherNext">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>

            <div class="toolbar-right">
              <el-button size="small" type="primary" @click="handleExportTeacherSchedule">导出课表</el-button>
            </div>
          </div>

          <!-- 课程表视图 -->
          <div class="schedule-content" v-if="selectedTeacherId">
            <CourseSchedule
              :courses="teacherScheduleCourses"
              :view-mode="teacherViewType"
              :dates="teacherComputedDates"
              :month="teacherComputedMonth"
              :cell-height="60"
              height="calc(100vh - 350px)"
              @view-detail="handleCourseDetail"
              @reschedule="handleCourseReschedule"
              @delete="handleCourseDelete"
            />
          </div>

          <!-- 未选择老师的提示 -->
          <div v-else class="empty-state">
            <el-empty description="请从左侧选择一位老师查看课表" />
          </div>
        </div>
      </div>
    </div>

    <!-- 教室课表内容 -->
    <div v-show="activeTab === 'classroom'" class="classroom-schedule">
      <div class="classroom-schedule-layout">
        <!-- 左侧教室列表 -->
        <div class="classroom-list-panel">
          <div class="panel-header">
            <span class="panel-title">教室列表</span>
            <span class="classroom-count">共 {{ classroomList.length }} 间</span>
          </div>
          <div class="search-box">
            <el-input
              v-model="classroomSearchKeyword"
              placeholder="搜索教室名称"
              clearable
              prefix-icon="Search"
              size="small"
            />
          </div>
          <div class="classroom-list">
            <div
              v-for="classroom in filteredClassroomList"
              :key="classroom.id"
              class="classroom-item"
              :class="{ active: selectedClassroomId === classroom.id }"
              @click="handleSelectClassroom(classroom.id)"
            >
              <div class="classroom-icon">
                <el-icon :size="32" color="#409EFF">
                  <OfficeBuilding />
                </el-icon>
              </div>
              <div class="classroom-info">
                <div class="classroom-name">{{ classroom.name }}</div>
                <div class="classroom-meta">
                  <span class="course-count">{{ classroom.courseCount || 0 }}节课</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧课程表 -->
        <div class="schedule-panel">
          <!-- 工具栏 -->
          <div class="schedule-toolbar">
            <div class="toolbar-left">
              <el-radio-group v-model="classroomViewType" size="small" @change="handleClassroomViewChange">
                <el-radio-button label="week">周视图</el-radio-button>
                <el-radio-button label="month">月视图</el-radio-button>
              </el-radio-group>
            </div>

            <div class="toolbar-center">
              <el-button size="small" icon="ArrowLeft" @click="handleClassroomPrevious" />
              <span class="date-range">{{ classroomDateRangeText }}</span>
              <el-button size="small" @click="handleClassroomNext">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>

            <div class="toolbar-right">
              <el-button size="small" type="primary" @click="handleExportClassroomSchedule">导出课表</el-button>
            </div>
          </div>

          <!-- 课程表视图 -->
          <div class="schedule-content" v-if="selectedClassroomId">
            <CourseSchedule
              :courses="classroomScheduleCourses"
              :view-mode="classroomViewType"
              :dates="classroomComputedDates"
              :month="classroomComputedMonth"
              :cell-height="60"
              height="calc(100vh - 350px)"
              @view-detail="handleCourseDetail"
              @reschedule="handleCourseReschedule"
              @delete="handleCourseDelete"
            />
          </div>

          <!-- 未选择教室的提示 -->
          <div v-else class="empty-state">
            <el-empty description="请从左侧选择一间教室查看课表" />
          </div>
        </div>
      </div>
    </div>

    <!-- 班级课表内容 -->
    <div v-show="activeTab === 'class'" class="class-schedule">
      <div class="class-schedule-layout">
        <!-- 左侧班级列表 -->
        <div class="class-list-panel">
          <div class="panel-header">
            <span class="panel-title">班级列表</span>
            <span class="class-count">共 {{ classList.length }} 个</span>
          </div>
          <div class="search-box">
            <el-input
              v-model="classSearchKeyword"
              placeholder="搜索班级名称"
              clearable
              prefix-icon="Search"
              size="small"
            />
          </div>
          <div class="class-list">
            <div
              v-for="cls in filteredClassList"
              :key="cls.id"
              class="class-item"
              :class="{ active: selectedClassId === cls.id }"
              @click="handleSelectClass(cls.id)"
            >
              <div class="class-icon">
                <el-icon :size="32" color="#67C23A">
                  <School />
                </el-icon>
              </div>
              <div class="class-info">
                <div class="class-name">{{ cls.name }}</div>
                <div class="class-meta">
                  <span class="course-count">{{ cls.courseCount || 0 }}节课</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧课程表 -->
        <div class="schedule-panel">
          <!-- 工具栏 -->
          <div class="schedule-toolbar">
            <div class="toolbar-left">
              <el-radio-group v-model="classViewType" size="small" @change="handleClassViewChange">
                <el-radio-button label="week">周视图</el-radio-button>
                <el-radio-button label="month">月视图</el-radio-button>
              </el-radio-group>
            </div>

            <div class="toolbar-center">
              <el-button size="small" icon="ArrowLeft" @click="handleClassPrevious" />
              <span class="date-range">{{ classDateRangeText }}</span>
              <el-button size="small" @click="handleClassNext">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>

            <div class="toolbar-right">
              <el-button size="small" type="primary" @click="handleExportClassSchedule">导出课表</el-button>
            </div>
          </div>

          <!-- 课程表视图 -->
          <div class="schedule-content" v-if="selectedClassId">
            <CourseSchedule
              :courses="classScheduleCourses"
              :view-mode="classViewType"
              :dates="classComputedDates"
              :month="classComputedMonth"
              :cell-height="60"
              height="calc(100vh - 350px)"
              @view-detail="handleCourseDetail"
              @reschedule="handleCourseReschedule"
              @delete="handleCourseDelete"
            />
          </div>

          <!-- 未选择班级的提示 -->
          <div v-else class="empty-state">
            <el-empty description="请从左侧选择一个班级查看课表" />
          </div>
        </div>
      </div>
    </div>

    <!-- 新增排课对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="800px" append-to-body>
      <el-form ref="scheduleFormRef" :model="scheduleForm" :rules="scheduleRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上课班级" prop="classId">
              <el-select v-model="scheduleForm.classId" placeholder="请选择班级" style="width: 100%;">
                <el-option
                  v-for="cls in classList"
                  :key="cls.id"
                  :label="cls.name"
                  :value="cls.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授课课程" prop="courseId">
              <el-select v-model="scheduleForm.courseId" placeholder="请选择课程" style="width: 100%;">
                <el-option
                  v-for="course in courseList"
                  :key="course.id"
                  :label="course.name"
                  :value="course.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上课老师" prop="teacherId">
              <el-select v-model="scheduleForm.teacherId" placeholder="请选择老师" style="width: 100%;">
                <el-option
                  v-for="teacher in teacherList"
                  :key="teacher.id"
                  :label="teacher.name"
                  :value="teacher.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上课教室" prop="classroomId">
              <el-select v-model="scheduleForm.classroomId" placeholder="请选择教室" style="width: 100%;">
                <el-option
                  v-for="room in classroomList"
                  :key="room.id"
                  :label="room.name"
                  :value="room.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startTime">
              <el-date-picker
                v-model="scheduleForm.startTime"
                type="datetime"
                placeholder="选择开始时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endTime">
              <el-date-picker
                v-model="scheduleForm.endTime"
                type="datetime"
                placeholder="选择结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="上课内容" prop="content">
          <el-input
            v-model="scheduleForm.content"
            type="textarea"
            :rows="3"
            placeholder="请输入上课内容"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmitSchedule">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 课程详情抽屉 -->
    <el-drawer
      v-model="courseDetailDrawerVisible"
      size="40%"
      destroy-on-close
    >
      <template #header>
        <div class="drawer-header">
          <span class="drawer-title">课程详情</span>
        </div>
      </template>

      <div v-if="selectedCourse" class="course-detail-drawer">
        <!-- 课程基本信息 -->
        <div class="detail-section">
          <div class="section-title">
            <span>基本信息</span>
            <div class="title-actions">
              <el-button type="primary" size="small" @click="handleEditCourse">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDeleteCourse">删除</el-button>
            </div>
          </div>
          <div class="detail-grid">
            <div class="detail-row">
              <span class="detail-label">课程名称：</span>
              <span class="detail-value">{{ selectedCourse.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">课程类型：</span>
              <span class="detail-value">{{ selectedCourse.courseName || selectedCourse.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">上课日期：</span>
              <span class="detail-value">{{ selectedCourse.date }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">上课时间：</span>
              <span class="detail-value">{{ selectedCourse.startTime }} - {{ selectedCourse.endTime }}</span>
            </div>
          </div>
        </div>

        <!-- 师资信息 -->
        <div class="detail-section">
          <div class="section-title">师资信息</div>
          <div class="detail-grid">
            <div class="detail-row">
              <span class="detail-label">授课老师：</span>
              <span class="detail-value">{{ selectedCourse.teacher || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">上课教室：</span>
              <span class="detail-value">{{ selectedCourse.classroom || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 学生信息 -->
        <div class="detail-section">
          <div class="section-title">
            <span>学生情况（{{ selectedCourse.studentCount || selectedCourse.students || 0 }}人）</span>
          </div>

          <!-- 学生名单表格 -->
          <div class="student-table-wrapper">
            <el-table
              :data="getStudentList(selectedCourse)"
              border
              stripe
              max-height="400"
              style="width: 100%"
            >
              <el-table-column type="index" label="序号" width="60" align="center" fixed />
              <el-table-column prop="name" label="学生姓名" width="100" align="center" fixed />
              <el-table-column prop="phone" label="手机号" width="120" align="center" />
              <el-table-column prop="consumeType" label="消耗方式" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.consumeType === '课时' ? 'primary' : 'warning'" size="small">
                    {{ row.consumeType }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remainingHours" label="剩余课时" width="100" align="center">
                <template #default="{ row }">
                  <span :class="{ 'low-hours': row.remainingHours < 5 }">
                    {{ row.remainingHours }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="attendanceStatus" label="到课状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    :type="getAttendanceTagType(row.attendanceStatus)"
                    size="small"
                  >
                    {{ row.attendanceStatus }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="makeupStatus" label="补课状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.makeupStatus"
                    :type="row.makeupStatus === '是' ? 'success' : 'info'"
                    size="small"
                  >
                    {{ row.makeupStatus }}
                  </el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="deductAmount" label="扣除额度" width="100" align="center">
                <template #default="{ row }">
                  <span class="deduct-amount">{{ row.deductAmount }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
            </el-table>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup name="AssistantSchedule">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowRight, OfficeBuilding, School } from '@element-plus/icons-vue'
import CourseSchedule from '@/components/CourseSchedule/index.vue'

// Tab状态
const activeTab = ref('time')

// 视图类型
const viewType = ref('week')

// 当前日期
const currentDate = ref(new Date())

// 筛选参数
const queryParams = ref({
  courseId: null,
  classId: null,
  teacherId: null
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增排课')
const scheduleFormRef = ref(null)

// 课程详情抽屉
const courseDetailDrawerVisible = ref(false)
const selectedCourse = ref(null)

// 表单数据
const scheduleForm = ref({
  classId: null,
  courseId: null,
  teacherId: null,
  classroomId: null,
  startTime: null,
  endTime: null,
  content: ''
})

// 表单验证规则
const scheduleRules = {
  classId: [{ required: true, message: '请选择上课班级', trigger: 'change' }],
  courseId: [{ required: true, message: '请选择授课课程', trigger: 'change' }],
  teacherId: [{ required: true, message: '请选择上课老师', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

// 课程数据
const scheduleCourses = ref([])

// 计算属性：根据视图类型生成日期数组
const computedDates = computed(() => {
  if (viewType.value === 'month') {
    return null // 月视图使用 month 参数
  }

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  if (viewType.value === 'day') {
    return [formatDate(currentDate.value)]
  }

  if (viewType.value === 'week') {
    const dates = []
    const start = new Date(currentDate.value)
    // 获取本周一
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(formatDate(date))
    }
    return dates
  }

  return []
})

// 计算属性：月视图的月份参数
const computedMonth = computed(() => {
  if (viewType.value !== 'month') {
    return null
  }
  const year = currentDate.value.getFullYear()
  const month = String(currentDate.value.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

// 计算属性：日期范围文本
const dateRangeText = computed(() => {
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }

  if (viewType.value === 'day') {
    return formatDate(currentDate.value)
  }

  if (viewType.value === 'week') {
    const start = new Date(currentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    const end = new Date(start)
    end.setDate(start.getDate() + 6)

    return `${formatDate(start)}~${formatDate(end).slice(5)}`
  }

  if (viewType.value === 'month') {
    const year = currentDate.value.getFullYear()
    const month = String(currentDate.value.getMonth() + 1).padStart(2, '0')
    return `${year}年${month}月`
  }

  return ''
})

// 统计数据
const totalCount = computed(() => scheduleCourses.value.length)
const unattendedCount = computed(() => Math.floor(scheduleCourses.value.length * 0.3))

// 模拟数据列表
const courseList = ref([
  { id: 1, name: '爵士舞' },
  { id: 2, name: '拉丁舞' },
  { id: 3, name: '芭蕾舞' },
  { id: 4, name: '街舞' }
])

const classList = ref([
  { id: 1, name: '爵士舞1班' },
  { id: 2, name: '爵士舞2班' },
  { id: 3, name: '拉丁舞1班' },
  { id: 4, name: '芭蕾舞1班' }
])

const teacherList = ref([
  { id: 1, name: '孟吉' },
  { id: 2, name: '忠贞' },
  { id: 3, name: '庆庆' },
  { id: 4, name: '李老师' }
])

const classroomList = ref([
  { id: 1, name: '爵士舞练习班' },
  { id: 2, name: '拉丁舞练习班' },
  { id: 3, name: '芭蕾舞练习班' },
  { id: 4, name: '多功能教室' }
])

// 老师课表相关数据
const selectedTeacherId = ref(null)
const teacherSearchKeyword = ref('')
const teacherViewType = ref('week')
const teacherCurrentDate = ref(new Date())
const teacherScheduleCourses = ref([])

// 过滤后的老师列表
const filteredTeacherList = computed(() => {
  if (!teacherSearchKeyword.value) {
    return teacherList.value
  }
  return teacherList.value.filter(teacher =>
    teacher.name.toLowerCase().includes(teacherSearchKeyword.value.toLowerCase())
  )
})

// 老师课表的日期数组
const teacherComputedDates = computed(() => {
  if (teacherViewType.value === 'month') {
    return null
  }

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  if (teacherViewType.value === 'week') {
    const dates = []
    const start = new Date(teacherCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(formatDate(date))
    }
    return dates
  }

  return []
})

// 老师课表的月份参数
const teacherComputedMonth = computed(() => {
  if (teacherViewType.value !== 'month') {
    return null
  }
  const year = teacherCurrentDate.value.getFullYear()
  const month = String(teacherCurrentDate.value.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

// 老师课表的日期范围文本
const teacherDateRangeText = computed(() => {
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }

  if (teacherViewType.value === 'week') {
    const start = new Date(teacherCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    const end = new Date(start)
    end.setDate(start.getDate() + 6)

    return `${formatDate(start)}~${formatDate(end).slice(5)}`
  }

  if (teacherViewType.value === 'month') {
    const year = teacherCurrentDate.value.getFullYear()
    const month = String(teacherCurrentDate.value.getMonth() + 1).padStart(2, '0')
    return `${year}年${month}月`
  }

  return ''
})

// 教室课表相关数据
const selectedClassroomId = ref(null)
const classroomSearchKeyword = ref('')
const classroomViewType = ref('week')
const classroomCurrentDate = ref(new Date())
const classroomScheduleCourses = ref([])

// 过滤后的教室列表
const filteredClassroomList = computed(() => {
  if (!classroomSearchKeyword.value) {
    return classroomList.value
  }
  return classroomList.value.filter(classroom =>
    classroom.name.toLowerCase().includes(classroomSearchKeyword.value.toLowerCase())
  )
})

// 教室课表的日期数组
const classroomComputedDates = computed(() => {
  if (classroomViewType.value === 'month') {
    return null
  }

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  if (classroomViewType.value === 'week') {
    const dates = []
    const start = new Date(classroomCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(formatDate(date))
    }
    return dates
  }

  return []
})

// 教室课表的月份参数
const classroomComputedMonth = computed(() => {
  if (classroomViewType.value !== 'month') {
    return null
  }
  const year = classroomCurrentDate.value.getFullYear()
  const month = String(classroomCurrentDate.value.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

// 教室课表的日期范围文本
const classroomDateRangeText = computed(() => {
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }

  if (classroomViewType.value === 'week') {
    const start = new Date(classroomCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    const end = new Date(start)
    end.setDate(start.getDate() + 6)

    return `${formatDate(start)}~${formatDate(end).slice(5)}`
  }

  if (classroomViewType.value === 'month') {
    const year = classroomCurrentDate.value.getFullYear()
    const month = String(classroomCurrentDate.value.getMonth() + 1).padStart(2, '0')
    return `${year}年${month}月`
  }

  return ''
})

// 班级课表相关数据
const selectedClassId = ref(null)
const classSearchKeyword = ref('')
const classViewType = ref('week')
const classCurrentDate = ref(new Date())
const classScheduleCourses = ref([])

// 过滤后的班级列表
const filteredClassList = computed(() => {
  if (!classSearchKeyword.value) {
    return classList.value
  }
  return classList.value.filter(cls =>
    cls.name.toLowerCase().includes(classSearchKeyword.value.toLowerCase())
  )
})

// 班级课表的日期数组
const classComputedDates = computed(() => {
  if (classViewType.value === 'month') {
    return null
  }

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  if (classViewType.value === 'week') {
    const dates = []
    const start = new Date(classCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(formatDate(date))
    }
    return dates
  }

  return []
})

// 班级课表的月份参数
const classComputedMonth = computed(() => {
  if (classViewType.value !== 'month') {
    return null
  }
  const year = classCurrentDate.value.getFullYear()
  const month = String(classCurrentDate.value.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

// 班级课表的日期范围文本
const classDateRangeText = computed(() => {
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }

  if (classViewType.value === 'week') {
    const start = new Date(classCurrentDate.value)
    const day = start.getDay()
    const diff = start.getDate() - day + (day === 0 ? -6 : 1)
    start.setDate(diff)

    const end = new Date(start)
    end.setDate(start.getDate() + 6)

    return `${formatDate(start)}~${formatDate(end).slice(5)}`
  }

  if (classViewType.value === 'month') {
    const year = classCurrentDate.value.getFullYear()
    const month = String(classCurrentDate.value.getMonth() + 1).padStart(2, '0')
    return `${year}年${month}月`
  }

  return ''
})

// 处理查询
function handleQuery() {
  console.log('查询参数:', queryParams.value)
  fetchEvents()
}

// 处理新增排课
function handleAddSchedule() {
  dialogTitle.value = '新增排课'
  scheduleForm.value = {
    classId: null,
    courseId: null,
    teacherId: null,
    classroomId: null,
    startTime: null,
    endTime: null,
    content: ''
  }
  dialogVisible.value = true
}

// 处理约课
function handleBooking() {
  ElMessage.info('约课功能开发中...')
}

// 处理更多操作
function handleMoreAction(command) {
  switch (command) {
    case 'export':
      ElMessage.info('导出课表功能开发中...')
      break
    case 'print':
      ElMessage.info('打印课表功能开发中...')
      break
    case 'settings':
      ElMessage.info('课表设置功能开发中...')
      break
  }
}

// 处理视图切换
function handleViewChange() {
  // 视图切换时不需要额外操作，computed 会自动更新
}

// 处理上一个时间段
function handlePrevious() {
  if (viewType.value === 'day') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 1))
  } else if (viewType.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 7))
  } else if (viewType.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1))
  }
}

// 处理下一个时间段
function handleNext() {
  if (viewType.value === 'day') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 1))
  } else if (viewType.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 7))
  } else if (viewType.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1))
  }
}

// 处理活动提醒
function handleReminder() {
  ElMessage.info('活动提醒功能开发中...')
}

// 提交排课表单
function handleSubmitSchedule() {
  scheduleFormRef.value.validate((valid) => {
    if (valid) {
      console.log('提交排课数据:', scheduleForm.value)
      // TODO: 调用API保存排课数据
      ElMessage.success('排课成功')
      dialogVisible.value = false
      fetchEvents()
    }
  })
}

// 查看课程详情
function handleCourseDetail(course) {
  console.log('查看课程详情:', course)
  selectedCourse.value = course
  courseDetailDrawerVisible.value = true
}

// 调课
function handleCourseReschedule(course) {
  console.log('调课:', course)
  ElMessage.info(`调课：${course.name}`)
  // TODO: 打开调课对话框
}

// 删除课程
function handleCourseDelete(course) {
  console.log('删除课程:', course)
  ElMessage.confirm(`确认删除课程"${course.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // TODO: 调用API删除课程
    ElMessage.success('删除成功')
    fetchEvents()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 编辑课程（从 drawer 中调用）
function handleEditCourse() {
  if (selectedCourse.value) {
    console.log('编辑课程:', selectedCourse.value)
    ElMessage.info(`编辑课程：${selectedCourse.value.name}`)
    // TODO: 打开编辑对话框或跳转到编辑页面
  }
}

// 删除课程（从 drawer 中调用）
function handleDeleteCourse() {
  if (selectedCourse.value) {
    ElMessage.confirm(`确认删除课程"${selectedCourse.value.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // TODO: 调用API删除课程
      ElMessage.success('删除成功')
      courseDetailDrawerVisible.value = false
      fetchEvents()
    }).catch(() => {
      ElMessage.info('已取消删除')
    })
  }
}

// 获取学生列表（将学生名单字符串转换为表格数据）
function getStudentList(course) {
  if (!course) return []

  // 如果课程对象中有完整的学生列表数据，直接返回
  if (course.studentList && Array.isArray(course.studentList)) {
    return course.studentList
  }

  // 否则从学生名单字符串生成模拟数据
  const studentNames = course.studentNames || course.studentList || ''
  if (!studentNames) return []

  // 将学生名单字符串按顿号或逗号分割
  const names = studentNames.split(/[、,，]/).filter(name => name.trim())

  // 转换为表格数据格式（包含所有字段）
  return names.map((name, index) => {
    // 生成模拟数据
    const consumeTypes = ['课时', '次卡']
    const attendanceStatuses = ['已到课', '未到课', '请假', '旷课']
    const makeupStatuses = ['是', '否', null]

    const consumeType = consumeTypes[index % 2]
    const remainingHours = Math.floor(Math.random() * 20) + 1 // 1-20
    const attendanceStatus = attendanceStatuses[index % 4]
    const makeupStatus = makeupStatuses[index % 3]
    const deductAmount = consumeType === '课时' ? '1课时' : '1次'

    return {
      id: index + 1,
      name: name.trim(),
      phone: `138****${String(1000 + index).slice(-4)}`, // 模拟手机号
      consumeType: consumeType,
      remainingHours: remainingHours,
      attendanceStatus: attendanceStatus,
      makeupStatus: makeupStatus,
      deductAmount: deductAmount,
      remark: index % 3 === 0 ? '需要重点关注' : ''
    }
  })
}

// 获取到课状态标签类型
function getAttendanceTagType(status) {
  const typeMap = {
    '已到课': 'success',
    '未到课': 'info',
    '请假': 'warning',
    '旷课': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取课程数据
function fetchEvents() {
  // 获取当前周的日期范围
  const today = new Date()
  const currentWeekStart = new Date(today)
  currentWeekStart.setDate(today.getDate() - today.getDay() + 1) // 本周一

  // 格式化日期为 YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // 生成本周的日期
  const weekDates = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart)
    date.setDate(currentWeekStart.getDate() + i)
    weekDates.push(formatDate(date))
  }

  // 颜色配置
  const colors = [
    '#67C23A', // 绿色
    '#409EFF', // 蓝色
    '#E6A23C', // 橙色
    '#F56C6C', // 红色
    '#909399', // 灰色
    '#9C27B0', // 紫色
  ]

  const mockCourses = []
  let courseId = 1

  // 为本周每天添加一些课程
  weekDates.forEach((date) => {
    // 每天上午 09:00-10:30 添加 2-3 个课程
    const morningCourseCount = 2 + Math.floor(Math.random() * 2)
    for (let i = 0; i < morningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7) // 8-14人
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '09:00',
        endTime: '10:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }

    // 每天下午 14:00-15:30 添加 2-4 个课程
    const afternoonCourseCount = 2 + Math.floor(Math.random() * 3)
    for (let i = 0; i < afternoonCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7) // 8-14人
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '14:00',
        endTime: '15:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }
  })

  scheduleCourses.value = mockCourses
}

// 老师课表相关方法
// 选择老师
function handleSelectTeacher(teacherId) {
  selectedTeacherId.value = teacherId
  fetchTeacherSchedule()
}

// 老师视图切换
function handleTeacherViewChange() {
  // 视图切换时重新加载数据
  fetchTeacherSchedule()
}

// 老师课表上一个时间段
function handleTeacherPrevious() {
  if (teacherViewType.value === 'week') {
    teacherCurrentDate.value = new Date(teacherCurrentDate.value.setDate(teacherCurrentDate.value.getDate() - 7))
  } else if (teacherViewType.value === 'month') {
    teacherCurrentDate.value = new Date(teacherCurrentDate.value.setMonth(teacherCurrentDate.value.getMonth() - 1))
  }
  fetchTeacherSchedule()
}

// 老师课表下一个时间段
function handleTeacherNext() {
  if (teacherViewType.value === 'week') {
    teacherCurrentDate.value = new Date(teacherCurrentDate.value.setDate(teacherCurrentDate.value.getDate() + 7))
  } else if (teacherViewType.value === 'month') {
    teacherCurrentDate.value = new Date(teacherCurrentDate.value.setMonth(teacherCurrentDate.value.getMonth() + 1))
  }
  fetchTeacherSchedule()
}

// 导出老师课表
function handleExportTeacherSchedule() {
  if (!selectedTeacherId.value) {
    ElMessage.warning('请先选择一位老师')
    return
  }
  ElMessage.info('导出老师课表功能开发中...')
}

// 获取老师课表数据
function fetchTeacherSchedule() {
  if (!selectedTeacherId.value) {
    teacherScheduleCourses.value = []
    return
  }

  // 获取当前周的日期范围
  const today = new Date(teacherCurrentDate.value)
  const currentWeekStart = new Date(today)
  currentWeekStart.setDate(today.getDate() - today.getDay() + 1) // 本周一

  // 格式化日期为 YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // 生成本周的日期
  const weekDates = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart)
    date.setDate(currentWeekStart.getDate() + i)
    weekDates.push(formatDate(date))
  }

  // 颜色配置
  const colors = [
    '#67C23A', // 绿色
    '#409EFF', // 蓝色
    '#E6A23C', // 橙色
    '#F56C6C', // 红色
    '#909399', // 灰色
    '#9C27B0', // 紫色
  ]

  // 找到选中的老师
  const selectedTeacher = teacherList.value.find(t => t.id === selectedTeacherId.value)
  const teacherName = selectedTeacher ? selectedTeacher.name : '老师'

  const mockCourses = []
  let courseId = 1

  // 为本周每天添加一些课程
  weekDates.forEach((date) => {
    // 每天上午 09:00-10:30 添加 1-2 个课程
    const morningCourseCount = 1 + Math.floor(Math.random() * 2)
    for (let i = 0; i < morningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '09:00',
        endTime: '10:30',
        date: date,
        teacher: teacherName,
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }

    // 每天下午 14:00-15:30 添加 1-3 个课程
    const afternoonCourseCount = 1 + Math.floor(Math.random() * 3)
    for (let i = 0; i < afternoonCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '14:00',
        endTime: '15:30',
        date: date,
        teacher: teacherName,
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }

    // 每天晚上 18:30-20:00 添加 0-2 个课程
    const eveningCourseCount = Math.floor(Math.random() * 3)
    for (let i = 0; i < eveningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '18:30',
        endTime: '20:00',
        date: date,
        teacher: teacherName,
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }
  })

  teacherScheduleCourses.value = mockCourses

  // 更新老师的课程数量
  if (selectedTeacher) {
    selectedTeacher.courseCount = mockCourses.length
  }
}

// 教室课表相关方法
// 选择教室
function handleSelectClassroom(classroomId) {
  selectedClassroomId.value = classroomId
  fetchClassroomSchedule()
}

// 教室视图切换
function handleClassroomViewChange() {
  fetchClassroomSchedule()
}

// 教室课表上一个时间段
function handleClassroomPrevious() {
  if (classroomViewType.value === 'week') {
    classroomCurrentDate.value = new Date(classroomCurrentDate.value.setDate(classroomCurrentDate.value.getDate() - 7))
  } else if (classroomViewType.value === 'month') {
    classroomCurrentDate.value = new Date(classroomCurrentDate.value.setMonth(classroomCurrentDate.value.getMonth() - 1))
  }
  fetchClassroomSchedule()
}

// 教室课表下一个时间段
function handleClassroomNext() {
  if (classroomViewType.value === 'week') {
    classroomCurrentDate.value = new Date(classroomCurrentDate.value.setDate(classroomCurrentDate.value.getDate() + 7))
  } else if (classroomViewType.value === 'month') {
    classroomCurrentDate.value = new Date(classroomCurrentDate.value.setMonth(classroomCurrentDate.value.getMonth() + 1))
  }
  fetchClassroomSchedule()
}

// 导出教室课表
function handleExportClassroomSchedule() {
  if (!selectedClassroomId.value) {
    ElMessage.warning('请先选择一间教室')
    return
  }
  ElMessage.info('导出教室课表功能开发中...')
}

// 获取教室课表数据
function fetchClassroomSchedule() {
  if (!selectedClassroomId.value) {
    classroomScheduleCourses.value = []
    return
  }

  const today = new Date(classroomCurrentDate.value)
  const currentWeekStart = new Date(today)
  currentWeekStart.setDate(today.getDate() - today.getDay() + 1)

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const weekDates = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart)
    date.setDate(currentWeekStart.getDate() + i)
    weekDates.push(formatDate(date))
  }

  const colors = ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C', '#909399', '#9C27B0']
  const selectedClassroom = classroomList.value.find(c => c.id === selectedClassroomId.value)
  const classroomName = selectedClassroom ? selectedClassroom.name : '教室'

  const mockCourses = []
  let courseId = 1

  weekDates.forEach((date) => {
    const morningCourseCount = 1 + Math.floor(Math.random() * 2)
    for (let i = 0; i < morningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '09:00',
        endTime: '10:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: classroomName,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }

    const afternoonCourseCount = 1 + Math.floor(Math.random() * 3)
    for (let i = 0; i < afternoonCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '14:00',
        endTime: '15:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: classroomName,
        studentCount: studentCount,
        studentNames: studentNames,
        color: colors[colorIndex]
      })
    }

    const eveningCourseCount = Math.floor(Math.random() * 3)
    for (let i = 0; i < eveningCourseCount; i++) {
      const colorIndex = i % colors.length
      mockCourses.push({
        id: courseId++,
        name: ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4],
        startTime: '18:30',
        endTime: '20:00',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: classroomName,
        color: colors[colorIndex]
      })
    }
  })

  classroomScheduleCourses.value = mockCourses

  if (selectedClassroom) {
    selectedClassroom.courseCount = mockCourses.length
  }
}

// 班级课表相关方法
// 选择班级
function handleSelectClass(classId) {
  selectedClassId.value = classId
  fetchClassSchedule()
}

// 班级视图切换
function handleClassViewChange() {
  fetchClassSchedule()
}

// 班级课表上一个时间段
function handleClassPrevious() {
  if (classViewType.value === 'week') {
    classCurrentDate.value = new Date(classCurrentDate.value.setDate(classCurrentDate.value.getDate() - 7))
  } else if (classViewType.value === 'month') {
    classCurrentDate.value = new Date(classCurrentDate.value.setMonth(classCurrentDate.value.getMonth() - 1))
  }
  fetchClassSchedule()
}

// 班级课表下一个时间段
function handleClassNext() {
  if (classViewType.value === 'week') {
    classCurrentDate.value = new Date(classCurrentDate.value.setDate(classCurrentDate.value.getDate() + 7))
  } else if (classViewType.value === 'month') {
    classCurrentDate.value = new Date(classCurrentDate.value.setMonth(classCurrentDate.value.getMonth() + 1))
  }
  fetchClassSchedule()
}

// 导出班级课表
function handleExportClassSchedule() {
  if (!selectedClassId.value) {
    ElMessage.warning('请先选择一个班级')
    return
  }
  ElMessage.info('导出班级课表功能开发中...')
}

// 获取班级课表数据
function fetchClassSchedule() {
  if (!selectedClassId.value) {
    classScheduleCourses.value = []
    return
  }

  const today = new Date(classCurrentDate.value)
  const currentWeekStart = new Date(today)
  currentWeekStart.setDate(today.getDate() - today.getDay() + 1)

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const weekDates = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart)
    date.setDate(currentWeekStart.getDate() + i)
    weekDates.push(formatDate(date))
  }

  const colors = ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C', '#909399', '#9C27B0']
  const selectedClass = classList.value.find(c => c.id === selectedClassId.value)
  const className = selectedClass ? selectedClass.name : '班级'

  const mockCourses = []
  let courseId = 1

  weekDates.forEach((date) => {
    const morningCourseCount = 1 + Math.floor(Math.random() * 2)
    for (let i = 0; i < morningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '09:00',
        endTime: '10:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        class: className,
        color: colors[colorIndex]
      })
    }

    const afternoonCourseCount = 1 + Math.floor(Math.random() * 3)
    for (let i = 0; i < afternoonCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '14:00',
        endTime: '15:30',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        classroom: `教室${i + 1}`,
        studentCount: studentCount,
        studentNames: studentNames,
        class: className,
        color: colors[colorIndex]
      })
    }

    const eveningCourseCount = Math.floor(Math.random() * 3)
    for (let i = 0; i < eveningCourseCount; i++) {
      const colorIndex = i % colors.length
      const courseName = ['爵士舞', '拉丁舞', '芭蕾舞', '街舞'][i % 4]
      const studentCount = 8 + Math.floor(Math.random() * 7)
      const studentNames = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二', '冯十三', '陈十四', '褚十五']
        .slice(0, studentCount)
        .join('、')

      mockCourses.push({
        id: courseId++,
        name: courseName,
        courseName: courseName,
        startTime: '18:30',
        endTime: '20:00',
        date: date,
        teacher: ['孟吉', '忠贞', '庆庆', '李老师'][i % 4],
        studentCount: studentCount,
        studentNames: studentNames,
        classroom: `教室${i + 1}`,
        class: className,
        color: colors[colorIndex]
      })
    }
  })

  classScheduleCourses.value = mockCourses

  if (selectedClass) {
    selectedClass.courseCount = mockCourses.length
  }
}

// 组件挂载时
onMounted(() => {
  fetchEvents()
})
</script>

<style lang="scss" scoped>
.schedule-container {
  padding: 20px;
  background: #fff;

  .schedule-tabs {
    margin-bottom: 20px;

    :deep(.el-tabs__nav-wrap::after) {
      height: 1px;
    }
  }

  .time-schedule {
    // 筛选条件栏
    .filter-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px;
      background: #f5f7fa;
      border-radius: 4px;
      margin-bottom: 15px;

      .filter-left {
        display: flex;
        align-items: center;
        flex: 1;

        .filter-label {
          font-size: 14px;
          color: #606266;
          white-space: nowrap;
        }
      }

      .filter-right {
        display: flex;
        gap: 10px;
      }
    }

    // 工具栏
    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 0;
      margin-bottom: 10px;

      .toolbar-left {
        flex: 1;
      }

      .toolbar-center {
        flex: 2;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;

        .date-range {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
          min-width: 200px;
          text-align: center;
        }
      }

      .toolbar-right {
        flex: 1;
        display: flex;
        justify-content: flex-end;
      }
    }

    // 统计信息
    .statistics {
      padding: 10px 0;
      font-size: 14px;
      color: #606266;

      strong {
        color: #303133;
        font-weight: 600;
      }
    }

    // 课程表容器
    .schedule-wrapper {
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      overflow: hidden;
    }
  }

  .tab-placeholder {
    padding: 100px 0;
    text-align: center;
  }

  // 老师课表布局
  .teacher-schedule {
    .teacher-schedule-layout {
      display: flex;
      gap: 20px;
      height: calc(100vh - 200px);

      // 左侧老师列表面板
      .teacher-list-panel {
        width: 280px;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .panel-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }

          .teacher-count {
            font-size: 12px;
            color: #909399;
          }
        }

        .search-box {
          padding: 15px;
          border-bottom: 1px solid #e4e7ed;
        }

        .teacher-list {
          flex: 1;
          overflow-y: auto;
          padding: 10px;

          .teacher-item {
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid transparent;

            &:hover {
              background: #f5f7fa;
              border-color: #e4e7ed;
            }

            &.active {
              background: #ecf5ff;
              border-color: #409EFF;

              .teacher-name {
                color: #409EFF;
                font-weight: 600;
              }
            }

            .teacher-avatar {
              margin-right: 12px;
            }

            .teacher-info {
              flex: 1;
              min-width: 0;

              .teacher-name {
                font-size: 14px;
                font-weight: 500;
                color: #303133;
                margin-bottom: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              .teacher-meta {
                font-size: 12px;
                color: #909399;

                .course-count {
                  margin-right: 10px;
                }
              }
            }
          }
        }
      }

      // 右侧课程表面板
      .schedule-panel {
        flex: 1;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .schedule-toolbar {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .toolbar-left {
            flex: 1;
          }

          .toolbar-center {
            flex: 2;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;

            .date-range {
              font-size: 16px;
              font-weight: 500;
              color: #303133;
              min-width: 200px;
              text-align: center;
            }
          }

          .toolbar-right {
            flex: 1;
            display: flex;
            justify-content: flex-end;
          }
        }

        .schedule-content {
          flex: 1;
          overflow: hidden;
          padding: 15px;
        }

        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }

  // 教室课表布局（复用老师课表样式）
  .classroom-schedule {
    .classroom-schedule-layout {
      display: flex;
      gap: 20px;
      height: calc(100vh - 200px);

      .classroom-list-panel {
        width: 280px;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .panel-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }

          .classroom-count {
            font-size: 12px;
            color: #909399;
          }
        }

        .search-box {
          padding: 15px;
          border-bottom: 1px solid #e4e7ed;
        }

        .classroom-list {
          flex: 1;
          overflow-y: auto;
          padding: 10px;

          .classroom-item {
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid transparent;

            &:hover {
              background: #f5f7fa;
              border-color: #e4e7ed;
            }

            &.active {
              background: #ecf5ff;
              border-color: #409EFF;

              .classroom-name {
                color: #409EFF;
                font-weight: 600;
              }
            }

            .classroom-icon {
              margin-right: 12px;
              display: flex;
              align-items: center;
              justify-content: center;
            }

            .classroom-info {
              flex: 1;
              min-width: 0;

              .classroom-name {
                font-size: 14px;
                font-weight: 500;
                color: #303133;
                margin-bottom: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              .classroom-meta {
                font-size: 12px;
                color: #909399;

                .course-count {
                  margin-right: 10px;
                }
              }
            }
          }
        }
      }

      .schedule-panel {
        flex: 1;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .schedule-toolbar {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .toolbar-left {
            flex: 1;
          }

          .toolbar-center {
            flex: 2;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;

            .date-range {
              font-size: 16px;
              font-weight: 500;
              color: #303133;
              min-width: 200px;
              text-align: center;
            }
          }

          .toolbar-right {
            flex: 1;
            display: flex;
            justify-content: flex-end;
          }
        }

        .schedule-content {
          flex: 1;
          overflow: hidden;
          padding: 15px;
        }

        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }

  // 班级课表布局（复用老师课表样式）
  .class-schedule {
    .class-schedule-layout {
      display: flex;
      gap: 20px;
      height: calc(100vh - 200px);

      .class-list-panel {
        width: 280px;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .panel-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }

          .class-count {
            font-size: 12px;
            color: #909399;
          }
        }

        .search-box {
          padding: 15px;
          border-bottom: 1px solid #e4e7ed;
        }

        .class-list {
          flex: 1;
          overflow-y: auto;
          padding: 10px;

          .class-item {
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid transparent;

            &:hover {
              background: #f5f7fa;
              border-color: #e4e7ed;
            }

            &.active {
              background: #f0f9ff;
              border-color: #67C23A;

              .class-name {
                color: #67C23A;
                font-weight: 600;
              }
            }

            .class-icon {
              margin-right: 12px;
              display: flex;
              align-items: center;
              justify-content: center;
            }

            .class-info {
              flex: 1;
              min-width: 0;

              .class-name {
                font-size: 14px;
                font-weight: 500;
                color: #303133;
                margin-bottom: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              .class-meta {
                font-size: 12px;
                color: #909399;

                .course-count {
                  margin-right: 10px;
                }
              }
            }
          }
        }
      }

      .schedule-panel {
        flex: 1;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        .schedule-toolbar {
          padding: 15px 20px;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #f5f7fa;

          .toolbar-left {
            flex: 1;
          }

          .toolbar-center {
            flex: 2;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;

            .date-range {
              font-size: 16px;
              font-weight: 500;
              color: #303133;
              min-width: 200px;
              text-align: center;
            }
          }

          .toolbar-right {
            flex: 1;
            display: flex;
            justify-content: flex-end;
          }
        }

        .schedule-content {
          flex: 1;
          overflow: hidden;
          padding: 15px;
        }

        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }

  // 课程详情抽屉头部样式
  .drawer-header {
    display: flex;
    align-items: center;

    .drawer-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  // 课程详情抽屉样式
  .course-detail-drawer {
    padding: 0;

    .detail-section {
      margin-bottom: 20px;

      .section-title {
        font-size: 15px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #409EFF;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .title-actions {
          display: flex;
          gap: 8px;
        }
      }

      .detail-grid {
        display: flex;
        flex-direction: column;
        gap: 10px;

        .detail-row {
          display: flex;
          align-items: flex-start;
          gap: 12px;

          &.full-width {
            flex-direction: column;
            gap: 6px;
          }

          .detail-label {
            font-size: 14px;
            color: #606266;
            font-weight: 500;
            min-width: 90px;
            flex-shrink: 0;
          }

          .detail-value {
            font-size: 14px;
            color: #303133;
            flex: 1;
            word-break: break-word;
          }
        }
      }

      // 学生表格容器
      .student-table-wrapper {
        margin-top: 12px;

        :deep(.el-table) {
          font-size: 13px;

          .el-table__header th {
            background-color: #f5f7fa;
            color: #606266;
            font-weight: 600;
          }

          .el-table__body td {
            padding: 8px 0;
          }

          // 剩余课时不足时的警告样式
          .low-hours {
            color: #F56C6C;
            font-weight: 600;
          }

          // 扣除额度样式
          .deduct-amount {
            color: #E6A23C;
            font-weight: 500;
          }
        }
      }
    }
  }
}
</style>


