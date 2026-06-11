<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- 班课Tab -->
      <el-tab-pane label="班课" name="groupClass">
        <!-- 搜索栏 -->
        <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="80px">
          <el-form-item label="班级名称" prop="className">
            <el-input
              v-model="queryParams.className"
              placeholder="请输入班级名称"
              clearable
              style="width: 200px;"
              @keyup.enter="handleQuery"
            />
          </el-form-item>
          <el-form-item label="类型筛选" prop="classType">
            <el-select
              v-model="queryParams.classType"
              placeholder="请选择类型"
              clearable
              style="width: 200px;"
            >
              <el-option label="全部" value="" />
              <el-option label="系统班型" value="system" />
              <el-option label="自建班型" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item label="招生状态" prop="enrollStatus">
            <el-select
              v-model="queryParams.enrollStatus"
              placeholder="请选择招生状态"
              clearable
              style="width: 200px;"
            >
              <el-option label="全部" value="" />
              <el-option label="招生中" value="1" />
              <el-option label="已满员" value="2" />
              <el-option label="已结课" value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleAdd">添加班级</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Upload" @click="handleImport">导入</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="info" plain icon="Download" @click="handleExport">导出</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-checkbox v-model="showOnlyMyClasses" @change="handleQuery">
              只看我的班级
            </el-checkbox>
          </el-col>
        </el-row>

        <!-- 班级列表 -->
        <el-table v-loading="loading" :data="classList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="班级名称" width="150" align="center">
            <template #default="scope">
              <el-link type="primary" @click="handleViewDetail(scope.row)">
                {{ scope.row.className }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="关联课程" prop="courseName" width="150" align="center" />
          <el-table-column label="班级老师" prop="teacherName" width="120" align="center" />
          <el-table-column label="人数/容量" width="100" align="center">
            <template #default="scope">
              {{ scope.row.currentStudents }}/{{ scope.row.maxStudents }}
            </template>
          </el-table-column>
          <el-table-column label="已上/预排课次" width="120" align="center">
            <template #default="scope">
              {{ scope.row.completedLessons }}/{{ scope.row.totalLessons }}
            </template>
          </el-table-column>
          <el-table-column label="已结课时" width="100" align="center" prop="completedHours" />
          <el-table-column label="允许充值购时" width="120" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.allowRecharge"
                :active-value="1"
                :inactive-value="0"
                @change="handleRechargeChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="班级分类" width="100" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.classType === 'system'" type="success">系统</el-tag>
              <el-tag v-else type="warning">自建</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="过往在读班级" width="120" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.isHistorical"
                :active-value="1"
                :inactive-value="0"
                disabled
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="200" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="handleViewDetail(scope.row)">
                学员管理
              </el-button>
              <el-button link type="primary" @click="handleEdit(scope.row)">
                点击
              </el-button>
              <el-button link type="danger" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </el-tab-pane>

      <!-- 一对一Tab -->
      <el-tab-pane label="一对一" name="oneToOne">
        <!-- 搜索栏 -->
        <el-form :model="oneToOneQueryParams" ref="oneToOneQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="课堂学员" prop="studentKeyword">
            <el-input
              v-model="oneToOneQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 200px;"
            >
              <template #suffix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="关联课程" prop="courseId">
            <el-select
              v-model="oneToOneQueryParams.courseId"
              placeholder="请选择课程"
              clearable
              style="width: 200px;"
            >
              <el-option
                v-for="course in courseOptions"
                :key="course.id"
                :label="course.courseName"
                :value="course.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="班级老师" prop="teacherId">
            <el-select
              v-model="oneToOneQueryParams.teacherId"
              placeholder="请选择老师"
              clearable
              style="width: 200px;"
            >
              <el-option
                v-for="teacher in teacherList"
                :key="teacher.id"
                :label="teacher.teacherName"
                :value="teacher.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleOneToOneQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetOneToOneQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleOneToOneAdd">新建/选择班级</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="info" plain icon="Upload">批量导入班级</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Download">导出</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-checkbox v-model="showOnlyMyOneToOneClasses">只看我的班级</el-checkbox>
          </el-col>
        </el-row>

        <!-- 一对一班级列表 -->
        <el-table
          v-loading="oneToOneLoading"
          :data="oneToOneClassList"
          border
          @selection-change="handleOneToOneSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="班级合称" width="150">
            <template #default="scope">
              <el-link type="primary" @click="handleOneToOneViewDetail(scope.row)">
                {{ scope.row.className }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="关联课程" prop="courseName" width="150" />
          <el-table-column label="学员姓名" prop="studentName" width="120" />
          <el-table-column label="手机号" prop="phone" width="130" />
          <el-table-column label="班级老师" prop="teacherName" width="120" />
          <el-table-column label="已上/排课课次" width="120">
            <template #default="scope">
              {{ scope.row.completedLessons }}/{{ scope.row.totalLessons }}
            </template>
          </el-table-column>
          <el-table-column label="已结课时" prop="completedHours" width="100" align="center" />
          <el-table-column label="剩余课时" prop="remainingHours" width="100" align="center" />
          <el-table-column label="允许充值购时" width="120" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.allowRecharge"
                :active-value="1"
                :inactive-value="0"
                @change="handleOneToOneRechargeChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="光阴充值课时" prop="rechargeHours" width="120" align="center" />
          <el-table-column label="班级分类" width="100" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.classType === 'system'" type="success">系统</el-tag>
              <el-tag v-else type="warning">自建</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="handleOneToOneViewDetail(scope.row)">点击</el-button>
              <el-button link type="danger" @click="handleOneToOneDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="oneToOneTotal > 0"
          :total="oneToOneTotal"
          v-model:page="oneToOneQueryParams.pageNum"
          v-model:limit="oneToOneQueryParams.pageSize"
          @pagination="getOneToOneList"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 新建/编辑班级对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px" append-to-body>
      <!-- 提示信息 -->
      <el-alert
        v-if="dialogType === 'oneToOne'"
        title="创建一对一班级方法，查看说明>>"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <!-- 班课表单 -->
      <el-form v-if="dialogType === 'groupClass'" ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 基本信息 -->
        <div style="font-weight: bold; margin-bottom: 15px; color: #303133;">基本信息</div>

        <el-form-item label="班级名称" prop="className">
          <el-input
            v-model="form.className"
            placeholder="请输入班级名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="关联课程" prop="courseId">
          <el-select
            v-model="form.courseId"
            placeholder="请选择关联课程"
            clearable
            style="width: 100%;"
          >
            <el-option
              v-for="course in courseOptions"
              :key="course.id"
              :label="course.courseName"
              :value="course.id"
            />
          </el-select>
          <el-tooltip content="选择该班级关联的课程" placement="top">
            <el-icon style="margin-left: 5px; cursor: pointer;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="班级容量">
          <el-radio-group v-model="form.capacityType">
            <el-radio :label="1">可超额</el-radio>
            <el-radio :label="0">不可超额</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="开课人数">
          <el-input-number
            v-model="form.minStudents"
            :min="0"
            :max="999"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="支持在线选课">
          <el-switch
            v-model="form.allowOnlineEnroll"
            :active-value="1"
            :inactive-value="0"
          />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            开启（在线商城）后可设置，
            <el-link type="primary" :underline="false">前往开启</el-link>
          </span>
        </el-form-item>

        <el-form-item label="允许充值购时">
          <el-switch
            v-model="form.allowRecharge"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>

        <el-form-item label="班级分类">
          <el-select
            v-model="form.classCategory"
            placeholder="不指定"
            clearable
            style="width: calc(100% - 60px);"
          >
            <el-option label="系统班型" value="system" />
            <el-option label="自建班型" value="custom" />
          </el-select>
          <el-link
            type="primary"
            :underline="false"
            style="margin-left: 10px;"
            @click="handleSetCategory"
          >
            设置
          </el-link>
        </el-form-item>

        <el-form-item label="自动派名">
          <el-switch
            v-model="form.autoAssignName"
            :active-value="1"
            :inactive-value="0"
          />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">关闭</span>
          <div style="margin-top: 5px; color: #909399; font-size: 12px; line-height: 1.5;">
            添加班级后，可前往【机构设置-规则设置-机构配置】中设置规则
          </div>
        </el-form-item>

        <!-- 上课信息 -->
        <div style="font-weight: bold; margin: 20px 0 15px 0; color: #303133;">上课信息</div>

        <el-form-item label="授课课时">
          <el-input-number
            v-model="form.lessonHours"
            :min="0"
            :max="999"
            :precision="1"
            :step="0.5"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="上课教室">
          <el-select
            v-model="form.classroomId"
            placeholder="不指定"
            clearable
            style="width: calc(100% - 60px);"
          >
            <el-option
              v-for="room in classroomOptions"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            />
          </el-select>
          <el-link
            type="primary"
            :underline="false"
            style="margin-left: 10px;"
            @click="handleSetClassroom"
          >
            设置
          </el-link>
        </el-form-item>

        <el-form-item label="班级老师">
          <el-input
            v-model="form.teacherNames"
            placeholder="添加老师"
            readonly
            @click="handleSelectTeacher"
            style="cursor: pointer;"
          >
            <template #suffix>
              <el-icon><Plus /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <!-- 一对一表单 -->
      <el-form v-if="dialogType === 'oneToOne'" ref="oneToOneFormRef" :model="oneToOneForm" :rules="oneToOneRules" label-width="120px">
        <!-- 基本信息 -->
        <div style="font-weight: bold; margin-bottom: 15px; color: #303133;">基本信息</div>

        <el-form-item label="关联学员" prop="studentId">
          <el-input
            v-model="oneToOneForm.studentName"
            placeholder="请输入"
            readonly
            style="cursor: pointer;"
            @click="handleSelectStudent"
          >
            <template #suffix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-tooltip content="选择该班级关联的学员" placement="top">
            <el-icon style="margin-left: 5px; cursor: pointer;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="消耗账户">
          <el-select
            v-model="oneToOneForm.consumerId"
            placeholder="请选择消耗账户"
            clearable
            style="width: 100%;"
          >
            <el-option label="账户1" value="1" />
            <el-option label="账户2" value="2" />
          </el-select>
        </el-form-item>

        <el-form-item label="关联一对一课程" prop="courseId">
          <el-select
            v-model="oneToOneForm.courseId"
            placeholder="请选择课程"
            clearable
            style="width: 100%;"
          >
            <el-option
              v-for="course in courseOptions"
              :key="course.id"
              :label="course.courseName"
              :value="course.id"
            />
          </el-select>
          <el-tooltip content="选择该班级关联的一对一课程" placement="top">
            <el-icon style="margin-left: 5px; cursor: pointer;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="班级名称">
          <el-input
            v-model="oneToOneForm.className"
            placeholder="请输入班级名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="班级分类">
          <el-select
            v-model="oneToOneForm.classCategory"
            placeholder="不指定"
            clearable
            style="width: calc(100% - 60px);"
          >
            <el-option label="系统班型" value="system" />
            <el-option label="自建班型" value="custom" />
          </el-select>
          <el-link
            type="primary"
            :underline="false"
            style="margin-left: 10px;"
            @click="handleSetCategory"
          >
            设置
          </el-link>
        </el-form-item>

        <el-form-item label="自动派名">
          <el-switch
            v-model="oneToOneForm.autoAssignName"
            :active-value="1"
            :inactive-value="0"
          />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">关闭</span>
          <div style="margin-top: 5px; color: #909399; font-size: 12px; line-height: 1.5;">
            添加班级后，可前往【机构设置-规则设置-机构配置】中设置规则
          </div>
        </el-form-item>

        <!-- 其他信息 -->
        <div style="font-weight: bold; margin: 20px 0 15px 0; color: #303133;">其他信息</div>

        <el-form-item label="默认消耗金额">
          <el-input-number
            v-model="oneToOneForm.defaultConsumption"
            :min="0"
            :max="99999"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="授课课时">
          <el-input-number
            v-model="oneToOneForm.lessonHours"
            :min="0"
            :max="999"
            :precision="1"
            :step="0.5"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="上课教室">
          <el-select
            v-model="oneToOneForm.classroomId"
            placeholder="不指定"
            clearable
            style="width: calc(100% - 60px);"
          >
            <el-option
              v-for="room in classroomOptions"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            />
          </el-select>
          <el-link
            type="primary"
            :underline="false"
            style="margin-left: 10px;"
            @click="handleSetClassroom"
          >
            设置
          </el-link>
        </el-form-item>

        <el-form-item label="班级老师">
          <el-input
            v-model="oneToOneForm.teacherNames"
            placeholder="添加老师"
            readonly
            @click="handleSelectTeacher"
            style="cursor: pointer;"
          >
            <template #suffix>
              <el-icon><Plus /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="oneToOneForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmit">保 存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择学员对话框 -->
    <el-dialog title="选择学员" v-model="studentDialogVisible" width="700px" append-to-body>
      <el-input
        v-model="studentSearchKeyword"
        placeholder="请输入学员姓名或手机号"
        clearable
        style="margin-bottom: 15px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        ref="studentTableRef"
        :data="filteredStudentList"
        border
        max-height="400"
        @row-click="handleStudentRowClick"
      >
        <el-table-column label="学员姓名" prop="studentName" width="150" />
        <el-table-column label="手机号" prop="phone" width="150" />
        <el-table-column label="家长姓名" prop="parentName" min-width="150" />
      </el-table>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="studentDialogVisible = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择老师对话框 -->
    <el-dialog title="选择老师" v-model="teacherDialogVisible" width="700px" append-to-body>
      <el-input
        v-model="teacherSearchKeyword"
        placeholder="请输入老师姓名"
        clearable
        style="margin-bottom: 15px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        ref="teacherTableRef"
        :data="filteredTeacherList"
        border
        max-height="400"
        @selection-change="handleTeacherSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="老师姓名" prop="teacherName" width="150" />
        <el-table-column label="工号" prop="teacherCode" width="120" />
        <el-table-column label="联系电话" prop="phone" min-width="150" />
      </el-table>

      <div style="margin-top: 15px; color: #909399; font-size: 14px;">
        已选择：<span style="color: #409EFF; font-weight: bold;">{{ selectedTeachers.length }}</span> 位老师
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="teacherDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmTeacherSelection">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantClass">
import { ref, computed, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import { nextTick } from 'vue';

const { proxy } = getCurrentInstance();
const router = useRouter();

// Tab相关
const activeTab = ref('groupClass');

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  className: '',
  classType: '',
  enrollStatus: ''
});

// 列表数据
const classList = ref([]);
const loading = ref(false);
const total = ref(0);
const showOnlyMyClasses = ref(false);

// 对话框相关
const dialogVisible = ref(false);
const dialogTitle = ref('');
const dialogType = ref('groupClass'); // 'groupClass' 或 'oneToOne'
const formRef = ref(null);
const showSearch = ref(true);
const form = ref({
  id: null,
  className: '',
  courseId: null,
  capacityType: 1, // 1-可超额, 0-不可超额
  minStudents: 0,
  allowOnlineEnroll: 0,
  allowRecharge: 1,
  classCategory: '',
  autoAssignName: 0,
  lessonHours: 0,
  classroomId: null,
  teacherIds: [],
  teacherNames: '',
  remark: ''
});

// 表单验证规则
const rules = {
  className: [
    { required: true, message: '请输入班级名称', trigger: 'blur' }
  ],
  courseId: [
    { required: true, message: '请选择关联课程', trigger: 'change' }
  ]
};

// 课程选项
const courseOptions = ref([
  { id: 1, courseName: '早教一对一课程' },
  { id: 2, courseName: '早教半年卡' },
  { id: 3, courseName: '早教年卡' },
  { id: 4, courseName: '钢琴二级课程' },
  { id: 5, courseName: '钢琴一级课程' },
  { id: 6, courseName: '钢琴一对一课程' },
  { id: 7, courseName: '按月托管' },
  { id: 8, courseName: '厨士舞' },
  { id: 9, courseName: '拉丁舞' }
]);

// 教室选项
const classroomOptions = ref([
  { id: 1, name: '教室A' },
  { id: 2, name: '教室B' },
  { id: 3, name: '教室C' },
  { id: 4, name: '多功能厅' },
  { id: 5, name: '舞蹈室' }
]);

// 选择老师对话框
const teacherDialogVisible = ref(false);
const teacherSearchKeyword = ref('');
const teacherTableRef = ref(null);
const selectedTeachers = ref([]);
const teacherList = ref([
  { id: 1, teacherName: '张老师', teacherCode: 'T001', phone: '13800138001' },
  { id: 2, teacherName: '李老师', teacherCode: 'T002', phone: '13800138002' },
  { id: 3, teacherName: '王老师', teacherCode: 'T003', phone: '13800138003' },
  { id: 4, teacherName: '主老师', teacherCode: '04431', phone: '13800138004' },
  { id: 5, teacherName: '劳动老师', teacherCode: 'T005', phone: '13800138005' }
]);

// 过滤后的老师列表
const filteredTeacherList = computed(() => {
  if (!teacherSearchKeyword.value) {
    return teacherList.value;
  }
  return teacherList.value.filter(teacher =>
    teacher.teacherName.includes(teacherSearchKeyword.value) ||
    teacher.teacherCode.includes(teacherSearchKeyword.value)
  );
});

// 一对一Tab相关
const oneToOneQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  courseId: null,
  teacherId: null
});

