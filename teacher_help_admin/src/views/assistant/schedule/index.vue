<template>
  <div class="app-container schedule-container">
    <el-tabs v-model="activeTab" class="schedule-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="时间课表" name="time" />
      <el-tab-pane label="老师课表" name="teacher" />
      <el-tab-pane label="教室课表" name="classroom" />
      <el-tab-pane label="班级课表" name="class" />
    </el-tabs>

    <div class="filter-bar">
      <div class="filter-left">
        <span class="filter-label">所属课程：</span>
        <el-select v-model="queryParams.courseId" placeholder="请选择课程" clearable filterable @change="handleQuery">
          <el-option v-for="course in courseList" :key="course.id" :label="course.name" :value="course.id" />
        </el-select>

        <span class="filter-label">上课班级：</span>
        <el-select v-model="queryParams.classId" placeholder="请选择班级" clearable filterable @change="handleQuery">
          <el-option v-for="cls in classList" :key="cls.id" :label="cls.name" :value="cls.id" />
        </el-select>

        <span class="filter-label">上课老师：</span>
        <el-select v-model="queryParams.teacherId" placeholder="请选择老师" clearable filterable @change="handleQuery">
          <el-option v-for="teacher in teacherList" :key="teacher.id" :label="teacher.name" :value="teacher.id" />
        </el-select>
      </div>

      <div class="filter-right">
        <el-button type="warning" @click="handleAddSchedule">新建排课</el-button>
        <el-button plain icon="Refresh" @click="loadActiveSchedule">刷新</el-button>
      </div>
    </div>

    <div class="toolbar">
      <div class="toolbar-left">
        <el-radio-group v-if="activeTab === 'time'" v-model="viewType" size="small" @change="loadActiveSchedule">
          <el-radio-button label="day">日</el-radio-button>
          <el-radio-button label="week">周</el-radio-button>
          <el-radio-button label="month">月</el-radio-button>
        </el-radio-group>
        <el-radio-group v-else v-model="resourceViewType" size="small" @change="loadActiveSchedule">
          <el-radio-button label="week">周视图</el-radio-button>
          <el-radio-button label="month">月视图</el-radio-button>
        </el-radio-group>
      </div>

      <div class="toolbar-center">
        <el-button size="small" icon="ArrowLeft" @click="handlePrevious" />
        <span class="date-range">{{ activeDateRangeText }}</span>
        <el-button size="small" icon="ArrowRight" @click="handleNext" />
      </div>

      <div class="toolbar-right">
        <span class="statistics">
          共 <strong>{{ activeCourses.length }}</strong> 节课，未点名
          <strong>{{ unattendedCount }}</strong> 节课
        </span>
      </div>
    </div>

    <div v-if="activeTab === 'time'" v-loading="scheduleLoading" class="schedule-wrapper">
      <CourseSchedule
        :courses="scheduleCourses"
        :view-mode="viewType"
        :dates="activeDates"
        :month="activeMonth"
        :cell-height="60"
        height="calc(100vh - 340px)"
        @view-detail="handleCourseDetail"
        @reschedule="handleCourseReschedule"
        @delete="handleCourseDelete"
      />
    </div>

    <div v-else class="resource-layout">
      <div class="resource-panel">
        <div class="panel-header">
          <span>{{ resourceTitle }}</span>
          <span class="muted">共 {{ activeResourceList.length }} 项</span>
        </div>
        <el-input v-model="resourceKeyword" placeholder="搜索" clearable prefix-icon="Search" size="small" />
        <div class="resource-list">
          <div
            v-for="resource in filteredResourceList"
            :key="resource.id"
            class="resource-item"
            :class="{ active: activeResourceId === resource.id }"
            @click="handleSelectResource(resource)"
          >
            <el-icon class="resource-icon">
              <User v-if="activeTab === 'teacher'" />
              <OfficeBuilding v-else-if="activeTab === 'classroom'" />
              <School v-else />
            </el-icon>
            <div class="resource-main">
              <div class="resource-name">{{ resource.name }}</div>
              <div class="resource-meta">{{ resource.courseCount || 0 }} 节课</div>
            </div>
          </div>
        </div>
      </div>

      <div v-loading="scheduleLoading" class="resource-schedule">
        <CourseSchedule
          v-if="activeResourceId"
          :courses="activeCourses"
          :view-mode="resourceViewType"
          :dates="activeDates"
          :month="activeMonth"
          :cell-height="60"
          height="calc(100vh - 340px)"
          @view-detail="handleCourseDetail"
          @reschedule="handleCourseReschedule"
          @delete="handleCourseDelete"
        />
        <el-empty v-else :description="`请选择${resourceTitle}`" />
      </div>
    </div>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="760px" append-to-body>
      <el-form ref="scheduleFormRef" :model="scheduleForm" :rules="scheduleRules" label-width="96px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="课程" prop="courseId">
              <el-select v-model="scheduleForm.courseId" placeholder="请选择课程" filterable style="width: 100%">
                <el-option v-for="course in courseList" :key="course.id" :label="course.name" :value="course.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="classId">
              <el-select v-model="scheduleForm.classId" placeholder="请选择班级" filterable style="width: 100%">
                <el-option v-for="cls in classList" :key="cls.id" :label="cls.name" :value="cls.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="上课日期" prop="courseDate">
              <el-date-picker
                v-model="scheduleForm.courseDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授课课时" prop="lessonHours">
              <el-input-number v-model="scheduleForm.lessonHours" :min="0.5" :step="0.5" :precision="1" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startClock">
              <el-time-picker
                v-model="scheduleForm.startClock"
                value-format="HH:mm"
                format="HH:mm"
                placeholder="开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endClock">
              <el-time-picker
                v-model="scheduleForm.endClock"
                value-format="HH:mm"
                format="HH:mm"
                placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="上课老师" prop="teacherId">
              <el-select v-model="scheduleForm.teacherId" placeholder="请选择老师" filterable style="width: 100%">
                <el-option v-for="teacher in teacherList" :key="teacher.id" :label="teacher.name" :value="teacher.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上课教室">
              <el-select
                v-model="scheduleForm.classroom"
                placeholder="请选择或输入教室"
                filterable
                allow-create
                clearable
                default-first-option
                style="width: 100%"
              >
                <el-option v-for="room in classroomList" :key="room.id" :label="room.name" :value="room.name" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="上课内容">
          <el-input
            v-model="scheduleForm.content"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="请输入上课内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmitSchedule">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-drawer title="课次详情" v-model="courseDetailDrawerVisible" size="660px" append-to-body>
      <el-skeleton :loading="detailLoading" animated>
        <template #default>
          <div v-if="selectedCourse.id" class="course-detail">
            <div class="detail-title">
              <span>{{ selectedCourse.className || selectedCourse.name }}</span>
              <div class="detail-actions">
                <el-button type="primary" size="small" @click="handleEditCourse">编辑课次</el-button>
                <el-button type="warning" size="small" @click="handleStartAttendance(selectedCourse)">点名</el-button>
                <el-button type="danger" size="small" @click="handleDeleteCourse">删除课次</el-button>
              </div>
            </div>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="上课时间">
                {{ selectedCourse.date }} {{ selectedCourse.startTime }}-{{ selectedCourse.endTime }}
              </el-descriptions-item>
              <el-descriptions-item label="授课课程">{{ selectedCourse.courseName || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上课班级">{{ selectedCourse.className || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上课老师">{{ selectedCourse.teacher || '-' }}</el-descriptions-item>
              <el-descriptions-item label="授课课时">{{ selectedCourse.lessonHours || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上课教室">{{ selectedCourse.classroom || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上课内容" :span="2">{{ selectedCourse.content || '-' }}</el-descriptions-item>
            </el-descriptions>

            <div class="sub-title">上课学员</div>
            <el-table :data="getStudentList(selectedCourse)" border>
              <el-table-column label="学员" prop="studentName" min-width="120" />
              <el-table-column label="到课状态" prop="statusName" width="100" align="center" />
              <el-table-column label="签到时间" prop="checkInTime" width="180" align="center" />
              <el-table-column label="备注" prop="notes" min-width="140" show-overflow-tooltip />
            </el-table>
          </div>
          <el-empty v-else description="课次不存在" />
        </template>
      </el-skeleton>
    </el-drawer>
  </div>
</template>

<script setup name="AssistantSchedule">
import { computed, getCurrentInstance, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { OfficeBuilding, School, User } from '@element-plus/icons-vue';
import CourseSchedule from '@/components/CourseSchedule/index.vue';
import {
  addScheduleEvent,
  delScheduleEvent,
  getScheduleEvent,
  listScheduleEvent,
  updateScheduleEvent
} from '@/api/teach/schedule';
import { listCourseOptions } from '@/api/assistant/course';
import { listClassOptions } from '@/api/assistant/class';
import { listTeacher } from '@/api/teach/teacher';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();

const activeTab = ref(route.query.tab || 'time');
const viewType = ref('week');
const resourceViewType = ref('week');
const currentDate = ref(new Date());
const resourceCurrentDate = ref(new Date());
const scheduleLoading = ref(false);
const submitLoading = ref(false);
const detailLoading = ref(false);

const queryParams = ref({
  courseId: null,
  classId: null,
  teacherId: null
});

const courseList = ref([]);
const classList = ref([]);
const teacherList = ref([]);
const classroomList = ref([]);

const scheduleCourses = ref([]);
const teacherScheduleCourses = ref([]);
const classroomScheduleCourses = ref([]);
const classScheduleCourses = ref([]);

const selectedTeacherId = ref(null);
const selectedClassroomId = ref(null);
const selectedClassId = ref(null);
const resourceKeyword = ref('');

const dialogVisible = ref(false);
const dialogTitle = ref('新建排课');
const scheduleFormRef = ref(null);
const courseDetailDrawerVisible = ref(false);
const selectedCourse = ref({});

const scheduleForm = ref(getDefaultScheduleForm());
const scheduleRules = {
  courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
  classId: [{ required: true, message: '请选择班级', trigger: 'change' }],
  courseDate: [{ required: true, message: '请选择上课日期', trigger: 'change' }],
  startClock: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endClock: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  teacherId: [{ required: true, message: '请选择上课老师', trigger: 'change' }]
};

const activeCourses = computed(() => {
  if (activeTab.value === 'teacher') {
    return teacherScheduleCourses.value;
  }
  if (activeTab.value === 'classroom') {
    return classroomScheduleCourses.value;
  }
  if (activeTab.value === 'class') {
    return classScheduleCourses.value;
  }
  return scheduleCourses.value;
});

const unattendedCount = computed(() => activeCourses.value.filter(item => item.status !== '2').length);

const activeDate = computed(() => (activeTab.value === 'time' ? currentDate.value : resourceCurrentDate.value));
const activeView = computed(() => (activeTab.value === 'time' ? viewType.value : resourceViewType.value));
const activeDates = computed(() => buildDates(activeDate.value, activeView.value));
const activeMonth = computed(() => (activeView.value === 'month' ? formatMonth(activeDate.value) : null));
const activeDateRangeText = computed(() => getDateRangeText(activeDate.value, activeView.value));

const resourceTitle = computed(() => {
  if (activeTab.value === 'teacher') {
    return '老师';
  }
  if (activeTab.value === 'classroom') {
    return '教室';
  }
  return '班级';
});

const activeResourceList = computed(() => {
  if (activeTab.value === 'teacher') {
    return teacherList.value;
  }
  if (activeTab.value === 'classroom') {
    return classroomList.value;
  }
  return classList.value;
});

const activeResourceId = computed(() => {
  if (activeTab.value === 'teacher') {
    return selectedTeacherId.value;
  }
  if (activeTab.value === 'classroom') {
    return selectedClassroomId.value;
  }
  return selectedClassId.value;
});

const filteredResourceList = computed(() => {
  const keyword = resourceKeyword.value.trim().toLowerCase();
  if (!keyword) {
    return activeResourceList.value;
  }
  return activeResourceList.value.filter(item => (item.name || '').toLowerCase().includes(keyword));
});

function getDefaultScheduleForm() {
  return {
    id: null,
    courseId: null,
    classId: null,
    courseDate: formatDate(new Date()),
    startClock: '09:00',
    endClock: '10:00',
    teacherId: null,
    classroom: '',
    lessonHours: 1,
    content: '',
    remark: ''
  };
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatMonth(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

function formatClock(value) {
  if (!value) {
    return '';
  }
  const text = String(value);
  if (/^\d{2}:\d{2}/.test(text)) {
    return text.slice(0, 5);
  }
  const date = new Date(text);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function buildDateTime(date, clock) {
  return `${date} ${clock}:00`;
}

function buildDates(date, view) {
  if (view === 'month') {
    return null;
  }
  if (view === 'day') {
    return [formatDate(date)];
  }
  const start = getWeekStart(date);
  return Array.from({ length: 7 }).map((_, index) => {
    const item = new Date(start);
    item.setDate(start.getDate() + index);
    return formatDate(item);
  });
}

function getWeekStart(date) {
  const start = new Date(date);
  const day = start.getDay();
  start.setDate(start.getDate() - day + (day === 0 ? -6 : 1));
  start.setHours(0, 0, 0, 0);
  return start;
}

function getRange(date, view) {
  if (view === 'day') {
    const start = new Date(date);
    start.setHours(0, 0, 0, 0);
    const end = new Date(date);
    end.setHours(23, 59, 59, 999);
    return { start, end };
  }
  if (view === 'month') {
    const start = new Date(date.getFullYear(), date.getMonth(), 1);
    const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);
    end.setHours(23, 59, 59, 999);
    return { start, end };
  }
  const start = getWeekStart(date);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  end.setHours(23, 59, 59, 999);
  return { start, end };
}

function getDateRangeText(date, view) {
  const { start, end } = getRange(date, view);
  if (view === 'day') {
    return formatChineseDate(start);
  }
  if (view === 'month') {
    return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月`;
  }
  return `${formatChineseDate(start)}~${formatChineseDate(end).slice(5)}`;
}

function formatChineseDate(date) {
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`;
}

async function loadOptions() {
  const [courseRes, classRes, teacherRes] = await Promise.all([
    listCourseOptions(),
    listClassOptions(),
    listTeacher({ pageNum: 1, pageSize: 500 })
  ]);
  courseList.value = (courseRes.data || []).map(item => ({
    ...item,
    name: item.courseName,
    color: item.scheduleColor
  }));
  classList.value = (classRes.data || []).map(item => ({
    ...item,
    name: item.className
  }));
  teacherList.value = (teacherRes.rows || []).map(item => ({
    ...item,
    name: item.teacherName
  }));
  refreshClassroomList();
}

function refreshClassroomList(events = []) {
  const names = new Set();
  classList.value.forEach(item => {
    if (item.classroom) {
      names.add(item.classroom);
    }
  });
  events.forEach(item => {
    if (item.classroom) {
      names.add(item.classroom);
    }
  });
  classroomList.value = Array.from(names).map(name => ({ id: name, name }));
}

function getBaseQuery(date, view) {
  const { start, end } = getRange(date, view);
  return {
    pageNum: 1,
    pageSize: 1000,
    startTime: buildDateTime(formatDate(start), '00:00'),
    endTime: buildDateTime(formatDate(end), '23:59')
  };
}

function buildScheduleQuery() {
  const base = getBaseQuery(activeDate.value, activeView.value);
  const query = {
    ...base,
    courseId: queryParams.value.courseId || undefined,
    classId: queryParams.value.classId || undefined,
    teacherId: queryParams.value.teacherId || undefined
  };
  if (activeTab.value === 'teacher') {
    query.teacherId = selectedTeacherId.value;
  }
  if (activeTab.value === 'classroom') {
    query.classroom = selectedClassroomId.value;
  }
  if (activeTab.value === 'class') {
    query.classId = selectedClassId.value;
  }
  return query;
}

async function loadActiveSchedule() {
  if (activeTab.value !== 'time' && !activeResourceId.value) {
    if (activeTab.value === 'teacher') {
      teacherScheduleCourses.value = [];
    } else if (activeTab.value === 'classroom') {
      classroomScheduleCourses.value = [];
    } else if (activeTab.value === 'class') {
      classScheduleCourses.value = [];
    }
    return;
  }
  scheduleLoading.value = true;
  try {
    const response = await listScheduleEvent(buildScheduleQuery());
    const rows = response.rows || [];
    const courses = rows.map(mapEventToCourse);
    refreshClassroomList(courses);
    if (activeTab.value === 'teacher') {
      teacherScheduleCourses.value = courses;
      updateResourceCount(teacherList.value, selectedTeacherId.value, courses.length);
    } else if (activeTab.value === 'classroom') {
      classroomScheduleCourses.value = courses;
      updateResourceCount(classroomList.value, selectedClassroomId.value, courses.length);
    } else if (activeTab.value === 'class') {
      classScheduleCourses.value = courses;
      updateResourceCount(classList.value, selectedClassId.value, courses.length);
    } else {
      scheduleCourses.value = courses;
    }
  } finally {
    scheduleLoading.value = false;
  }
}

function updateResourceCount(list, id, count) {
  const item = list.find(resource => resource.id === id);
  if (item) {
    item.courseCount = count;
  }
}

function mapEventToCourse(item) {
  const date = item.eventDate || formatDate(new Date(item.startTime));
  const courseName = item.courseName || '-';
  return {
    ...item,
    id: item.id,
    name: item.className || courseName,
    courseName,
    className: item.className,
    date,
    startTime: formatClock(item.startTime),
    endTime: formatClock(item.endTime),
    teacher: item.teacherName,
    classroom: item.classroom,
    studentCount: item.cachedPlanned || 0,
    students: item.cachedPlanned || 0,
    color: item.scheduleColor || getCourseColor(item.courseId),
    content: item.content,
    lessonHours: item.lessonHours,
    status: String(item.status ?? '0')
  };
}

function getCourseColor(courseId) {
  const course = courseList.value.find(item => item.id === courseId);
  return course?.color || '#409EFF';
}

function handleQuery() {
  loadActiveSchedule();
}

function handleTabChange() {
  resourceKeyword.value = '';
  ensureResourceSelected();
  loadActiveSchedule();
}

function ensureResourceSelected() {
  if (activeTab.value === 'teacher' && !selectedTeacherId.value && teacherList.value.length) {
    selectedTeacherId.value = teacherList.value[0].id;
  }
  if (activeTab.value === 'classroom' && !selectedClassroomId.value && classroomList.value.length) {
    selectedClassroomId.value = classroomList.value[0].id;
  }
  if (activeTab.value === 'class' && !selectedClassId.value && classList.value.length) {
    selectedClassId.value = classList.value[0].id;
  }
}

function handleSelectResource(resource) {
  if (activeTab.value === 'teacher') {
    selectedTeacherId.value = resource.id;
  } else if (activeTab.value === 'classroom') {
    selectedClassroomId.value = resource.id;
  } else {
    selectedClassId.value = resource.id;
  }
  loadActiveSchedule();
}

function handlePrevious() {
  const target = activeTab.value === 'time' ? currentDate : resourceCurrentDate;
  const view = activeView.value;
  const next = new Date(target.value);
  if (view === 'day') {
    next.setDate(next.getDate() - 1);
  } else if (view === 'month') {
    next.setMonth(next.getMonth() - 1);
  } else {
    next.setDate(next.getDate() - 7);
  }
  target.value = next;
  loadActiveSchedule();
}

function handleNext() {
  const target = activeTab.value === 'time' ? currentDate : resourceCurrentDate;
  const view = activeView.value;
  const next = new Date(target.value);
  if (view === 'day') {
    next.setDate(next.getDate() + 1);
  } else if (view === 'month') {
    next.setMonth(next.getMonth() + 1);
  } else {
    next.setDate(next.getDate() + 7);
  }
  target.value = next;
  loadActiveSchedule();
}

function handleAddSchedule() {
  dialogTitle.value = '新建排课';
  scheduleForm.value = getDefaultScheduleForm();
  scheduleForm.value.courseId = queryParams.value.courseId;
  scheduleForm.value.classId = activeTab.value === 'class' ? selectedClassId.value : queryParams.value.classId;
  scheduleForm.value.teacherId = activeTab.value === 'teacher' ? selectedTeacherId.value : queryParams.value.teacherId;
  scheduleForm.value.classroom = activeTab.value === 'classroom' ? selectedClassroomId.value : '';
  applyClassDefaults(scheduleForm.value.classId);
  dialogVisible.value = true;
}

function applyClassDefaults(classId) {
  const cls = classList.value.find(item => item.id === classId);
  if (!cls) {
    return;
  }
  scheduleForm.value.courseId = cls.courseId;
  scheduleForm.value.teacherId = scheduleForm.value.teacherId || cls.teacherId;
  scheduleForm.value.classroom = scheduleForm.value.classroom || cls.classroom || '';
  scheduleForm.value.lessonHours = Number(cls.lessonHours || scheduleForm.value.lessonHours || 1);
}

watch(
  () => scheduleForm.value.classId,
  classId => {
    if (dialogVisible.value && !scheduleForm.value.id) {
      applyClassDefaults(classId);
    }
  }
);

async function handleSubmitSchedule() {
  await scheduleFormRef.value.validate();
  const startTime = buildDateTime(scheduleForm.value.courseDate, scheduleForm.value.startClock);
  const endTime = buildDateTime(scheduleForm.value.courseDate, scheduleForm.value.endClock);
  if (new Date(endTime.replace(/-/g, '/')) <= new Date(startTime.replace(/-/g, '/'))) {
    proxy.$modal.msgWarning('结束时间必须晚于开始时间');
    return;
  }
  submitLoading.value = true;
  try {
    const payload = {
      classId: scheduleForm.value.classId,
      courseId: scheduleForm.value.courseId,
      teacherId: scheduleForm.value.teacherId,
      startTime,
      endTime,
      classroom: scheduleForm.value.classroom,
      lessonHours: scheduleForm.value.lessonHours,
      content: scheduleForm.value.content,
      remark: scheduleForm.value.remark
    };
    if (scheduleForm.value.id) {
      await updateScheduleEvent({ ...payload, id: scheduleForm.value.id });
      proxy.$modal.msgSuccess('修改成功');
    } else {
      await addScheduleEvent(payload);
      proxy.$modal.msgSuccess('排课成功');
    }
    dialogVisible.value = false;
    await loadActiveSchedule();
  } finally {
    submitLoading.value = false;
  }
}

async function handleCourseDetail(course) {
  courseDetailDrawerVisible.value = true;
  detailLoading.value = true;
  selectedCourse.value = {};
  try {
    const response = await getScheduleEvent(course.id);
    selectedCourse.value = mapEventDetail(response.data || {});
  } finally {
    detailLoading.value = false;
  }
}

function mapEventDetail(data) {
  return {
    ...mapEventToCourse(data),
    studentList: data.students || []
  };
}

async function handleCourseReschedule(course) {
  const response = await getScheduleEvent(course.id);
  openEditDialog(mapEventDetail(response.data || course));
}

function handleEditCourse() {
  openEditDialog(selectedCourse.value);
}

function openEditDialog(course) {
  dialogTitle.value = '编辑排课';
  scheduleForm.value = {
    id: course.id,
    courseId: course.courseId,
    classId: course.classId,
    courseDate: course.date,
    startClock: course.startTime,
    endClock: course.endTime,
    teacherId: course.teacherId,
    classroom: course.classroom || '',
    lessonHours: Number(course.lessonHours || 1),
    content: course.content || '',
    remark: course.remark || ''
  };
  dialogVisible.value = true;
}

function handleCourseDelete(course) {
  deleteCourse(course);
}

function handleDeleteCourse() {
  deleteCourse(selectedCourse.value);
}

function deleteCourse(course) {
  proxy.$modal.confirm(`确认删除“${course.name || course.courseName}”这节课吗？`).then(async () => {
    await delScheduleEvent(course.id);
    proxy.$modal.msgSuccess('删除成功');
    courseDetailDrawerVisible.value = false;
    await loadActiveSchedule();
  }).catch(() => {});
}

function handleStartAttendance(course) {
  if (!course.classId) {
    proxy.$modal.msgWarning('当前课次未关联班级，不能进入班级点名');
    return;
  }
  router.push({ path: `/assistant/class/attendance/${course.classId}`, query: { eventId: course.id } });
}

function getStudentList(course) {
  return course?.studentList || [];
}

async function applyRouteQuery() {
  if (route.query.classId) {
    const classId = Number(route.query.classId);
    activeTab.value = 'class';
    selectedClassId.value = classId;
    queryParams.value.classId = classId;
  }
  if (route.query.teacherId) {
    activeTab.value = 'teacher';
    selectedTeacherId.value = Number(route.query.teacherId);
  }
  if (route.query.classroom) {
    activeTab.value = 'classroom';
    selectedClassroomId.value = String(route.query.classroom);
  }
  ensureResourceSelected();
  await loadActiveSchedule();
  if (route.query.action === 'add') {
    handleAddSchedule();
  }
}

onMounted(async () => {
  await loadOptions();
  await applyRouteQuery();
});
</script>

<style scoped lang="scss">
.schedule-container {
  background: #fff;

  .schedule-tabs {
    margin-bottom: 12px;
  }

  .filter-bar,
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
  }

  .filter-bar {
    padding: 14px 16px;
    background: #f5f7fa;
    border-radius: 4px;
  }

  .filter-left,
  .filter-right,
  .toolbar-left,
  .toolbar-center,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .filter-left {
    flex-wrap: wrap;
  }

  .filter-label,
  .muted {
    color: #606266;
  }

  .filter-left .el-select {
    width: 180px;
  }

  .date-range {
    min-width: 220px;
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .statistics {
    color: #606266;
  }

  .schedule-wrapper,
  .resource-schedule {
    min-height: 420px;
  }

  .resource-layout {
    display: flex;
    gap: 16px;
  }

  .resource-panel {
    width: 240px;
    flex: 0 0 240px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 12px;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-weight: 600;
    color: #303133;
  }

  .resource-list {
    margin-top: 10px;
    max-height: calc(100vh - 360px);
    overflow-y: auto;
  }

  .resource-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;

    &:hover,
    &.active {
      background: #ecf5ff;
      color: #409eff;
    }
  }

  .resource-icon {
    font-size: 24px;
  }

  .resource-main {
    min-width: 0;
  }

  .resource-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .resource-meta {
    margin-top: 3px;
    font-size: 12px;
    color: #909399;
  }

  .resource-schedule {
    flex: 1;
    min-width: 0;
  }

  .dialog-footer {
    text-align: right;
  }

  .detail-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    font-size: 16px;
    font-weight: 600;
    color: #ff7d00;
  }

  .detail-actions {
    display: flex;
    gap: 8px;
  }

  .sub-title {
    margin: 18px 0 10px;
    font-weight: 600;
    color: #303133;
  }
}
</style>
