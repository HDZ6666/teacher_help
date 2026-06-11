<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="家长姓名" prop="parentName">
        <el-input
          v-model="queryParams.parentName"
          placeholder="请输入家长姓名"
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
      <el-form-item label="职业" prop="occupation">
        <el-input
          v-model="queryParams.occupation"
          placeholder="请输入职业"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="家长状态" clearable style="width: 240px">
          <el-option
            v-for="dict in sys_normal_disable"
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
          v-hasPermi="['teach:parent:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['teach:parent:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['teach:parent:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['teach:parent:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="parentList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="家长ID" align="center" prop="id" />
      <el-table-column label="家长姓名" align="center" prop="parentName" />
      <el-table-column label="昵称" align="center" prop="nickname" />
      <el-table-column label="手机号码" align="center" prop="phone" />
      <el-table-column label="头像" align="center" prop="avatarUrl" width="100">
        <template #default="scope">
          <image-preview :src="scope.row.avatarUrl" :width="50" :height="50"/>
        </template>
      </el-table-column>
      <el-table-column label="职业" align="center" prop="occupation" />
      <el-table-column label="教育程度" align="center" prop="educationLevel" />
      <el-table-column label="收入范围" align="center" prop="incomeRange" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.incomeRange === 1" type="info">5万以下</el-tag>
          <el-tag v-else-if="scope.row.incomeRange === 2" type="success">5-10万</el-tag>
          <el-tag v-else-if="scope.row.incomeRange === 3" type="warning">10-20万</el-tag>
          <el-tag v-else-if="scope.row.incomeRange === 4" type="danger">20万以上</el-tag>
          <el-tag v-else type="default">未知</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status">
        <template #default="scope">
          <el-tag v-if="scope.row.status === 1" type="success">正常</el-tag>
          <el-tag v-else-if="scope.row.status === 2" type="warning">暂停</el-tag>
          <el-tag v-else-if="scope.row.status === 3" type="danger">已注销</el-tag>
          <el-tag v-else type="info">未知</el-tag>
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
            <el-button link type="primary" icon="View" @click="handleDetail(scope.row)" v-hasPermi="['teach:parent:query']"></el-button>
          </el-tooltip>
          <el-tooltip content="修改" placement="top">
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['teach:parent:edit']"></el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['teach:parent:remove']"></el-button>
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

    <!-- 添加或修改家长对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="parentRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="家长姓名" prop="parentName">
              <el-input v-model="form.parentName" placeholder="请输入家长真实姓名" maxlength="50" />
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
            <el-form-item label="微信号" prop="wechatId">
              <el-input v-model="form.wechatId" placeholder="请输入微信号" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急联系人" prop="emergencyContact">
              <el-input v-model="form.emergencyContact" placeholder="请输入紧急联系人姓名" maxlength="50" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="紧急联系电话" prop="emergencyPhone">
              <el-input v-model="form.emergencyPhone" placeholder="请输入紧急联系电话" maxlength="11" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="form.idCard" placeholder="请输入身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="家庭地址" prop="familyAddress">
          <el-input v-model="form.familyAddress" placeholder="请输入家庭地址" maxlength="255" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职业" prop="occupation">
              <el-input v-model="form.occupation" placeholder="请输入职业" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="教育程度" prop="educationLevel">
              <el-select v-model="form.educationLevel" placeholder="请选择教育程度" clearable style="width: 100%">
                <el-option
                  v-for="dict in teach_education_level"
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
            <el-form-item label="家庭收入" prop="incomeRange">
              <el-select v-model="form.incomeRange" placeholder="请选择家庭收入范围" clearable style="width: 100%">
                <el-option
                  v-for="dict in teach_income_range"
                  :key="dict.value"
                  :label="dict.label"
                  :value="parseInt(dict.value)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="付费偏好" prop="paymentPreference">
              <el-select v-model="form.paymentPreference" placeholder="请选择付费偏好" style="width: 100%">
                <el-option
                  v-for="dict in teach_payment_preference"
                  :key="dict.value"
                  :label="dict.label"
                  :value="parseInt(dict.value)"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="家长状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio
              v-for="dict in sys_normal_disable"
              :key="dict.value"
              :label="parseInt(dict.value)"
            >{{dict.label}}</el-radio>
          </el-radio-group>
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

<script setup name="Parent">
import { listParent, getParent, delParent, addParent, updateParent, exportParent } from "@/api/teach/parent";

const { proxy } = getCurrentInstance();
const { sys_normal_disable, teach_education_level, teach_income_range, teach_payment_preference } = proxy.useDict('sys_normal_disable', 'teach_education_level', 'teach_income_range', 'teach_payment_preference');

const parentList = ref([]);
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
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    parentName: null,
    nickname: null,
    phone: null,
    occupation: null,
    status: null,
  },
  rules: {
    parentName: [
      { required: true, message: "家长姓名不能为空", trigger: "blur" },
      { min: 2, max: 50, message: '家长姓名长度必须介于 2 和 50 之间', trigger: 'blur' }
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
    wechatId: [
      { max: 50, message: "微信号长度不能超过50个字符", trigger: "blur" }
    ],
    emergencyContact: [
      { max: 50, message: "紧急联系人姓名长度不能超过50个字符", trigger: "blur" }
    ],
    emergencyPhone: [
      {
        pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
        message: "请输入正确的手机号码",
        trigger: "blur"
      }
    ],
    idCard: [
      {
        pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
        message: "请输入正确的身份证号码",
        trigger: "blur"
      }
    ],
    familyAddress: [
      { max: 255, message: "地址长度不能超过255个字符", trigger: "blur" }
    ],
    occupation: [
      { max: 50, message: "职业长度不能超过50个字符", trigger: "blur" }
    ]
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询家长列表 */
function getList() {
  loading.value = true;
  listParent(proxy.addDateRange(queryParams.value, dateRange.value)).then(response => {
    parentList.value = response.rows;
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
    userId: null,
    parentName: null,
    nickname: null,
    phone: null,
    password: null,
    avatarUrl: null,
    idCard: null,
    wechatId: null,
    emergencyContact: null,
    emergencyPhone: null,
    familyAddress: null,
    occupation: null,
    educationLevel: null,
    incomeRange: null,
    paymentPreference: 1,
    status: 1,
    remark: null
  };
  proxy.resetForm("parentRef");
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
  title.value = "添加家长";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _id = row.id || ids.value
  getParent(_id).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改家长";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["parentRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        updateParent(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addParent(form.value).then(response => {
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
  proxy.$modal.confirm('是否确认删除家长编号为"' + _ids + '"的数据项？').then(function() {
    return delParent(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}





/** 导出按钮操作 */
function handleExport() {
  proxy.$modal.confirm("是否确认导出所有家长数据项?").then(() => {
    exportParent(queryParams.value).then(response => {
      proxy.$download.saveAs(response, `parent_${new Date().getTime()}.xlsx`);
    });
  });
}

/** 详情按钮操作 */
function handleDetail(row) {
  proxy.$router.push("/teach/parent-detail/index/" + row.id);
}

onMounted(() => {
  getList();
});
</script>
