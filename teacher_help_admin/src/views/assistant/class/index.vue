<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="班课" name="group">
        <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="搜索班级" prop="className">
            <el-input
              v-model="queryParams.className"
              placeholder="请输入班级名称"
              clearable
              style="width: 240px"
              @keyup.enter="handleQuery"
            />
          </el-form-item>
          <el-form-item label="关联课程" prop="courseId">
            <el-select v-model="queryParams.courseId" placeholder="请选择课程" clearable filterable style="width: 220px">
              <el-option v-for="course in courseOptions" :key="course.id" :label="course.courseName" :value="course.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="招生状态" prop="enrollStatus">
            <el-select v-model="queryParams.enrollStatus" placeholder="请选择状态" clearable style="width: 160px">
              <el-option label="招生中" :value="1" />
              <el-option label="已满员" :value="2" />
              <el-option label="已结课" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['teach:class:add']">
              添加班级
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['teach:class:remove']">
              批量删除
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="info" plain icon="Upload" @click="classImportOpen = true" v-hasPermi="['teach:class:import']">导入班级</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Top" :disabled="!ids.length" @click="openPromote" v-hasPermi="['teach:class:promote']">批量升班</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Finished" :disabled="!ids.length" @click="openGraduate" v-hasPermi="['teach:class:graduate']">批量结业</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
        </el-row>

        <class-table
          :loading="loading"
          :class-list="classList"
          @selection-change="handleSelectionChange"
          @detail="handleViewDetail"
          @edit="handleUpdate"
          @delete="handleDelete"
          @recharge-change="handleRechargeChange"
        />
      </el-tab-pane>

      <el-tab-pane label="一对一" name="one_to_one">
        <el-form :model="oneToOneQueryParams" ref="oneToOneQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="课堂学员" prop="studentKeyword">
            <el-input
              v-model="oneToOneQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 220px"
              @keyup.enter="handleOneToOneQuery"
            />
          </el-form-item>
          <el-form-item label="关联课程" prop="courseId">
            <el-select v-model="oneToOneQueryParams.courseId" placeholder="请选择课程" clearable filterable style="width: 220px">
              <el-option v-for="course in oneToOneCourses" :key="course.id" :label="course.courseName" :value="course.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="班级老师" prop="teacherId">
            <el-select v-model="oneToOneQueryParams.teacherId" placeholder="请选择老师" clearable filterable style="width: 180px">
              <el-option v-for="teacher in teacherOptions" :key="teacher.id" :label="teacher.teacherName" :value="teacher.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleOneToOneQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetOneToOneQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleOneToOneAdd" v-hasPermi="['teach:class:add']">
              新建/选择班级
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="danger" plain icon="Delete" :disabled="oneToOneMultiple" @click="handleOneToOneDelete" v-hasPermi="['teach:class:remove']">
              批量删除
            </el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getOneToOneList"></right-toolbar>
        </el-row>

        <class-table
          :loading="oneToOneLoading"
          :class-list="oneToOneClassList"
          one-to-one
          @selection-change="handleOneToOneSelectionChange"
          @detail="handleViewDetail"
          @edit="handleUpdate"
          @delete="handleOneToOneDelete"
          @recharge-change="handleRechargeChange"
        />
      </el-tab-pane>
    </el-tabs>

    <pagination
      v-show="currentTotal > 0"
      :total="currentTotal"
      v-model:page="currentQuery.pageNum"
      v-model:limit="currentQuery.pageSize"
      @pagination="activeTab === 'group' ? getList() : getOneToOneList()"
    />

    <el-drawer :title="drawerTitle" v-model="open" size="520px" append-to-body>
      <el-alert
        v-if="form.classMode === 'one_to_one'"
        title="一对一班级可先建立教学承载，后续在班级详情添加学员并排课点名。"
        type="warning"
        :closable="false"
        class="mb16"
      />
      <el-form ref="classRef" :model="form" :rules="rules" label-width="110px">
        <div class="form-section-title">基本信息</div>
        <el-form-item label="班级名称" prop="className">
          <el-input v-model="form.className" placeholder="请输入班级名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="班级编号">
          <el-input v-model="form.classNo" placeholder="不填则自动生成" maxlength="50" />
        </el-form-item>
        <el-form-item label="关联课程" prop="courseId">
          <el-select v-model="form.courseId" placeholder="请选择关联课程" filterable clearable style="width: 100%">
            <el-option
              v-for="course in drawerCourseOptions"
              :key="course.id"
              :label="course.courseName"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级容量">
          <div class="inline-control">
            <el-input-number v-model="form.maxStudents" :min="0" :max="999" controls-position="right" />
            <el-radio-group v-model="form.allowOverCapacity">
              <el-radio :label="1">可超额</el-radio>
              <el-radio :label="0">不可超额</el-radio>
            </el-radio-group>
          </div>
        </el-form-item>
        <el-form-item label="开课人数">
          <el-input-number v-model="form.minStudents" :min="0" :max="999" controls-position="right" />
        </el-form-item>
        <el-form-item label="支持在线选班">
          <el-switch v-model="form.allowOnlineEnroll" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="允许充值购时">
          <el-switch v-model="form.allowRecharge" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="班级分类">
          <el-select v-model="form.classType" placeholder="请选择班级分类" style="width: 100%">
            <el-option label="系统班型" value="system" />
            <el-option label="自建班型" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="自动点名">
          <el-switch v-model="form.autoAssignName" :active-value="1" :inactive-value="0" />
        </el-form-item>

        <div class="form-section-title">上课信息</div>
        <el-form-item label="授课课时">
          <el-input-number v-model="form.lessonHours" :min="0" :max="999" :precision="2" :step="0.5" controls-position="right" />
        </el-form-item>
        <el-form-item label="上课教室">
          <el-input v-model="form.classroom" placeholder="请输入教室或场地名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="班级老师">
          <el-select v-model="form.teacherId" placeholder="请选择老师" filterable clearable style="width: 100%">
            <el-option v-for="teacher in teacherOptions" :key="teacher.id" :label="teacher.teacherName" :value="teacher.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="cancel">取消</el-button>
          <el-button type="warning" :loading="submitLoading" @click="submitForm">保存</el-button>
        </div>
      </template>
    </el-drawer>

    <excel-import-dialog
      v-model="classImportOpen"
      title="导入班级"
      template-url="teach/class-batch/import/template"
      template-name="班级导入模板.xlsx"
      upload-url="/teach/class-batch/import"
      :tips="['请先下载模板，按“填写说明”页填写；当前一个班级只能关联一门课程，班级名称不能与已有班级重复。']"
      @success="getList"
    />

    <el-dialog title="批量升班" v-model="promoteOpen" width="1000px" append-to-body destroy-on-close>
      <el-alert type="info" :closable="false" show-icon class="mb8">
        <template #title>
          <div>每个原班级创建一个新班级，原班级全部在读学员转入新班并从原班级移出；不复制原班级排课，请升班后在新班级重新排课。</div>
          <div>新班级课程与原班级相同时沿用学员原课程账户；课程不同时绑定学员在新课程下的有效账户，没有的学员点名前需先报读。</div>
        </template>
      </el-alert>
      <el-table :data="promoteItems" border size="small">
        <el-table-column label="原班级" prop="sourceClassName" min-width="130" show-overflow-tooltip />
        <el-table-column label="在读人数" prop="currentStudents" width="80" align="center" />
        <el-table-column label="新班级名称" min-width="170">
          <template #default="scope"><el-input v-model="scope.row.className" maxlength="100" /></template>
        </el-table-column>
        <el-table-column label="关联课程" min-width="170">
          <template #default="scope">
            <el-select v-model="scope.row.courseId" filterable style="width: 100%">
              <el-option v-for="course in courseOptions" :key="course.id" :label="course.courseName" :value="course.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="班级老师" min-width="140">
          <template #default="scope">
            <el-select v-model="scope.row.teacherId" filterable clearable placeholder="沿用原班" style="width: 100%">
              <el-option v-for="teacher in teacherOptions" :key="teacher.id" :label="teacher.teacherName" :value="teacher.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="开班日期" width="160">
          <template #default="scope">
            <el-date-picker v-model="scope.row.startDate" type="date" value-format="YYYY-MM-DD" style="width: 140px" />
          </template>
        </el-table-column>
      </el-table>
      <el-checkbox v-model="promoteGraduateSource" style="margin-top: 12px">升班后将原班级标记为“已结课”</el-checkbox>
      <template #footer>
        <el-button @click="promoteOpen = false">取 消</el-button>
        <el-button type="primary" :loading="batchLoading" @click="submitPromote">提 交</el-button>
      </template>
    </el-dialog>

    <el-dialog title="批量结业" v-model="graduateOpen" width="680px" append-to-body destroy-on-close>
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        class="mb8"
        :title="`已选 ${graduateRows.length} 个班级。结业后班级在读学员将全部移出（课程账户与剩余课时不变），班级标记为已结课，不能再报名入班；已排未上的课次不会自动删除。`"
      />
      <el-table :data="graduateRows" border size="small">
        <el-table-column label="班级名称" prop="className" min-width="150" />
        <el-table-column label="关联课程" prop="courseName" min-width="140" />
        <el-table-column label="班级老师" prop="teacherName" width="110" />
        <el-table-column label="人数/容量" width="100">
          <template #default="scope">{{ scope.row.currentStudents || 0 }}/{{ scope.row.maxStudents || '未设置' }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="graduateOpen = false">取 消</el-button>
        <el-button type="danger" :loading="batchLoading" @click="submitGraduate">确定结业</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantClass">
