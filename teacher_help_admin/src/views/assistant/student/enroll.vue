<template>
  <div class="app-container student-enroll">
    <el-page-header @back="goBack" content="报名/续费" style="margin-bottom: 20px" />

    <el-card>
      <div class="enroll-content">
        <div class="enroll-header">
          <div class="student-info-brief">
            <el-tag type="success">{{ getStudentStatusName(studentInfo.status) }}</el-tag>
            <span class="student-name">{{ studentInfo.studentName || '-' }}</span>
            <span class="student-phone">{{ studentInfo.parentPhone || studentInfo.phone || '-' }}</span>
            <el-icon class="edit-icon" @click="handleEditStudent"><Edit /></el-icon>
          </div>
          <div class="stats-info">
            <span>报名课程数: {{ selectedCourseCount }}</span>
            <span style="margin-left: 20px;">项目数: {{ enrollForm.items.length }}</span>
            <span style="margin-left: 20px;">消费金额: ¥ {{ calculateTotalAmount() }}</span>
          </div>
        </div>

        <div class="action-buttons">
          <el-button type="warning" size="small" @click="handleSelectCourse">选择课程</el-button>
          <el-button type="warning" size="small" @click="handleSelectItem">选择物品</el-button>
          <el-button type="warning" size="small" @click="handleSelectFee">选择费用</el-button>
          <el-button type="warning" size="small" @click="handleSelectPackage">选择套餐</el-button>
        </div>

        <el-table
          v-loading="loading"
          :data="enrollForm.items"
          border
          class="enroll-table"
          empty-text="请选择购买项目"
        >
          <el-table-column label="购买项目" width="190" fixed="left">
            <template #default="scope">
              <div class="item-name-cell">
                <el-tag size="small" :type="getItemTagType(scope.row.itemType)">
                  {{ getItemTypeName(scope.row.itemType) }}
                </el-tag>
                <div>
                  <div class="item-name">{{ scope.row.itemName }}</div>
                  <div v-if="scope.row.packageName" class="item-extra">套餐: {{ scope.row.packageName }}</div>
                  <div v-if="scope.row.specName && scope.row.itemType !== 'course'" class="item-extra">
                    {{ scope.row.specName }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="定价标准" width="220">
            <template #default="scope">
              <el-select
                v-if="scope.row.itemType === 'course'"
                v-model="scope.row.selectedPriceOption"
                size="small"
                placeholder="请选择"
                style="width: 100%;"
                :disabled="!!scope.row.packageId"
                @change="handlePriceStandardChange(scope.row)"
              >
                <el-option
                  v-for="option in scope.row.priceOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <span v-else>{{ scope.row.specName || `${formatMoney(scope.row.unitPrice)}元/${scope.row.unit}` }}</span>
            </template>
          </el-table-column>

          <el-table-column label="购买数量" width="130" align="center">
            <template #default="scope">
              <div class="quantity-cell">
                <el-input-number
                  v-model="scope.row.quantity"
                  :min="1"
                  :max="scope.row.itemType === 'item' ? scope.row.stock || 99999 : 99999"
                  :step="1"
                  :disabled="!scope.row.canEditQuantity"
                  size="small"
                  controls-position="right"
                  style="width: 76px;"
                  @change="handleQuantityChange(scope.row)"
                />
                <span>{{ scope.row.unit }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="总价" width="120" align="right">
            <template #default="scope">
              <span>¥ {{ formatMoney(scope.row.totalPrice) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="赠送数量" width="130" align="center">
            <template #default="scope">
              <div v-if="scope.row.itemType === 'course'" class="quantity-cell">
                <el-input-number
                  v-model="scope.row.giftQuantity"
                  :min="0"
                  :step="1"
                  size="small"
                  controls-position="right"
                  style="width: 76px;"
                  @change="handleGiftQuantityChange(scope.row)"
                />
                <span>{{ scope.row.unit }}</span>
              </div>
              <span v-else class="muted-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="课程起止日期" width="250">
            <template #default="scope">
              <div v-if="isPeriodCourse(scope.row)" class="date-range-cell">
                <el-date-picker
                  v-model="scope.row.startDate"
                  type="date"
                  placeholder="开始日期"
                  size="small"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 112px;"
                  @change="handleStartDateChange(scope.row)"
                />
                <span>至</span>
                <el-date-picker
                  v-model="scope.row.endDate"
                  type="date"
                  placeholder="结束日期"
                  size="small"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 112px;"
                />
              </div>
              <span v-else class="muted-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="班级" width="140">
            <template #default="scope">
              <el-input
                v-if="scope.row.itemType === 'course'"
                v-model="scope.row.className"
                size="small"
                placeholder="未选班"
              />
              <span v-else class="muted-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="课程有效期" width="150">
            <template #default="scope">
              <el-select
                v-if="scope.row.itemType === 'course' && !isPeriodCourse(scope.row)"
                v-model="scope.row.validityType"
                size="small"
                placeholder="请选择"
                style="width: 100%;"
              >
                <el-option label="不设置" value="not_set" />
                <el-option label="立即生效" value="immediate" />
                <el-option label="第一次点名生效" value="first_attendance" />
              </el-select>
              <span v-else class="muted-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="请假免扣次数" width="130" align="center">
            <template #default="scope">
              <div v-if="scope.row.itemType === 'course'" class="quantity-cell">
                <el-input-number
                  v-model="scope.row.leaveExemptCount"
                  :min="0"
                  :step="1"
                  size="small"
                  controls-position="right"
                  style="width: 76px;"
                />
                <span>次</span>
              </div>
              <span v-else class="muted-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="直减/折扣" width="180" align="right">
            <template #default="scope">
              <div class="discount-cell">
                <el-select
                  v-model="scope.row.discountType"
                  size="small"
                  style="width: 72px;"
                  @change="updateItemAmount(scope.row)"
                >
                  <el-option label="直减" value="reduce" />
                  <el-option label="折扣" value="discount" />
                </el-select>
                <el-input-number
                  v-model="scope.row.discountValue"
                  :min="0"
                  :precision="2"
                  size="small"
                  controls-position="right"
                  style="width: 88px;"
                  @change="updateItemAmount(scope.row)"
                />
              </div>
            </template>
          </el-table-column>

          <el-table-column label="小计" width="130" align="right" fixed="right">
            <template #default="scope">
              <span class="subtotal-text">¥ {{ formatMoney(scope.row.subtotalPrice) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="80" fixed="right" align="center">
            <template #default="scope">
              <el-button type="danger" link @click="removeItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="other-info-section">
          <div class="section-title">其他信息</div>
          <el-form :model="enrollForm" label-width="100px" class="enroll-detail-form">
            <el-form-item label="经办日期：">
              <el-date-picker
                v-model="enrollForm.enrollDate"
                type="date"
                placeholder="选择日期"
                style="width: 200px;"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>

            <el-form-item label="业绩归属人：">
              <div class="performance-row">
                <el-input v-model="enrollForm.performanceOwner" placeholder="业绩归属人" style="width: 160px;" />
                <el-select v-model="enrollForm.performanceType" placeholder="业绩类型" style="width: 140px;">
                  <el-option label="销售业绩" value="sale" />
                  <el-option label="绩效业绩" value="performance" />
                </el-select>
                <el-input-number
                  v-model="enrollForm.performanceAmount"
                  :min="0"
                  :precision="2"
                  controls-position="right"
                  placeholder="请输入"
                  style="width: 140px;"
                />
              </div>
            </el-form-item>

            <el-form-item label="备注：">
              <el-input
                v-model="enrollForm.remark"
                type="textarea"
                :rows="4"
                placeholder="请输入备注"
                style="width: 520px;"
              />
            </el-form-item>

            <el-form-item label="附件：">
              <div class="attachment-area">
                <el-button size="small" disabled>选择文件</el-button>
                <span class="attachment-tip">附件上传将在收据/财务闭环中接入</span>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div class="enroll-summary">
          <div class="summary-left">
            <span class="summary-label">共 {{ enrollForm.items.length }} 个项目</span>
          </div>
          <div class="summary-right">
            <span class="total-amount-label">应收金额:</span>
            <span class="total-amount-value">¥ {{ calculateTotalAmount() }}</span>
            <el-button @click="goBack" style="margin-left: 20px;">取消</el-button>
            <el-button type="warning" :loading="submitting" @click="handleConfirmEnroll">确认报名</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="selectCourseDialogVisible"
      title="选择课程"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-input
        v-model="courseSearchKeyword"
        placeholder="请输入课程名称"
        clearable
        style="margin-bottom: 15px;"
        @keyup.enter="loadCourseOptions"
      >
        <template #suffix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        v-loading="courseLoading"
        :data="filteredCourseList"
        border
        max-height="400px"
        @selection-change="handleCourseSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="课程名称" prop="courseName" min-width="160" />
        <el-table-column label="课程类型" prop="courseType" width="120" />
        <el-table-column label="定价标准" prop="priceStandard" min-width="260" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <span class="total-text">共{{ availableCourseList.length }}条数据</span>
        <el-pagination
          v-model:current-page="coursePagination.currentPage"
          v-model:page-size="coursePagination.pageSize"
          :total="availableCourseList.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, jumper"
        />
      </div>

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

    <el-dialog
      v-model="selectItemDialogVisible"
      title="选择物品"
      width="880px"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input
            v-model="itemSearchKeyword"
            placeholder="请输入物品名称"
            clearable
            style="width: 220px;"
            @keyup.enter="loadAvailableItems"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="loadAvailableItems">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="itemLoading"
        :data="availableItemList"
        row-key="id"
        max-height="420"
      >
        <el-table-column type="expand">
          <template #default="props">
            <div class="sku-table-wrap">
              <el-table
                :data="props.row.skus || []"
                border
                :row-key="(row) => `${props.row.id}_${row.id}`"
                @selection-change="(selection) => handleSkuSelectionChange(selection, props.row)"
              >
                <el-table-column type="selection" width="55" :reserve-selection="true" />
                <el-table-column label="规格组合" prop="specText" min-width="180" />
                <el-table-column label="单价" prop="price" width="120" align="right">
                  <template #default="scope">¥ {{ formatMoney(scope.row.price) }}</template>
                </el-table-column>
                <el-table-column label="库存" width="100" align="center">
                  <template #default="scope">
                    <span :class="{ 'stock-warning': getSkuStock(scope.row) <= 0 }">
                      {{ getSkuStock(scope.row) }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="物品名称" prop="itemName" min-width="180" />
        <el-table-column label="单价" prop="priceRange" width="160" align="right" />
        <el-table-column label="库存" prop="totalStock" width="100" align="center" />
      </el-table>

      <div class="selection-footer">
        <span>已选择: {{ selectedSkuList.length }}项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectItemDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmSelectItem">选好了</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="selectFeeDialogVisible"
      title="选择费用"
      width="640px"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-input
        v-model="feeSearchKeyword"
        placeholder="请输入费用名称"
        clearable
        style="margin-bottom: 15px;"
        @keyup.enter="loadFees"
      >
        <template #suffix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        v-loading="feeLoading"
        :data="filteredFeeList"
        border
        max-height="400px"
        @selection-change="handleFeeSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="费用名称" prop="feeName" min-width="220" />
        <el-table-column label="单价" prop="price" width="140" align="right">
          <template #default="scope">¥ {{ formatMoney(scope.row.price || scope.row.amount) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <span class="total-text">共{{ availableFeeList.length }}条数据</span>
        <el-pagination
          v-model:current-page="feePagination.currentPage"
          v-model:page-size="feePagination.pageSize"
          :total="availableFeeList.length"
          :page-sizes="[10, 20, 50]"
          layout="prev, pager, next"
        />
      </div>

      <div class="selection-footer">
        <span>已选择: {{ selectedFees.length }}项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectFeeDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmSelectFee">选好了</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="selectPackageDialogVisible"
      title="选择套餐"
      width="760px"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-input
        v-model="packageSearchKeyword"
        placeholder="请输入套餐名称"
        clearable
        style="margin-bottom: 15px;"
        @keyup.enter="loadPackages"
      >
        <template #suffix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        v-loading="packageLoading"
        :data="filteredPackageList"
        border
        max-height="400px"
        @selection-change="handlePackageSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="套餐名称" prop="packageName" min-width="180" />
        <el-table-column label="套餐内容" prop="itemSummary" min-width="260" show-overflow-tooltip />
        <el-table-column label="套餐金额" prop="totalPrice" width="140" align="right">
          <template #default="scope">¥ {{ formatMoney(scope.row.totalPrice) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <span class="total-text">共{{ availablePackageList.length }}条数据</span>
        <el-pagination
          v-model:current-page="packagePagination.currentPage"
          v-model:page-size="packagePagination.pageSize"
          :total="availablePackageList.length"
          :page-sizes="[10, 20, 50]"
          layout="prev, pager, next"
        />
      </div>

      <div class="selection-footer">
        <span>已选择: {{ selectedPackages.length }}项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectPackageDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleConfirmSelectPackage">选好了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="StudentEnroll">
import { computed, getCurrentInstance, onMounted, ref } from 'vue';
import { Edit, Search } from '@element-plus/icons-vue';
import { useRoute, useRouter } from 'vue-router';
import { getStudent, getStudentCourses, submitStudentEnroll } from '@/api/teach/student';
import { getCoursePackage, listCourseOptions, listCoursePackage } from '@/api/assistant/course';
import { listAvailableItems, listFee } from '@/api/assistant/inventory';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();

const studentId = Number(route.params.id);
const loading = ref(false);
const submitting = ref(false);
const studentInfo = ref({});
const existingCourseIds = ref([]);

const enrollForm = ref({
  items: [],
  enrollDate: formatDate(new Date()),
  performanceOwner: '',
  performanceType: 'sale',
  performanceAmount: 0,
  remark: ''
});

const selectCourseDialogVisible = ref(false);
const courseLoading = ref(false);
const courseSearchKeyword = ref('');
const availableCourseList = ref([]);
const selectedCourses = ref([]);
const coursePagination = ref({
  currentPage: 1,
  pageSize: 10
});

const selectItemDialogVisible = ref(false);
const itemLoading = ref(false);
const itemSearchKeyword = ref('');
const availableItemList = ref([]);
const selectedSkuList = ref([]);

const selectFeeDialogVisible = ref(false);
const feeLoading = ref(false);
const feeSearchKeyword = ref('');
const availableFeeList = ref([]);
const selectedFees = ref([]);
const feePagination = ref({
  currentPage: 1,
  pageSize: 10
});

const selectPackageDialogVisible = ref(false);
const packageLoading = ref(false);
const packageSearchKeyword = ref('');
const availablePackageList = ref([]);
const selectedPackages = ref([]);
const packagePagination = ref({
  currentPage: 1,
  pageSize: 10
});

const chargeTypeUnits = {
  class: '课时',
  lesson: '课时',
  month: '月',
  day: '天',
  item: '件',
  fee: '笔'
};

const selectedCourseCount = computed(() => {
  return enrollForm.value.items.filter(item => item.itemType === 'course').length;
});

const filteredCourseList = computed(() => {
  const keyword = courseSearchKeyword.value.trim().toLowerCase();
  let list = availableCourseList.value;
  if (keyword) {
    list = list.filter(course => (course.courseName || '').toLowerCase().includes(keyword));
  }
  return getPagedList(list, coursePagination.value);
});

const filteredFeeList = computed(() => {
  const keyword = feeSearchKeyword.value.trim().toLowerCase();
  let list = availableFeeList.value;
  if (keyword) {
    list = list.filter(fee => (fee.feeName || '').toLowerCase().includes(keyword));
  }
  return getPagedList(list, feePagination.value);
});

const filteredPackageList = computed(() => {
  const keyword = packageSearchKeyword.value.trim().toLowerCase();
  let list = availablePackageList.value;
  if (keyword) {
    list = list.filter(item => (item.packageName || '').toLowerCase().includes(keyword));
  }
  return getPagedList(list, packagePagination.value);
});

function getPagedList(list, pagination) {
  const start = (pagination.currentPage - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  return list.slice(start, end);
}

function formatDate(value) {
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

function toNumber(value, defaultValue = 0) {
  const numberValue = Number(value);
  return Number.isNaN(numberValue) ? defaultValue : numberValue;
}

function getStudentStatusName(status) {
  const statusMap = {
    0: '在读',
    1: '在读',
    2: '休学',
    3: '转学',
    4: '毕业'
  };
  return statusMap[status] || '在读';
}

function getItemTypeName(itemType) {
  return {
    course: '课程',
    item: '物品',
    fee: '费用'
  }[itemType] || itemType;
}

function getItemTagType(itemType) {
  return {
    course: 'warning',
    item: 'success',
    fee: 'info'
  }[itemType] || '';
}

function isPeriodCourse(row) {
  return row.itemType === 'course' && ['month', 'day'].includes(row.chargeType);
}

function getSkuStock(sku) {
  return toNumber(sku.stock ?? sku.availableStock, 0);
}

function getRowKey(row) {
  return [row.itemType, row.itemId, row.specId || '', row.packageId || ''].join('_');
}

function hasSelectedRow(row) {
  return enrollForm.value.items.some(item => getRowKey(item) === getRowKey(row));
}

function goBack() {
  router.back();
}

function handleEditStudent() {
  router.push(`/assistant/student/edit/${studentId}`);
}

async function loadStudentInfo() {
  const response = await getStudent(studentId);
  studentInfo.value = response.data || {};
}

async function loadExistingCourses() {
  const response = await getStudentCourses(studentId);
  existingCourseIds.value = (response.data || []).map(item => Number(item.courseId));
}

async function loadCourseOptions() {
  courseLoading.value = true;
  try {
    const response = await listCourseOptions({ keyword: courseSearchKeyword.value });
    availableCourseList.value = response.data || [];
  } finally {
    courseLoading.value = false;
  }
}

async function loadAvailableItems() {
  itemLoading.value = true;
  try {
    const response = await listAvailableItems({ keyword: itemSearchKeyword.value });
    availableItemList.value = response.data || [];
  } finally {
    itemLoading.value = false;
  }
}

async function loadFees() {
  feeLoading.value = true;
  try {
    const response = await listFee({
      pageNum: 1,
      pageSize: 200,
      feeName: feeSearchKeyword.value,
      status: 1
    });
    availableFeeList.value = response.rows || response.data || [];
  } finally {
    feeLoading.value = false;
  }
}

async function loadPackages() {
  packageLoading.value = true;
  try {
    const response = await listCoursePackage({
      pageNum: 1,
      pageSize: 200,
      packageName: packageSearchKeyword.value,
      status: 1
    });
    availablePackageList.value = response.rows || response.data || [];
  } finally {
    packageLoading.value = false;
  }
}

function buildCoursePriceOptions(course) {
  const prices = course.prices || [];
  if (!prices.length) {
    return [
      {
        value: 'default',
        label: '未设置定价(0元/课时)',
        specId: null,
        specName: '未设置定价',
        chargeType: 'class',
        unit: '课时',
        quantity: 1,
        unitPrice: 0,
        totalPrice: 0,
        canEditQuantity: true
      }
    ];
  }

  return prices.map(price => {
    const chargeType = price.chargeType || 'class';
    const unit = chargeTypeUnits[chargeType] || '课时';
    const quantity = Math.max(toNumber(price.quantity, 1), 1);
    const totalPrice = toNumber(price.totalPrice, 0);
    const unitPrice = toNumber(price.unitPrice, quantity ? totalPrice / quantity : totalPrice);
    const priceName = price.priceName || price.name || '单价';
    return {
      value: price.id,
      label: price.displayText || `${priceName}(${formatMoney(totalPrice)}元${quantity}${unit})`,
      specId: price.id,
      specName: priceName,
      chargeType,
      unit,
      quantity,
      unitPrice,
      totalPrice,
      canEditQuantity: quantity === 1
    };
  });
}

function createBaseRow(payload) {
  const row = {
    giftQuantity: 0,
    leaveExemptCount: 0,
    discountType: 'reduce',
    discountValue: 0,
    startDate: '',
    endDate: '',
    validityType: 'not_set',
    className: '',
    stock: null,
    canEditQuantity: true,
    ...payload
  };
  updateItemAmount(row);
  return row;
}

function createCourseRow(course, packageInfo = null, packageItem = null) {
  const priceOptions = packageItem?.priceOptions?.length ? packageItem.priceOptions.map(price => ({
    value: price.id,
    label: price.displayText || price.priceName || price.name,
    specId: price.id,
    specName: price.priceName || price.name,
    chargeType: price.chargeType || 'class',
    unit: chargeTypeUnits[price.chargeType || 'class'] || '课时',
    quantity: toNumber(price.quantity, 1),
    unitPrice: toNumber(price.unitPrice, 0),
    totalPrice: toNumber(price.totalPrice, 0),
    canEditQuantity: false
  })) : buildCoursePriceOptions(course);
  const matchedOption = priceOptions.find(option => option.specId === packageItem?.specId) || priceOptions[0];
  return createBaseRow({
    itemType: 'course',
    itemId: course.id || packageItem?.itemId,
    itemName: course.courseName || packageItem?.itemName,
    courseType: course.courseType,
    selectedPriceOption: matchedOption.value,
    priceOptions,
    specId: matchedOption.specId,
    specName: matchedOption.specName,
    chargeType: matchedOption.chargeType,
    unit: packageItem?.unit || matchedOption.unit,
    quantity: packageItem?.quantity || matchedOption.quantity,
    unitPrice: packageItem ? toNumber(packageItem.unitPrice, matchedOption.unitPrice) : matchedOption.unitPrice,
    giftQuantity: packageItem?.giftQuantity || 0,
    leaveExemptCount: packageItem?.leaveFreeQuantity || 0,
    discountType: packageItem?.discountType || 'reduce',
    discountValue: toNumber(packageItem?.discountValue, 0),
    packageId: packageInfo?.id,
    packageName: packageInfo?.packageName,
    canEditQuantity: packageInfo ? false : matchedOption.canEditQuantity
  });
}

function createInventoryRow(item, sku, packageInfo = null, packageItem = null) {
  return createBaseRow({
    itemType: 'item',
    itemId: item.id || packageItem?.itemId,
    itemName: item.itemName || packageItem?.itemName,
    specId: sku?.id || packageItem?.specId,
    specName: sku?.specText || sku?.skuName || packageItem?.specName,
    chargeType: 'item',
    unit: packageItem?.unit || '件',
    quantity: packageItem?.quantity || 1,
    unitPrice: packageItem ? toNumber(packageItem.unitPrice, 0) : toNumber(sku?.price, 0),
    discountType: packageItem?.discountType || 'reduce',
    discountValue: toNumber(packageItem?.discountValue, 0),
    stock: sku?.id ? getSkuStock(sku) : null,
    packageId: packageInfo?.id,
    packageName: packageInfo?.packageName,
    canEditQuantity: !packageInfo
  });
}

function createFeeRow(fee, packageInfo = null, packageItem = null) {
  return createBaseRow({
    itemType: 'fee',
    itemId: fee.id || packageItem?.itemId,
    itemName: fee.feeName || packageItem?.itemName,
    specId: packageItem?.specId,
    specName: packageItem?.specName,
    chargeType: 'fee',
    unit: packageItem?.unit || '笔',
    quantity: packageItem?.quantity || 1,
    unitPrice: packageItem ? toNumber(packageItem.unitPrice, 0) : toNumber(fee.price || fee.amount, 0),
    discountType: packageItem?.discountType || 'reduce',
    discountValue: toNumber(packageItem?.discountValue, 0),
    packageId: packageInfo?.id,
    packageName: packageInfo?.packageName,
    canEditQuantity: !packageInfo
  });
}

function addRow(row) {
  if (hasSelectedRow(row)) {
    return false;
  }
  enrollForm.value.items.push(row);
  return true;
}

function handleSelectCourse() {
  selectCourseDialogVisible.value = true;
  selectedCourses.value = [];
  coursePagination.value.currentPage = 1;
  loadCourseOptions();
}

function handleCourseSelectionChange(selection) {
  selectedCourses.value = selection;
}

function handleConfirmSelectCourse() {
  if (!selectedCourses.value.length) {
    proxy.$modal.msgWarning('请至少选择一个课程');
    return;
  }

  let addedCount = 0;
  selectedCourses.value.forEach(course => {
    if (addRow(createCourseRow(course))) {
      addedCount += 1;
    }
  });
  selectCourseDialogVisible.value = false;
  proxy.$modal.msgSuccess(`已添加 ${addedCount} 个课程`);
}

function handleSelectItem() {
  selectItemDialogVisible.value = true;
  selectedSkuList.value = [];
  loadAvailableItems();
}

function handleSkuSelectionChange(selection, parentItem) {
  selectedSkuList.value = selectedSkuList.value.filter(item => item.parentItemId !== parentItem.id);
  selectedSkuList.value.push(
    ...selection.map(sku => ({
      parentItemId: parentItem.id,
      parentItem: parentItem,
      sku
    }))
  );
}

function handleConfirmSelectItem() {
  if (!selectedSkuList.value.length) {
    proxy.$modal.msgWarning('请至少选择一个物品');
    return;
  }

  let addedCount = 0;
  selectedSkuList.value.forEach(({ parentItem, sku }) => {
    if (getSkuStock(sku) <= 0) {
      return;
    }
    if (addRow(createInventoryRow(parentItem, sku))) {
      addedCount += 1;
    }
  });
  selectItemDialogVisible.value = false;
  proxy.$modal.msgSuccess(`已添加 ${addedCount} 个物品`);
}

function handleSelectFee() {
  selectFeeDialogVisible.value = true;
  selectedFees.value = [];
  feePagination.value.currentPage = 1;
  loadFees();
}

function handleFeeSelectionChange(selection) {
  selectedFees.value = selection;
}

function handleConfirmSelectFee() {
  if (!selectedFees.value.length) {
    proxy.$modal.msgWarning('请至少选择一个费用');
    return;
  }

  let addedCount = 0;
  selectedFees.value.forEach(fee => {
    if (addRow(createFeeRow(fee))) {
      addedCount += 1;
    }
  });
  selectFeeDialogVisible.value = false;
  proxy.$modal.msgSuccess(`已添加 ${addedCount} 个费用`);
}

function handleSelectPackage() {
  selectPackageDialogVisible.value = true;
  selectedPackages.value = [];
  packagePagination.value.currentPage = 1;
  loadPackages();
}

function handlePackageSelectionChange(selection) {
  selectedPackages.value = selection;
}

async function handleConfirmSelectPackage() {
  if (!selectedPackages.value.length) {
    proxy.$modal.msgWarning('请至少选择一个套餐');
    return;
  }

  let addedCount = 0;
  for (const selectedPackage of selectedPackages.value) {
    const response = await getCoursePackage(selectedPackage.id);
    const packageDetail = response.data || selectedPackage;
    const packageInfo = {
      id: packageDetail.id,
      packageName: packageDetail.packageName
    };
    (packageDetail.items || []).forEach(packageItem => {
      let row = null;
      if (packageItem.itemType === 'course') {
        row = createCourseRow(
          {
            id: packageItem.itemId,
            courseName: packageItem.itemName,
            prices: packageItem.priceOptions || []
          },
          packageInfo,
          packageItem
        );
      } else if (packageItem.itemType === 'item') {
        row = createInventoryRow({}, {}, packageInfo, packageItem);
      } else if (packageItem.itemType === 'fee') {
        row = createFeeRow({}, packageInfo, packageItem);
      }
      if (row && addRow(row)) {
        addedCount += 1;
      }
    });
  }
  selectPackageDialogVisible.value = false;
  proxy.$modal.msgSuccess(`已添加 ${addedCount} 个套餐项目`);
}

function handlePriceStandardChange(row) {
  const selectedOption = row.priceOptions.find(option => option.value === row.selectedPriceOption);
  if (!selectedOption) {
    return;
  }
  row.specId = selectedOption.specId;
  row.specName = selectedOption.specName;
  row.chargeType = selectedOption.chargeType;
  row.unit = selectedOption.unit;
  row.unitPrice = selectedOption.unitPrice;
  row.canEditQuantity = selectedOption.canEditQuantity;
  if (!selectedOption.canEditQuantity) {
    row.quantity = selectedOption.quantity;
  }
  handleQuantityChange(row);
}

function handleQuantityChange(row) {
  updateItemAmount(row);
  calculateEndDate(row, true);
}

function handleGiftQuantityChange(row) {
  calculateEndDate(row, true);
}

function handleStartDateChange(row) {
  calculateEndDate(row, true);
}

function updateItemAmount(row) {
  const quantity = Math.max(toNumber(row.quantity, 1), 1);
  const totalPrice = toNumber(row.unitPrice, 0) * quantity;
  const discountValue = toNumber(row.discountValue, 0);
  let subtotalPrice = totalPrice;

  if (row.discountType === 'discount' && discountValue > 0) {
    subtotalPrice = totalPrice * (discountValue <= 10 ? discountValue / 10 : discountValue / 100);
  } else {
    subtotalPrice = totalPrice - discountValue;
  }

  row.quantity = quantity;
  row.totalPrice = Number(totalPrice.toFixed(2));
  row.subtotalPrice = Number(Math.max(subtotalPrice, 0).toFixed(2));
}

function calculateEndDate(row, autoUpdate = true) {
  if (!isPeriodCourse(row) || !row.startDate) {
    if (autoUpdate && isPeriodCourse(row)) {
      row.endDate = '';
    }
    return '';
  }

  const totalQuantity = toNumber(row.quantity, 0) + toNumber(row.giftQuantity, 0);
  if (totalQuantity <= 0) {
    row.endDate = '';
    return '';
  }

  const startDate = new Date(row.startDate);
  const endDate = new Date(startDate);
  if (row.chargeType === 'day') {
    endDate.setDate(startDate.getDate() + totalQuantity - 1);
  } else {
    endDate.setMonth(startDate.getMonth() + totalQuantity);
    endDate.setDate(endDate.getDate() - 1);
  }

  const result = formatDate(endDate);
  if (autoUpdate) {
    row.endDate = result;
  }
  return result;
}

function removeItem(index) {
  enrollForm.value.items.splice(index, 1);
}

function calculateTotalAmount() {
  return enrollForm.value.items.reduce((total, item) => total + toNumber(item.subtotalPrice, 0), 0).toFixed(2);
}

function validateEnrollItems() {
  if (!enrollForm.value.items.length) {
    proxy.$modal.msgWarning('请至少选择一个购买项目');
    return false;
  }
  const stockErrorItem = enrollForm.value.items.find(item => {
    return item.itemType === 'item' && item.stock !== null && item.stock !== undefined && item.stock < item.quantity;
  });
  if (stockErrorItem) {
    proxy.$modal.msgWarning(`物品 ${stockErrorItem.itemName} 库存不足`);
    return false;
  }
  return true;
}

function buildSubmitPayload() {
  const hasRenewCourse = enrollForm.value.items.some(item => {
    return item.itemType === 'course' && existingCourseIds.value.includes(Number(item.itemId));
  });
  return {
    studentId,
    orderType: hasRenewCourse ? 'renew' : 'enroll',
    enrollDate: enrollForm.value.enrollDate,
    performanceOwner: enrollForm.value.performanceOwner,
    performanceType: enrollForm.value.performanceType,
    performanceAmount: enrollForm.value.performanceAmount,
    remark: enrollForm.value.remark,
    items: enrollForm.value.items.map((item, index) => ({
      itemType: item.itemType,
      itemId: item.itemId,
      itemName: item.itemName,
      specId: item.specId,
      specName: item.specName,
      chargeType: item.chargeType,
      unit: item.unit,
      quantity: item.quantity,
      giftQuantity: item.itemType === 'course' ? item.giftQuantity || 0 : 0,
      leaveExemptCount: item.itemType === 'course' ? item.leaveExemptCount || 0 : 0,
      unitPrice: item.unitPrice,
      totalPrice: item.totalPrice,
      discountType: item.discountType,
      discountValue: item.discountValue,
      subtotalPrice: item.subtotalPrice,
      startDate: item.startDate || undefined,
      endDate: item.endDate || undefined,
      validityType: item.validityType,
      className: item.className,
      packageId: item.packageId,
      packageName: item.packageName,
      remark: item.remark,
      sort: index
    }))
  };
}

function handleConfirmEnroll() {
  if (!validateEnrollItems()) {
    return;
  }

  proxy.$modal.confirm('确认提交报名/续费订单吗？').then(async () => {
    submitting.value = true;
    try {
      const response = await submitStudentEnroll(buildSubmitPayload());
      proxy.$modal.msgSuccess(response.msg || '报名成功');
      router.push(`/assistant/student/detail/${studentId}`);
    } finally {
      submitting.value = false;
    }
  });
}

onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([loadStudentInfo(), loadExistingCourses()]);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped lang="scss">
.student-enroll {
  .enroll-content {
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

        .edit-icon {
          cursor: pointer;
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

    .enroll-table {
      margin-top: 15px;
    }

    .item-name-cell {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      line-height: 1.4;

      .item-name {
        font-weight: 500;
        color: #303133;
      }

      .item-extra {
        color: #909399;
        font-size: 12px;
      }
    }

    .quantity-cell,
    .date-range-cell,
    .discount-cell,
    .performance-row {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .muted-text {
      color: #C0C4CC;
    }

    .subtotal-text {
      color: #E6A23C;
      font-weight: 600;
      font-size: 15px;
    }

    .other-info-section {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #EBEEF5;

      .section-title {
        font-size: 16px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 20px;
        padding-left: 10px;
        border-left: 3px solid #E6A23C;
      }

      .attachment-area {
        display: flex;
        align-items: center;

        .attachment-tip {
          margin-left: 10px;
          color: #909399;
          font-size: 12px;
        }
      }
    }

    .enroll-summary {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: #F5F7FA;
      border-radius: 4px;
      margin-top: 30px;

      .summary-label,
      .total-amount-label {
        font-size: 14px;
        color: #606266;
      }

      .summary-right {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .total-amount-value {
        font-size: 20px;
        font-weight: 600;
        color: #E6A23C;
      }
    }
  }

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

  .sku-table-wrap {
    padding: 0 50px;
  }

  .stock-warning {
    color: #F56C6C;
  }
}
</style>
