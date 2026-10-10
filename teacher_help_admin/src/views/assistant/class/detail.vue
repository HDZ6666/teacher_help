<template>
  <div class="app-container class-detail">
    <div class="detail-header">
      <el-page-header @back="goBack" :content="classInfo.className || '班级详情'">
        <template #icon>
          <el-icon><ArrowLeft /></el-icon>
        </template>
      </el-page-header>
      <el-button type="warning" @click="handleEdit">编辑班级信息</el-button>
    </div>

    <el-skeleton :loading="loading" animated>
      <template #template>
        <el-skeleton-item variant="p" style="width: 40%" />
        <el-skeleton-item variant="p" style="width: 80%" />
      </template>
      <template #default>
        <div class="class-info-card">
          <div class="class-title">
            <span class="class-name">{{ classInfo.className }}</span>
            <el-tag v-if="classInfo.classMode === 'group'" type="success" size="small">班课</el-tag>
            <el-tag v-else type="warning" size="small">一对一</el-tag>
            <el-tag v-if="classInfo.classType === 'system'" type="success" size="small">系统班型</el-tag>
            <el-tag v-else type="info" size="small">自建班型</el-tag>
          </div>

          <el-row :gutter="20" class="info-row">
            <el-col :span="8">
              <span class="label">关联课程：</span>
              <span class="value">{{ classInfo.courseName || '-' }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">实际在读人数：</span>
              <span class="value">{{ classInfo.currentStudents || 0 }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">班级老师：</span>
              <span class="value">{{ classInfo.teacherName || '待分配' }}</span>
            </el-col>
          </el-row>
          <el-row :gutter="20" class="info-row">
            <el-col :span="8">
              <span class="label">人数/容量：</span>
              <span class="value">{{ classInfo.currentStudents || 0 }}/{{ classInfo.maxStudents || '未设置' }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">授课课时：</span>
              <span class="value">{{ classInfo.lessonHours || 0 }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">上课教室：</span>
              <span class="value">{{ classInfo.classroom || '-' }}</span>
            </el-col>
          </el-row>
          <el-row :gutter="20" class="info-row">
            <el-col :span="8">
              <span class="label">支持在线选班：</span>
              <span class="value">{{ classInfo.allowOnlineEnroll === 1 ? '是' : '否' }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">允许充值购时：</span>
              <span class="value">{{ classInfo.allowRecharge === 1 ? '是' : '否' }}</span>
            </el-col>
            <el-col :span="8">
              <span class="label">备注：</span>
              <span class="value">{{ classInfo.remark || '-' }}</span>
            </el-col>
          </el-row>
        </div>
      </template>
    </el-skeleton>

    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="排课信息" name="schedule">
        <div class="toolbar-line">
          <el-button type="primary" size="small" icon="Plus" @click="handleScheduleClass">排课</el-button>
          <el-button size="small" icon="Calendar" @click="openWeeklyDialog" v-hasPermi="['teach:schedule:event:batch']">按周重复排课</el-button>
          <el-button size="small" @click="loadScheduleList">刷新</el-button>
        </div>
        <el-table v-loading="scheduleLoading" :data="scheduleList" border>
          <el-table-column label="上课日期" prop="eventDate" width="120" align="center" />
          <el-table-column label="上课时间" width="150" align="center">
            <template #default="{ row }">
              {{ row.startClock }} - {{ row.endClock }}
            </template>
          </el-table-column>
          <el-table-column label="授课课程" prop="courseName" min-width="150" show-overflow-tooltip />
          <el-table-column label="上课老师" prop="teacherName" width="120" align="center" />
          <el-table-column label="上课教室" prop="classroom" min-width="120" show-overflow-tooltip />
          <el-table-column label="学员数" prop="cachedPlanned" width="90" align="center" />
          <el-table-column label="状态" prop="statusName" width="90" align="center" />
          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleViewSchedule(row)">查看</el-button>
              <el-button link type="warning" @click="handleScheduleAttendance(row)">点名</el-button>
              <el-button link type="danger" @click="handleDeleteSchedule(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="班级学员" name="members">
        <div class="toolbar-line">
          <el-button type="warning" size="small" @click="handleAddStudent" v-hasPermi="['teach:class:edit']">
            添加学员
          </el-button>
          <el-button size="small" :disabled="!selectedMemberIds.length" @click="handleBatchRemove">
            移出班级
          </el-button>
          <el-input
            v-model="memberSearchKeyword"
            placeholder="搜索学员姓名/手机号"
            clearable
            style="width: 260px; margin-left: auto"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table
          v-loading="membersLoading"
          :data="filteredMemberList"
          border
          @selection-change="handleMemberSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="姓名" min-width="120">
            <template #default="{ row }">
              <el-link type="primary" @click="handleViewStudent(row)">{{ row.studentName }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="性别" prop="genderName" width="80" align="center" />
          <el-table-column label="手机号" prop="phone" width="140" />
          <el-table-column label="消耗方式" prop="consumeMethod" min-width="220" show-overflow-tooltip />
          <el-table-column label="剩余数量" width="120" align="center">
            <template #default="{ row }">
              <span v-if="row.remainingQuantity !== null && row.remainingQuantity !== undefined">
                {{ row.remainingQuantity }}{{ row.remainingType || '' }}
              </span>
              <span v-else class="muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="加入日期" prop="joinDate" width="120" align="center" />
          <el-table-column label="操作" width="220" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleViewStudent(row)">学员详情</el-button>
              <el-button link type="warning" @click="handleStudentLeave(row)" v-hasPermi="['teach:leave:add']">请假</el-button>
              <el-button link type="danger" @click="handleRemoveStudent(row)">移出</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="点名情况" name="attendance">
        <div class="toolbar-line">
          <el-button type="warning" size="small" @click="handleDirectAttendance">未排课直接点名</el-button>
          <el-button size="small" @click="loadAttendanceList">刷新</el-button>
        </div>
        <el-table v-loading="attendanceLoading" :data="attendanceList" border>
          <el-table-column label="上课日期" prop="classDate" width="120" align="center" />
          <el-table-column label="上课时间" width="160" align="center">
            <template #default="{ row }">
              {{ row.startTime }} - {{ row.endTime }}
            </template>
          </el-table-column>
          <el-table-column label="授课课程" prop="courseName" min-width="150" show-overflow-tooltip />
          <el-table-column label="上课老师" prop="teacherName" width="120" align="center" />
          <el-table-column label="应到" prop="studentCount" width="80" align="center" />
          <el-table-column label="到课" prop="presentCount" width="80" align="center" />
          <el-table-column label="迟到" prop="lateCount" width="80" align="center" />
          <el-table-column label="请假" prop="leaveCount" width="80" align="center" />
          <el-table-column label="未到" prop="absentCount" width="80" align="center" />
          <el-table-column label="扣课合计" prop="deductedQuantity" width="100" align="center" />
          <el-table-column label="点名时间" prop="createTime" width="180" align="center" />
          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleViewAttendance(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog title="添加学员" v-model="studentDialogVisible" width="860px" append-to-body>
      <div class="dialog-toolbar">
        <el-input
          v-model="availableStudentKeyword"
          placeholder="请输入学员姓名/手机号"
          clearable
          style="width: 280px"
          @keyup.enter="loadAvailableStudents"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" icon="Search" @click="loadAvailableStudents">搜索</el-button>
      </div>
      <el-table
        v-loading="availableLoading"
        :data="availableStudents"
        border
        max-height="420"
        @selection-change="handleAvailableSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="学员名称" prop="studentName" min-width="120" />
        <el-table-column label="性别" prop="genderName" width="80" align="center" />
        <el-table-column label="手机号" prop="phone" width="140" />
        <el-table-column label="课程来源" prop="courseName" min-width="160" />
        <el-table-column label="消耗方式" prop="consumeMethod" min-width="180" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <div class="dialog-footer">
          <span class="selected-count">已选择：{{ selectedAvailableIds.length }}人</span>
          <el-button @click="studentDialogVisible = false">取消</el-button>
          <el-button type="warning" :loading="addStudentLoading" @click="confirmAddStudents">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <el-drawer title="排课详情" v-model="scheduleDrawerVisible" size="620px" append-to-body>
      <el-skeleton :loading="scheduleDetailLoading" animated>
        <template #default>
          <div class="attendance-title">
            {{ scheduleDetail.className || '-' }} {{ scheduleDetail.eventDate || '' }}
            {{ scheduleDetail.startClock || '' }}-{{ scheduleDetail.endClock || '' }}
          </div>
          <el-descriptions title="课次信息" :column="2" border>
            <el-descriptions-item label="授课课程">{{ scheduleDetail.courseName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课班级">{{ scheduleDetail.className || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课老师">{{ scheduleDetail.teacherName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="授课课时">{{ scheduleDetail.lessonHours || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课教室">{{ scheduleDetail.classroom || '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ scheduleDetail.statusName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课内容" :span="2">{{ scheduleDetail.content || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div class="sub-title">上课学员</div>
          <el-table :data="scheduleDetail.students || []" border>
            <el-table-column label="学员" prop="studentName" min-width="120" />
            <el-table-column label="到课状态" prop="statusName" width="100" align="center" />
            <el-table-column label="签到时间" prop="checkInTime" width="180" align="center" />
            <el-table-column label="备注" prop="notes" min-width="120" show-overflow-tooltip />
          </el-table>
        </template>
      </el-skeleton>
    </el-drawer>

    <el-drawer title="课次详情" v-model="attendanceDrawerVisible" size="620px" append-to-body>
      <el-skeleton :loading="attendanceDetailLoading" animated>
        <template #default>
          <div class="attendance-title">
            {{ attendanceDetail.courseName || '-' }} {{ attendanceDetail.classDate || '' }}
            {{ attendanceDetail.startTime || '' }}-{{ attendanceDetail.endTime || '' }}
          </div>
          <el-descriptions title="课次信息" :column="2" border>
            <el-descriptions-item label="上课时间">
              {{ attendanceDetail.startTime || '-' }} - {{ attendanceDetail.endTime || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="授课课程">{{ attendanceDetail.courseName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课老师">{{ attendanceDetail.teacherName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="授课课时">{{ attendanceDetail.lessonHours || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课教室">{{ attendanceDetail.classroom || '-' }}</el-descriptions-item>
            <el-descriptions-item label="上课内容">{{ attendanceDetail.content || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div class="sub-title">上课学员</div>
          <el-table :data="attendanceDetail.details || []" border>
            <el-table-column label="学员" prop="studentName" min-width="100" />
            <el-table-column label="手机号" prop="phone" min-width="120" />
            <el-table-column label="到课状态" prop="statusName" width="90" align="center" />
            <el-table-column label="扣除额度" width="100" align="center">
              <template #default="{ row }">
                {{ row.deductQuantity || 0 }}课时
              </template>
            </el-table-column>
            <el-table-column label="剩余额度" width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.afterRemaining !== null && row.afterRemaining !== undefined">{{ row.afterRemaining }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="备注" prop="remark" min-width="120" show-overflow-tooltip />
          </el-table>
        </template>
      </el-skeleton>
    </el-drawer>
    <leave-apply-dialog v-model="leaveOpen" :preset="leavePreset" />

    <el-dialog v-model="weeklyVisible" title="按周重复排课" width="620px" append-to-body>
      <el-form ref="weeklyFormRef" :model="weeklyForm" :rules="weeklyRules" label-width="96px">
        <el-form-item label="日期范围" prop="dateRange">
          <el-date-picker
            v-model="weeklyForm.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="每周" prop="weekdays">
          <el-checkbox-group v-model="weeklyForm.weekdays">
            <el-checkbox v-for="(label, index) in weekdayLabels" :key="index" :label="index + 1">{{ label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="上课时间" required>
          <el-time-picker v-model="weeklyForm.startClock" value-format="HH:mm" format="HH:mm" placeholder="开始" style="width: 45%" />
          <span class="range-sep">-</span>
          <el-time-picker v-model="weeklyForm.endClock" value-format="HH:mm" format="HH:mm" placeholder="结束" style="width: 45%" />
        </el-form-item>
        <el-form-item label="上课教室">
          <el-input v-model="weeklyForm.classroom" maxlength="100" placeholder="不填则使用班级教室" />
        </el-form-item>
        <el-form-item label="授课课时">
          <el-input-number v-model="weeklyForm.lessonHours" :min="0.5" :max="99" :step="0.5" :precision="2" />
        </el-form-item>
        <el-form-item label="上课内容">
          <el-input v-model="weeklyForm.content" maxlength="500" />
        </el-form-item>
        <div class="weekly-tip">上课老师为班级主讲老师（{{ classInfo.teacherName || '未设置' }}）；名单为当前在读学员。任一日期与老师/班级/教室冲突时整批不生成，单次最多 100 节。</div>
      </el-form>
      <template #footer>
        <el-button @click="weeklyVisible = false">取消</el-button>
        <el-button type="primary" :loading="weeklySubmitting" @click="submitWeekly">生成课次</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantClassDetail">
import { computed, getCurrentInstance, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  addClassStudents,
  getClass,
  getClassAttendance,
  listClassAttendance,
  listAvailableClassStudents,
  listClassStudents,
  removeClassStudents
} from '@/api/assistant/class';
import { delScheduleEvent, getScheduleEvent, listScheduleEvent } from '@/api/teach/schedule';
import { weeklySchedule } from '@/api/teach/lesson';
import LeaveApplyDialog from '@/views/assistant/leave/components/LeaveApplyDialog';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();

const classId = computed(() => Number(route.params.id));
const loading = ref(false);
const membersLoading = ref(false);
const availableLoading = ref(false);
const attendanceLoading = ref(false);
const scheduleLoading = ref(false);
const addStudentLoading = ref(false);
const activeTab = ref(route.query.tab || 'schedule');
const classInfo = ref({});
const memberList = ref([]);
const scheduleList = ref([]);
const attendanceList = ref([]);
const scheduleDetail = ref({});
const attendanceDetail = ref({});
const selectedMemberIds = ref([]);
const memberSearchKeyword = ref('');
const studentDialogVisible = ref(false);
const scheduleDrawerVisible = ref(false);
const attendanceDrawerVisible = ref(false);
const scheduleDetailLoading = ref(false);
const attendanceDetailLoading = ref(false);
const availableStudentKeyword = ref('');
const availableStudents = ref([]);
const selectedAvailableIds = ref([]);

const filteredMemberList = computed(() => {
  const keyword = memberSearchKeyword.value.trim().toLowerCase();
  if (!keyword) {
    return memberList.value;
  }
  return memberList.value.filter(item => {
    return (item.studentName || '').toLowerCase().includes(keyword) || (item.phone || '').includes(keyword);
  });
});

async function loadDetail() {
  loading.value = true;
  try {
    const response = await getClass(classId.value);
    classInfo.value = response.data || {};
  } finally {
    loading.value = false;
  }
}

async function loadMembers() {
  membersLoading.value = true;
  try {
    const response = await listClassStudents(classId.value);
    memberList.value = response.data || [];
  } finally {
    membersLoading.value = false;
  }
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

function formatScheduleRow(row) {
  return {
    ...row,
    startClock: formatClock(row.startTime),
    endClock: formatClock(row.endTime),
  };
}

const weekdayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const weeklyVisible = ref(false);
const weeklySubmitting = ref(false);
const weeklyFormRef = ref(null);
const weeklyForm = ref({});
const weeklyRules = {
  dateRange: [{ required: true, message: '请选择日期范围', trigger: 'change' }],
  weekdays: [{ type: 'array', required: true, min: 1, message: '请选择星期', trigger: 'change' }]
};

function openWeeklyDialog() {
  if (!classInfo.value.teacherId) {
    proxy.$modal.msgWarning('请先在班级信息中设置主讲老师');
    return;
  }
  weeklyForm.value = {
    dateRange: [],
    weekdays: [],
    startClock: '',
    endClock: '',
    classroom: '',
    lessonHours: Number(classInfo.value.lessonHours || 1),
    content: ''
  };
  weeklyVisible.value = true;
}

function submitWeekly() {
  weeklyFormRef.value.validate(async valid => {
    if (!valid) return;
    const form = weeklyForm.value;
    if (!form.startClock || !form.endClock || form.endClock <= form.startClock) {
      proxy.$modal.msgWarning('请正确选择上课时间');
      return;
    }
    weeklySubmitting.value = true;
    try {
      const response = await weeklySchedule({
        classId: classId.value,
        startDate: form.dateRange[0],
        endDate: form.dateRange[1],
        weekdays: form.weekdays,
        startClock: form.startClock,
        endClock: form.endClock,
        classroom: form.classroom || undefined,
        lessonHours: form.lessonHours,
        content: form.content || undefined
      });
      proxy.$modal.msgSuccess(response.msg || '排课成功');
      weeklyVisible.value = false;
      await Promise.all([loadScheduleList(), loadDetail()]);
    } finally {
      weeklySubmitting.value = false;
    }
  });
}

async function loadScheduleList() {
  scheduleLoading.value = true;
  try {
    const response = await listScheduleEvent({
      pageNum: 1,
      pageSize: 1000,
      classId: classId.value,
    });
    scheduleList.value = (response.rows || []).map(formatScheduleRow);
  } finally {
    scheduleLoading.value = false;
  }
}

async function loadAttendanceList() {
  attendanceLoading.value = true;
  try {
    const response = await listClassAttendance(classId.value);
    attendanceList.value = response.data || [];
  } finally {
    attendanceLoading.value = false;
  }
}

async function loadAvailableStudents() {
  availableLoading.value = true;
  try {
    const response = await listAvailableClassStudents(classId.value, { keyword: availableStudentKeyword.value });
    availableStudents.value = response.data || [];
  } finally {
    availableLoading.value = false;
  }
}

function handleAddStudent() {
  selectedAvailableIds.value = [];
  availableStudentKeyword.value = '';
  studentDialogVisible.value = true;
  loadAvailableStudents();
}

function handleAvailableSelectionChange(selection) {
  selectedAvailableIds.value = selection.map(item => item.id);
}

async function confirmAddStudents() {
  if (!selectedAvailableIds.value.length) {
    proxy.$modal.msgWarning('请选择要添加的学员');
    return;
  }
  addStudentLoading.value = true;
  try {
    await addClassStudents(classId.value, { studentIds: selectedAvailableIds.value });
    proxy.$modal.msgSuccess('添加成功');
    studentDialogVisible.value = false;
    await Promise.all([loadDetail(), loadMembers()]);
  } finally {
    addStudentLoading.value = false;
  }
}

function handleMemberSelectionChange(selection) {
  selectedMemberIds.value = selection.map(item => item.studentId);
}

function handleBatchRemove() {
  removeStudents(selectedMemberIds.value);
}

function handleRemoveStudent(row) {
  removeStudents([row.studentId]);
}

function removeStudents(studentIds) {
  if (!studentIds.length) {
    return;
  }
  proxy.$modal.confirm('确认将选中的学员移出本班吗？').then(async () => {
    await removeClassStudents(classId.value, studentIds.join(','));
    proxy.$modal.msgSuccess('移出成功');
    selectedMemberIds.value = [];
    await Promise.all([loadDetail(), loadMembers()]);
  }).catch(() => {});
}

function handleViewStudent(row) {
  router.push(`/assistant/student/detail/${row.studentId}`);
}

function handleEdit() {
  router.push('/assistant/class');
}

function handleScheduleClass() {
  router.push({ path: '/assistant/schedule', query: { tab: 'class', classId: classId.value, action: 'add' } });
}

function handleDirectAttendance() {
  router.push(`/assistant/class/attendance/${classId.value}`);
}

async function handleViewSchedule(row) {
  scheduleDrawerVisible.value = true;
  scheduleDetailLoading.value = true;
  scheduleDetail.value = {};
  try {
    const response = await getScheduleEvent(row.id);
    scheduleDetail.value = formatScheduleRow(response.data || {});
  } finally {
    scheduleDetailLoading.value = false;
  }
}

function handleScheduleAttendance(row) {
  router.push({ path: `/assistant/class/attendance/${classId.value}`, query: { eventId: row.id } });
}

function handleDeleteSchedule(row) {
  proxy.$modal.confirm(`确认删除 ${row.eventDate} ${row.startClock}-${row.endClock} 的课次吗？`).then(async () => {
    await delScheduleEvent(row.id);
    proxy.$modal.msgSuccess('删除成功');
    await Promise.all([loadDetail(), loadScheduleList()]);
  }).catch(() => {});
}

async function handleViewAttendance(row) {
  attendanceDrawerVisible.value = true;
  attendanceDetailLoading.value = true;
  attendanceDetail.value = {};
  try {
    const response = await getClassAttendance(row.id);
    attendanceDetail.value = response.data || {};
  } finally {
    attendanceDetailLoading.value = false;
  }
}

const leaveOpen = ref(false);
const leavePreset = ref({});

function handleStudentLeave(row) {
  leavePreset.value = { studentId: row.studentId, studentName: row.studentName, classId: classId.value };
  leaveOpen.value = true;
}

function goBack() {
  router.push('/assistant/class');
}

onMounted(() => {
  loadDetail();
  loadMembers();
  loadScheduleList();
  loadAttendanceList();
});
</script>

<style scoped lang="scss">
.class-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .class-info-card,
  .detail-tabs {
    background: #fff;
    border-radius: 4px;
    padding: 18px;
    margin-bottom: 12px;
  }

  .class-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 18px;

    .class-name {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .info-row {
    margin-bottom: 14px;
    color: #606266;

    .label {
      color: #909399;
    }

    .value {
      color: #303133;
    }
  }

  .toolbar-line,
  .dialog-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }

  .muted {
    color: #909399;
  }

  .dialog-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;

    .selected-count {
      margin-right: auto;
      color: #606266;
    }
  }

  .attendance-title {
    margin-bottom: 18px;
    font-size: 16px;
    font-weight: 600;
    color: #ff7d00;
  }

  .sub-title {
    margin: 20px 0 12px;
    font-weight: 600;
    color: #303133;
  }
}
.range-sep {
  margin: 0 6px;
}

.weekly-tip {
  padding-left: 96px;
  color: #909399;
  font-size: 12px;
  line-height: 18px;
}
</style>