import { computed, defineComponent, getCurrentInstance, h, onMounted, reactive, ref, resolveComponent, toRefs } from 'vue';
import { useRouter } from 'vue-router';
import { addClass, changeClassRecharge, delClass, listClass, updateClass } from '@/api/assistant/class';
import { listCourseOptions } from '@/api/assistant/course';
import { graduateClasses, promoteClasses } from '@/api/assistant/classBatch';
import ExcelImportDialog from '@/components/ExcelImportDialog/index.vue';
import { listTeacher } from '@/api/teach/teacher';

const ClassTable = defineComponent({
  name: 'ClassTable',
  props: {
    loading: Boolean,
    classList: {
      type: Array,
      default: () => []
    },
    oneToOne: Boolean
  },
  emits: ['selection-change', 'detail', 'edit', 'delete', 'recharge-change'],
  setup(props, { emit }) {
    const ElTable = resolveComponent('el-table');
    const ElTableColumn = resolveComponent('el-table-column');
    const ElLink = resolveComponent('el-link');
    const ElButton = resolveComponent('el-button');
    const ElSwitch = resolveComponent('el-switch');
    const ElTag = resolveComponent('el-tag');

    const columns = [
      h(ElTableColumn, { type: 'selection', width: 55, align: 'center' }),
      h(ElTableColumn, { label: props.oneToOne ? '班级合称' : '班级名称', minWidth: 160 }, {
        default: ({ row }) => h(ElLink, { type: 'primary', onClick: () => emit('detail', row) }, () => row.className)
      }),
      h(ElTableColumn, { label: '关联课程', prop: 'courseName', minWidth: 150, showOverflowTooltip: true }),
      props.oneToOne
        ? h(ElTableColumn, { label: '在读学员', prop: 'studentNames', width: 120, showOverflowTooltip: true })
        : null,
      h(ElTableColumn, { label: '班级老师', prop: 'teacherName', width: 120 }),
      h(ElTableColumn, { label: '人数/容量', width: 100, align: 'center' }, {
        default: ({ row }) => `${row.currentStudents || 0}/${row.maxStudents || '未设置'}`
      }),
      h(ElTableColumn, { label: '已上/预排课次', width: 120, align: 'center' }, {
        default: ({ row }) => `${row.completedLessons || 0}/${row.totalLessons || 0}`
      }),
      h(ElTableColumn, { label: '已结课时', prop: 'completedHours', width: 100, align: 'center' }),
      h(ElTableColumn, { label: '允许充值购时', width: 120, align: 'center' }, {
        default: ({ row }) => h(ElSwitch, {
          modelValue: row.allowRecharge,
          'onUpdate:modelValue': value => {
            row.allowRecharge = value;
            emit('recharge-change', row, value);
          },
          activeValue: 1,
          inactiveValue: 0
        })
      }),
      h(ElTableColumn, { label: '班级分类', width: 100, align: 'center' }, {
        default: ({ row }) => h(ElTag, { type: row.classType === 'system' ? 'success' : 'warning' }, () => row.classTypeName || '自建')
      }),
      h(ElTableColumn, { label: '招生状态', width: 100, align: 'center' }, {
        default: ({ row }) => h(ElTag, { type: row.enrollStatus === 1 ? 'success' : row.enrollStatus === 2 ? 'warning' : 'info' }, () => row.enrollStatusName || '-')
      }),
      h(ElTableColumn, { label: '操作', width: 220, align: 'center', fixed: 'right' }, {
        default: ({ row }) => [
          h(ElButton, { link: true, type: 'primary', onClick: () => emit('detail', row) }, () => '学员管理'),
          h(ElButton, { link: true, type: 'primary', onClick: () => emit('edit', row) }, () => '编辑'),
          h(ElButton, { link: true, type: 'danger', onClick: () => emit('delete', row) }, () => '删除')
        ]
      })
    ].filter(Boolean);

    return () => h(ElTable, {
      loading: props.loading,
      data: props.classList,
      border: true,
      onSelectionChange: selection => emit('selection-change', selection)
    }, () => columns);
  }
});

