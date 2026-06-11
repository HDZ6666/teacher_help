<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>家长详情</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-descriptions title="基本信息" :column="1" border>
            <el-descriptions-item label="家长ID">{{ parentInfo.id }}</el-descriptions-item>
            <el-descriptions-item label="家长姓名">{{ parentInfo.parentName }}</el-descriptions-item>
            <el-descriptions-item label="昵称">{{ parentInfo.nickname }}</el-descriptions-item>
            <el-descriptions-item label="手机号码">{{ parentInfo.phone }}</el-descriptions-item>
            <el-descriptions-item label="微信号">{{ parentInfo.wechatId || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系人">{{ parentInfo.emergencyContact || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="家庭地址">{{ parentInfo.familyAddress || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="parentInfo.status === 1 ? 'success' : 'danger'">
                {{ parentInfo.status === 1 ? '正常' : '停用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ parseTime(parentInfo.createTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</el-descriptions-item>
            <el-descriptions-item label="最后更新">{{ parseTime(parentInfo.updateTime, '{y}-{m}-{d} {h}:{i}:{s}') }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
        
        <el-col :span="12">
          <el-descriptions title="个人信息" :column="1" border>
            <el-descriptions-item label="头像">
              <image-preview v-if="parentInfo.avatarUrl" :src="parentInfo.avatarUrl" :width="100" :height="100"/>
              <span v-else>暂无头像</span>
            </el-descriptions-item>
            <el-descriptions-item label="职业">{{ parentInfo.occupation || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="教育程度">{{ parentInfo.educationLevel || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="家庭收入">
              <el-tag v-if="parentInfo.incomeRange === 1" type="info">5万以下</el-tag>
              <el-tag v-else-if="parentInfo.incomeRange === 2" type="success">5-10万</el-tag>
              <el-tag v-else-if="parentInfo.incomeRange === 3" type="warning">10-20万</el-tag>
              <el-tag v-else-if="parentInfo.incomeRange === 4" type="danger">20万以上</el-tag>
              <el-tag v-else type="default">未知</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="付费偏好">
              <el-tag v-if="parentInfo.paymentPreference === 1" type="success">按课时</el-tag>
              <el-tag v-else-if="parentInfo.paymentPreference === 2" type="warning">包月</el-tag>
              <el-tag v-else-if="parentInfo.paymentPreference === 3" type="info">包季</el-tag>
              <el-tag v-else-if="parentInfo.paymentPreference === 4" type="default">包年</el-tag>
              <el-tag v-else type="default">未知</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
      
      <!-- 备注信息 -->
      <el-row :gutter="20" style="margin-top: 20px;" v-if="parentInfo.remark">
        <el-col :span="24">
          <el-descriptions title="备注信息" :column="1" border>
            <el-descriptions-item label="备注">{{ parentInfo.remark }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>

    <!-- 孩子信息 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="clearfix">
          <span>孩子信息</span>
        </div>
      </template>
      
      <el-table :data="childrenList" v-loading="childrenLoading">
        <el-table-column label="学生姓名" align="center" prop="studentName" />
        <el-table-column label="性别" align="center" prop="gender">
          <template #default="scope">
            <dict-tag :options="sys_user_sex" :value="scope.row.gender"/>
          </template>
        </el-table-column>
        <el-table-column label="年级" align="center" prop="grade" />
        <el-table-column label="学校" align="center" prop="schoolName" />
        <el-table-column label="学习风格" align="center" prop="learningStyle">
          <template #default="scope">
            <el-tag v-if="scope.row.learningStyle === 1" type="success">视觉型</el-tag>
            <el-tag v-else-if="scope.row.learningStyle === 2" type="warning">听觉型</el-tag>
            <el-tag v-else-if="scope.row.learningStyle === 3" type="info">动觉型</el-tag>
            <el-tag v-else type="default">未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" align="center" prop="status">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" align="center" prop="createTime" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
          <template #default="scope">
            <el-tooltip content="查看详情" placement="top">
              <el-button link type="primary" icon="View" @click="handleViewStudent(scope.row)" v-hasPermi="['teach:student:query']"></el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="ParentDetail">
import { getParent, getParentChildren } from "@/api/teach/parent";

const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();
const { sys_user_sex } = proxy.useDict('sys_user_sex');

const parentInfo = ref({});
const childrenList = ref([]);
const childrenLoading = ref(false);

/** 获取家长详情 */
function getParentDetail() {
  const parentId = route.params.id;
  getParent(parentId).then(response => {
    parentInfo.value = response.data;
  });
}

/** 获取家长的孩子信息 */
function getParentChildrenList() {
  childrenLoading.value = true;
  const parentId = route.params.id;
  getParentChildren(parentId).then(response => {
    childrenList.value = response.data;
    childrenLoading.value = false;
  }).catch(() => {
    childrenList.value = [];
    childrenLoading.value = false;
  });
}

/** 查看学生详情 */
function handleViewStudent(row) {
  router.push("/teach/student-detail/index/" + row.id);
}

/** 返回 */
function goBack() {
  router.go(-1);
}

onMounted(() => {
  getParentDetail();
  getParentChildrenList();
});
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}
</style>