const oneToOneClassList = ref([]);
const oneToOneLoading = ref(false);
const oneToOneTotal = ref(0);
const showOnlyMyOneToOneClasses = ref(false);
const oneToOneQueryRef = ref(null);

// 一对一表单
const oneToOneForm = ref({
  id: null,
  studentId: null,
  studentName: '',
  consumerId: null,
  consumerName: '',
  courseId: null,
  className: '',
  classCategory: '',
  autoAssignName: 0,
  defaultConsumption: 0,
  lessonHours: 0,
  classroomId: null,
  teacherIds: [],
  teacherNames: '',
  remark: ''
});

// 一对一表单验证规则
const oneToOneRules = {
  studentId: [
    { required: true, message: '请选择关联学员', trigger: 'change' }
  ],
  courseId: [
    { required: true, message: '请选择关联一对一课程', trigger: 'change' }
  ]
};

// 选择学员对话框
const studentDialogVisible = ref(false);
const studentSearchKeyword = ref('');
const studentTableRef = ref(null);
const studentList = ref([
  { id: 1, studentName: '张三', phone: '13800138001', parentName: '张父' },
  { id: 2, studentName: '李四', phone: '13800138002', parentName: '李父' },
  { id: 3, studentName: '王五', phone: '13800138003', parentName: '王父' },
  { id: 4, studentName: '赵六', phone: '13800138004', parentName: '赵父' },
  { id: 5, studentName: '孙七', phone: '13800138005', parentName: '孙父' }
]);

