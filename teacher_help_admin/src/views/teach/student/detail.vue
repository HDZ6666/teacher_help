<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>学生详情</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-descriptions title="基本信息" :column="1" border>
            <el-descriptions-item label="学生ID">{{ studentInfo.id }}</el-descriptions-item>
            <el-descriptions-item label="学生姓名">{{ studentInfo.studentName }}</el-descriptions-item>
            <el-descriptions-item label="性别">
              <dict-tag :options="sys_user_sex" :value="studentInfo.gender"/>
            </el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ parseTime(studentInfo.birthday, '{y}-{m}-{d}') }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ calculateAge(studentInfo.birthday) }}岁</el-descriptions-item>
            <el-descriptions-item label="学校名称">{{ studentInfo.schoolName || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="年级">{{ studentInfo.grade || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="班级">{{ studentInfo.className || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="学号">{{ studentInfo.studentIdInSchool || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系人">{{ studentInfo.emergencyContact || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="String(studentInfo.status) === '0' ? 'success' : 'warning'">
                {{ ({ '0': '在读', '1': '休学', '2': '转学', '3': '毕业' })[String(studentInfo.status)] || '未知' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ parseTime(studentInfo.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
        
        <el-col :span="12">
          <el-descriptions title="学习特征" :column="1" border>
            <el-descriptions-item label="学习风格">
              <el-tag v-if="studentInfo.learningStyle === 1" type="success">视觉型</el-tag>
              <el-tag v-else-if="studentInfo.learningStyle === 2" type="warning">听觉型</el-tag>
              <el-tag v-else-if="studentInfo.learningStyle === 3" type="info">动觉型</el-tag>
              <el-tag v-else type="default">未知</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="个性特征">
              <el-tag
                v-for="trait in studentInfo.personalityTraits"
                :key="trait"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ trait }}
              </el-tag>
              <span v-if="!studentInfo.personalityTraits || studentInfo.personalityTraits.length === 0">未填写</span>
            </el-descriptions-item>
            <el-descriptions-item label="兴趣爱好">
              <el-tag
                v-for="hobby in studentInfo.interestsHobbies"
                :key="hobby"
                type="success"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ hobby }}
              </el-tag>
              <span v-if="!studentInfo.interestsHobbies || studentInfo.interestsHobbies.length === 0">未填写</span>
            </el-descriptions-item>
            <el-descriptions-item label="学习困难">
              {{ studentInfo.learningDifficulties || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="医疗备注">
              {{ studentInfo.medicalNotes || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-descriptions title="家长信息" :column="1" border>
            <el-descriptions-item label="家长姓名">{{ studentInfo.parentName }}</el-descriptions-item>
            <el-descriptions-item label="家长手机号">{{ studentInfo.parentPhone }}</el-descriptions-item>
            <el-descriptions-item label="家长昵称">{{ studentInfo.parentNickname }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
        <el-col :span="12">
          <el-descriptions title="备注信息" :column="1" border>
            <el-descriptions-item label="备注">
              {{ studentInfo.remark || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>

    <!-- 课程报名信息 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="clearfix">
          <span>课程报名信息</span>
        </div>
      </template>
      
      <el-table :data="courseList" v-loading="courseLoading">
        <el-table-column label="课程名称" align="center" prop="courseName" />
        <el-table-column label="科目" align="center" prop="subject" />
        <el-table-column label="教师" align="center" prop="teacherName" />
        <el-table-column label="报名状态" align="center" prop="status">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 1" type="success">在读</el-tag>
            <el-tag v-else type="info">已退课</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="报名时间" align="center" prop="enrolledAt" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.enrolledAt, '{y}-{m}-{d}') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
          <template #default="scope">
            <el-tooltip v-if="scope.row.status === 1" content="退课退款功能暂未接入后端" placement="top">
              <span>
                <el-button link type="danger" disabled>退课（未接入）</el-button>
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="StudentDetail">
import { getStudent, getStudentCourses } from "@/api/teach/student";

const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();
const { sys_user_sex } = proxy.useDict('sys_user_sex');

const studentInfo = ref({});
const courseList = ref([]);
const courseLoading = ref(false);

/** 获取学生详情 */
function getStudentDetail() {
  const studentId = route.params.id;
  getStudent(studentId).then(response => {
    studentInfo.value = response.data;
  });
}

/** 获取学生课程信息 */
function getStudentCourseList() {
  courseLoading.value = true;
  const studentId = route.params.id;
  getStudentCourses(studentId).then(response => {
    courseList.value = response.data;
    courseLoading.value = false;
  });
}

/** 计算年龄 */
function calculateAge(birthday) {
  if (!birthday) return 0;
  const today = new Date();
  const birthDate = new Date(birthday);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

/** 返回 */
function goBack() {
  router.go(-1);
}

onMounted(() => {
  getStudentDetail();
  getStudentCourseList();
});
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}
</style>
