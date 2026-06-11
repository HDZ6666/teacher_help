<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>教师详情</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-descriptions title="基本信息" :column="1" border>
            <el-descriptions-item label="教师ID">{{ teacherInfo.id }}</el-descriptions-item>
            <el-descriptions-item label="教师姓名">{{ teacherInfo.teacherName }}</el-descriptions-item>
            <el-descriptions-item label="昵称">{{ teacherInfo.nickname }}</el-descriptions-item>
            <el-descriptions-item label="手机号码">{{ teacherInfo.phone }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ teacherInfo.idCard || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="资格证书">{{ teacherInfo.qualificationCert || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="工作经验">{{ teacherInfo.workExperience }}年</el-descriptions-item>
            <el-descriptions-item label="课时费">¥{{ teacherInfo.hourlyRate }}/小时</el-descriptions-item>
            <el-descriptions-item label="状态">
              <dict-tag :options="sys_normal_disable" :value="teacherInfo.status"/>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ parseTime(teacherInfo.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</el-descriptions-item>
            <el-descriptions-item label="最后更新">{{ parseTime(teacherInfo.updateTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
        
        <el-col :span="12">
          <el-descriptions title="教学信息" :column="1" border>
            <el-descriptions-item label="头像">
              <image-preview v-if="teacherInfo.avatarUrl" :src="teacherInfo.avatarUrl" :width="100" :height="100"/>
              <span v-else>暂无头像</span>
            </el-descriptions-item>
            <el-descriptions-item label="教学科目">
              <el-tag
                v-for="subject in teacherInfo.teachingSubjects"
                :key="subject"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ subject }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="教学年级">
              <el-tag
                v-for="grade in teacherInfo.teachingGrades"
                :key="grade"
                type="success"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ grade }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="银行账户">{{ teacherInfo.bankAccount || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="开户银行">{{ teacherInfo.bankName || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="结算周期">
              <el-tag v-if="teacherInfo.settlementCycle === 1" type="info">周结</el-tag>
              <el-tag v-else-if="teacherInfo.settlementCycle === 2" type="success">月结</el-tag>
              <el-tag v-else-if="teacherInfo.settlementCycle === 3" type="warning">季结</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>

      <!-- 个人简介 -->
      <el-row :gutter="20" style="margin-top: 20px;" v-if="teacherInfo.introduction">
        <el-col :span="24">
          <el-descriptions title="个人简介" :column="1" border>
            <el-descriptions-item label="简介">{{ teacherInfo.introduction }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>

      <!-- 备注信息 -->
      <el-row :gutter="20" style="margin-top: 20px;" v-if="teacherInfo.remark">
        <el-col :span="24">
          <el-descriptions title="备注信息" :column="1" border>
            <el-descriptions-item label="备注">{{ teacherInfo.remark }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计信息 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="clearfix">
          <span>统计信息</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statsInfo.courseCount || 0 }}</div>
            <div class="stat-label">开设课程</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statsInfo.studentCount || 0 }}</div>
            <div class="stat-label">教授学生</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statsInfo.lessonCount || 0 }}</div>
            <div class="stat-label">总课节数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statsInfo.monthIncome || 0 }}</div>
            <div class="stat-label">本月收入</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 课程信息 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="clearfix">
          <span>开设课程</span>
        </div>
      </template>
      
      <el-table :data="courseList" v-loading="courseLoading">
        <el-table-column label="课程名称" align="center" prop="name" />
        <el-table-column label="科目" align="center" prop="subject" />
        <el-table-column label="课程描述" align="center" prop="description" show-overflow-tooltip />
        <el-table-column label="状态" align="center" prop="status">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 1" type="success">开课中</el-tag>
            <el-tag v-else type="info">已结课</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" align="center" prop="createdAt" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createdAt, '{y}-{m}-{d}') }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 学生信息 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="clearfix">
          <span>教授学生</span>
        </div>
      </template>
      
      <el-table :data="studentList" v-loading="studentLoading">
        <el-table-column label="学生姓名" align="center" prop="studentName" />
        <el-table-column label="性别" align="center" prop="gender">
          <template #default="scope">
            <dict-tag :options="sys_user_sex" :value="scope.row.gender"/>
          </template>
        </el-table-column>
        <el-table-column label="年级" align="center" prop="grade" />
        <el-table-column label="学校" align="center" prop="schoolName" />
        <el-table-column label="家长姓名" align="center" prop="parentName" />
        <el-table-column label="家长手机号" align="center" prop="parentPhone" />
        <el-table-column label="学习风格" align="center" prop="learningStyle">
          <template #default="scope">
            <el-tag v-if="scope.row.learningStyle === 1" type="success">视觉型</el-tag>
            <el-tag v-else-if="scope.row.learningStyle === 2" type="warning">听觉型</el-tag>
            <el-tag v-else-if="scope.row.learningStyle === 3" type="info">动觉型</el-tag>
            <el-tag v-else type="default">未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" align="center" prop="createTime" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="TeacherDetail">
import { getTeacher, getTeacherCourses, getTeacherStudents, getTeacherStats } from "@/api/teach/teacher";

const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();
const { sys_normal_disable, sys_user_sex } = proxy.useDict('sys_normal_disable', 'sys_user_sex');

const teacherInfo = ref({});
const courseList = ref([]);
const studentList = ref([]);
const statsInfo = ref({});
const courseLoading = ref(false);
const studentLoading = ref(false);

/** 获取教师详情 */
function getTeacherDetail() {
  const teacherId = route.params.id;
  getTeacher(teacherId).then(response => {
    teacherInfo.value = response.data;
  });
}

/** 获取教师课程信息 */
function getTeacherCourseList() {
  courseLoading.value = true;
  const teacherId = route.params.id;
  getTeacherCourses(teacherId).then(response => {
    courseList.value = response.data;
    courseLoading.value = false;
  });
}

/** 获取教师学生信息 */
function getTeacherStudentList() {
  studentLoading.value = true;
  const teacherId = route.params.id;
  getTeacherStudents(teacherId).then(response => {
    studentList.value = response.data;
    studentLoading.value = false;
  });
}

/** 获取教师统计信息 */
function getTeacherStatsInfo() {
  const teacherId = route.params.id;
  getTeacherStats(teacherId).then(response => {
    statsInfo.value = response.data;
  });
}

/** 返回 */
function goBack() {
  router.go(-1);
}

onMounted(() => {
  getTeacherDetail();
  getTeacherCourseList();
  getTeacherStudentList();
  getTeacherStatsInfo();
});
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}
</style>