// 过滤后的学员列表
const filteredStudentList = computed(() => {
  if (!studentSearchKeyword.value) {
    return studentList.value;
  }
  return studentList.value.filter(student =>
    student.studentName.includes(studentSearchKeyword.value) ||
    student.phone.includes(studentSearchKeyword.value)
  );
});

/** Tab切换 */
function handleTabClick(tab) {
  if (tab.props.name === 'groupClass') {
    getList();
  } else if (tab.props.name === 'oneToOne') {
    getOneToOneList();
  }
}

/** 查询班级列表 */
function getList() {
  loading.value = true;

  // 模拟数据
  setTimeout(() => {
    const mockData = [
      {
        id: 1,
        className: '书画3班',
        courseName: '美国留学门',
        teacherName: '',
        currentStudents: 0,
        maxStudents: 0,
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      },
      {
        id: 2,
        className: '社德2班',
        courseName: '美国留学门',
        teacherName: '',
        currentStudents: 0,
        maxStudents: 0,
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      },
      {
        id: 3,
        className: '英语3A-春招',
        courseName: '英语',
        teacherName: '',
        currentStudents: 0,
        maxStudents: 0,
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      },
      {
        id: 4,
        className: '美美美术3班',
        courseName: '美国留学门',
        teacherName: '主老师(04431)',
        currentStudents: 3,
        maxStudents: 20,
        completedLessons: 1,
        totalLessons: 5,
        completedHours: 1,
        allowRecharge: 1,
        classType: 'custom',
        isHistorical: 0
      },
      {
        id: 5,
        className: '快乐课堂2期5',
        courseName: '快乐课堂2期门',
        teacherName: '劳动老师',
        currentStudents: 2,
        maxStudents: 2,
        completedLessons: 9,
        totalLessons: 71,
        completedHours: 9,
        allowRecharge: 1,
        classType: 'custom',
        isHistorical: 0
      },
      {
        id: 6,
        className: '数学几题1+0',
        courseName: '副标准题1',
        teacherName: '',
        currentStudents: 0,
        maxStudents: 0,
        completedLessons: 1,
        totalLessons: 2,
        completedHours: 1,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      },
      {
        id: 7,
        className: '数学',
        courseName: '小学一对三',
        teacherName: '',
        currentStudents: 3,
        maxStudents: 0,
        completedLessons: 6,
        totalLessons: 61,
        completedHours: 9,
        allowRecharge: 1,
        classType: 'custom',
        isHistorical: 0
      },
      {
        id: 8,
        className: '英语3J',
        courseName: '英语课程门',
        teacherName: '',
        currentStudents: 1,
        maxStudents: 0,
        completedLessons: 2,
        totalLessons: 15,
        completedHours: 3.5,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      },
      {
        id: 9,
        className: '春节班级课程',
        courseName: '春节班级课程2',
        teacherName: '',
        currentStudents: 0,
        maxStudents: 0,
        completedLessons: 5,
        totalLessons: 5,
        completedHours: 5,
        allowRecharge: 1,
        classType: 'custom',
        isHistorical: 0
      },
      {
        id: 10,
        className: '英语',
        courseName: '英语',
        teacherName: '',
        currentStudents: 2,
        maxStudents: 0,
        completedLessons: 2,
        totalLessons: 3,
        completedHours: 2,
        allowRecharge: 1,
        classType: 'system',
        isHistorical: 0
      }
    ];

    classList.value = mockData;
    total.value = mockData.length;
    loading.value = false;
  }, 500);
}

