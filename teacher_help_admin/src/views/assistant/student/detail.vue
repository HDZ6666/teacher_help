<template>
  <div class="app-container student-detail">
    <el-page-header @back="goBack" content="学员详情" style="margin-bottom: 20px" />

    <el-card class="student-info-card" v-loading="loading">
      <el-row :gutter="20">
        <el-col :span="2">
          <el-avatar :size="80" :src="studentInfo.avatar" style="background-color: #f0f0f0">
            <span style="font-size: 32px; color: #999">{{ studentInfo.studentName?.charAt(0) || '-' }}</span>
          </el-avatar>
        </el-col>

        <el-col :span="18">
          <div class="student-header">
            <h2>{{ studentInfo.studentName || '-' }}</h2>
            <el-tag type="success" size="large">{{ getStudentStatusName(studentInfo.status) }}</el-tag>
          </div>

          <el-row :gutter="40" class="info-row">
            <el-col :span="8">
              <div class="info-item">
                <span class="label">出生日期:</span>
                <span class="value">{{ studentInfo.birthday || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">就读学校:</span>
                <span class="value">{{ studentInfo.schoolName || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">当前年级:</span>
                <span class="value">{{ studentInfo.grade || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">班级:</span>
                <span class="value">{{ studentInfo.className || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学号:</span>
                <span class="value">{{ studentInfo.studentIdInSchool || '-' }}</span>
              </div>
            </el-col>

            <el-col :span="8">
              <div class="info-item">
                <span class="label">家长姓名:</span>
                <span class="value">{{ studentInfo.parentName || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">家长手机:</span>
                <span class="value">{{ studentInfo.parentPhone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">紧急联系人:</span>
                <span class="value">{{ studentInfo.emergencyContact || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学习风格:</span>
                <span class="value">{{ studentInfo.learningStyleName || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学习困难点:</span>
                <span class="value">{{ studentInfo.learningDifficulties || '-' }}</span>
              </div>
            </el-col>

            <el-col :span="8">
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ studentInfo.createTime || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ studentInfo.updateTime || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">性格特点:</span>
                <span class="value">
                  <el-tag
                    v-for="tag in studentInfo.personalityTraits || []"
                    :key="tag"
                    size="small"
                    style="margin-right: 5px"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="!studentInfo.personalityTraits?.length">-</span>
                </span>
              </div>
              <div class="info-item">
                <span class="label">兴趣爱好:</span>
                <span class="value">
                  <el-tag
                    v-for="tag in studentInfo.interestsHobbies || []"
                    :key="tag"
                    size="small"
                    style="margin-right: 5px"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="!studentInfo.interestsHobbies?.length">-</span>
                </span>
              </div>
              <div class="info-item">
                <span class="label">备注:</span>
                <span class="value">{{ studentInfo.remark || '-' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="4" class="action-col">
          <el-button type="warning" plain @click="handleEnroll">报名</el-button>
          <el-button type="success" plain disabled>办卡</el-button>
          <el-button type="primary" plain disabled>试听</el-button>
          <el-button plain @click="handleEdit">编辑资料</el-button>
          <el-dropdown style="width: 100%">
            <el-button style="width: 100%">
              更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>查看档案</el-dropdown-item>
                <el-dropdown-item disabled>打印资料</el-dropdown-item>
                <el-dropdown-item disabled>删除学员</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="报读课程" name="courses">
          <div class="course-stats">
            <span>报读课程数: {{ courseList.length }}</span>
            <span style="margin-left: 30px">剩余课时/期数: {{ remainingQuantityTotal }}</span>
            <el-button type="primary" size="small" style="margin-left: 20px" @click="handleEnroll">选班购课</el-button>
          </div>

          <el-table v-loading="courseLoading" :data="courseList" border style="margin-top: 20px">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="课程名称" prop="courseName" min-width="160">
              <template #default="scope">
                <el-link type="primary" :underline="false">{{ scope.row.courseName }}</el-link>
              </template>
            </el-table-column>
            <el-table-column label="收费方式" width="110">
              <template #default="scope">{{ getChargeTypeName(scope.row.chargeType) }}</template>
            </el-table-column>
            <el-table-column label="购买数量" width="110">
              <template #default="scope">{{ scope.row.purchasedQuantity }}{{ scope.row.unit || '' }}</template>
            </el-table-column>
            <el-table-column label="赠送数量" width="110">
              <template #default="scope">{{ scope.row.giftQuantity }}{{ scope.row.unit || '' }}</template>
            </el-table-column>
            <el-table-column label="已消耗" width="100">
              <template #default="scope">{{ scope.row.consumedQuantity }}{{ scope.row.unit || '' }}</template>
            </el-table-column>
            <el-table-column label="剩余" width="100">
              <template #default="scope">{{ scope.row.remainingQuantity }}{{ scope.row.unit || '' }}</template>
            </el-table-column>
            <el-table-column label="请假免扣" width="100">
              <template #default="scope">{{ scope.row.leaveExemptCount || 0 }}次</template>
            </el-table-column>
            <el-table-column label="所在班级" prop="className" min-width="130">
              <template #default="scope">{{ scope.row.className || '未选班' }}</template>
            </el-table-column>
            <el-table-column label="订单号" prop="orderNo" min-width="180" show-overflow-tooltip />
            <el-table-column label="课程有效期" min-width="190">
              <template #default="scope">
                {{ formatDateRange(scope.row.validStartDate, scope.row.validEndDate) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="scope">
                <el-tag size="small" :type="accountStatusType(scope.row.status)">{{ scope.row.statusName || '有效' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="handleRenew(scope.row)">续费</el-button>
                <template v-if="scope.row.status === 'active'">
                  <el-button type="primary" link @click="openAccountOp('transfer', scope.row)" v-hasPermi="['teach:student:account']">转课</el-button>
                  <el-button type="primary" link @click="openAccountOp('stop', scope.row)" v-hasPermi="['teach:student:account']">停课</el-button>
                </template>
                <el-button v-if="scope.row.status === 'stopped'" type="primary" link @click="openAccountOp('resume', scope.row)" v-hasPermi="['teach:student:account']">复课</el-button>
                <el-button v-if="['active', 'stopped'].includes(scope.row.status)" type="danger" link @click="openAccountOp('complete', scope.row)" v-hasPermi="['teach:student:account']">结课</el-button>
                <el-button type="primary" link disabled title="退课退款需财务规则确认后接入">退课</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-collapse class="account-log" @change="handleLogCollapse">
            <el-collapse-item title="课程变更记录（转课/清零/有效期/停课/复课/结课/导入）" name="logs">
              <el-table v-loading="logLoading" :data="accountLogs" border size="small">
                <el-table-column label="时间" prop="createTime" width="160" />
                <el-table-column label="操作" prop="opTypeName" width="90" />
                <el-table-column label="课程" prop="courseName" min-width="130" show-overflow-tooltip />
                <el-table-column label="数量变化" width="120">
                  <template #default="scope">{{ scope.row.beforeRemaining ?? '-' }} → {{ scope.row.afterRemaining ?? '-' }}</template>
                </el-table-column>
                <el-table-column label="状态" width="120">
                  <template #default="scope">{{ scope.row.beforeStatusName || '-' }} → {{ scope.row.afterStatusName || '-' }}</template>
                </el-table-column>
                <el-table-column label="有效期至" width="190">
                  <template #default="scope">{{ scope.row.beforeValidEnd || '-' }} → {{ scope.row.afterValidEnd || '-' }}</template>
                </el-table-column>
                <el-table-column label="原因/备注" prop="reason" min-width="160" show-overflow-tooltip />
                <el-table-column label="操作人" prop="createBy" width="90" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </el-tab-pane>

        <el-tab-pane label="充值账户" name="recharge">
          <el-empty description="系统暂未提供储值/充值账户（无充值数据表），报名缴费请在“消费记录”查看" />
        </el-tab-pane>

        <el-tab-pane label="持有卡项" name="cards">
          <el-table v-loading="tabLoading.cards" :data="cardList" border>
            <el-table-column label="卡名称" prop="cardName" min-width="140" />
            <el-table-column label="卡类型" prop="cardTypeName" width="110" />
            <el-table-column label="发放/剩余次数" width="130">
              <template #default="scope">{{ scope.row.grantCount ?? '-' }} / {{ scope.row.remainingCount ?? '-' }}</template>
            </el-table-column>
            <el-table-column label="有效期" min-width="190">
              <template #default="scope">{{ formatDateRange(scope.row.validStartDate, scope.row.validEndDate) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="scope">{{ GRANT_STATUS[scope.row.grantStatus] || '-' }}</template>
            </el-table-column>
            <el-table-column label="发放时间" prop="grantTime" width="170" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="跟进管理" name="follow" lazy>
          <follow-panel :student-id="studentId" />
        </el-tab-pane>

        <el-tab-pane label="消费记录" name="consume">
          <div class="consume-toolbar">
            <el-radio-group v-model="consumeView" size="small">
              <el-radio-button label="orders">订单记录</el-radio-button>
              <el-radio-button label="items">订单明细</el-radio-button>
            </el-radio-group>
            <div class="consume-summary">
              <span>订单总金额(元) {{ formatMoney(orderSummary.totalAmount) }}</span>
              <span>实收金额(元) {{ formatMoney(orderSummary.paidAmount) }}</span>
              <span>欠费金额(元) {{ formatMoney(orderSummary.debtAmount) }}</span>
            </div>
          </div>

          <el-table
            v-if="consumeView === 'orders'"
            v-loading="orderLoading"
            :data="orderList"
            border
            style="margin-top: 15px"
          >
            <el-table-column type="expand">
              <template #default="props">
                <el-table :data="props.row.items || []" border class="order-item-table">
                  <el-table-column label="项目类型" prop="itemTypeName" width="100" />
                  <el-table-column label="购买项目" min-width="180">
                    <template #default="scope">
                      {{ scope.row.itemName }}
                      <span v-if="scope.row.specName" class="muted-text">({{ scope.row.specName }})</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="数量" width="100">
                    <template #default="scope">{{ scope.row.quantity }}{{ scope.row.unit || '' }}</template>
                  </el-table-column>
                  <el-table-column label="单价" width="110" align="right">
                    <template #default="scope">¥ {{ formatMoney(scope.row.unitPrice) }}</template>
                  </el-table-column>
                  <el-table-column label="小计" width="120" align="right">
                    <template #default="scope">¥ {{ formatMoney(scope.row.subtotalPrice) }}</template>
                  </el-table-column>
                </el-table>
              </template>
            </el-table-column>
            <el-table-column label="订单号" prop="orderNo" min-width="190" show-overflow-tooltip />
            <el-table-column label="订单类型" prop="orderTypeName" width="100" />
            <el-table-column label="购买项目" prop="itemSummary" min-width="260" show-overflow-tooltip />
            <el-table-column label="应收(元)" width="120" align="right">
              <template #default="scope">¥ {{ formatMoney(scope.row.receivableAmount) }}</template>
            </el-table-column>
            <el-table-column label="实收(元)" width="120" align="right">
              <template #default="scope">¥ {{ formatMoney(scope.row.paidAmount) }}</template>
            </el-table-column>
            <el-table-column label="订单来源" prop="orderSource" width="120" />
            <el-table-column label="业绩归属" prop="performanceOwner" width="120">
              <template #default="scope">{{ scope.row.performanceOwner || '-' }}</template>
            </el-table-column>
            <el-table-column label="订单状态" width="100">
              <template #default="scope">
                <el-tag size="small" type="success">{{ scope.row.statusName || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="createTime" min-width="170" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="receiptRef.open(scope.row.id)">查看收据</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-table
            v-else
            v-loading="orderLoading"
            :data="orderItemList"
            border
            style="margin-top: 15px"
          >
            <el-table-column label="订单号" prop="orderNo" min-width="190" show-overflow-tooltip />
            <el-table-column label="项目类型" prop="itemTypeName" width="100" />
            <el-table-column label="购买项目" min-width="220">
              <template #default="scope">
                {{ scope.row.itemName }}
                <span v-if="scope.row.specName" class="muted-text">({{ scope.row.specName }})</span>
              </template>
            </el-table-column>
            <el-table-column label="套餐" prop="packageName" min-width="140">
              <template #default="scope">{{ scope.row.packageName || '-' }}</template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="scope">{{ scope.row.quantity }}{{ scope.row.unit || '' }}</template>
            </el-table-column>
            <el-table-column label="小计" width="120" align="right">
              <template #default="scope">¥ {{ formatMoney(scope.row.subtotalPrice) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="上课记录" name="attendance">
          <el-table v-loading="tabLoading.lessons" :data="pages.lessons.rows" border>
            <el-table-column label="上课日期" prop="classDate" width="110" />
            <el-table-column label="时间" width="120">
              <template #default="scope">{{ scope.row.startTime }}-{{ scope.row.endTime }}</template>
            </el-table-column>
            <el-table-column label="班级" prop="className" min-width="130" show-overflow-tooltip />
            <el-table-column label="课程" prop="courseName" min-width="130" show-overflow-tooltip />
            <el-table-column label="老师" prop="teacherName" width="100" />
            <el-table-column label="到课状态" prop="statusName" width="90" />
            <el-table-column label="扣课" prop="deductQuantity" width="70" />
            <el-table-column label="扣后剩余" prop="afterRemaining" width="90" />
            <el-table-column label="补课" width="70">
              <template #default="scope">{{ scope.row.makeupFlag === 1 ? '已补' : '-' }}</template>
            </el-table-column>
          </el-table>
          <pagination v-show="pages.lessons.total > 0" :total="pages.lessons.total" v-model:page="pages.lessons.pageNum" v-model:limit="pages.lessons.pageSize" @pagination="loadTab('lessons')" />
        </el-tab-pane>

        <el-tab-pane label="考勤记录" name="checkin">
          <el-table v-loading="tabLoading.checkins" :data="pages.checkins.rows" border>
            <el-table-column label="课次日期" prop="eventDate" width="110" />
            <el-table-column label="上课时间" min-width="200">
              <template #default="scope">{{ scope.row.startTime }} ~ {{ scope.row.endTime }}</template>
            </el-table-column>
            <el-table-column label="班级" prop="className" min-width="130" show-overflow-tooltip />
            <el-table-column label="课程" prop="courseName" min-width="130" show-overflow-tooltip />
            <el-table-column label="考勤" prop="statusName" width="80" />
            <el-table-column label="签到时间" prop="checkInTime" width="170" />
            <el-table-column label="签到方式" prop="checkInMethod" width="90" />
            <el-table-column label="备注" prop="notes" min-width="120" show-overflow-tooltip />
          </el-table>
          <pagination v-show="pages.checkins.total > 0" :total="pages.checkins.total" v-model:page="pages.checkins.pageNum" v-model:limit="pages.checkins.pageSize" @pagination="loadTab('checkins')" />
        </el-tab-pane>

        <el-tab-pane label="成长档案" name="growth">
          <el-table v-loading="tabLoading.comments" :data="pages.comments.rows" border>
            <el-table-column label="上课日期" prop="classDate" width="110" />
            <el-table-column label="课程" prop="courseName" min-width="120" show-overflow-tooltip />
            <el-table-column label="老师" prop="teacherName" width="100" />
            <el-table-column label="课堂表现" prop="performanceScore" width="90" />
            <el-table-column label="作业" prop="homeworkScore" width="70" />
            <el-table-column label="点评内容" prop="commentContent" min-width="260" show-overflow-tooltip />
            <el-table-column label="改进建议" prop="suggestions" min-width="160" show-overflow-tooltip />
          </el-table>
          <pagination v-show="pages.comments.total > 0" :total="pages.comments.total" v-model:page="pages.comments.pageNum" v-model:limit="pages.comments.pageSize" @pagination="loadTab('comments')" />
        </el-tab-pane>

        <el-tab-pane label="学习报告" name="report">
          <el-empty description="学习报告需产品确认报告口径（统计维度/生成周期）后接入，课后点评见“成长档案”" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <course-account-ops ref="accountOpsRef" @done="handleAccountOpDone" />
    <receipt-dialog ref="receiptRef" />
  </div>
</template>

<script setup name="StudentDetail">
import { computed, getCurrentInstance, onMounted, reactive, ref } from 'vue';
import { ArrowDown } from '@element-plus/icons-vue';
import { useRoute, useRouter } from 'vue-router';
import { getStudent, getStudentCourses, getStudentOrders } from '@/api/teach/student';
import { listCourseAccountLog, listStudentCheckins, listStudentComments, listStudentLessons } from '@/api/teach/studentAccount';
import { listStudentCards } from '@/api/teach/card';
import CourseAccountOps from './components/CourseAccountOps.vue';
import ReceiptDialog from './components/ReceiptDialog.vue';
import FollowPanel from './components/FollowPanel.vue';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();

const studentId = Number(route.params.id);
const activeTab = ref('courses');
const consumeView = ref('orders');
const loading = ref(false);
const courseLoading = ref(false);
const orderLoading = ref(false);
const studentInfo = ref({});
const courseList = ref([]);
const orderList = ref([]);
const accountOpsRef = ref();
const receiptRef = ref();
const accountLogs = ref([]);
const logLoading = ref(false);
const logOpened = ref(false);
const cardList = ref([]);
const GRANT_STATUS = { 1: '有效', 2: '过期', 3: '用完', 4: '作废' };
const tabLoading = reactive({ cards: false, lessons: false, checkins: false, comments: false });
const pages = reactive({
  lessons: { rows: [], total: 0, pageNum: 1, pageSize: 10 },
  checkins: { rows: [], total: 0, pageNum: 1, pageSize: 10 },
  comments: { rows: [], total: 0, pageNum: 1, pageSize: 10 }
});
const TAB_LOADERS = { lessons: listStudentLessons, checkins: listStudentCheckins, comments: listStudentComments };

const remainingQuantityTotal = computed(() => {
  return courseList.value.reduce((total, course) => total + Number(course.remainingQuantity || 0), 0);
});

const orderSummary = computed(() => {
  const totalAmount = orderList.value.reduce((total, order) => total + Number(order.receivableAmount || 0), 0);
  const paidAmount = orderList.value.reduce((total, order) => total + Number(order.paidAmount || 0), 0);
  return {
    totalAmount,
    paidAmount,
    debtAmount: Math.max(totalAmount - paidAmount, 0)
  };
});

const orderItemList = computed(() => {
  const result = [];
  orderList.value.forEach(order => {
    (order.items || []).forEach(item => {
      result.push({
        ...item,
        orderNo: order.orderNo
      });
    });
  });
  return result;
});

function getStudentStatusName(status) {
  const statusMap = {
    0: '在读学员',
    1: '休学',
    2: '转学',
    3: '毕业'
  };
  return statusMap[status] || '在读学员';
}

function getChargeTypeName(chargeType) {
  return {
    class: '按课时',
    lesson: '按课时',
    month: '按月',
    day: '按天'
  }[chargeType] || '-';
}

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

function formatDateRange(startDate, endDate) {
  if (!startDate && !endDate) {
    return '不设置';
  }
  return `${startDate || '-'} 至 ${endDate || '-'}`;
}

function goBack() {
  router.back();
}

function handleEdit() {
  router.push(`/assistant/student/edit/${studentId}`);
}

function handleEnroll() {
  router.push(`/assistant/student/enroll/${studentId}`);
}

function handleRenew(row) {
  router.push({
    path: `/assistant/student/enroll/${studentId}`,
    query: { courseId: row.courseId }
  });
}

function handleTabChange(tab) {
  if (tab === 'courses') {
    loadStudentCourses();
  } else if (tab === 'consume') {
    loadStudentOrders();
  } else if (tab === 'cards') {
    loadCards();
  } else if (tab === 'attendance') {
    loadTab('lessons');
  } else if (tab === 'checkin') {
    loadTab('checkins');
  } else if (tab === 'growth') {
    loadTab('comments');
  }
}

function accountStatusType(status) {
  return { active: 'success', stopped: 'warning', completed: 'info', transferred: 'info' }[status] || 'info';
}

function openAccountOp(action, row) {
  accountOpsRef.value.open(action, [{ ...row, studentName: studentInfo.value.studentName }]);
}

function handleAccountOpDone() {
  loadStudentCourses();
  if (logOpened.value) {
    loadAccountLogs();
  }
}

function handleLogCollapse(names) {
  if (names.includes('logs')) {
    logOpened.value = true;
    loadAccountLogs();
  }
}

async function loadAccountLogs() {
  logLoading.value = true;
  try {
    const res = await listCourseAccountLog({ studentId });
    accountLogs.value = res.data || [];
  } finally {
    logLoading.value = false;
  }
}

async function loadCards() {
  tabLoading.cards = true;
  try {
    const res = await listStudentCards(studentId);
    cardList.value = res.data || [];
  } finally {
    tabLoading.cards = false;
  }
}

async function loadTab(key) {
  tabLoading[key] = true;
  try {
    const page = pages[key];
    const res = await TAB_LOADERS[key](studentId, { pageNum: page.pageNum, pageSize: page.pageSize });
    page.rows = res.rows || [];
    page.total = res.total || 0;
  } finally {
    tabLoading[key] = false;
  }
}

async function loadStudentDetail() {
  loading.value = true;
  try {
    const response = await getStudent(studentId);
    studentInfo.value = response.data || {};
  } finally {
    loading.value = false;
  }
}

async function loadStudentCourses() {
  courseLoading.value = true;
  try {
    const response = await getStudentCourses(studentId);
    courseList.value = response.data || [];
  } finally {
    courseLoading.value = false;
  }
}

async function loadStudentOrders() {
  orderLoading.value = true;
  try {
    const response = await getStudentOrders(studentId);
    orderList.value = response.data || [];
  } finally {
    orderLoading.value = false;
  }
}

onMounted(async () => {
  if (!studentId) {
    proxy.$modal.msgError('学员ID不存在');
    goBack();
    return;
  }
  await Promise.all([loadStudentDetail(), loadStudentCourses(), loadStudentOrders()]);
});
</script>

<style scoped lang="scss">
.student-detail {
  .student-info-card {
    .student-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;

      h2 {
        margin: 0;
      }
    }

    .info-row {
      .info-item {
        display: flex;
        margin-bottom: 12px;
        font-size: 14px;

        .label {
          flex: 0 0 86px;
          color: #909399;
        }

        .value {
          color: #303133;
          word-break: break-all;
        }
      }
    }

    .action-col {
      display: flex;
      flex-direction: column;
      gap: 10px;
      align-items: stretch;
    }
  }

  .course-stats {
    padding: 10px 0;
    font-size: 14px;
  }

  .consume-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;

    .consume-summary {
      display: flex;
      gap: 20px;
      flex: 1;
      justify-content: flex-end;
      padding: 9px 12px;
      background: #FFF7E6;
      color: #303133;
      font-size: 14px;
    }
  }

  .order-item-table {
    margin: 8px 36px;
    width: calc(100% - 72px);
  }

  .muted-text {
    color: #909399;
  }

  .account-log {
    margin-top: 16px;
  }
}
</style>
