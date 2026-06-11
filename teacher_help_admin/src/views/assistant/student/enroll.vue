<template>
  <div class="app-container student-enroll">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" content="报名/续费" style="margin-bottom: 20px" />

    <!-- 主要内容 -->
    <el-card>
      <div class="enroll-content">
        <!-- 顶部信息栏 -->
        <div class="enroll-header">
          <div class="student-info-brief">
            <el-tag>在读</el-tag>
            <span class="student-name">{{ studentInfo.studentName }}</span>
            <span class="student-phone">{{ studentInfo.phone }}</span>
            <el-icon style="margin-left: 5px; cursor: pointer;"><Edit /></el-icon>
          </div>
          <div class="stats-info">
            <span>报名课程数: {{ enrollForm.courses.length }}</span>
            <span style="margin-left: 20px;">问题单数: 0</span>
            <span style="margin-left: 20px;">问题金额: {{ enrollForm.problemAmount }}</span>
          </div>
        </div>

        <!-- 操作按钮组 -->
        <div class="action-buttons">
          <el-button type="warning" size="small" @click="handleSelectCourse">选择课程</el-button>
          <el-button type="warning" size="small" @click="handleSelectItem">选择物品</el-button>
          <el-button type="warning" size="small" @click="handleSelectFee">选择费用</el-button>
          <el-button type="warning" size="small" plain>选择卡项</el-button>
        </div>

        <!-- 空状态提示 -->
        <div v-if="enrollForm.courses.length === 0" class="empty-state-inline">
          <div class="empty-icon">📦</div>
          <div class="empty-text">暂无有效项目</div>
        </div>

        <!-- 已选课程列表 -->
        <div v-else class="enroll-form">

          <!-- 课程列表表格 -->
          <el-table :data="enrollForm.courses" border style="margin-top: 15px;">
            <!-- 购买项目 -->
            <el-table-column label="购买项目" width="150" fixed="left">
              <template #default="scope">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-tag size="small" type="warning">{{ scope.row.itemType }}</el-tag>
                  <span style="font-weight: 500;">{{ scope.row.courseName }}</span>
                </div>
              </template>
            </el-table-column>

            <!-- 定价标准 -->
            <el-table-column label="定价标准" width="180">
              <template #default="scope">
                <el-select
                  v-model="scope.row.selectedPriceOption"
                  size="small"
                  placeholder="请选择"
                  style="width: 100%;"
                  @change="handlePriceStandardChange(scope.$index)"
                >
                  <el-option
                    v-for="option in scope.row.priceOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </template>
            </el-table-column>

            <!-- 购买数量 -->
            <el-table-column label="购买数量" width="110" align="center">
              <template #default="scope">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px;">
                  <el-input-number
                    v-model="scope.row.quantity"
                    :min="1"
                    :step="1"
                    :disabled="!scope.row.canEditQuantity"
                    size="small"
                    controls-position="right"
                    style="width: 60px;"
                    @input="handleQuantityChange(scope.$index)"
                  />
                  <span>{{ scope.row.unit }}</span>
                </div>
              </template>
            </el-table-column>

            <!-- 总价 -->
            <el-table-column label="总价" width="110" align="right">
              <template #default="scope">
                <span style="color: #303133; font-weight: 500;">¥ {{ (scope.row.unitPrice * scope.row.quantity).toFixed(2) }}</span>
              </template>
            </el-table-column>

            <!-- 赠送数量 -->
            <el-table-column label="赠送数量" width="110" align="center">
              <template #default="scope">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px;">
                  <el-input-number
                    v-model="scope.row.giftQuantity"
                    :min="0"
                    :step="1"
                    size="small"
                    controls-position="right"
                    style="width: 60px;"
                    @input="handleGiftQuantityChange(scope.$index)"
                  />
                  <span>{{ scope.row.unit }}</span>
                </div>
              </template>
            </el-table-column>

            <!-- 课程起止日期 (按天/按月课程显示) -->
            <el-table-column label="课程起止日期" width="240">
              <template #default="scope">
                <div v-if="scope.row.chargeType === 'month' || scope.row.chargeType === 'day'" style="display: flex; align-items: center; gap: 5px;">
                  <el-date-picker
                    v-model="scope.row.startDate"
                    type="date"
                    placeholder="开始日期"
                    size="small"
                    style="width: 110px;"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    @change="handleStartDateChange(scope.$index)"
                  />
                  <span>至</span>
                  <el-date-picker
                    v-model="scope.row.endDate"
                    type="date"
                    placeholder="结束日期"
                    size="small"
                    style="width: 110px;"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </div>
                <span v-else style="color: #C0C4CC;">-</span>
              </template>
            </el-table-column>

            <!-- 班级 -->
            <el-table-column label="班级" width="120">
              <template #default="scope">
                <el-select
                  v-model="scope.row.group"
                  size="small"
                  placeholder="请选择"
                  style="width: 100%;"
                >
                  <el-option label="班级" value="class" />
                  <el-option label="高级班级" value="advanced" />
                </el-select>
              </template>
            </el-table-column>

            <!-- 课程有效期 (按课时课程显示) -->
            <el-table-column label="课程有效期" width="150">
              <template #default="scope">
                <el-select
                  v-if="scope.row.chargeType === 'lesson'"
                  v-model="scope.row.validityType"
                  size="small"
                  placeholder="请选择"
                  style="width: 100%;"
                >
                  <el-option label="不设置" value="not_set" />
                  <el-option label="立即生效" value="immediate" />
                  <el-option label="第一次点名生效" value="first_attendance" />
                </el-select>
                <span v-else style="color: #C0C4CC;">-</span>
              </template>
            </el-table-column>

            <!-- 请假免扣次数 -->
            <el-table-column label="请假免扣次数" width="130" align="center">
              <template #default="scope">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px;">
                  <el-input-number
                    v-model="scope.row.leaveExemptCount"
                    :min="0"
                    :step="1"
                    size="small"
                    controls-position="right"
                    style="width: 60px;"
                  />
                  <span>次</span>
                </div>
              </template>
            </el-table-column>

            <!-- 直减/折扣 -->
            <el-table-column label="直减/折扣" width="140" align="right">
              <template #default="scope">
                <el-input-number
                  v-model="scope.row.discount"
                  :min="0"
                  :step="1"
                  :precision="2"
                  size="small"
                  placeholder="0"
                  controls-position="right"
                  style="width: 100%;"
                  @input="updateCourseAmount(scope.$index)"
                />
              </template>
            </el-table-column>

            <!-- 小计 -->
            <el-table-column label="小计" width="120" align="right" fixed="right">
              <template #default="scope">
                <span style="color: #E6A23C; font-weight: 600; font-size: 16px;">¥ {{ calculateSubtotal(scope.row) }}</span>
              </template>
            </el-table-column>

            <!-- 操作 -->
            <el-table-column label="操作" width="80" fixed="right" align="center">
              <template #default="scope">
                <el-button type="danger" link @click="removeCourse(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 其他信息区域 -->
        <div class="other-info-section">
          <div class="section-title">其他信息</div>

          <el-form :model="enrollForm" label-width="100px" class="enroll-detail-form">
            <!-- 缴办日期 -->
            <el-form-item label="缴办日期：">
              <el-date-picker
                v-model="enrollForm.enrollDate"
                type="date"
                placeholder="选择日期"
                style="width: 200px;"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>

            <!-- 业绩归属人 -->
            <el-form-item label="业绩归属人：">
              <div style="display: flex; align-items: center; gap: 10px;">
                <el-select v-model="enrollForm.performanceOwner" placeholder="业绩归属人" style="width: 150px;">
                  <el-option label="元" value="yuan" />
                  <el-option label="其他" value="other" />
                </el-select>

                <el-select v-model="enrollForm.performanceType" placeholder="绩效业绩" style="width: 150px;">
                  <el-option label="绩效业绩" value="performance" />
                </el-select>

                <el-input
                  v-model="enrollForm.performanceInput"
                  placeholder="请输入"
                  style="width: 100px;"
                />

                <el-link type="warning" :underline="false">创建</el-link>

                <el-button type="warning" text>+ 添加 (1/10)</el-button>
              </div>
            </el-form-item>

            <!-- 对应标签 -->
            <el-form-item label="对应标签：">
              <div style="display: flex; gap: 10px;">
                <el-checkbox-group v-model="enrollForm.tags">
                  <el-checkbox label="手续费已上传至上级账户" />
                  <el-checkbox label="上传在期限内" />
                  <el-checkbox label="图片/文件/手续费/png" />
                  <el-checkbox label="包含文件夹" />
                  <el-checkbox label="物流费用已计入20M" />
                </el-checkbox-group>
              </div>
            </el-form-item>

            <!-- 备注 -->
            <el-form-item label="备注：">
              <el-input
                v-model="enrollForm.remark"
                type="textarea"
                :rows="4"
                placeholder="请输入备注"
                style="width: 500px;"
              />
            </el-form-item>

            <!-- 附件 -->
            <el-form-item label="附件：">
              <div class="attachment-area">
                <el-button size="small">选择文件</el-button>
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                  支持扩展名: .jpg .png .pdf .doc .docx
                </span>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 底部汇总 -->
        <div class="enroll-summary">
          <div class="summary-left">
            <span class="summary-label">共 {{ enrollForm.courses.length }} 个项目</span>
          </div>
          <div class="summary-right">
            <span class="total-amount-label">应收金额:</span>
            <span class="total-amount-value">¥ {{ calculateTotalAmount() }}</span>
            <el-button @click="goBack" style="margin-left: 20px;">取消</el-button>
            <el-button type="warning" @click="handleConfirmEnroll">确认提交</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 选择课程弹窗 -->
    <el-dialog
      v-model="selectCourseDialogVisible"
      title="选择课程"
      width="800px"
      :close-on-click-modal="false"
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

    <!-- 选择物品弹窗 -->
    <el-dialog
      v-model="selectItemDialogVisible"
      title="选择物品"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
    >
      <!-- 搜索框 -->
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input
            v-model="itemSearchKeyword"
            placeholder="请输入物品名称"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="searchAvailableItems">搜索</el-button>
        </el-form-item>
      </el-form>

      <!-- 物品列表 -->
      <el-table
        :data="availableItemList"
        @expand-change="handleItemExpand"
        row-key="id"
        max-height="400"
      >
        <el-table-column type="expand">
          <template #default="props">
            <div style="padding: 0 50px;">
              <el-table
                :data="props.row.skus"
                border
                @selection-change="(selection) => handleSkuSelectionChange(selection, props.row)"
                :row-key="(row) => `${props.row.id}_${row.id}`"
              >
                <el-table-column type="selection" width="55" :reserve-selection="true" />
                <el-table-column label="规格组合" prop="specText" />
                <el-table-column label="单价" prop="price" width="120">
                  <template #default="scope">
                    ¥ {{ scope.row.price }}
                  </template>
                </el-table-column>
                <el-table-column label="库存" prop="stock" width="100" />
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="物品名称" prop="itemName" />
        <el-table-column label="库存" prop="totalStock" width="100" align="center">
          <template #default="scope">
            {{ scope.row.totalStock }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 底部已选提示 -->
      <div class="selection-footer" style="margin-top: 15px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
        <span>已选择: {{ selectedSkuList.length }} 项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectItemDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmSelectItem">确定了</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择费用弹窗 -->
    <el-dialog
      v-model="selectFeeDialogVisible"
      title="选择费用"
      width="600px"
      :close-on-click-modal="false"
      append-to-body
    >
      <!-- 搜索框 -->
      <el-input
        v-model="feeSearchKeyword"
        placeholder="请输入费用名称"
        clearable
        style="margin-bottom: 15px;"
      >
        <template #suffix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 费用列表表格 -->
      <el-table
        :data="filteredFeeList"
        border
        @selection-change="handleFeeSelectionChange"
        max-height="400px"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="费用名称" prop="feeName" min-width="200" />
        <el-table-column label="单价" prop="price" width="120" align="right">
          <template #default="scope">
            ¥ {{ scope.row.price.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <span class="total-text">共{{ availableFeeList.length }}条数据</span>
        <el-pagination
          v-model:current-page="feePagination.currentPage"
          v-model:page-size="feePagination.pageSize"
          :total="availableFeeList.length"
          :page-sizes="[10, 20, 50]"
          layout="prev, pager, next"
          @current-change="handleFeePageChange"
        />
      </div>

      <!-- 底部已选提示 -->
      <div class="selection-footer">
        <span>已选择: {{ selectedFees.length }}项</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectFeeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmSelectFee">选好了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="StudentEnroll">
import { ref, computed, onMounted } from 'vue';
import { Search, Edit } from '@element-plus/icons-vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();

// 学员信息
const studentInfo = ref({
  studentName: '张同学',
  phone: '186****2799'
});

// 报名表单
const enrollForm = ref({
  courses: [
    // 示例数据 - 按天收费(单价类型)
    {
      itemType: '课程',
      courseName: '数学启蒙',
      chargeType: 'day',
      selectedPriceOption: 'single_day',
      priceOptions: [
        { label: '单价(200元/天)', value: 'single_day', type: 'single', unitPrice: 200, quantity: 1, unit: '天' },
        { label: '24天(4800元24天)', value: 'package_24', type: 'package', unitPrice: 4800, quantity: 24, unit: '天' },
        { label: '48天(9600元48天)', value: 'package_48', type: 'package', unitPrice: 9600, quantity: 48, unit: '天' }
      ],
      canEditQuantity: true,
      quantity: 1,
      unit: '天',
      unitPrice: 200.00,
      giftQuantity: 0,
      leaveExemptCount: 0,  // 请假免扣次数
      startDate: '2025-11-05',
      endDate: '',
      group: 'class',
      discount: 0,
      subtotal: 0
    },
    // 示例数据 - 按月收费(套餐类型)
    {
      itemType: '课程',
      courseName: '钢琴课',
      chargeType: 'month',
      selectedPriceOption: 'package_24',
      priceOptions: [
        { label: '单价(1200元/月)', value: 'single_month', type: 'single', unitPrice: 1200, quantity: 1, unit: '月' },
        { label: '24月(4800元24月)', value: 'package_24', type: 'package', unitPrice: 4800, quantity: 2, unit: '月' },
        { label: '48月(9600元48月)', value: 'package_48', type: 'package', unitPrice: 9600, quantity: 4, unit: '月' }
      ],
      canEditQuantity: false,
      quantity: 2,
      unit: '月',
      unitPrice: 4800.00,
      giftQuantity: 0,
      leaveExemptCount: 0,
      startDate: '2025-11-05',
      endDate: '',
      group: 'class',
      discount: 1800,
      subtotal: 0
    },
    // 示例数据 - 按课时收费(单价类型)
    {
      itemType: '课程',
      courseName: '记忆训练',
      chargeType: 'lesson',
      selectedPriceOption: 'single_lesson',
      priceOptions: [
        { label: '单价(900元/月)', value: 'single_lesson', type: 'single', unitPrice: 900, quantity: 1, unit: '课时' },
        { label: '24课时(4800元24课时)', value: 'package_24', type: 'package', unitPrice: 4800, quantity: 24, unit: '课时' },
        { label: '48课时(9600元48课时)', value: 'package_48', type: 'package', unitPrice: 9600, quantity: 48, unit: '课时' }
      ],
      canEditQuantity: true,
      quantity: 1,
      unit: '课时',
      unitPrice: 900.00,
      giftQuantity: 0,
      leaveExemptCount: 0,
      validityType: 'not_set',  // 不设置、立即生效、第一次点名生效
      group: 'class',
      discount: 0,
      subtotal: 0
    }
  ],
  problemAmount: 6380,
  enrollDate: '2025-11-05',
  performanceOwner: '',
  performanceType: '',
  performanceInput: '',
  tags: [],
  remark: '',
  attachments: []
});



// 选择课程相关
const selectCourseDialogVisible = ref(false);
const courseSearchKeyword = ref('');
const selectedCourses = ref([]);
const coursePagination = ref({
  currentPage: 1,
  pageSize: 10
});

// 选择物品相关
const selectItemDialogVisible = ref(false);
const itemSearchKeyword = ref('');
const availableItemList = ref([]);
const selectedSkuList = ref([]); // 存储所有选中的SKU

// 选择费用相关
const selectFeeDialogVisible = ref(false);
const feeSearchKeyword = ref('');
const selectedFees = ref([]);
const feePagination = ref({
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

// 可选费用列表(模拟数据)
const availableFeeList = ref([
  { id: 1, feeName: '银泰店蓝球1小时', price: 30.00 },
  { id: 2, feeName: '大悦城蓝球1小时', price: 30.00 },
  { id: 3, feeName: '天府店蓝球1小时', price: 30.00 },
  { id: 4, feeName: '教材费', price: 50.00 },
  { id: 5, feeName: '服装费', price: 80.00 },
  { id: 6, feeName: '保险费', price: 100.00 },
  { id: 7, feeName: '活动费', price: 120.00 },
  { id: 8, feeName: '考级费', price: 200.00 }
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

// 过滤后的费用列表(用于分页显示)
const filteredFeeList = computed(() => {
  let list = availableFeeList.value;

  // 搜索过滤
  if (feeSearchKeyword.value) {
    list = list.filter(fee =>
      fee.feeName.toLowerCase().includes(feeSearchKeyword.value.toLowerCase())
    );
  }

  // 分页
  const start = (feePagination.value.currentPage - 1) * feePagination.value.pageSize;
  const end = start + feePagination.value.pageSize;
  return list.slice(start, end);
});

/** 返回 */
function goBack() {
  router.back();
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
      // 根据课程定价标准判断收费类型
      let chargeType = 'lesson'; // 默认按课时
      let unit = '课时';

      if (course.priceStandard.includes('月')) {
        chargeType = 'month';
        unit = '月';
      } else if (course.priceStandard.includes('天')) {
        chargeType = 'day';
        unit = '天';
      }

      // 创建定价选项列表(模拟数据,实际应该从API获取)
      const priceOptions = [
        { label: `单价(200元/${unit})`, value: 'single', type: 'single', unitPrice: 200, quantity: 1, unit: unit },
        { label: `24${unit}(4800元24${unit})`, value: 'package_24', type: 'package', unitPrice: 4800, quantity: 24, unit: unit },
        { label: `48${unit}(9600元48${unit})`, value: 'package_48', type: 'package', unitPrice: 9600, quantity: 48, unit: unit }
      ];

      // 创建课程对象
      const newCourse = {
        itemType: '课程',
        courseId: course.id,
        courseName: course.courseName,
        courseType: course.courseType,
        chargeType: chargeType,
        selectedPriceOption: 'single',  // 默认选择单价
        priceOptions: priceOptions,
        canEditQuantity: true,  // 单价类型可以编辑数量
        quantity: 1,
        unit: unit,
        unitPrice: 200,
        giftQuantity: 0,
        leaveExemptCount: 0,  // 请假免扣次数
        discount: 0,
        subtotal: 200
      };

      // 根据收费类型添加特定字段
      if (chargeType === 'month' || chargeType === 'day') {
        // 按月/按日收费
        newCourse.startDate = '';
        newCourse.endDate = '';
        newCourse.group = '';
      } else if (chargeType === 'lesson') {
        // 按课时收费
        newCourse.validityType = 'not_set';  // 不设置、立即生效、第一次点名生效
        newCourse.group = '';
      }

      enrollForm.value.courses.push(newCourse);
    }
  });

  selectCourseDialogVisible.value = false;
  ElMessage.success(`已添加 ${selectedCourses.value.length} 个课程`);
}

/** 打开选择物品对话框 */
function handleSelectItem() {
  selectItemDialogVisible.value = true;
  selectedSkuList.value = []; // 清空之前的选择
  loadAvailableItems();
}

/** 加载可选物品列表 */
function loadAvailableItems() {
  // 模拟物品数据(实际应该从API获取)
  availableItemList.value = [
    {
      id: 1,
      itemName: '加拿大骑羽球',
      totalStock: 56,
      skus: [
        { id: 1, specText: 'xl: 白色', price: 150, stock: 10 },
        { id: 2, specText: 'xl: 黑色', price: 150, stock: 10 },
        { id: 3, specText: 'm: 白色', price: 150, stock: 10 },
        { id: 4, specText: 'm: 黑色', price: 150, stock: 10 },
        { id: 5, specText: 'l: 白色', price: 150, stock: 8 },
        { id: 6, specText: 'l: 黑色', price: 150, stock: 8 }
      ]
    },
    {
      id: 2,
      itemName: '手包',
      totalStock: 2,
      skus: [
        { id: 7, specText: '默认规格', price: 200, stock: 2 }
      ]
    },
    {
      id: 3,
      itemName: '篮球',
      totalStock: 15,
      skus: [
        { id: 8, specText: '7号球', price: 180, stock: 8 },
        { id: 9, specText: '5号球', price: 150, stock: 7 }
      ]
    }
  ];
}

/** 搜索可选物品 */
function searchAvailableItems() {
  loadAvailableItems();
  if (itemSearchKeyword.value) {
    availableItemList.value = availableItemList.value.filter(item =>
      item.itemName.includes(itemSearchKeyword.value)
    );
  }
}

/** 物品展开变化 */
function handleItemExpand(row, expandedRows) {
  // 可以在这里处理展开逻辑
}

/** SKU选择变化处理 */
function handleSkuSelectionChange(selection, parentItem) {
  // 移除该物品下之前选中的SKU
  selectedSkuList.value = selectedSkuList.value.filter(
    item => item.parentItemId !== parentItem.id
  );

  // 添加新选中的SKU
  const newSelections = selection.map(sku => ({
    parentItemId: parentItem.id,
    itemName: parentItem.itemName,
    specText: sku.specText,
    price: sku.price,
    quantity: 1, // 默认数量为1
    stock: sku.stock,
    skuId: sku.id
  }));

  selectedSkuList.value.push(...newSelections);
}

/** 确认选择物品 */
function handleConfirmSelectItem() {
  if (selectedSkuList.value.length === 0) {
    ElMessage.warning('请至少选择一个物品');
    return;
  }

  // 将选中的SKU添加到课程列表中
  selectedSkuList.value.forEach(sku => {
    const newItem = {
      itemType: '物品',
      itemId: sku.parentItemId,
      courseName: `${sku.itemName} - ${sku.specText}`,
      chargeType: 'item', // 物品类型
      selectedPriceOption: 'single',
      priceOptions: [
        { label: `单价(${sku.price}元/个)`, value: 'single', type: 'single', unitPrice: sku.price, quantity: 1, unit: '个' }
      ],
      canEditQuantity: true,
      quantity: sku.quantity,
      unit: '个',
      unitPrice: sku.price,
      giftQuantity: 0,
      leaveExemptCount: 0,
      group: '',
      discount: 0,
      subtotal: sku.price * sku.quantity
    };

    enrollForm.value.courses.push(newItem);
  });

  selectItemDialogVisible.value = false;
  ElMessage.success(`已添加 ${selectedSkuList.value.length} 个物品`);
}

/** 打开选择费用对话框 */
function handleSelectFee() {
  selectFeeDialogVisible.value = true;
  selectedFees.value = [];
}

/** 费用选择变化 */
function handleFeeSelectionChange(selection) {
  selectedFees.value = selection;
}

/** 费用分页变化 */
function handleFeePageChange(page) {
  feePagination.value.currentPage = page;
}

/** 确认选择费用 */
function handleConfirmSelectFee() {
  if (selectedFees.value.length === 0) {
    ElMessage.warning('请至少选择一个费用');
    return;
  }

  // 将选中的费用添加到课程列表中
  selectedFees.value.forEach(fee => {
    const newFee = {
      itemType: '费用',
      feeId: fee.id,
      courseName: fee.feeName,
      chargeType: 'fee', // 费用类型
      selectedPriceOption: 'single',
      priceOptions: [
        { label: `单价(${fee.price}元/次)`, value: 'single', type: 'single', unitPrice: fee.price, quantity: 1, unit: '次' }
      ],
      canEditQuantity: true,
      quantity: 1,
      unit: '次',
      unitPrice: fee.price,
      giftQuantity: 0,
      leaveExemptCount: 0,
      group: '',
      discount: 0,
      subtotal: fee.price
    };

    enrollForm.value.courses.push(newFee);
  });

  selectFeeDialogVisible.value = false;
  ElMessage.success(`已添加 ${selectedFees.value.length} 个费用`);
}

/** 处理定价标准变化 */
function handlePriceStandardChange(index) {
  const course = enrollForm.value.courses[index];

  // 查找选中的定价选项
  const selectedOption = course.priceOptions.find(
    option => option.value === course.selectedPriceOption
  );

  if (!selectedOption) {
    return;
  }

  // 更新课程信息
  course.unit = selectedOption.unit;
  course.unitPrice = selectedOption.unitPrice;

  // 判断是否可以编辑购买数量
  if (selectedOption.type === 'single') {
    // 单价类型: 可以编辑数量
    course.canEditQuantity = true;
    // 如果当前数量为0或未设置,设置为1
    if (!course.quantity || course.quantity === 0) {
      course.quantity = 1;
    }
  } else if (selectedOption.type === 'package') {
    // 套餐类型: 不可编辑数量,使用套餐固定数量
    course.canEditQuantity = false;
    course.quantity = selectedOption.quantity;
  }

  // 重新计算金额
  updateCourseAmount(index);

  // 重新计算结束日期(如果是按天/按月收费)
  if (course.chargeType === 'day' || course.chargeType === 'month') {
    calculateEndDate(index, true);
  }
}

/** 计算结束日期(辅助函数) */
function calculateEndDate(index, autoUpdate = true) {
  const course = enrollForm.value.courses[index];

  // 只有按月或按日收费的课程才需要计算结束日期
  if (course.chargeType !== 'month' && course.chargeType !== 'day') {
    return;
  }

  // 检查是否有开始日期
  if (!course.startDate) {
    if (autoUpdate) {
      course.endDate = '';
    }
    return;
  }

  // 计算总数量 = 购买数量 + 赠送数量
  const totalQuantity = (course.quantity || 0) + (course.giftQuantity || 0);

  if (totalQuantity <= 0) {
    if (autoUpdate) {
      course.endDate = '';
    }
    return;
  }

  // 解析开始日期
  const startDate = new Date(course.startDate);

  // 根据收费类型计算结束日期
  let endDate = new Date(startDate);

  if (course.chargeType === 'day') {
    // 按天: 结束日期 = 开始日期 + (总数量 - 1)天
    endDate.setDate(startDate.getDate() + totalQuantity - 1);
  } else if (course.chargeType === 'month') {
    // 按月: 结束日期 = 开始日期 + 总数量月 - 1天
    endDate.setMonth(startDate.getMonth() + totalQuantity);
    endDate.setDate(endDate.getDate() - 1);
  }

  // 格式化结束日期为 YYYY-MM-DD
  const year = endDate.getFullYear();
  const month = String(endDate.getMonth() + 1).padStart(2, '0');
  const day = String(endDate.getDate()).padStart(2, '0');
  const calculatedEndDate = `${year}-${month}-${day}`;

  // 只有在autoUpdate为true时才自动更新结束日期
  if (autoUpdate) {
    course.endDate = calculatedEndDate;
  }

  return calculatedEndDate;
}

/** 处理开始日期变化 */
function handleStartDateChange(index) {
  // 自动计算并更新结束日期
  calculateEndDate(index, true);
}

/** 处理购买数量变化 */
function handleQuantityChange(index) {
  // 更新金额
  updateCourseAmount(index);
  // 自动计算并更新结束日期
  calculateEndDate(index, true);
}

/** 处理赠送数量变化 */
function handleGiftQuantityChange(index) {
  // 自动计算并更新结束日期
  calculateEndDate(index, true);
}

/** 计算单个课程的小计 */
function calculateSubtotal(course) {
  // 计算小计 = 单价 × 数量 - 直减/折扣
  const totalBeforeDiscount = (course.unitPrice || 0) * (course.quantity || 0);
  const discountAmount = parseFloat(course.discount) || 0;
  let subtotal = totalBeforeDiscount - discountAmount;

  // 确保小计不为负数
  if (subtotal < 0) {
    subtotal = 0;
  }

  // 更新course对象的subtotal(用于总计计算)
  course.subtotal = subtotal;

  return subtotal.toFixed(2);
}

/** 更新课程金额 */
function updateCourseAmount(index) {
  // 触发重新计算(通过访问course对象来触发响应式更新)
  const course = enrollForm.value.courses[index];
  calculateSubtotal(course);
}

/** 移除课程 */
function removeCourse(index) {
  enrollForm.value.courses.splice(index, 1);
}

/** 计算总金额 */
function calculateTotalAmount() {
  return enrollForm.value.courses.reduce((total, course) => {
    // 使用calculateSubtotal确保获取最新的小计值
    const subtotal = parseFloat(calculateSubtotal(course));
    return total + subtotal;
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

  // 返回学员详情页
  setTimeout(() => {
    goBack();
  }, 1000);
}

/** 获取学员信息 */
function getStudentInfo() {
  const studentId = route.params.id;
  // 这里应该调用API获取学员信息
  // 暂时使用模拟数据
  studentInfo.value = {
    studentName: '黄同学',
    phone: '111****1111'
  };
}

onMounted(() => {
  getStudentInfo();

  // 初始化所有课程的结束日期
  enrollForm.value.courses.forEach((course, index) => {
    if (course.chargeType === 'month' || course.chargeType === 'day') {
      calculateEndDate(index);
    }
  });
});
</script>

<style scoped lang="scss">
.student-enroll {
  // 报名内容样式
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

    .empty-state-inline {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 0;
      margin-top: 15px;
      border: 1px dashed #DCDFE6;
      border-radius: 4px;
      background: #FAFAFA;

      .empty-icon {
        font-size: 48px;
        margin-bottom: 12px;
      }

      .empty-text {
        font-size: 14px;
        color: #909399;
      }
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

      .enroll-detail-form {
        .el-form-item {
          margin-bottom: 20px;
        }

        .attachment-area {
          display: flex;
          align-items: center;
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

      .summary-left {
        display: flex;
        align-items: center;

        .summary-label {
          font-size: 14px;
          color: #606266;
        }
      }

      .summary-right {
        display: flex;
        align-items: center;
        gap: 10px;

        .total-amount-label {
          font-size: 14px;
          color: #606266;
        }

        .total-amount-value {
          font-size: 20px;
          font-weight: 600;
          color: #E6A23C;
          margin-right: 10px;
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

