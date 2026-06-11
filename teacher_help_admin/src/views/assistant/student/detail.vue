<template>
  <div class="app-container student-detail">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" content="学员详情" style="margin-bottom: 20px" />

    <!-- 学员基本信息卡片 -->
    <el-card class="student-info-card">
      <el-row :gutter="20">
        <!-- 左侧头像 -->
        <el-col :span="2">
          <el-avatar :size="80" :src="studentInfo.avatar" style="background-color: #f0f0f0">
            <span style="font-size: 32px; color: #999">{{ studentInfo.studentName?.charAt(0) || 'M' }}</span>
          </el-avatar>
        </el-col>

        <!-- 中间信息 -->
        <el-col :span="18">
          <div class="student-header">
            <h2 style="margin: 0 10px 10px 0; display: inline-block">{{ studentInfo.studentName }}</h2>
            <el-tag type="success" size="large">在读学员</el-tag>
          </div>

          <el-row :gutter="40" class="info-row">
            <el-col :span="8">
              <div class="info-item">
                <span class="label">出生日期:</span>
                <span class="value">{{ studentInfo.birthday || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">领证学校:</span>
                <span class="value">{{ studentInfo.school || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">当前年级:</span>
                <span class="value">{{ studentInfo.grade || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学号:</span>
                <span class="value">{{ studentInfo.studentNo || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">国外手机号:</span>
                <span class="value">{{ studentInfo.foreignPhone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">体重:</span>
                <span class="value">{{ studentInfo.weight || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">身份证号:</span>
                <span class="value">{{ studentInfo.idCard || '-' }}</span>
              </div>
            </el-col>

            <el-col :span="8">
              <div class="info-item">
                <span class="label">妈妈手机:</span>
                <span class="value">{{ studentInfo.phone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">各项手机:</span>
                <span class="value">{{ studentInfo.mainContactPhone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">实质住址:</span>
                <span class="value">{{ studentInfo.address || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">卡号:</span>
                <span class="value">{{ studentInfo.cardNo || '-' }}</span>
              </div>
            </el-col>

            <el-col :span="8">
              <div class="info-item">
                <span class="label">学员水源:</span>
                <span class="value">{{ studentInfo.source || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">跟进人:</span>
                <span class="value">{{ studentInfo.follower || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学管师:</span>
                <span class="value">{{ studentInfo.advisor || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学员创建人:</span>
                <span class="value">{{ studentInfo.creator || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ studentInfo.createTime || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">标签:</span>
                <span class="value">
                  <el-tag v-for="tag in studentInfo.tags" :key="tag" size="small" style="margin-right: 5px">
                    {{ tag }}
                  </el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="label">备注:</span>
                <span class="value">{{ studentInfo.remark || '-' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-col>

        <!-- 右侧操作按钮 -->
        <el-col :span="4" style="text-align: right">
          <el-button type="warning" plain @click="handleEnroll">报名</el-button>
          <el-button type="success" plain style="margin-top: 10px">办卡</el-button>
          <el-button type="primary" plain style="margin-top: 10px">试听</el-button>
          <el-button plain style="margin-top: 10px" @click="handleEdit">编辑资料</el-button>
          <el-dropdown style="margin-top: 10px; width: 100%">
            <el-button style="width: 100%">
              更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>查看档案</el-dropdown-item>
                <el-dropdown-item>打印资料</el-dropdown-item>
                <el-dropdown-item>删除学员</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-col>
      </el-row>
    </el-card>

    <!-- Tab页签 -->
    <el-card style="margin-top: 20px">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="报读课程" name="courses">
          <div class="course-stats">
            <span>剩余调课数(周中): {{ courseStats.remainingWeekday }}</span>
            <span style="margin-left: 30px">超上调课数(周中): {{ courseStats.overWeekday }}</span>
            <el-button type="primary" size="small" style="margin-left: 20px">选班购课</el-button>
          </div>

          <el-table :data="courseList" border style="margin-top: 20px">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="小学数学9999" width="150">
              <template #default>
                <div style="color: #f56c6c">📕 小学数学9999</div>
              </template>
            </el-table-column>
            <el-table-column label="剩余调课" prop="remainingTransfer" width="100" />
            <el-table-column label="购买课时" prop="purchaseCount" width="100" />
            <el-table-column label="消费记录" width="350">
              <template #default="scope">
                <div>消课时期间时: {{ scope.row.consumePeriod }}</div>
                <div>所在班级: {{ scope.row.className }} <el-link type="primary">未选班</el-link></div>
              </template>
            </el-table-column>
            <el-table-column label="订单号" prop="orderNo" width="180" />
            <el-table-column label="购买教费" prop="purchaseAmount" width="100" />
            <el-table-column label="赠送教费" prop="giftAmount" width="100" />
            <el-table-column label="订购转教费" prop="transferAmount" width="120" />
            <el-table-column label="退转教费" prop="refundAmount" width="100" />
            <el-table-column label="剩余教费" prop="remainingAmount" width="100" />
            <el-table-column label="课程右效期" prop="expireDate" width="120" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default>
                <el-button type="primary" link>续费</el-button>
                <el-button type="primary" link>转课</el-button>
                <el-button type="primary" link>退课</el-button>
                <el-button type="primary" link>结课</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="充值账户" name="recharge">
          <div>充值账户功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="持有卡项" name="cards">
          <div>持有卡项功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="跟进管理" name="follow">
          <div>跟进管理功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="消费记录" name="consume">
          <div>消费记录功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="上课记录" name="attendance">
          <div>上课记录功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="考勤记录" name="checkin">
          <div>考勤记录功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="成长档案" name="growth">
          <div>成长档案功能开发中...</div>
        </el-tab-pane>

        <el-tab-pane label="学习报告" name="report">
          <div>学习报告功能开发中...</div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 报名对话框 -->
    <el-dialog
      v-model="enrollDialogVisible"
      title="报名/续费"
      width="1000px"
      :close-on-click-modal="false"
    >
      <div class="enroll-content">
        <!-- 空状态提示 -->
        <div v-if="enrollForm.courses.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <div class="empty-text">暂无有效项目</div>
        </div>

        <!-- 已选课程列表 -->
        <div v-else class="enroll-form">
          <!-- 顶部信息 -->
          <div class="enroll-header">
            <div class="student-info-brief">
              <el-tag>在读</el-tag>
              <span class="student-name">{{ studentInfo.studentName }}</span>
              <span class="student-phone">{{ studentInfo.phone }}</span>
            </div>
            <div class="stats-info">
              <span>报名课程数: {{ enrollForm.courses.length }}</span>
              <span style="margin-left: 20px;">问题单数: 0</span>
              <span style="margin-left: 20px;">问题金额: 0</span>
            </div>
          </div>

          <!-- 操作按钮组 -->
          <div class="action-buttons">
            <el-button type="warning" size="small" @click="handleSelectCourse">选择课程</el-button>
            <el-button type="warning" size="small" plain>选择协议</el-button>
            <el-button type="warning" size="small" plain>选择套餐</el-button>
            <el-button type="warning" size="small" plain>选择卡项</el-button>
          </div>

          <!-- 课程列表表格 -->
          <el-table :data="enrollForm.courses" border style="margin-top: 15px;">
            <el-table-column label="购买项目" width="150">
              <template #default="scope">
                <div style="display: flex; align-items: center;">
                  <el-tag size="small" style="margin-right: 5px;">课程</el-tag>
                  <span>{{ scope.row.courseName }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="定价标准" width="200">
              <template #default="scope">
                <el-select v-model="scope.row.priceStandard" size="small" style="width: 100%;">
                  <el-option
                    v-for="price in scope.row.priceOptions"
                    :key="price.value"
                    :label="price.label"
                    :value="price.value"
                  />
                </el-select>
              </template>
            </el-table-column>

            <el-table-column label="购买数量" width="100">
              <template #default="scope">
                <el-input-number
                  v-model="scope.row.quantity"
                  :min="1"
                  size="small"
                  controls-position="right"
                  style="width: 100%;"
                />
              </template>
            </el-table-column>

            <el-table-column label="总价" width="100">
              <template #default="scope">
                <span style="color: #E6A23C; font-weight: 500;">¥ {{ scope.row.totalPrice }}</span>
              </template>
            </el-table-column>

            <el-table-column label="总价" width="80">
              <template #default="scope">
                <span>{{ scope.row.quantity }}</span>
              </template>
            </el-table-column>

            <el-table-column label="赠送数量" width="120">
              <template #default="scope">
                <el-input-number
                  v-model="scope.row.giftQuantity"
                  :min="0"
                  size="small"
                  controls-position="right"
                  style="width: 100%;"
                />
              </template>
            </el-table-column>

            <el-table-column label="课程有效期" width="150">
              <template #default="scope">
                <el-select v-model="scope.row.validityType" size="small" style="width: 100%;">
                  <el-option label="课时" value="lesson" />
                  <el-option label="不限期" value="unlimited" />
                </el-select>
              </template>
            </el-table-column>

            <el-table-column label="小计" width="100">
              <template #default="scope">
                <span style="color: #E6A23C; font-weight: 500;">¥ {{ scope.row.subtotal }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="80" fixed="right">
              <template #default="scope">
                <el-button type="danger" link @click="removeCourse(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 底部汇总 -->
          <div class="enroll-summary">
            <div class="summary-left">
              <el-checkbox v-model="enrollForm.agreeTerms">
                我已阅读并同意
              </el-checkbox>
              <el-link type="warning" :underline="false" style="margin-left: 5px;">
                《培训协议》
              </el-link>
            </div>
            <div class="summary-right">
              <span class="summary-label">应收金额:</span>
              <span class="summary-amount">¥ {{ calculateTotalAmount() }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="enrollDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmEnroll">确认提交</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择课程弹窗 -->
    <el-dialog
      v-model="selectCourseDialogVisible"
      title="选择课程"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
    >
      <!-- 搜索框 -->
      <el-input
        v-model="courseSearchKeyword"
        placeholder="请输入课程名称"
        clearable
        style="margin-bottom: 15px;"
      >
        <template #suffix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 课程列表表格 -->
      <el-table
        :data="filteredCourseList"
        border
        @selection-change="handleCourseSelectionChange"
        max-height="400px"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="课程名称" prop="courseName" width="150" />
        <el-table-column label="课程类型" prop="courseType" width="120" />
        <el-table-column label="定价标准" prop="priceStandard" min-width="200" />
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <span class="total-text">共{{ availableCourseList.length }}条数据</span>
        <el-pagination
          v-model:current-page="coursePagination.currentPage"
          v-model:page-size="coursePagination.pageSize"
          :total="availableCourseList.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, jumper"
          @current-change="handleCoursePageChange"
        />
      </div>

      <!-- 底部已选提示 -->
      <div class="selection-footer">
        <span>已选择: {{ selectedCourses.length }}项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectCourseDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmSelectCourse">选好了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="StudentDetail">
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { ArrowDown, Search } from '@element-plus/icons-vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();

const activeTab = ref('courses');
const studentInfo = ref({});
const courseStats = ref({
  remainingWeekday: 79,
  overWeekday: 0
});
const courseList = ref([]);

// 报名相关
const enrollDialogVisible = ref(false);
const enrollForm = ref({
  courses: [],
  agreeTerms: false
});

// 选择课程相关
const selectCourseDialogVisible = ref(false);
const courseSearchKeyword = ref('');
const selectedCourses = ref([]);
const coursePagination = ref({
  currentPage: 1,
  pageSize: 10
});

// 可选课程列表(模拟数据)
const availableCourseList = ref([
  { id: 1, courseName: '托管卡', courseType: '一对多', priceStandard: '单价(900元/月)等2项' },
  { id: 2, courseName: '启蒙英语', courseType: '一对多', priceStandard: '单价(200元/课时)等3项' },
  { id: 3, courseName: '初级卡', courseType: '一对多', priceStandard: '单价(1200元/月)' },
  { id: 4, courseName: '篮球课?9', courseType: '一对多', priceStandard: '单价(120元/课时)等3项' },
  { id: 5, courseName: '篮球课', courseType: '一对多', priceStandard: '单价(120元/课时)等2项' },
  { id: 6, courseName: '暑期499活动课', courseType: '一对多', priceStandard: '单价(200元/课时)等3项' },
  { id: 7, courseName: '书法课', courseType: '一对多', priceStandard: '单价(68.8元/课时)等2项' },
  { id: 8, courseName: '架子鼓', courseType: '一对多', priceStandard: '单价(100元/课时)等2项' },
  { id: 9, courseName: '美术探索', courseType: '一对多', priceStandard: '单价(110元/课时)等5项' },
  { id: 10, courseName: '街舞', courseType: '一对多', priceStandard: '单价(79元/课时)等3项' },
  { id: 11, courseName: '爵士舞', courseType: '一对多', priceStandard: '单价(85元/课时)等4项' },
  { id: 12, courseName: '拉丁舞', courseType: '一对多', priceStandard: '单价(90元/课时)等3项' },
  { id: 13, courseName: '中国舞', courseType: '一对多', priceStandard: '单价(88元/课时)等2项' },
  { id: 14, courseName: '芭蕾舞', courseType: '一对多', priceStandard: '单价(95元/课时)等3项' },
  { id: 15, courseName: '钢琴课', courseType: '一对多', priceStandard: '单价(150元/课时)等4项' },
  { id: 16, courseName: '吉他课', courseType: '一对多', priceStandard: '单价(120元/课时)等3项' },
  { id: 17, courseName: '小提琴', courseType: '一对多', priceStandard: '单价(130元/课时)等2项' }
]);

// 过滤后的课程列表(用于分页显示)
const filteredCourseList = computed(() => {
  let list = availableCourseList.value;

  // 搜索过滤
  if (courseSearchKeyword.value) {
    list = list.filter(course =>
      course.courseName.toLowerCase().includes(courseSearchKeyword.value.toLowerCase())
    );
  }

  // 分页
  const start = (coursePagination.value.currentPage - 1) * coursePagination.value.pageSize;
  const end = start + coursePagination.value.pageSize;
  return list.slice(start, end);
});

/** 获取学员详情 */
function getStudentDetail() {
  const studentId = route.params.id;
  
  // 模拟数据
  setTimeout(() => {
    studentInfo.value = {
      id: studentId,
      studentName: "黄同学",
      avatar: null,
      birthday: "2014-10-15",
      phone: "111****1111",
      school: "某进小学",
      grade: "三年级",
      studentNo: "200410",
      foreignPhone: "",
      weight: "",
      idCard: "",
      mainContactPhone: "各项手机",
      address: "实质住址",
      cardNo: "点击绑定",
      source: "线上推广",
      follower: "H泉",
      advisor: "迅优文化（黄老师体验）",
      creator: "H泉",
      createTime: "2025-11-03 10:31",
      tags: [],
      remark: ""
    };

    courseList.value = [
      {
        id: 1,
        courseName: "小学数学9999",
        remainingTransfer: "31课时",
        purchaseCount: "0课时",
        consumePeriod: "将在下方中的中间设置",
        className: "未选班",
        orderNo: "20251102315490600002",
        purchaseAmount: "1课时",
        giftAmount: "0课时",
        transferAmount: "0课时",
        refundAmount: "0课时",
        remainingAmount: "1课时",
        expireDate: "王没有右效期"
      }
    ];
  }, 300);
}

/** 返回 */
function goBack() {
  router.back();
}

/** 编辑资料 */
function handleEdit() {
  router.push(`/assistant/student/edit/${studentInfo.value.id}`);
}

/** Tab切换 */
function handleTabChange(tab) {
  console.log('切换到Tab:', tab);
}

/** 打开报名对话框 */
function handleEnroll() {
  // 跳转到报名页面
  router.push(`/assistant/student/enroll/${studentInfo.value.id}`);
}

/** 打开选择课程弹窗 */
function handleSelectCourse() {
  selectCourseDialogVisible.value = true;
  selectedCourses.value = [];
  courseSearchKeyword.value = '';
  coursePagination.value.currentPage = 1;
}

/** 课程选择变化 */
function handleCourseSelectionChange(selection) {
  selectedCourses.value = selection;
}

/** 课程分页变化 */
function handleCoursePageChange(page) {
  coursePagination.value.currentPage = page;
}

/** 确认选择课程 */
function handleConfirmSelectCourse() {
  if (selectedCourses.value.length === 0) {
    ElMessage.warning('请至少选择一个课程');
    return;
  }

  // 将选中的课程添加到报名表单中
  selectedCourses.value.forEach(course => {
    // 检查是否已存在
    const exists = enrollForm.value.courses.find(c => c.courseId === course.id);
    if (!exists) {
      enrollForm.value.courses.push({
        courseId: course.id,
        courseName: course.courseName,
        courseType: course.courseType,
        priceStandard: '单价(200元/课时)等3项',
        priceOptions: [
          { label: '单价(200元/课时)等3项', value: 'option1' },
          { label: '单价(180元/课时)等2项', value: 'option2' }
        ],
        quantity: 1,
        totalPrice: 200.00,
        giftQuantity: 0,
        validityType: 'lesson',
        subtotal: 200.00
      });
    }
  });

  selectCourseDialogVisible.value = false;
  ElMessage.success(`已添加 ${selectedCourses.value.length} 个课程`);
}

/** 移除课程 */
function removeCourse(index) {
  enrollForm.value.courses.splice(index, 1);
}

/** 计算总金额 */
function calculateTotalAmount() {
  return enrollForm.value.courses.reduce((total, course) => {
    return total + (course.subtotal || 0);
  }, 0).toFixed(2);
}

/** 确认报名 */
function handleConfirmEnroll() {
  if (enrollForm.value.courses.length === 0) {
    ElMessage.warning('请至少选择一个课程');
    return;
  }

  if (!enrollForm.value.agreeTerms) {
    ElMessage.warning('请阅读并同意培训协议');
    return;
  }

  // 这里应该调用API提交报名信息
  console.log('提交报名:', enrollForm.value);
  ElMessage.success('报名成功');
  enrollDialogVisible.value = false;

  // 刷新课程列表
  getStudentDetail();
}

onMounted(() => {
  getStudentDetail();
});
</script>

<style scoped lang="scss">
.student-detail {
  .student-info-card {
    .student-header {
      margin-bottom: 15px;
    }

    .info-row {
      .info-item {
        margin-bottom: 12px;
        font-size: 14px;

        .label {
          color: #909399;
          margin-right: 8px;
        }

        .value {
          color: #303133;
        }
      }
    }
  }

  .course-stats {
    padding: 10px 0;
    font-size: 14px;
  }

  // 报名对话框样式
  .enroll-content {
    min-height: 300px;

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 0;

      .empty-icon {
        font-size: 64px;
        margin-bottom: 16px;
      }

      .empty-text {
        font-size: 16px;
        color: #909399;
      }
    }

    .enroll-form {
      .enroll-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: #F5F7FA;
        border-radius: 4px;
        margin-bottom: 15px;

        .student-info-brief {
          display: flex;
          align-items: center;
          gap: 10px;

          .student-name {
            font-weight: 500;
            color: #303133;
          }

          .student-phone {
            color: #909399;
          }
        }

        .stats-info {
          font-size: 14px;
          color: #606266;
        }
      }

      .action-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
      }

      .enroll-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        background: #FFF7E6;
        border-radius: 4px;
        margin-top: 15px;

        .summary-left {
          display: flex;
          align-items: center;
        }

        .summary-right {
          display: flex;
          align-items: center;
          gap: 10px;

          .summary-label {
            font-size: 14px;
            color: #606266;
          }

          .summary-amount {
            font-size: 20px;
            font-weight: 600;
            color: #E6A23C;
          }
        }
      }
    }
  }

  // 选择课程弹窗样式
  .pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;

    .total-text {
      font-size: 14px;
      color: #606266;
    }
  }

  .selection-footer {
    margin-top: 15px;
    padding: 12px 16px;
    background: #F5F7FA;
    border-radius: 4px;
    font-size: 14px;
    color: #606266;
  }
}
</style>

