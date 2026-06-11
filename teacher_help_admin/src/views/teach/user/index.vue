<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="教师姓名" prop="teacherName">
        <el-input
          v-model="queryParams.teacherName"
          placeholder="请输入教师姓名"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input
          v-model="queryParams.nickname"
          placeholder="请输入昵称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="手机号码" prop="phone">
        <el-input
          v-model="queryParams.phone"
          placeholder="请输入手机号码"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="教学科目" prop="teachingSubjects">
        <el-select v-model="queryParams.teachingSubjects" placeholder="请选择教学科目" clearable style="width: 240px">
          <el-option
            v-for="dict in (teach_subjects || [])"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="教师状态" clearable style="width: 240px">
          <el-option
            v-for="dict in (teacher_status || [])"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间" style="width: 308px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['teach:teacher:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['teach:teacher:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['teach:teacher:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['teach:teacher:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="teacherList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="教师ID" align="center" prop="id" />
      <el-table-column label="教师姓名" align="center" prop="teacherName" />
      <el-table-column label="昵称" align="center" prop="nickname" />
      <el-table-column label="手机号码" align="center" prop="phone" />
      <el-table-column label="头像" align="center" prop="avatarUrl" width="100">
        <template #default="scope">
          <image-preview :src="scope.row.avatarUrl" :width="50" :height="50"/>
        </template>
      </el-table-column>
      <el-table-column label="教学科目" align="center" prop="teachingSubjects" width="120">
        <template #default="scope">
          <el-tag
            v-for="subject in (scope.row.teachingSubjects || [])"
            :key="subject"
            size="small"
            style="margin: 2px;"
          >
            {{ subject }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="教学年级" align="center" prop="teachingGrades" width="150">
        <template #default="scope">
          <el-tag
            v-for="grade in (scope.row.teachingGrades || [])"
            :key="grade"
            type="success"
            size="small"
            style="margin: 2px;"
          >
            {{ grade }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="课时费" align="center" prop="hourlyRate" width="100">
        <template #default="scope">
          <span>¥{{ scope.row.hourlyRate }}/时</span>
        </template>
      </el-table-column>
      <el-table-column label="工作经验" align="center" prop="workExperience" width="100">
        <template #default="scope">
          <span>{{ scope.row.workExperience }}年</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status">
        <template #default="scope">
          <dict-tag :options="teacher_status" :value="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-tooltip content="详情" placement="top">
            <el-button link type="primary" icon="View" @click="handleDetail(scope.row)" v-hasPermi="['teach:teacher:query']"></el-button>
          </el-tooltip>
          <el-tooltip content="修改" placement="top">
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['teach:teacher:edit']"></el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['teach:teacher:remove']"></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    
    <pagination
      v-show="total>0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改教师对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="teacherRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="教师姓名" prop="teacherName">
              <el-input v-model="form.teacherName" placeholder="请输入教师真实姓名" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="form.nickname" placeholder="请输入昵称" maxlength="50" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号码" maxlength="11" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item v-if="form.id == undefined" label="用户密码" prop="password">
              <el-input v-model="form.password" placeholder="请输入用户密码" type="password" maxlength="20" show-password/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="form.idCard" placeholder="请输入身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资格证书" prop="qualificationCert">
              <el-input v-model="form.qualificationCert" placeholder="请输入教师资格证书编号" maxlength="255" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作经验" prop="workExperience">
              <el-input-number v-model="form.workExperience" :min="0" :max="50" placeholder="年" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课时费" prop="hourlyRate">
              <el-input-number v-model="form.hourlyRate" :min="0" :precision="2" placeholder="元/小时" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="教学科目" prop="teachingSubjects">
          <el-select v-model="form.teachingSubjects" multiple placeholder="请选择教学科目" style="width: 100%">
            <el-option
              v-for="dict in (teach_subjects || [])"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教学年级" prop="teachingGrades">
          <el-select v-model="form.teachingGrades" multiple placeholder="请选择教学年级" style="width: 100%">
            <el-option
              v-for="dict in (teach_grade || [])"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="银行账户" prop="bankAccount">
              <el-input v-model="form.bankAccount" placeholder="请输入银行账户" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开户银行" prop="bankName">
              <el-input v-model="form.bankName" placeholder="请输入开户银行" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="结算周期" prop="settlementCycle">
              <el-select v-model="form.settlementCycle" placeholder="请选择结算周期" style="width: 100%">
                <el-option
                  v-for="dict in (teach_settlement_cycle || [])"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="教师状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio
                  v-for="dict in teacher_status"
                  :key="dict.value"
                  :label="dict.value"
                >
                  {{ dict.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="个人简介" prop="introduction">
          <el-input v-model="form.introduction" type="textarea" :rows="3" placeholder="请输入个人简介" maxlength="500" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Teacher">
import { listTeacher, getTeacher, delTeacher, addTeacher, updateTeacher, exportTeacher } from "@/api/teach/teacher";

const { proxy } = getCurrentInstance();
const { teach_subjects, teach_grade, teach_settlement_cycle, teacher_status } = proxy.useDict('teach_subjects', 'teach_grade', 'teach_settlement_cycle', 'teacher_status');

const teacherList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const dateRange = ref([]);

const data = reactive({
  form: {
    id: null,
    userId: null,
    teacherName: null,
    nickname: null,
    phone: null,
    password: null,
    avatarUrl: null,
    idCard: null,
    teachingSubjects: [],
    teachingGrades: [],
    qualificationCert: null,
    workExperience: 0,
    introduction: null,
    hourlyRate: 0,
    bankAccount: null,
    bankName: null,
    settlementCycle: '0',
    status: '1',
    remark: null
  },
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    teacherName: null,
    nickname: null,
    phone: null,
    teachingSubjects: null,
    status: null,
  },
  rules: {
    teacherName: [
      { required: true, message: "教师姓名不能为空", trigger: "blur" },
      { min: 2, max: 50, message: '教师姓名长度必须介于 2 和 50 之间', trigger: 'blur' }
    ],
    nickname: [
      { min: 2, max: 50, message: '昵称长度必须介于 2 和 50 之间', trigger: 'blur' }
    ],
    phone: [
      { required: true, message: "手机号码不能为空", trigger: "blur" },
      {
        pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
        message: "请输入正确的手机号码",
        trigger: "blur"
      }
    ],
    password: [
      { required: true, message: "用户密码不能为空", trigger: "blur" },
      { min: 6, max: 20, message: "用户密码长度必须介于 6 和 20 之间", trigger: "blur" }
    ],
    idCard: [
      {
        pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
        message: "请输入正确的身份证号码",
        trigger: "blur"
      }
    ],
    teachingSubjects: [
      { required: true, message: "请选择教学科目", trigger: "change" }
    ],
    teachingGrades: [
      { required: true, message: "请选择教学年级", trigger: "change" }
    ],
    workExperience: [
      { type: 'number', min: 0, max: 50, message: "工作经验必须在0-50年之间", trigger: "blur" }
    ],
    hourlyRate: [
      { type: 'number', min: 0, message: "课时费不能为负数", trigger: "blur" }
    ],
    qualificationCert: [
      { max: 255, message: "资格证书编号长度不能超过255个字符", trigger: "blur" }
    ],
    bankAccount: [
      { max: 50, message: "银行账户长度不能超过50个字符", trigger: "blur" }
    ],
    bankName: [
      { max: 100, message: "开户银行长度不能超过100个字符", trigger: "blur" }
    ],
    introduction: [
      { max: 500, message: "个人简介长度不能超过500个字符", trigger: "blur" }
    ]
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询教师列表 */
function getList() {
  loading.value = true;
  listTeacher(proxy.addDateRange(queryParams.value, dateRange.value)).then(response => {
    // 确保每个教师对象都有必要的数组字段
    teacherList.value = (response.rows || []).map(teacher => ({
      ...teacher,
      teachingSubjects: teacher.teachingSubjects || [],
      teachingGrades: teacher.teachingGrades || []
    }));
    total.value = response.total || 0;
    loading.value = false;
  }).catch(() => {
    loading.value = false;
  });
}

// 取消按钮
function cancel() {
  open.value = false;
  reset();
}

// 表单重置
function reset() {
  form.value = {
    id: null,
    userId: null,
    teacherName: null,
    nickname: null,
    phone: null,
    password: null,
    avatarUrl: null,
    idCard: null,
    teachingSubjects: [],
    teachingGrades: [],
    qualificationCert: null,
    workExperience: 0,
    introduction: null,
    hourlyRate: 0,
    bankAccount: null,
    bankName: null,
    settlementCycle: '0',
    status: '1',
    remark: null
  };
  proxy.resetForm("teacherRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加教师";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _id = row.id || ids.value
  getTeacher(_id).then(response => {
    const data = response.data || {};
    form.value = {
      ...form.value,
      ...data,
      teachingSubjects: data.teachingSubjects || [],
      teachingGrades: data.teachingGrades || [],
      workExperience: data.workExperience || 0,
      hourlyRate: data.hourlyRate || 0,
      settlementCycle: data.settlementCycle || '0',
      status: data.status || '1'
    };
    open.value = true;
    title.value = "修改教师";
  }).catch(error => {
    console.error('获取教师信息失败:', error);
    proxy.$modal.msgError("获取教师信息失败");
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["teacherRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        updateTeacher(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addTeacher(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除教师编号为"' + _ids + '"的数据项？').then(function() {
    return delTeacher(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}





/** 导出按钮操作 */
function handleExport() {
  proxy.$modal.confirm("是否确认导出所有教师数据项?").then(() => {
    exportTeacher(queryParams.value).then(response => {
      proxy.$download.saveAs(response, `teacher_${new Date().getTime()}.xlsx`);
    });
  });
}

/** 详情按钮操作 */
function handleDetail(row) {
  proxy.$router.push("/teach/teacher-detail/index/" + row.id);
}

onMounted(() => {
  getList();
});
</script>