/** 搜索 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置 */
function resetQuery() {
  proxy.resetForm('queryRef');
  handleQuery();
}

/** 添加班级 */
function handleAdd() {
  dialogTitle.value = '新建班级';
  dialogType.value = 'groupClass';
  dialogVisible.value = true;
  form.value = {
    id: null,
    className: '',
    courseId: null,
    capacityType: 1,
    minStudents: 0,
    allowOnlineEnroll: 0,
    allowRecharge: 1,
    classCategory: '',
    autoAssignName: 0,
    lessonHours: 0,
    classroomId: null,
    teacherIds: [],
    teacherNames: '',
    remark: ''
  };
  selectedTeachers.value = [];
}

/** 导入 */
function handleImport() {
  proxy.$modal.msgInfo('导入功能开发中');
}

/** 导出 */
function handleExport() {
  proxy.$modal.msgInfo('导出功能开发中');
}

/** 查看班级详情 */
function handleViewDetail(row) {
  router.push({
    path: `/assistant/class/detail/${row.id}`,
    query: { type: 'groupClass' }
  });
}

/** 学员管理 */
function handleManage(row) {
  proxy.$modal.msgInfo('学员管理功能开发中');
}

/** 编辑 */
function handleEdit(row) {
  dialogTitle.value = '编辑班级';
  dialogType.value = 'groupClass';
  dialogVisible.value = true;
  form.value = {
    id: row.id,
    className: row.className,
    courseId: row.courseId,
    capacityType: row.capacityType || 1,
    minStudents: row.minStudents || 0,
    allowOnlineEnroll: row.allowOnlineEnroll || 0,
    allowRecharge: row.allowRecharge,
    classCategory: row.classType,
    autoAssignName: row.autoAssignName || 0,
    lessonHours: row.lessonHours || 0,
    classroomId: row.classroomId,
    teacherIds: row.teacherIds || [],
    teacherNames: row.teacherName || '',
    remark: row.remark || ''
  };
}