const { proxy } = getCurrentInstance();
const router = useRouter();

const activeTab = ref('group');
const showSearch = ref(true);
const loading = ref(false);
const oneToOneLoading = ref(false);
const submitLoading = ref(false);
const open = ref(false);
const drawerTitle = ref('');
const ids = ref([]);
const selectedClasses = ref([]);
const classImportOpen = ref(false);
const promoteOpen = ref(false);
const promoteItems = ref([]);
const promoteGraduateSource = ref(false);
const graduateOpen = ref(false);
const graduateRows = ref([]);
const batchLoading = ref(false);
const oneToOneIds = ref([]);
const classList = ref([]);
const oneToOneClassList = ref([]);
const courseOptions = ref([]);
const oneToOneCourses = ref([]);
const teacherOptions = ref([]);
const total = ref(0);
const oneToOneTotal = ref(0);

const data = reactive({
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    classMode: 'group',
    className: '',
    courseId: null,
    enrollStatus: null
  },
  oneToOneQueryParams: {
    pageNum: 1,
    pageSize: 10,
    classMode: 'one_to_one',
    studentKeyword: '',
    courseId: null,
    teacherId: null
  },
  form: {},
  rules: {
    className: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
    courseId: [{ required: true, message: '请选择关联课程', trigger: 'change' }]
  }
});

