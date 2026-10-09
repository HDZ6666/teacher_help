<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="学生姓名" prop="studentName">
        <el-input
          v-model="queryParams.studentName"
          placeholder="请输入学生姓名"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="性别" prop="gender">
        <el-select v-model="queryParams.gender" placeholder="请选择性别" clearable style="width: 240px">
          <el-option label="男" value="1" />
          <el-option label="女" value="2" />
        </el-select>
      </el-form-item>
      <el-form-item label="学校名称" prop="schoolName">
        <el-input
          v-model="queryParams.schoolName"
          placeholder="请输入学校名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="年级" prop="grade">
        <el-select v-model="queryParams.grade" placeholder="请选择年级" clearable style="width: 240px">
          <el-option
            v-for="dict in teach_grade"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="家长手机号" prop="parentPhone">
        <el-input
          v-model="queryParams.parentPhone"
          placeholder="请输入家长手机号"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
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
          v-hasPermi="['teach:student:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['teach:student:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['teach:student:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['teach:student:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="studentList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="学生ID" align="center" prop="id" />
      <el-table-column label="学生姓名" align="center" prop="studentName" />
      <el-table-column label="性别" align="center" prop="gender">
        <template #default="scope">
          <dict-tag :options="sys_user_sex" :value="scope.row.gender"/>
        </template>
      </el-table-column>
      <el-table-column label="出生日期" align="center" prop="birthday" width="120">
        <template #default="scope">
          <span>{{ parseTime(scope.row.birthday, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="学校名称" align="center" prop="schoolName" />
      <el-table-column label="年级" align="center" prop="grade" />
      <el-table-column label="班级" align="center" prop="className" />
      <el-table-column label="学习风格" align="center" prop="learningStyle" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.learningStyle === 1" type="success">视觉型</el-tag>
          <el-tag v-else-if="scope.row.learningStyle === 2" type="warning">听觉型</el-tag>
          <el-tag v-else-if="scope.row.learningStyle === 3" type="info">动觉型</el-tag>
          <el-tag v-else type="default">未知</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="家长姓名" align="center" prop="parentName" />
      <el-table-column label="家长手机号" align="center" prop="parentPhone" />
      <el-table-column label="状态" align="center" prop="status">
        <template #default="scope">
          <el-tag v-if="String(scope.row.status) === '0'" type="success">在读</el-tag>
          <el-tag v-else-if="String(scope.row.status) === '1'" type="warning">休学</el-tag>
          <el-tag v-else-if="String(scope.row.status) === '2'" type="info">转学</el-tag>
          <el-tag v-else-if="String(scope.row.status) === '3'" type="primary">毕业</el-tag>
          <el-tag v-else type="default">未知</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)" v-hasPermi="['teach:student:query']">详情</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['teach:student:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['teach:student:remove']">删除</el-button>
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

    <!-- 添加或修改学生对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="studentRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学生姓名" prop="studentName">
              <el-input v-model="form.studentName" placeholder="请输入学生姓名" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio :label="1">男</el-radio>
                <el-radio :label="2">女</el-radio>
                <el-radio :label="0">未知</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birthday">
              <el-date-picker clearable
                v-model="form.birthday"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择出生日期"
                style="width: 100%">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联家长" prop="parentId">
              <el-select v-model="form.parentId" placeholder="请选择家长" clearable style="width: 100%">
                <el-option
                  v-for="parent in parentList"
                  :key="parent.id"
                  :label="parent.parentName + '(' + parent.phone + ')'"
                  :value="parent.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学校名称" prop="schoolName">
              <el-input v-model="form.schoolName" placeholder="请输入学校名称" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年级" prop="grade">
              <el-select v-model="form.grade" placeholder="请选择年级" clearable style="width: 100%">
                <el-option
                  v-for="dict in teach_grade"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="班级" prop="className">
              <el-input v-model="form.className" placeholder="请输入班级" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学号" prop="studentIdInSchool">
              <el-input v-model="form.studentIdInSchool" placeholder="请输入学号" maxlength="50" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学习风格" prop="learningStyle">
              <el-select v-model="form.learningStyle" placeholder="请选择学习风格" clearable style="width: 100%">
                <el-option
                  v-for="dict in teach_learning_style"
                  :key="dict.value"
                  :label="dict.label"
                  :value="parseInt(dict.value)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急联系人" prop="emergencyContact">
              <el-input v-model="form.emergencyContact" placeholder="请输入紧急联系人电话" maxlength="20" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="个性特征" prop="personalityTraits">
          <el-select v-model="form.personalityTraits" multiple placeholder="请选择个性特征" style="width: 100%">
            <el-option label="活泼开朗" value="活泼开朗" />
            <el-option label="内向安静" value="内向安静" />
            <el-option label="好奇心强" value="好奇心强" />
            <el-option label="专注力强" value="专注力强" />
            <el-option label="创造力强" value="创造力强" />
            <el-option label="逻辑思维强" value="逻辑思维强" />
            <el-option label="语言表达能力强" value="语言表达能力强" />
            <el-option label="动手能力强" value="动手能力强" />
          </el-select>
        </el-form-item>
        <el-form-item label="兴趣爱好" prop="interests">
          <el-select v-model="form.interests" multiple placeholder="请选择兴趣爱好" style="width: 100%">
            <el-option label="阅读" value="阅读" />
            <el-option label="绘画" value="绘画" />
            <el-option label="音乐" value="音乐" />
            <el-option label="体育运动" value="体育运动" />
            <el-option label="科学实验" value="科学实验" />
            <el-option label="手工制作" value="手工制作" />
            <el-option label="电脑游戏" value="电脑游戏" />
            <el-option label="舞蹈" value="舞蹈" />
          </el-select>
        </el-form-item>
        <el-form-item label="学习特点" prop="learningCharacteristics">
          <el-select v-model="form.learningCharacteristics" multiple placeholder="请选择学习特点" style="width: 100%">
            <el-option label="记忆力强" value="记忆力强" />
            <el-option label="理解力强" value="理解力强" />
            <el-option label="逻辑思维好" value="逻辑思维好" />
            <el-option label="想象力丰富" value="想象力丰富" />
            <el-option label="注意力集中" value="注意力集中" />
            <el-option label="学习主动性强" value="学习主动性强" />
          </el-select>
        </el-form-item>
        <el-form-item label="学习目标" prop="learningGoals">
          <el-input v-model="form.learningGoals" type="textarea" :rows="2" placeholder="请输入学习目标" maxlength="500" />
        </el-form-item>
        <el-form-item label="薄弱科目" prop="weakSubjects">
          <el-select v-model="form.weakSubjects" multiple placeholder="请选择薄弱科目" style="width: 100%">
            <el-option
              v-for="dict in teach_subjects"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注信息" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注信息" maxlength="500" />
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

<script setup name="Student">
import { listStudent, getStudent, delStudent, addStudent, updateStudent, listParents, exportStudent } from "@/api/teach/student";

const { proxy } = getCurrentInstance();
const { sys_user_sex, teach_grade, teach_learning_style, teach_subjects } = proxy.useDict('sys_user_sex', 'teach_grade', 'teach_learning_style', 'teach_subjects');

const studentList = ref([]);
const parentList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    studentName: null,
    gender: null,
    schoolName: null,
    grade: null,
    parentPhone: null,
  },
  rules: {
    studentName: [
      { required: true, message: "学生姓名不能为空", trigger: "blur" },
      { min: 2, max: 50, message: '学生姓名长度必须介于 2 和 50 之间', trigger: 'blur' }
    ],
    parentId: [
      { required: true, message: "请选择关联家长", trigger: "change" }
    ],
    schoolName: [
      { max: 100, message: "学校名称长度不能超过100个字符", trigger: "blur" }
    ],
    className: [
      { max: 50, message: "班级名称长度不能超过50个字符", trigger: "blur" }
    ],
    studentIdInSchool: [
      { max: 50, message: "学号长度不能超过50个字符", trigger: "blur" }
    ],
    nickname: [
      { max: 50, message: "昵称长度不能超过50个字符", trigger: "blur" }
    ],
    avatarUrl: [
      { max: 512, message: "头像URL长度不能超过512个字符", trigger: "blur" }
    ],
    learningGoals: [
      { max: 500, message: "学习目标长度不能超过500个字符", trigger: "blur" }
    ]
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询学生列表 */
function getList() {
  loading.value = true;
  listStudent(queryParams.value).then(response => {
    studentList.value = response.rows;
    total.value = response.total;
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
    parentId: null,
    studentName: null,
    nickname: null,
    avatarUrl: null,
    gender: null,
    birthday: null,
    schoolName: null,
    grade: null,
    className: null,
    learningCharacteristics: [],
    interests: [],
    personalityTraits: [],
    learningGoals: null,
    weakSubjects: [],
    status: '0',
    remark: null
  };
  proxy.resetForm("studentRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
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
  getParentList();
  open.value = true;
  title.value = "添加学生";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  getParentList();
  const _id = row.id || ids.value
  getStudent(_id).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改学生";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["studentRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        updateStudent(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addStudent(form.value).then(response => {
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
  proxy.$modal.confirm('是否确认删除学生编号为"' + _ids + '"的数据项？').then(function() {
    return delStudent(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}



/** 详情按钮操作 */
function handleDetail(row) {
  proxy.$router.push("/teach/student-detail/index/" + row.id);
}

/** 导出按钮操作 */
function handleExport() {
  proxy.$modal.confirm("是否确认导出所有学生数据项?").then(() => {
    exportStudent(queryParams.value).then(response => {
      proxy.$download.saveAs(response, `student_${new Date().getTime()}.xlsx`);
    });
  });
}

/** 获取家长列表 */
function getParentList() {
  listParents().then(response => {
    parentList.value = response.rows || response.data || [];
  });
}

onMounted(() => {
  getList();
});
</script>
