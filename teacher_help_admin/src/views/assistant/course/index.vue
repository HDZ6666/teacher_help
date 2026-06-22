<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="课程" name="course">
        <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="搜索课程" prop="courseName">
            <el-input
              v-model="queryParams.courseName"
              placeholder="请输入课程名称"
              clearable
              style="width: 260px"
              @keyup.enter="handleQuery"
            />
          </el-form-item>
          <el-form-item label="课程类型" prop="courseType">
            <el-checkbox-group v-model="courseTypeFilter" @change="handleTypeFilterChange">
              <el-checkbox label="one_to_many">一对多</el-checkbox>
              <el-checkbox label="one_to_one">一对一</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="课程状态" prop="status">
            <el-checkbox-group v-model="statusFilter" @change="handleStatusFilterChange">
              <el-checkbox :label="1">启用</el-checkbox>
              <el-checkbox :label="0">停用</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['teach:course:add']">
              新建课程
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleBatchAdd" v-hasPermi="['teach:course:add']">
              批量新建课程
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="danger"
              plain
              icon="Delete"
              :disabled="multiple"
              @click="handleDelete"
              v-hasPermi="['teach:course:remove']"
            >
              批量删除
            </el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
        </el-row>

        <el-table v-loading="loading" :data="courseList" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="课程名称" prop="courseName" min-width="180">
            <template #default="scope">
              <div class="course-name-cell">
                <span class="course-color-dot" :style="{ backgroundColor: scope.row.scheduleColor || '#409EFF' }"></span>
                <span>{{ scope.row.courseName }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="类型" prop="courseTypeName" width="120" align="center" />
          <el-table-column label="收费方式" prop="chargeTypeText" width="150" align="center" />
          <el-table-column label="定价标准" prop="priceStandard" min-width="260">
            <template #default="scope">
              <div v-if="scope.row.priceLines && scope.row.priceLines.length" class="price-lines">
                <span v-for="line in scope.row.priceLines" :key="line">{{ line }}</span>
              </div>
              <span v-else class="muted">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="在读学员数" prop="studentCount" width="120" align="center" />
          <el-table-column label="启用状态" prop="status" width="120" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.status"
                :active-value="1"
                :inactive-value="0"
                @change="value => handleStatusChange(scope.row, value)"
                v-hasPermi="['teach:course:edit']"
              />
            </template>
          </el-table-column>
          <el-table-column label="线上售卖" prop="onlineSale" width="120" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.onlineSale === 1" type="success">已售卖</el-tag>
              <span v-else class="muted">未售卖</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['teach:course:edit']">
                编辑
              </el-button>
              <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['teach:course:remove']">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </el-tab-pane>

      <el-tab-pane label="套餐" name="package">
        <el-form :model="packageQueryParams" ref="packageQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="搜索套餐" prop="packageName">
            <el-input
              v-model="packageQueryParams.packageName"
              placeholder="请输入套餐名称"
              clearable
              style="width: 260px"
              @keyup.enter="handlePackageQuery"
            />
          </el-form-item>
          <el-form-item label="启用状态" prop="status">
            <el-checkbox-group v-model="packageStatusFilter" @change="handlePackageStatusFilterChange">
              <el-checkbox :label="1">启用</el-checkbox>
              <el-checkbox :label="0">停用</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handlePackageQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetPackageQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handlePackageAdd" v-hasPermi="['teach:course:add']">
              添加套餐
            </el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="danger"
              plain
              icon="Delete"
              :disabled="packageMultiple"
              @click="handlePackageDelete"
              v-hasPermi="['teach:course:remove']"
            >
              批量删除
            </el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getActiveList"></right-toolbar>
        </el-row>

        <el-table v-loading="packageLoading" :data="packageList" @selection-change="handlePackageSelectionChange">
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="套餐名称" prop="packageName" min-width="180" />
          <el-table-column label="套餐价" prop="totalPrice" width="140" align="center">
            <template #default="scope">¥ {{ formatMoney(scope.row.totalPrice) }}</template>
          </el-table-column>
          <el-table-column label="套餐内容" prop="itemSummary" min-width="260" show-overflow-tooltip>
            <template #default="scope">
              <span v-if="scope.row.itemSummary">{{ scope.row.itemSummary }}</span>
              <span v-else class="muted">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="明细数量" prop="itemCount" width="100" align="center" />
          <el-table-column label="启用状态" prop="status" width="120" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.status"
                :active-value="1"
                :inactive-value="0"
                @change="value => handlePackageStatusChange(scope.row, value)"
                v-hasPermi="['teach:course:edit']"
              />
            </template>
          </el-table-column>
          <el-table-column label="线上售卖" prop="onlineSale" width="120" align="center">
            <template #default="scope">
              <el-tag v-if="scope.row.onlineSale === 1" type="success">已售卖</el-tag>
              <span v-else class="muted">未售卖</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="scope">
              <el-button
                link
                type="primary"
                icon="Edit"
                @click="handlePackageUpdate(scope.row)"
                v-hasPermi="['teach:course:edit']"
              >
                编辑
              </el-button>
              <el-button
                link
                type="danger"
                icon="Delete"
                @click="handlePackageDelete(scope.row)"
                v-hasPermi="['teach:course:remove']"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="packageTableTotal > 0"
          :total="packageTableTotal"
          v-model:page="packageQueryParams.pageNum"
          v-model:limit="packageQueryParams.pageSize"
          @pagination="getPackageList"
        />
      </el-tab-pane>
    </el-tabs>

    <el-dialog :title="title" v-model="open" width="980px" append-to-body destroy-on-close>
      <el-form ref="courseFormRef" :model="form" :rules="rules" label-width="104px">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="课程名称" prop="courseName">
              <el-input v-model="form.courseName" placeholder="请输入" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程类型" prop="courseType">
              <el-radio-group v-model="form.courseType">
                <el-radio label="one_to_many">一对多</el-radio>
                <el-radio label="one_to_one">一对一</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="8">
            <el-form-item label="年级" prop="grade">
              <el-select v-model="form.grade" placeholder="请选择" clearable>
                <el-option v-for="item in gradeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="科目" prop="subject">
              <el-select v-model="form.subject" placeholder="请选择" clearable>
                <el-option v-for="item in subjectOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学期" prop="semester">
              <el-select v-model="form.semester" placeholder="请选择" clearable>
                <el-option v-for="item in semesterOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="课表颜色">
              <div class="color-swatches">
                <button
                  v-for="color in colorOptions"
                  :key="color"
                  class="color-swatch"
                  type="button"
                  :class="{ active: form.scheduleColor === color }"
                  :style="{ backgroundColor: color }"
                  @click="form.scheduleColor = color"
                ></button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启用状态">
              <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="线上售卖">
              <el-switch v-model="form.onlineSale" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">收费方式</el-divider>
        <div v-for="section in chargeSections" :key="section.type" class="charge-section">
          <div class="charge-title">
            <span>{{ section.label }}</span>
            <el-switch
              v-model="form[section.enabledKey]"
              :active-value="true"
              :inactive-value="false"
              @change="value => handleChargeToggle(section, value)"
            />
          </div>
          <div v-if="form[section.enabledKey]" class="charge-body">
            <template v-if="section.type === 'class'">
              <el-form-item label="扣课时规则">
                <el-radio-group v-model="form.classDeductRule">
                  <el-radio label="deduct">扣</el-radio>
                  <el-radio label="none">不扣</el-radio>
                  <el-radio label="part_free">部分免扣</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="未到是否扣课时">
                <el-radio-group v-model="form.classAbsenceRule">
                  <el-radio label="deduct">扣</el-radio>
                  <el-radio label="none">不扣</el-radio>
                </el-radio-group>
              </el-form-item>
            </template>
            <el-alert
              title="为方便报名时灵活选择购买数量，建议保留一条数量为 1 的单价价目。"
              type="warning"
              show-icon
              :closable="false"
              class="price-alert"
            />
            <el-table :data="form[section.listKey]" border>
              <el-table-column label="名称" min-width="160">
                <template #default="scope">
                  <el-input v-model="scope.row.priceName" placeholder="单价" maxlength="100" />
                </template>
              </el-table-column>
              <el-table-column :label="section.quantityLabel" width="160">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" :max="999" controls-position="right" />
                </template>
              </el-table-column>
              <el-table-column label="总价(元)" width="170">
                <template #default="scope">
                  <el-input-number
                    v-model="scope.row.totalPrice"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                    placeholder="请输入"
                  />
                </template>
              </el-table-column>
              <el-table-column :label="section.unitPriceLabel" width="170" align="center">
                <template #default="scope">
                  {{ calcUnitPrice(scope.row) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="90" align="center">
                <template #default="scope">
                  <el-button link type="danger" @click="removePriceRow(section, scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="add-price">
              <el-button
                link
                type="primary"
                icon="Plus"
                :disabled="form[section.listKey].length >= 10"
                @click="addPriceRow(section)"
              >
                添加({{ form[section.listKey].length }}/10)
              </el-button>
            </div>
          </div>
        </div>

        <el-divider content-position="left">其他信息</el-divider>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog title="批量新建课程" v-model="batchOpen" width="1100px" append-to-body destroy-on-close>
      <el-table :data="batchForm.courses" border>
        <el-table-column label="课程名称" min-width="170">
          <template #default="scope">
            <el-input v-model="scope.row.courseName" placeholder="请输入课程名称" maxlength="100" />
          </template>
        </el-table-column>
        <el-table-column label="课程类型" width="140">
          <template #default="scope">
            <el-select v-model="scope.row.courseType" placeholder="请选择">
              <el-option label="一对多" value="one_to_many" />
              <el-option label="一对一" value="one_to_one" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="收费方式" width="130">
          <template #default="scope">
            <el-select v-model="scope.row.chargeType" placeholder="请选择">
              <el-option label="按课时" value="class" />
              <el-option label="按月" value="month" />
              <el-option label="按天" value="day" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="定价名称" min-width="140">
          <template #default="scope">
            <el-input v-model="scope.row.priceName" placeholder="单价" maxlength="100" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="130">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="1" :max="999" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="总价(元)" width="150">
          <template #default="scope">
            <el-input-number
              v-model="scope.row.totalPrice"
              :min="0"
              :precision="2"
              controls-position="right"
              placeholder="请输入"
            />
          </template>
        </el-table-column>
        <el-table-column label="颜色" width="110">
          <template #default="scope">
            <el-color-picker v-model="scope.row.scheduleColor" :predefine="colorOptions" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="scope">
            <el-button
              link
              type="danger"
              :disabled="batchForm.courses.length <= 1"
              @click="removeBatchCourseRow(scope.$index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="batch-actions">
        <el-button link type="primary" icon="Plus" :disabled="batchForm.courses.length >= 20" @click="addBatchCourseRow">
          添加课程({{ batchForm.courses.length }}/20)
        </el-button>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchOpen = false">取消</el-button>
          <el-button type="primary" :loading="batchSubmitLoading" @click="submitBatchForm">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog :title="packageTitle" v-model="packageOpen" width="1180px" append-to-body destroy-on-close>
      <el-form ref="packageFormRef" :model="packageForm" :rules="packageRules" label-width="96px">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="套餐名称" prop="packageName">
              <el-input v-model="packageForm.packageName" placeholder="请输入套餐名称" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启用状态">
              <el-switch v-model="packageForm.status" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="线上售卖">
              <el-switch v-model="packageForm.onlineSale" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">套餐明细</el-divider>
        <div class="package-toolbar">
          <el-button type="primary" plain icon="Plus" @click="openSelector('course')">选择课程</el-button>
          <el-button type="primary" plain icon="Plus" @click="openSelector('item')">选择物品</el-button>
          <el-button type="primary" plain icon="Plus" @click="openSelector('fee')">选择费用</el-button>
        </div>
        <el-table :data="packageForm.items" border class="package-item-table">
          <el-table-column label="购买项目" prop="itemName" min-width="150">
            <template #default="scope">
              <el-tag class="mr5" size="small" :type="packageTypeTag(scope.row.itemType)">
                {{ packageTypeName(scope.row.itemType) }}
              </el-tag>
              <span>{{ scope.row.itemName }}</span>
            </template>
          </el-table-column>
          <el-table-column label="定价标准" min-width="190">
            <template #default="scope">
              <el-select
                v-if="scope.row.itemType === 'course'"
                v-model="scope.row.specId"
                placeholder="请选择"
                @change="value => handlePackageSpecChange(scope.row, value)"
              >
                <el-option
                  v-for="price in scope.row.priceOptions"
                  :key="price.id"
                  :label="price.displayText"
                  :value="price.id"
                />
              </el-select>
              <span v-else>{{ scope.row.specName || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="购买数量" width="150">
            <template #default="scope">
              <div class="quantity-cell">
                <el-input-number
                  v-model="scope.row.quantity"
                  :min="1"
                  :max="999"
                  controls-position="right"
                  @change="refreshPackageItem(scope.row)"
                />
                <span>{{ scope.row.unit }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="总价" width="120" align="center">
            <template #default="scope">¥ {{ formatMoney(scope.row.totalPrice) }}</template>
          </el-table-column>
          <el-table-column label="请假免扣次数" width="150">
            <template #default="scope">
              <el-input-number
                v-if="scope.row.itemType === 'course'"
                v-model="scope.row.leaveFreeQuantity"
                :min="0"
                :max="999"
                controls-position="right"
              />
              <span v-else class="muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="赠送数量" width="150">
            <template #default="scope">
              <div class="quantity-cell">
                <el-input-number
                  v-model="scope.row.giftQuantity"
                  :min="0"
                  :max="999"
                  controls-position="right"
                />
                <span>{{ scope.row.unit }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="直减/折扣" width="210">
            <template #default="scope">
              <div class="discount-cell">
                <el-select
                  v-model="scope.row.discountType"
                  @change="refreshPackageItem(scope.row)"
                >
                  <el-option label="直减" value="reduce" />
                  <el-option label="折扣" value="discount" />
                </el-select>
                <el-input-number
                  v-model="scope.row.discountValue"
                  :min="0"
                  :precision="2"
                  controls-position="right"
                  @change="refreshPackageItem(scope.row)"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="小计" width="150">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.subtotalPrice"
                :min="0"
                :precision="2"
                controls-position="right"
                @change="refreshPackageTotal"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="scope">
              <el-button link type="danger" @click="removePackageItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="package-total">
          套餐价：
          <span>¥ {{ formatMoney(packageTotalPrice) }}</span>
        </div>
        <el-divider content-position="left">其他信息</el-divider>
        <el-form-item label="备注">
          <el-input v-model="packageForm.remark" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="packageOpen = false">取消</el-button>
          <el-button type="primary" :loading="packageSubmitLoading" @click="submitPackageForm">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog :title="selectorTitle" v-model="selectorOpen" width="860px" append-to-body destroy-on-close>
      <div class="selector-header">
        <el-input
          v-model="selectorKeyword"
          :placeholder="selectorPlaceholder"
          clearable
          style="width: 280px"
          @keyup.enter="loadSelectorOptions"
        >
          <template #suffix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" icon="Search" @click="loadSelectorOptions">搜索</el-button>
        <span class="selected-count">已选：{{ selectorSelection.length }} 项</span>
      </div>

      <el-table
        ref="selectorTableRef"
        v-loading="selectorLoading"
        :data="selectorOptions"
        row-key="selectorKey"
        @selection-change="handleSelectorSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <template v-if="selectorType === 'course'">
          <el-table-column label="课程名称" prop="courseName" min-width="180" />
          <el-table-column label="课程类型" prop="courseType" width="120" align="center" />
          <el-table-column label="定价标准" prop="priceStandard" min-width="240" show-overflow-tooltip />
        </template>
        <template v-else-if="selectorType === 'item'">
          <el-table-column label="物品名称" prop="itemName" min-width="180" />
          <el-table-column label="单价" prop="priceRange" width="160" align="center" />
          <el-table-column label="库存" prop="availableStock" width="120" align="center">
            <template #default="scope">
              <span :class="{ 'danger-text': Number(scope.row.availableStock || 0) < 0 }">
                {{ scope.row.availableStock || 0 }}
              </span>
            </template>
          </el-table-column>
        </template>
        <template v-else>
          <el-table-column label="费用名称" prop="feeName" min-width="220" />
          <el-table-column label="单价" prop="amount" width="160" align="center">
            <template #default="scope">¥ {{ formatMoney(scope.row.amount) }}</template>
          </el-table-column>
          <el-table-column label="绑定课程" prop="courseName" min-width="220" show-overflow-tooltip />
        </template>
      </el-table>

      <template #footer>
        <div class="dialog-footer selector-footer">
          <span>已选择：{{ selectorSelection.length }} 项</span>
          <div>
            <el-button @click="selectorOpen = false">取消</el-button>
            <el-button type="primary" @click="confirmSelector">选好了</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantCourse">
import { computed, getCurrentInstance, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import {
  addCourse,
  addCoursePackage,
  batchAddCourse,
  changeCoursePackageStatus,
  changeCourseStatus,
  delCoursePackage,
  delCourse,
  getCourse,
  getCoursePackage,
  listCourse,
  listCourseOptions,
  listCoursePackage,
  updateCoursePackage,
  updateCourse
} from '@/api/assistant/course'
import { listAvailableItems, listFee } from '@/api/assistant/inventory'

const { proxy } = getCurrentInstance()

const activeTab = ref('course')
const showSearch = ref(true)
const loading = ref(false)
const submitLoading = ref(false)
const batchSubmitLoading = ref(false)
const open = ref(false)
const batchOpen = ref(false)
const title = ref('')
const courseList = ref([])
const packageList = ref([])
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const courseTypeFilter = ref([])
const statusFilter = ref([1])
const courseFormRef = ref(null)
const packageLoading = ref(false)
const packageSubmitLoading = ref(false)
const packageOpen = ref(false)
const packageTitle = ref('')
const packageTableTotal = ref(0)
const packageIds = ref([])
const packageMultiple = ref(true)
const packageStatusFilter = ref([1])
const packageFormRef = ref(null)
const selectorOpen = ref(false)
const selectorType = ref('course')
const selectorKeyword = ref('')
const selectorLoading = ref(false)
const selectorOptions = ref([])
const selectorSelection = ref([])
const selectorTableRef = ref(null)

const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  courseName: '',
  courseType: '',
  status: 1
})

const packageQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  packageName: '',
  status: 1
})

const gradeOptions = [
  { label: '一年级', value: '1' },
  { label: '二年级', value: '2' },
  { label: '三年级', value: '3' },
  { label: '四年级', value: '4' },
  { label: '五年级', value: '5' },
  { label: '六年级', value: '6' },
  { label: '初一', value: '7' },
  { label: '初二', value: '8' },
  { label: '初三', value: '9' },
  { label: '高一', value: '10' },
  { label: '高二', value: '11' },
  { label: '高三', value: '12' }
]
const subjectOptions = [
  { label: '语文', value: '1' },
  { label: '数学', value: '2' },
  { label: '英语', value: '3' },
  { label: '物理', value: '4' },
  { label: '化学', value: '5' },
  { label: '生物', value: '6' },
  { label: '政治', value: '7' },
  { label: '历史', value: '8' },
  { label: '地理', value: '9' }
]
const semesterOptions = [
  { label: '春季', value: '1' },
  { label: '暑假', value: '2' },
  { label: '秋季', value: '3' },
  { label: '寒假', value: '4' }
]
const colorOptions = ['#409EFF', '#F59A23', '#67C23A', '#36CFC9', '#F56C6C', '#9254DE', '#909399']
const chargeSections = [
  {
    type: 'class',
    label: '按课时收费',
    enabledKey: 'chargeByClass',
    listKey: 'classPrices',
    quantityLabel: '数量(课时)',
    unitPriceLabel: '单价(元/课时)'
  },
  {
    type: 'month',
    label: '按月收费',
    enabledKey: 'chargeByMonth',
    listKey: 'monthPrices',
    quantityLabel: '数量(月)',
    unitPriceLabel: '单价(元/月)'
  },
  {
    type: 'day',
    label: '按天收费',
    enabledKey: 'chargeByDay',
    listKey: 'dayPrices',
    quantityLabel: '数量(天)',
    unitPriceLabel: '单价(元/天)'
  }
]

const rules = {
  courseName: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  courseType: [{ required: true, message: '请选择课程类型', trigger: 'change' }]
}
const packageRules = {
  packageName: [{ required: true, message: '请输入套餐名称', trigger: 'blur' }]
}

const selectorMeta = {
  course: {
    title: '选择课程',
    placeholder: '请输入课程名称'
  },
  item: {
    title: '选择物品',
    placeholder: '请输入物品名称'
  },
  fee: {
    title: '选择费用',
    placeholder: '请输入费用名称'
  }
}

const selectorTitle = computed(() => selectorMeta[selectorType.value].title)
const selectorPlaceholder = computed(() => selectorMeta[selectorType.value].placeholder)
const packageTotalPrice = computed(() => {
  return packageForm.value.items.reduce((totalPrice, item) => totalPrice + Number(item.subtotalPrice || 0), 0)
})

function defaultPrice(chargeType) {
  return {
    chargeType,
    priceName: '单价',
    quantity: 1,
    totalPrice: null,
    unitPrice: null,
    status: 1
  }
}

function defaultForm() {
  return {
    id: null,
    courseNo: '',
    courseName: '',
    courseType: 'one_to_many',
    scheduleColor: '#409EFF',
    grade: '',
    gradeLabel: '',
    subject: '',
    subjectLabel: '',
    semester: '',
    semesterLabel: '',
    studentCount: 0,
    onlineSale: 0,
    status: 1,
    chargeByClass: true,
    chargeByMonth: false,
    chargeByDay: false,
    classDeductRule: 'none',
    classAbsenceRule: 'deduct',
    classPrices: [defaultPrice('class')],
    monthPrices: [],
    dayPrices: [],
    remark: ''
  }
}

const form = ref(defaultForm())

function defaultPackageForm() {
  return {
    id: null,
    packageNo: '',
    packageName: '',
    totalPrice: 0,
    onlineSale: 0,
    status: 1,
    items: [],
    remark: ''
  }
}

const packageForm = ref(defaultPackageForm())

function defaultBatchCourseRow() {
  return {
    courseName: '',
    courseType: 'one_to_many',
    chargeType: 'class',
    priceName: '单价',
    quantity: 1,
    totalPrice: null,
    scheduleColor: '#409EFF',
    status: 1,
    onlineSale: 0
  }
}

function defaultBatchForm() {
  return {
    courses: [defaultBatchCourseRow(), defaultBatchCourseRow(), defaultBatchCourseRow()]
  }
}

const batchForm = ref(defaultBatchForm())

function cleanQuery(query) {
  const result = {}
  Object.keys(query || {}).forEach(key => {
    const value = query[key]
    if (value !== '' && value !== undefined && value !== null) {
      result[key] = value
    }
  })
  return result
}

function optionLabel(options, value) {
  return options.find(item => item.value === value)?.label || ''
}

function getList() {
  loading.value = true
  const query = cleanQuery({
    ...queryParams.value,
    courseType: courseTypeFilter.value.length === 1 ? courseTypeFilter.value[0] : '',
    status: statusFilter.value.length === 1 ? statusFilter.value[0] : ''
  })
  listCourse(query).then(response => {
    courseList.value = response.rows || []
    total.value = response.total || 0
  }).finally(() => {
    loading.value = false
  })
}

function getPackageList() {
  packageLoading.value = true
  const query = cleanQuery({
    ...packageQueryParams.value,
    status: packageStatusFilter.value.length === 1 ? packageStatusFilter.value[0] : ''
  })
  listCoursePackage(query).then(response => {
    packageList.value = response.rows || []
    packageTableTotal.value = response.total || 0
  }).finally(() => {
    packageLoading.value = false
  })
}

function getActiveList() {
  if (activeTab.value === 'package') {
    getPackageList()
  } else {
    getList()
  }
}

function handleTabClick(tab) {
  if (tab.props.name === 'course') {
    getList()
  } else if (tab.props.name === 'package') {
    getPackageList()
  }
}

function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

function resetQuery() {
  queryParams.value = {
    pageNum: 1,
    pageSize: queryParams.value.pageSize,
    courseName: '',
    courseType: '',
    status: 1
  }
  courseTypeFilter.value = []
  statusFilter.value = [1]
  handleQuery()
}

function handleTypeFilterChange() {
  handleQuery()
}

function handleStatusFilterChange() {
  handleQuery()
}

function handlePackageQuery() {
  packageQueryParams.value.pageNum = 1
  getPackageList()
}

function resetPackageQuery() {
  packageQueryParams.value = {
    pageNum: 1,
    pageSize: packageQueryParams.value.pageSize,
    packageName: '',
    status: 1
  }
  packageStatusFilter.value = [1]
  handlePackageQuery()
}

function handlePackageStatusFilterChange() {
  handlePackageQuery()
}

function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length !== 1
  multiple.value = !selection.length
}

function handlePackageSelectionChange(selection) {
  packageIds.value = selection.map(item => item.id)
  packageMultiple.value = !selection.length
}

function handleAdd() {
  form.value = defaultForm()
  title.value = '新增课程'
  open.value = true
}

function handleBatchAdd() {
  batchForm.value = defaultBatchForm()
  batchOpen.value = true
}

function addBatchCourseRow() {
  if (batchForm.value.courses.length >= 20) {
    return
  }
  batchForm.value.courses.push(defaultBatchCourseRow())
}

function removeBatchCourseRow(index) {
  batchForm.value.courses.splice(index, 1)
}

function normalizePriceRow(row, chargeType) {
  return {
    chargeType,
    priceName: row.priceName || row.name || '单价',
    quantity: Number(row.quantity || 1),
    totalPrice: row.totalPrice === undefined || row.totalPrice === null ? null : Number(row.totalPrice),
    unitPrice: row.unitPrice === undefined || row.unitPrice === null ? null : Number(row.unitPrice),
    status: row.status ?? 1
  }
}

function normalizeDetail(data) {
  const result = {
    ...defaultForm(),
    ...data,
    courseType: data.courseType || 'one_to_many',
    grade: data.grade || '',
    subject: data.subject || '',
    semester: data.semester || '',
    scheduleColor: data.scheduleColor || '#409EFF',
    status: data.status ?? 1,
    onlineSale: data.onlineSale ?? 0,
    classDeductRule: data.classDeductRule || data.classPrices?.[0]?.deductRule || 'none',
    classAbsenceRule: data.classAbsenceRule || data.classPrices?.[0]?.absenceRule || 'deduct',
    classPrices: (data.classPrices || []).map(row => normalizePriceRow(row, 'class')),
    monthPrices: (data.monthPrices || []).map(row => normalizePriceRow(row, 'month')),
    dayPrices: (data.dayPrices || []).map(row => normalizePriceRow(row, 'day'))
  }
  result.chargeByClass = result.classPrices.length > 0
  result.chargeByMonth = result.monthPrices.length > 0
  result.chargeByDay = result.dayPrices.length > 0
  if (result.chargeByClass && result.classPrices.length === 0) {
    result.classPrices = [defaultPrice('class')]
  }
  return result
}

function formatMoney(value) {
  return Number(value || 0).toFixed(2)
}

function packageTypeName(type) {
  const typeMap = {
    course: '课程',
    item: '物品',
    fee: '费用'
  }
  return typeMap[type] || type
}

function packageTypeTag(type) {
  const tagMap = {
    course: 'success',
    item: 'warning',
    fee: 'info'
  }
  return tagMap[type] || ''
}

function chargeUnit(chargeType) {
  const unitMap = {
    class: '课时',
    month: '月',
    day: '天'
  }
  return unitMap[chargeType] || ''
}

function calcPackageSubtotal(row) {
  const totalPrice = Number(row.totalPrice || 0)
  const discountValue = Number(row.discountValue || 0)
  if (row.discountType === 'discount' && discountValue > 0) {
    if (discountValue <= 10) {
      return Math.max(0, totalPrice * discountValue / 10)
    }
    if (discountValue <= 100) {
      return Math.max(0, totalPrice * discountValue / 100)
    }
    return totalPrice
  }
  return Math.max(0, totalPrice - discountValue)
}

function refreshPackageItem(row) {
  row.quantity = Number(row.quantity || 1)
  row.unitPrice = Number(row.unitPrice || 0)
  row.totalPrice = Number((row.quantity * row.unitPrice).toFixed(2))
  row.subtotalPrice = Number(calcPackageSubtotal(row).toFixed(2))
}

function fillPackageItemAmount(row) {
  row.quantity = Number(row.quantity || 1)
  row.unitPrice = Number(row.unitPrice || 0)
  row.totalPrice = Number(row.totalPrice || (row.quantity * row.unitPrice).toFixed(2))
  if (row.subtotalPrice === undefined || row.subtotalPrice === null || row.subtotalPrice === '') {
    row.subtotalPrice = Number(calcPackageSubtotal(row).toFixed(2))
  } else {
    row.subtotalPrice = Number(row.subtotalPrice || 0)
  }
}

function refreshPackageTotal() {
  packageForm.value.totalPrice = Number(packageTotalPrice.value.toFixed(2))
}

function normalizePackageItem(row) {
  const item = {
    id: row.id,
    itemType: row.itemType,
    itemId: row.itemId,
    itemName: row.itemName,
    specId: row.specId,
    specName: row.specName,
    unit: row.unit || '',
    quantity: Number(row.quantity || 1),
    giftQuantity: Number(row.giftQuantity || 0),
    leaveFreeQuantity: Number(row.leaveFreeQuantity || 0),
    unitPrice: Number(row.unitPrice || 0),
    totalPrice: Number(row.totalPrice || 0),
    discountType: row.discountType || 'reduce',
    discountValue: Number(row.discountValue || 0),
    subtotalPrice: Number(row.subtotalPrice || 0),
    sort: Number(row.sort || 0),
    priceOptions: row.priceOptions || row.prices || []
  }
  fillPackageItemAmount(item)
  return item
}

function normalizePackageDetail(data) {
  const result = {
    ...defaultPackageForm(),
    ...data,
    status: data.status ?? 1,
    onlineSale: data.onlineSale ?? 0,
    items: (data.items || []).map(normalizePackageItem)
  }
  result.totalPrice = Number(result.totalPrice || packageTotalPrice.value || 0)
  return result
}

function getDefaultPrice(row) {
  const prices = row.prices || []
  const firstPrice = prices[0] || {}
  return {
    specId: firstPrice.id || null,
    specName: firstPrice.displayText || firstPrice.priceName || row.priceStandard || '',
    unit: chargeUnit(firstPrice.chargeType) || '',
    quantity: Number(firstPrice.quantity || 1),
    unitPrice: Number(firstPrice.unitPrice || firstPrice.totalPrice || 0),
    priceOptions: prices
  }
}

function makeCoursePackageItem(row) {
  const price = getDefaultPrice(row)
  return normalizePackageItem({
    itemType: 'course',
    itemId: row.id,
    itemName: row.courseName,
    ...price,
    giftQuantity: 0,
    leaveFreeQuantity: 0,
    discountType: 'reduce',
    discountValue: 0,
    sort: packageForm.value.items.length
  })
}

function getFirstSku(row) {
  return (row.skus || [])[0] || {}
}

function makeItemPackageItem(row) {
  const sku = getFirstSku(row)
  return normalizePackageItem({
    itemType: 'item',
    itemId: row.id,
    itemName: row.itemName,
    specId: sku.id || null,
    specName: sku.specText || sku.skuName || '',
    unit: row.unit || '件',
    quantity: 1,
    giftQuantity: 0,
    leaveFreeQuantity: 0,
    unitPrice: Number(sku.price || row.defaultPrice || row.singlePrice || 0),
    discountType: 'reduce',
    discountValue: 0,
    sort: packageForm.value.items.length
  })
}

function makeFeePackageItem(row) {
  return normalizePackageItem({
    itemType: 'fee',
    itemId: row.id,
    itemName: row.feeName,
    specId: null,
    specName: '',
    unit: '项',
    quantity: 1,
    giftQuantity: 0,
    leaveFreeQuantity: 0,
    unitPrice: Number(row.amount || row.price || 0),
    discountType: 'reduce',
    discountValue: 0,
    sort: packageForm.value.items.length
  })
}

function packageItemKey(row) {
  return `${row.itemType}_${row.itemId}_${row.specId || ''}`
}

function appendPackageItems(items) {
  const exists = new Set(packageForm.value.items.map(packageItemKey))
  items.forEach(item => {
    if (exists.has(packageItemKey(item))) {
      return
    }
    item.sort = packageForm.value.items.length
    packageForm.value.items.push(item)
    exists.add(packageItemKey(item))
  })
  refreshPackageTotal()
}

function handleUpdate(row) {
  const courseId = row.id || ids.value[0]
  getCourse(courseId).then(response => {
    form.value = normalizeDetail(response.data || {})
    title.value = '编辑课程'
    open.value = true
  })
}

function handleDelete(row) {
  const courseIds = row.id ? row.id : ids.value.join(',')
  proxy.$modal.confirm('确认删除选中的课程吗？').then(() => {
    return delCourse(courseIds)
  }).then(() => {
    proxy.$modal.msgSuccess('删除成功')
    getList()
  })
}

function handleStatusChange(row, value) {
  changeCourseStatus({ id: row.id, status: value }).then(() => {
    proxy.$modal.msgSuccess('状态修改成功')
  }).catch(() => {
    row.status = value === 1 ? 0 : 1
  })
}

function handlePackageAdd() {
  packageForm.value = defaultPackageForm()
  packageTitle.value = '添加套餐'
  packageOpen.value = true
}

function handlePackageUpdate(row) {
  const packageId = row.id || packageIds.value[0]
  getCoursePackage(packageId).then(response => {
    packageForm.value = normalizePackageDetail(response.data || {})
    packageTitle.value = '编辑套餐'
    packageOpen.value = true
  })
}

function handlePackageDelete(row) {
  const deleteIds = row.id ? row.id : packageIds.value.join(',')
  proxy.$modal.confirm('确认删除选中的套餐吗？').then(() => {
    return delCoursePackage(deleteIds)
  }).then(() => {
    proxy.$modal.msgSuccess('删除成功')
    getPackageList()
  })
}

function handlePackageStatusChange(row, value) {
  changeCoursePackageStatus({ id: row.id, status: value }).then(() => {
    proxy.$modal.msgSuccess('状态修改成功')
  }).catch(() => {
    row.status = value === 1 ? 0 : 1
  })
}

function removePackageItem(index) {
  packageForm.value.items.splice(index, 1)
  packageForm.value.items.forEach((item, itemIndex) => {
    item.sort = itemIndex
  })
  refreshPackageTotal()
}

function handlePackageSpecChange(row, value) {
  const price = row.priceOptions.find(item => item.id === value)
  if (!price) {
    return
  }
  row.specName = price.displayText || price.priceName
  row.unit = chargeUnit(price.chargeType)
  row.quantity = Number(price.quantity || 1)
  row.unitPrice = Number(price.unitPrice || price.totalPrice || 0)
  refreshPackageItem(row)
}

function openSelector(type) {
  selectorType.value = type
  selectorKeyword.value = ''
  selectorSelection.value = []
  selectorOptions.value = []
  selectorOpen.value = true
  loadSelectorOptions()
}

function normalizeSelectorRows(rows) {
  return (rows || []).map(row => ({
    ...row,
    selectorKey: `${selectorType.value}_${row.id}`
  }))
}

function loadSelectorOptions() {
  selectorLoading.value = true
  const query = cleanQuery({
    keyword: selectorKeyword.value,
    feeName: selectorKeyword.value,
    pageNum: 1,
    pageSize: 50,
    status: 1
  })
  let request
  if (selectorType.value === 'course') {
    request = listCourseOptions({ keyword: selectorKeyword.value })
  } else if (selectorType.value === 'item') {
    request = listAvailableItems({ keyword: selectorKeyword.value })
  } else {
    request = listFee(query)
  }
  request.then(response => {
    selectorOptions.value = normalizeSelectorRows(response.data || response.rows || [])
  }).finally(() => {
    selectorLoading.value = false
  })
}

function handleSelectorSelectionChange(selection) {
  selectorSelection.value = selection
}

function confirmSelector() {
  if (!selectorSelection.value.length) {
    proxy.$modal.msgWarning('请选择项目')
    return
  }
  const builders = {
    course: makeCoursePackageItem,
    item: makeItemPackageItem,
    fee: makeFeePackageItem
  }
  appendPackageItems(selectorSelection.value.map(row => builders[selectorType.value](row)))
  selectorOpen.value = false
}

function handleChargeToggle(section, value) {
  if (value && form.value[section.listKey].length === 0) {
    form.value[section.listKey].push(defaultPrice(section.type))
  }
}

function addPriceRow(section) {
  if (form.value[section.listKey].length >= 10) {
    return
  }
  form.value[section.listKey].push(defaultPrice(section.type))
}

function removePriceRow(section, index) {
  form.value[section.listKey].splice(index, 1)
}

function calcUnitPrice(row) {
  const totalPrice = Number(row.totalPrice || 0)
  const quantity = Number(row.quantity || 0)
  if (!totalPrice || !quantity) {
    return '自动计算'
  }
  return (totalPrice / quantity).toFixed(2)
}

function validatePrices() {
  const enabledSections = chargeSections.filter(section => form.value[section.enabledKey])
  if (!enabledSections.length) {
    proxy.$modal.msgWarning('请至少开启一种收费方式')
    return false
  }
  for (const section of enabledSections) {
    const rows = form.value[section.listKey] || []
    if (!rows.length) {
      proxy.$modal.msgWarning(`${section.label}至少添加一条定价标准`)
      return false
    }
    const invalidRow = rows.find(row => !row.priceName || !row.quantity || Number(row.totalPrice || 0) <= 0)
    if (invalidRow) {
      proxy.$modal.msgWarning(`${section.label}的名称、数量和总价不能为空`)
      return false
    }
  }
  return true
}

function buildPricePayload(section) {
  if (!form.value[section.enabledKey]) {
    return []
  }
  return form.value[section.listKey].map((row, index) => ({
    chargeType: section.type,
    priceName: row.priceName,
    quantity: Number(row.quantity || 1),
    totalPrice: Number(row.totalPrice || 0),
    unitPrice: Number(row.totalPrice || 0) / Number(row.quantity || 1),
    deductRule: section.type === 'class' ? form.value.classDeductRule : undefined,
    absenceRule: section.type === 'class' ? form.value.classAbsenceRule : undefined,
    sort: index,
    status: 1
  }))
}

function buildPayload() {
  const gradeLabel = optionLabel(gradeOptions, form.value.grade)
  const subjectLabel = optionLabel(subjectOptions, form.value.subject)
  const semesterLabel = optionLabel(semesterOptions, form.value.semester)
  return {
    id: form.value.id,
    courseNo: form.value.courseNo,
    courseName: form.value.courseName,
    courseType: form.value.courseType,
    scheduleColor: form.value.scheduleColor,
    grade: form.value.grade,
    gradeLabel,
    subject: form.value.subject,
    subjectLabel,
    semester: form.value.semester,
    semesterLabel,
    studentCount: Number(form.value.studentCount || 0),
    onlineSale: form.value.onlineSale,
    status: form.value.status,
    chargeByClass: form.value.chargeByClass,
    chargeByMonth: form.value.chargeByMonth,
    chargeByDay: form.value.chargeByDay,
    classDeductRule: form.value.classDeductRule,
    classAbsenceRule: form.value.classAbsenceRule,
    classPrices: buildPricePayload(chargeSections[0]),
    monthPrices: buildPricePayload(chargeSections[1]),
    dayPrices: buildPricePayload(chargeSections[2]),
    remark: form.value.remark
  }
}

function buildBatchPricePayload(row) {
  return {
    chargeType: row.chargeType,
    priceName: row.priceName || '单价',
    quantity: Number(row.quantity || 1),
    totalPrice: Number(row.totalPrice || 0),
    unitPrice: Number(row.totalPrice || 0) / Number(row.quantity || 1),
    deductRule: row.chargeType === 'class' ? 'none' : undefined,
    absenceRule: row.chargeType === 'class' ? 'deduct' : undefined,
    sort: 0,
    status: 1
  }
}

function buildBatchCoursePayload(row) {
  const price = buildBatchPricePayload(row)
  const payload = {
    courseName: row.courseName,
    courseType: row.courseType,
    scheduleColor: row.scheduleColor,
    studentCount: 0,
    onlineSale: row.onlineSale,
    status: row.status,
    chargeByClass: row.chargeType === 'class',
    chargeByMonth: row.chargeType === 'month',
    chargeByDay: row.chargeType === 'day',
    classDeductRule: 'none',
    classAbsenceRule: 'deduct',
    classPrices: [],
    monthPrices: [],
    dayPrices: [],
    remark: ''
  }
  if (row.chargeType === 'class') {
    payload.classPrices = [price]
  } else if (row.chargeType === 'month') {
    payload.monthPrices = [price]
  } else {
    payload.dayPrices = [price]
  }
  return payload
}

function validateBatchCourses() {
  const rows = batchForm.value.courses || []
  if (!rows.length) {
    proxy.$modal.msgWarning('请至少添加一门课程')
    return false
  }
  const invalidRowIndex = rows.findIndex(row => {
    return !row.courseName || !row.chargeType || !row.quantity || Number(row.totalPrice || 0) <= 0
  })
  if (invalidRowIndex > -1) {
    proxy.$modal.msgWarning(`请完善第 ${invalidRowIndex + 1} 行课程名称、收费方式、数量和总价`)
    return false
  }
  return true
}

function validatePackageItems() {
  if (!packageForm.value.items.length) {
    proxy.$modal.msgWarning('请至少选择一个套餐项目')
    return false
  }
  const invalidItem = packageForm.value.items.find(item => {
    return !item.itemName || !item.quantity || Number(item.unitPrice || 0) < 0 || Number(item.subtotalPrice || 0) < 0
  })
  if (invalidItem) {
    proxy.$modal.msgWarning('请检查套餐明细的项目、数量和金额')
    return false
  }
  const invalidCourse = packageForm.value.items.find(item => item.itemType === 'course' && !item.specId)
  if (invalidCourse) {
    proxy.$modal.msgWarning('请选择课程明细的定价标准')
    return false
  }
  return true
}

function buildPackagePayload() {
  refreshPackageTotal()
  return {
    id: packageForm.value.id,
    packageNo: packageForm.value.packageNo,
    packageName: packageForm.value.packageName,
    totalPrice: packageForm.value.totalPrice,
    onlineSale: packageForm.value.onlineSale,
    status: packageForm.value.status,
    remark: packageForm.value.remark,
    items: packageForm.value.items.map((item, index) => ({
      itemType: item.itemType,
      itemId: item.itemId,
      itemName: item.itemName,
      specId: item.specId,
      specName: item.specName,
      unit: item.unit,
      quantity: Number(item.quantity || 1),
      giftQuantity: Number(item.giftQuantity || 0),
      leaveFreeQuantity: Number(item.leaveFreeQuantity || 0),
      unitPrice: Number(item.unitPrice || 0),
      totalPrice: Number(item.totalPrice || 0),
      discountType: item.discountType || 'reduce',
      discountValue: Number(item.discountValue || 0),
      subtotalPrice: Number(item.subtotalPrice || 0),
      sort: index
    }))
  }
}

function submitForm() {
  courseFormRef.value.validate(valid => {
    if (!valid || !validatePrices()) {
      return
    }
    submitLoading.value = true
    const payload = buildPayload()
    const request = payload.id ? updateCourse(payload) : addCourse(payload)
    request.then(() => {
      proxy.$modal.msgSuccess(payload.id ? '修改成功' : '新增成功')
      open.value = false
      getList()
    }).finally(() => {
      submitLoading.value = false
    })
  })
}

function submitBatchForm() {
  if (!validateBatchCourses()) {
    return
  }
  batchSubmitLoading.value = true
  const payload = {
    courses: batchForm.value.courses.map(buildBatchCoursePayload)
  }
  batchAddCourse(payload).then(response => {
    proxy.$modal.msgSuccess(response.msg || '批量新增成功')
    batchOpen.value = false
    getList()
  }).finally(() => {
    batchSubmitLoading.value = false
  })
}

function submitPackageForm() {
  packageFormRef.value.validate(valid => {
    if (!valid || !validatePackageItems()) {
      return
    }
    packageSubmitLoading.value = true
    const payload = buildPackagePayload()
    const request = payload.id ? updateCoursePackage(payload) : addCoursePackage(payload)
    request.then(() => {
      proxy.$modal.msgSuccess(payload.id ? '修改成功' : '新增成功')
      packageOpen.value = false
      getPackageList()
    }).finally(() => {
      packageSubmitLoading.value = false
    })
  })
}

function cancel() {
  open.value = false
}

getList()
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.course-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.price-lines {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 20px;
}

.muted {
  color: #909399;
}

.color-swatches {
  display: flex;
  gap: 12px;
  align-items: center;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border: 2px solid transparent;
  border-radius: 50%;
  cursor: pointer;
}

.color-swatch.active {
  border-color: #303133;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.18);
}

.charge-section {
  border-top: 1px solid #ebeef5;
  padding: 18px 0;
}

.charge-section:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.charge-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-left: 24px;
  font-size: 16px;
  font-weight: 600;
}

.charge-body {
  padding-left: 24px;
}

.price-alert {
  margin-bottom: 12px;
}

.add-price {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.batch-actions {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}

.package-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.package-item-table {
  width: 100%;
}

.quantity-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.quantity-cell :deep(.el-input-number) {
  width: 104px;
}

.discount-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.discount-cell :deep(.el-select) {
  width: 82px;
  flex: 0 0 82px;
}

.discount-cell :deep(.el-input-number) {
  width: 104px;
}

.package-total {
  display: flex;
  justify-content: flex-end;
  align-items: baseline;
  gap: 8px;
  margin-top: 14px;
  font-size: 16px;
}

.package-total span {
  color: #f56c6c;
  font-size: 24px;
  font-weight: 600;
}

.selector-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.selected-count {
  color: #606266;
}

.selector-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.danger-text {
  color: #f56c6c;
}
</style>