const { queryParams, oneToOneQueryParams, form, rules } = toRefs(data);

const multiple = computed(() => !ids.value.length);
const oneToOneMultiple = computed(() => !oneToOneIds.value.length);
const currentTotal = computed(() => activeTab.value === 'group' ? total.value : oneToOneTotal.value);
const currentQuery = computed(() => activeTab.value === 'group' ? queryParams.value : oneToOneQueryParams.value);
const drawerCourseOptions = computed(() => form.value.classMode === 'one_to_one' ? oneToOneCourses.value : courseOptions.value);

function reset() {
  form.value = {
    id: null,
    classNo: '',
    className: '',
    classMode: activeTab.value,
    classType: 'custom',
    courseId: null,
    teacherId: null,
    maxStudents: 0,
    minStudents: 0,
    allowOverCapacity: 1,
    allowOnlineEnroll: 0,
    allowRecharge: 1,
    autoAssignName: 0,
    lessonHours: 1,
    classroom: '',
    remark: ''
  };
  proxy?.resetForm('classRef');
}

async function loadOptions() {
  const [courseRes, teacherRes] = await Promise.all([
    listCourseOptions(),
    listTeacher({ pageNum: 1, pageSize: 500 })
  ]);
  const courses = courseRes.data || [];
  courseOptions.value = courses.filter(item => item.courseTypeValue !== 'one_to_one');
  oneToOneCourses.value = courses.filter(item => item.courseTypeValue === 'one_to_one');
  teacherOptions.value = teacherRes.rows || [];
}

async function getList() {
  loading.value = true;
  try {
    const response = await listClass(queryParams.value);
    classList.value = response.rows || [];
    total.value = response.total || 0;
  } finally {
    loading.value = false;
  }
}

async function getOneToOneList() {
  oneToOneLoading.value = true;
  try {
    const response = await listClass(oneToOneQueryParams.value);
    oneToOneClassList.value = response.rows || [];
    oneToOneTotal.value = response.total || 0;
  } finally {
    oneToOneLoading.value = false;
  }
}

function handleTabChange() {
  if (activeTab.value === 'group') {
    getList();
  } else {
    getOneToOneList();
  }
}

function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

function resetQuery() {
  proxy.resetForm('queryRef');
  queryParams.value.classMode = 'group';
  handleQuery();
}

function handleOneToOneQuery() {
  oneToOneQueryParams.value.pageNum = 1;
  getOneToOneList();
}

function resetOneToOneQuery() {
  proxy.resetForm('oneToOneQueryRef');
  oneToOneQueryParams.value.classMode = 'one_to_one';
  handleOneToOneQuery();
}

function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  selectedClasses.value = selection;
}

function openPromote() {
  promoteItems.value = selectedClasses.value.map(row => ({
    sourceClassId: row.id,
    sourceClassName: row.className,
    currentStudents: row.currentStudents || 0,
    className: `${row.className}（升班）`,
    courseId: row.courseId,
    teacherId: null,
    startDate: null
  }));
  promoteGraduateSource.value = false;
  promoteOpen.value = true;
}