/** 设置班级分类 */
function handleSetCategory() {
  proxy.$modal.msgInfo('设置班级分类功能开发中');
}

/** 设置教室 */
function handleSetClassroom() {
  proxy.$modal.msgInfo('设置教室功能开发中');
}

/** 选择老师 */
function handleSelectTeacher() {
  teacherDialogVisible.value = true;
  teacherSearchKeyword.value = '';
  selectedTeachers.value = [];

  // 延迟设置已选中的老师
  nextTick(() => {
    if (teacherTableRef.value && form.value.teacherIds && form.value.teacherIds.length > 0) {
      const selectedRows = teacherList.value.filter(teacher =>
        form.value.teacherIds.includes(teacher.id)
      );
      selectedRows.forEach(row => {
        teacherTableRef.value.toggleRowSelection(row, true);
      });
    }
  });
}

/** 老师选择变化 */
function handleTeacherSelectionChange(selection) {
  selectedTeachers.value = selection;
}

/** 确认选择老师 */
function confirmTeacherSelection() {
  if (!selectedTeachers.value || selectedTeachers.value.length === 0) {
    proxy.$modal.msgWarning('请至少选择一位老师');
    return;
  }

  form.value.teacherIds = selectedTeachers.value.map(teacher => teacher.id);
  form.value.teacherNames = selectedTeachers.value.map(teacher => teacher.teacherName).join('、');
  teacherDialogVisible.value = false;
}