async function submitPromote() {
  if (promoteItems.value.some(item => !String(item.className || '').trim() || !item.courseId)) {
    proxy.$modal.msgWarning('请填写新班级名称并选择关联课程');
    return;
  }
  batchLoading.value = true;
  try {
    const res = await promoteClasses({
      items: promoteItems.value.map(item => ({
        sourceClassId: item.sourceClassId,
        className: item.className.trim(),
        courseId: item.courseId,
        teacherId: item.teacherId || null,
        startDate: item.startDate || null
      })),
      graduateSource: promoteGraduateSource.value
    });
    proxy.$modal.msgSuccess(res.msg || '升班成功');
    promoteOpen.value = false;
    getList();
  } finally {
    batchLoading.value = false;
  }
}

function openGraduate() {
  graduateRows.value = [...selectedClasses.value];
  graduateOpen.value = true;
}

async function submitGraduate() {
  batchLoading.value = true;
  try {
    const res = await graduateClasses({ classIds: graduateRows.value.map(row => row.id) });
    proxy.$modal.msgSuccess(res.msg || '结业成功');
    graduateOpen.value = false;
    getList();
  } finally {
    batchLoading.value = false;
  }
}

function handleOneToOneSelectionChange(selection) {
  oneToOneIds.value = selection.map(item => item.id);
}

function handleAdd() {
  reset();
  form.value.classMode = 'group';
  drawerTitle.value = '新建班级';
  open.value = true;
}

function handleOneToOneAdd() {
  reset();
  form.value.classMode = 'one_to_one';
  form.value.maxStudents = 1;
  form.value.allowOverCapacity = 0;
  drawerTitle.value = '新建一对一班级';
  open.value = true;
}

function handleUpdate(row) {
  reset();
  form.value = {
    ...row,
    maxStudents: row.maxStudents || 0,
    minStudents: row.minStudents || 0,
    allowOverCapacity: row.allowOverCapacity ?? 1,
    allowOnlineEnroll: row.allowOnlineEnroll ?? 0,
    allowRecharge: row.allowRecharge ?? 1,
    autoAssignName: row.autoAssignName ?? 0,
    lessonHours: Number(row.lessonHours || 1)
  };
  drawerTitle.value = '编辑班级';
  open.value = true;
}

async function submitForm() {
  proxy.$refs.classRef.validate(async valid => {
    if (!valid) {
      return;
    }
    submitLoading.value = true;
    try {
      if (form.value.id) {
        await updateClass(form.value);
        proxy.$modal.msgSuccess('修改成功');
      } else {
        await addClass(form.value);
        proxy.$modal.msgSuccess('新增成功');
      }
      open.value = false;
      activeTab.value === 'group' ? getList() : getOneToOneList();
    } finally {
      submitLoading.value = false;
    }
  });
}

function cancel() {
  open.value = false;
  reset();
}

function handleViewDetail(row) {
  router.push({
    path: `/assistant/class/detail/${row.id}`,
    query: { type: row.classMode }
  });
}

function handleDelete(row) {
  const deleteIds = row?.id ? [row.id] : ids.value;
  if (!deleteIds.length) {
    return;
  }
  proxy.$modal.confirm('确认删除选中的班级吗？').then(async () => {
    await delClass(deleteIds.join(','));
    proxy.$modal.msgSuccess('删除成功');
    getList();
  }).catch(() => {});
}

function handleOneToOneDelete(row) {
  const deleteIds = row?.id ? [row.id] : oneToOneIds.value;
  if (!deleteIds.length) {
    return;
  }
  proxy.$modal.confirm('确认删除选中的一对一班级吗？').then(async () => {
    await delClass(deleteIds.join(','));
    proxy.$modal.msgSuccess('删除成功');
    getOneToOneList();
  }).catch(() => {});
}

async function handleRechargeChange(row, value) {
  try {
    await changeClassRecharge({ id: row.id, allowRecharge: value });
    proxy.$modal.msgSuccess('状态修改成功');
  } catch (error) {
    row.allowRecharge = value === 1 ? 0 : 1;
  }
}

onMounted(async () => {
  await loadOptions();
  getList();
});
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}

.mb16 {
  margin-bottom: 16px;
}

.form-section-title {
  margin: 8px 0 16px;
  font-weight: 600;
  color: #303133;
}

.inline-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