/** 选择学员 */
function handleSelectStudent() {
  studentDialogVisible.value = true;
  studentSearchKeyword.value = '';
}

/** 学员行点击 */
function handleStudentRowClick(row) {
  oneToOneForm.value.studentId = row.id;
  oneToOneForm.value.studentName = row.studentName;
  studentDialogVisible.value = false;
}

/** 提交表单 */
function handleSubmit() {
  if (dialogType.value === 'groupClass') {
    formRef.value.validate(valid => {
      if (valid) {
        const action = form.value.id ? '修改' : '新增';
        proxy.$modal.msgSuccess(action + '成功');
        dialogVisible.value = false;
        getList();
      }
    });
  } else if (dialogType.value === 'oneToOne') {
    // 一对一表单提交
    const oneToOneFormRef = proxy.$refs.oneToOneFormRef;
    if (oneToOneFormRef) {
      oneToOneFormRef.validate(valid => {
        if (valid) {
          const action = oneToOneForm.value.id ? '修改' : '新增';
          proxy.$modal.msgSuccess(action + '成功');
          dialogVisible.value = false;
          getOneToOneList();
        }
      });
    }
  }
}

/** 删除 */
function handleDelete(row) {
  proxy.$modal.confirm('确认删除班级"' + row.className + '"吗？').then(() => {
    proxy.$modal.msgSuccess('删除成功');
    getList();
  });
}

/** 允许充值购时切换 */
function handleRechargeChange(row) {
  const status = row.allowRecharge === 1 ? '开启' : '关闭';
  proxy.$modal.msgSuccess('已' + status + '允许充值购时');
}

// 一对一Tab方法
/** 查询一对一班级列表 */
function getOneToOneList() {
  oneToOneLoading.value = true;
  // TODO: 调用实际API
  setTimeout(() => {
    oneToOneClassList.value = [
      {
        id: 1,
        className: '新市场交易',
        courseName: '1对1语文',
        studentName: '市场',
        phone: '13757110422',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 10,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 2,
        className: '1对1语文_天天',
        courseName: '1对1语文',
        studentName: '天天',
        phone: '18004662807',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 10,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 3,
        className: '1对1数学_小华-D',
        courseName: '1对1数学',
        studentName: '钰瑶',
        phone: '13757110431',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 9,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 4,
        className: '1对1语文_小华',
        courseName: '1对1语文',
        studentName: '李华',
        phone: '13757110431',
        teacherName: '待分配',
        completedLessons: 4,
        totalLessons: 6,
        completedHours: 4,
        remainingHours: 9,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 5,
        className: '1对1语文_小华-D',
        courseName: '1对1语文',
        studentName: '李华',
        phone: '13757110431',
        teacherName: '待分配',
        completedLessons: 1,
        totalLessons: 1,
        completedHours: 1,
        remainingHours: 9,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 6,
        className: '小家课堂VIP_小一',
        courseName: '小家课堂VIP',
        studentName: '小一',
        phone: '12356987456',
        teacherName: '待分配',
        completedLessons: 1,
        totalLessons: 440,
        completedHours: 1,
        remainingHours: 0,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 7,
        className: '小家课堂VIP_小小花',
        courseName: '小家课堂VIP',
        studentName: '小小花',
        phone: '16789265789',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 1,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 8,
        className: '小家课堂VIP_小小花',
        courseName: '小家课堂VIP',
        studentName: '小小花',
        phone: '15987456321',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 10,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 9,
        className: '小家课堂VIP_爱小花',
        courseName: '小家课堂VIP',
        studentName: '爱小花',
        phone: '15700002345',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 20,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      },
      {
        id: 10,
        className: '小家课堂VIP_小小花',
        courseName: '小家课堂VIP',
        studentName: '小小花',
        phone: '15987456321',
        teacherName: '待分配',
        completedLessons: 0,
        totalLessons: 0,
        completedHours: 0,
        remainingHours: 10,
        allowRecharge: 1,
        rechargeHours: 0,
        classType: 'system'
      }
    ];
    oneToOneTotal.value = 21;
    oneToOneLoading.value = false;
  }, 500);
}

/** 搜索按钮操作 */
function handleOneToOneQuery() {
  oneToOneQueryParams.value.pageNum = 1;
  getOneToOneList();
}

/** 重置按钮操作 */
function resetOneToOneQuery() {
  oneToOneQueryRef.value?.resetFields();
  handleOneToOneQuery();
}

/** 新增按钮操作 */
function handleOneToOneAdd() {
  dialogTitle.value = '新建班级';
  dialogType.value = 'oneToOne';
  dialogVisible.value = true;
  oneToOneForm.value = {
    id: null,
    studentId: null,
    studentName: '',
    consumerId: null,
    consumerName: '',
    courseId: null,
    className: '',
    classCategory: '',
    autoAssignName: 0,
    defaultConsumption: 0,
    lessonHours: 0,
    classroomId: null,
    teacherIds: [],
    teacherNames: '',
    remark: ''
  };
  selectedTeachers.value = [];
}

/** 查看一对一班级详情 */
function handleOneToOneViewDetail(row) {
  router.push({
    path: `/assistant/class/detail/${row.id}`,
    query: { type: 'oneToOne' }
  });
}

/** 修改按钮操作 */
function handleOneToOneEdit(row) {
  const classId = row.id;
  // TODO: 获取一对一班级详情
  oneToOneForm.value = { ...row };
  dialogTitle.value = '修改班级';
  dialogType.value = 'oneToOne';
  dialogVisible.value = true;
}

/** 删除按钮操作 */
function handleOneToOneDelete(row) {
  proxy.$modal.confirm('是否确认删除班级"' + row.className + '"？').then(() => {
    // TODO: 调用删除API
    proxy.$modal.msgSuccess('删除成功');
    getOneToOneList();
  }).catch(() => {});
}

/** 多选框选中数据 */
function handleOneToOneSelectionChange(selection) {
  // 处理一对一班级的多选
}

/** 允许充值开关变化 */
function handleOneToOneRechargeChange(row) {
  const text = row.allowRecharge === 1 ? '启用' : '停用';
  proxy.$modal.confirm('确认要"' + text + '"该班级的充值功能吗？').then(() => {
    // TODO: 调用API更新充值状态
    proxy.$modal.msgSuccess(text + '成功');
  }).catch(() => {
    row.allowRecharge = row.allowRecharge === 1 ? 0 : 1;
  });
}

// 初始化加载
getList();
</script>

<style scoped lang="scss">
.mb8 {
  margin-bottom: 8px;
}
</style>

