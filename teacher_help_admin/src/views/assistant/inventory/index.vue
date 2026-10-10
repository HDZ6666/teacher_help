<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- 物品Tab -->
      <el-tab-pane label="物品" name="item">
        <!-- 物品子Tab -->
        <el-tabs v-model="itemSubTab" @tab-click="handleItemSubTabClick">
          <!-- 物品管理子Tab -->
          <el-tab-pane label="物品管理" name="itemManage">
            <!-- 搜索栏 -->
            <el-form :model="itemQueryParams" ref="itemQueryRef" :inline="true" v-show="showSearch" label-width="68px">
              <el-form-item label="物品名称" prop="itemName">
                <el-input
                  v-model="itemQueryParams.itemName"
                  placeholder="请输入物品名称"
                  clearable
                  @keyup.enter="handleItemQuery"
                />
              </el-form-item>
              <el-form-item label="启用状态" prop="status">
                <el-radio-group v-model="itemQueryParams.status">
                  <el-radio-button label="">全部</el-radio-button>
                  <el-radio-button label="1">启用</el-radio-button>
                  <el-radio-button label="0">停用</el-radio-button>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" icon="Search" @click="handleItemQuery">搜索</el-button>
                <el-button icon="Refresh" @click="resetItemQuery">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 操作按钮 -->
            <el-row :gutter="10" class="mb8">
              <el-col :span="1.5">
                <el-button type="primary" plain icon="Plus" @click="handleAddItem">新增物品</el-button>
              </el-col>
              <el-col :span="1.5">
                <el-button type="success" plain icon="Download" @click="handleExport">导出</el-button>
              </el-col>
              <right-toolbar v-model:showSearch="showSearch" @queryTable="getItemList"></right-toolbar>
            </el-row>

            <!-- 物品列表 -->
            <el-table v-loading="itemLoading" :data="itemList" class="item-manage-table" table-layout="auto" style="width: 100%;">
              <el-table-column label="物品名称" align="center" prop="itemName" min-width="160" show-overflow-tooltip />
              <el-table-column label="物品图片" align="center" prop="imageUrl" width="76">
                <template #default="scope">
                  <image-preview v-if="scope.row.imageUrl" :src="scope.row.imageUrl" :width="36" :height="36" />
                  <span v-else style="color: #909399;">-</span>
                </template>
              </el-table-column>
              <el-table-column label="物品编码" align="center" prop="itemCode" width="130" show-overflow-tooltip />
              <el-table-column label="物品类型" align="center" prop="itemType" width="90">
                <template #default="scope">
                  <el-tag v-if="String(scope.row.itemType) === '1'">实物</el-tag>
                  <el-tag v-else type="info">虚拟</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="SKU数量" align="center" prop="skuCount" width="86">
                <template #default="scope">
                  <span style="color: #409EFF;">{{ scope.row.skuCount }}种</span>
                </template>
              </el-table-column>
              <el-table-column label="总库存" align="center" prop="totalStock" width="86">
                <template #default="scope">
                  <span :style="{ color: scope.row.isWarning ? '#F56C6C' : '#303133', fontWeight: scope.row.isWarning ? 'bold' : 'normal' }">
                    {{ scope.row.totalStock }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="库存预警" align="center" prop="warningStock" width="96">
                <template #default="scope">
                  <el-tag v-if="scope.row.isWarning" type="danger">≤ {{ scope.row.warningStock }}</el-tag>
                  <span v-else>{{ scope.row.warningStock || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="单价范围" align="center" prop="priceRange" width="120" show-overflow-tooltip />
              <el-table-column label="绑定课程" align="center" prop="courseName" min-width="170" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.courseName" style="color: #409EFF;">{{ scope.row.courseName }}</span>
                  <span v-else style="color: #909399;">未绑定</span>
                </template>
              </el-table-column>
              <el-table-column label="开启库存" align="center" prop="enableStock" width="88">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.enableStock"
                    :active-value="1"
                    :inactive-value="0"
                    @change="handleItemEnableStockChange(scope.row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="线上售卖" align="center" prop="onlineSale" width="88">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.onlineSale"
                    :active-value="1"
                    :inactive-value="0"
                    @change="handleItemOnlineSaleChange(scope.row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="启用状态" align="center" prop="status" width="88">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.status"
                    :active-value="1"
                    :inactive-value="0"
                    @change="handleItemStatusChange(scope.row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" align="center" width="220" fixed="right" class-name="small-padding fixed-width">
                <template #default="scope">
                  <el-button link type="primary" icon="View" @click="handleViewItem(scope.row)">出入库记录</el-button>
                  <el-button link type="primary" icon="Edit" @click="handleUpdateItem(scope.row)">编辑</el-button>
                  <el-button link type="primary" icon="Delete" @click="handleDeleteItem(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <pagination
              v-show="itemTotal > 0"
              :total="itemTotal"
              v-model:page="itemQueryParams.pageNum"
              v-model:limit="itemQueryParams.pageSize"
              @pagination="getItemList"
            />
          </el-tab-pane>

          <!-- 出入库管理子Tab -->
          <el-tab-pane label="出入库管理" name="stockManage">
            <!-- 搜索栏 -->
            <el-form :model="stockQueryParams" ref="stockQueryRef" :inline="true" v-show="showSearch" label-width="96px" class="stock-search-form">
              <el-form-item label="物品名称" prop="itemNames">
                <el-select
                  v-model="stockQueryParams.itemNames"
                  multiple
                  filterable
                  clearable
                  collapse-tags
                  collapse-tags-tooltip
                  placeholder="请选择物品(支持多选)"
                  style="width: 320px;"
                >
                  <el-option
                    v-for="item in stockItemOptions"
                    :key="item.id"
                    :label="item.itemName"
                    :value="item.itemName"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="出入库日期" prop="dateRange">
                <el-date-picker
                  v-model="stockQueryParams.dateRange"
                  type="daterange"
                  value-format="YYYY-MM-DD"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 320px;"
                />
              </el-form-item>
              <el-form-item label="出入库类型" prop="stockTypes">
                <el-checkbox-group v-model="stockQueryParams.stockTypes">
                  <el-checkbox label="out">出库</el-checkbox>
                  <el-checkbox label="in">入库</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="业务类型" prop="businessType">
                <el-select v-model="stockQueryParams.businessType" placeholder="请选择" clearable style="width: 180px;">
                  <el-option label="全部" value="" />
                  <el-option label="销售" value="sale" />
                  <el-option label="采购" value="purchase" />
                  <el-option label="领用" value="receive" />
                  <el-option label="退领" value="return" />
                  <el-option label="盘点" value="inventory" />
                </el-select>
              </el-form-item>
              <el-form-item label="角色类型" prop="relatedType">
                <el-select v-model="stockQueryParams.relatedType" placeholder="请选择" clearable style="width: 180px;">
                  <el-option label="学员" value="student" />
                  <el-option label="员工" value="staff" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item label="角色姓名" prop="relatedName">
                <el-input
                  v-model="stockQueryParams.relatedName"
                  placeholder="请输入姓名/手机号"
                  clearable
                  style="width: 220px;"
                />
              </el-form-item>
              <el-form-item label="记录状态" prop="excludeVoided">
                <el-checkbox v-model="stockQueryParams.excludeVoided">过滤已作废</el-checkbox>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" icon="Search" @click="handleStockQuery">搜索</el-button>
                <el-button icon="Refresh" @click="resetStockQuery">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 操作按钮 -->
            <div class="stock-action-row mb8">
              <div class="stock-action-buttons">
                <el-button type="primary" plain icon="Plus" @click="handlePurchase">采购</el-button>
                <el-dropdown trigger="click" @command="handlePurchaseCommand">
                  <el-button type="primary" plain icon="ArrowDown" class="purchase-more-button" />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="create">新建采购</el-dropdown-item>
                      <el-dropdown-item command="import">导入采购单</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button type="success" plain icon="Minus" @click="handleReceive">领用</el-button>
                <el-button type="warning" plain icon="RefreshLeft" @click="handleReturn">退领</el-button>
                <el-button type="danger" plain icon="DocumentChecked" @click="handleInventory">盘点</el-button>
                <el-button type="info" plain icon="Download" @click="handleStockExport">导出</el-button>
              </div>
              <right-toolbar v-model:showSearch="showSearch" @queryTable="getStockList"></right-toolbar>
            </div>

            <div class="stock-summary-bar">
              <span>当前结果：共 {{ stockSummary.currentCount }} 条记录</span>
              <span>入库总计：{{ stockSummary.inTotal }}</span>
              <span>出库总计：{{ stockSummary.outTotal }}</span>
              <span>出入库总计：{{ stockSummary.netTotal }}</span>
            </div>

            <!-- 出入库记录列表 -->
            <el-table :key="stockTableKey" v-loading="stockLoading" :data="stockList" class="stock-record-table" table-layout="auto" style="width: 100%;">
              <el-table-column label="出入库日期" align="center" prop="stockDate" width="168">
                <template #default="scope">
                  {{ formatDate(scope.row.stockDate) || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="物品名称" align="left" prop="itemName" min-width="180" show-overflow-tooltip>
                <template #default="scope">
                  <div class="item-name-cell">
                    <span>{{ scope.row.itemName || '-' }}</span>
                    <small v-if="scope.row.specText && scope.row.specText !== '默认'">{{ scope.row.specText }}</small>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="业务类型" align="center" prop="businessType" width="92">
                <template #default="scope">
                  <el-tag v-if="scope.row.businessType === 'sale'" type="primary">销售</el-tag>
                  <el-tag v-else-if="scope.row.businessType === 'purchase'" type="success">采购</el-tag>
                  <el-tag v-else-if="scope.row.businessType === 'receive'" type="warning">领用</el-tag>
                  <el-tag v-else-if="scope.row.businessType === 'return'" type="info">退领</el-tag>
                  <el-tag v-else-if="scope.row.businessType === 'inventory'" type="danger">盘点</el-tag>
                  <el-tag v-else>{{ scope.row.businessTypeLabel || '-' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="出入库数量" align="center" prop="quantity" width="108">
                <template #default="scope">
                  <span :style="{ color: scope.row.quantity > 0 ? '#67C23A' : '#F56C6C' }">
                    {{ scope.row.quantity > 0 ? '+' : '' }}{{ scope.row.quantity }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="角色类型" align="center" prop="roleType" width="92">
                <template #default="scope">
                  {{ scope.row.roleTypeLabel || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="角色姓名" align="center" prop="roleName" width="120" show-overflow-tooltip />
              <el-table-column label="关联业务" align="center" prop="businessNo" min-width="160" show-overflow-tooltip>
                <template #default="scope">
                  <el-button v-if="scope.row.businessNo" link type="primary" @click="handleViewStock(scope.row)">
                    {{ scope.row.businessNo }}
                  </el-button>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="经办人" align="center" prop="operator" width="90" show-overflow-tooltip />
              <el-table-column label="备注" align="center" prop="remark" min-width="120" show-overflow-tooltip>
                <template #default="scope">
                  {{ scope.row.remark || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" align="center" width="116" fixed="right" class-name="small-padding fixed-width">
                <template #default="scope">
                  <el-button link type="primary" icon="View" @click="handleViewStock(scope.row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <pagination
              v-show="stockTotal > 0"
              :total="stockTotal"
              v-model:page="stockQueryParams.pageNum"
              v-model:limit="stockQueryParams.pageSize"
              @pagination="getStockList"
            />
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>

      <!-- 费用Tab -->
      <el-tab-pane label="费用" name="fee">
        <!-- 搜索区域 -->
        <el-form :model="feeQueryParams" ref="feeQueryRef" :inline="true" v-show="showSearch" label-width="80px">
          <el-form-item label="费用名称" prop="feeName">
            <el-input
              v-model="feeQueryParams.feeName"
              placeholder="请输入费用名称"
              clearable
              @keyup.enter="getFeeList"
            />
          </el-form-item>
          <el-form-item label="启用状态" prop="status">
            <el-radio-group v-model="feeQueryParams.status">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="1">启用</el-radio-button>
              <el-radio-button label="0">停用</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="getFeeList">搜索</el-button>
            <el-button icon="Refresh" @click="resetFeeQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleAddFee">新建费用</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button plain icon="Upload" @click="feeImportVisible = true" v-hasPermi="['ast:fee:import']">导入费用</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getFeeList"></right-toolbar>
        </el-row>

        <!-- 费用列表 -->
        <el-table v-loading="feeLoading" :data="feeList">
          <el-table-column label="费用名称" align="center" prop="feeName" width="200" />
          <el-table-column label="售卖单价" align="center" prop="price" width="150">
            <template #default="scope">
              <span style="color: #F56C6C; font-weight: bold;">¥ {{ scope.row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column label="绑定课程" align="center" prop="courseName" min-width="200">
            <template #default="scope">
              <span v-if="scope.row.courseName" style="color: #409EFF;">{{ scope.row.courseName }}</span>
              <span v-else style="color: #909399;">未绑定</span>
            </template>
          </el-table-column>
          <el-table-column label="线上售卖" align="center" width="120">
            <template #default="scope">
              <el-switch
                v-model="scope.row.onlineSale"
                :active-value="1"
                :inactive-value="0"
                @change="handleFeeOnlineSaleChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="启用状态" align="center" width="120">
            <template #default="scope">
              <el-switch
                v-model="scope.row.status"
                :active-value="1"
                :inactive-value="0"
                @change="handleFeeStatusChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="180" fixed="right" class-name="small-padding fixed-width">
            <template #default="scope">
              <el-button link type="primary" icon="Edit" @click="handleEditFee(scope.row)">编辑</el-button>
              <el-button link type="danger" icon="Delete" @click="handleDeleteFee(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="feeTotal > 0"
          :total="feeTotal"
          v-model:page="feeQueryParams.pageNum"
          v-model:limit="feeQueryParams.pageSize"
          @pagination="getFeeList"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 新增/修改物品对话框 -->
    <el-dialog :title="itemTitle" v-model="itemOpen" width="1080px" class="item-form-dialog" append-to-body destroy-on-close>
      <el-form ref="itemFormRef" :model="itemForm" :rules="itemRules" label-width="100px" class="item-form">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物品名称" prop="itemName">
              <el-input v-model="itemForm.itemName" placeholder="请输入物品名称" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物品类型" prop="itemType">
              <el-radio-group v-model="itemForm.itemType">
                <el-radio label="1">实物</el-radio>
                <el-radio label="2">虚拟</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="物品图片" prop="imageUrl">
              <image-upload v-model="itemForm.imageUrl" :limit="5" :file-size="5" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="开启库存">
              <el-switch v-model="itemForm.enableStock" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存预警">
              <el-input-number
                v-model="itemForm.warningStock"
                :min="0"
                :precision="0"
                :controls="false"
                style="width: 100%;"
                placeholder="请输入预警数量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="线上售卖">
              <el-switch v-model="itemForm.onlineSale" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="绑定课程">
              <div class="course-bind-area">
                <div v-if="itemForm.courseIds && itemForm.courseIds.length > 0" style="margin-bottom: 10px;">
                  <el-tag
                    v-for="(courseName, index) in itemForm.courseNames"
                    :key="itemForm.courseIds[index]"
                    closable
                    @close="removeItemCourse(index)"
                    style="margin-right: 8px; margin-bottom: 8px;"
                    type="primary"
                  >
                    {{ courseName }}
                  </el-tag>
                </div>
                <el-button icon="Plus" @click="openSelectCourseDialog('item')">
                  {{ itemForm.courseIds && itemForm.courseIds.length > 0 ? '继续添加课程' : '选择课程' }}
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- SKU信息 -->
        <el-divider content-position="left">
          <span style="font-size: 14px; font-weight: bold;">物品规格</span>
        </el-divider>

        <!-- 规格选项 -->
        <el-form-item label="规格" prop="specs">
          <el-table :data="itemForm.specs" border class="spec-table" table-layout="auto" style="width: 100%;">
            <el-table-column label="排序" width="88" align="center">
              <template #default="scope">
                <el-button
                  link
                  icon="Top"
                  :disabled="scope.$index === 0"
                  @click="moveSpecUp(scope.$index)"
                />
                <el-button
                  link
                  icon="Bottom"
                  :disabled="scope.$index === itemForm.specs.length - 1"
                  @click="moveSpecDown(scope.$index)"
                />
              </template>
            </el-table-column>
            <el-table-column label="规格名称" width="190">
              <template #default="scope">
                <el-input
                  v-model="scope.row.name"
                  placeholder="规格名(如:颜色)"
                  @blur="autoGenerateSKU"
                />
              </template>
            </el-table-column>
            <el-table-column label="规格值（可使用回车键生成快速添加规格值）" min-width="420">
              <template #default="scope">
                <div class="spec-value-editor">
                  <el-tag
                    v-for="(tag, tagIndex) in scope.row.tags"
                    :key="tagIndex"
                    closable
                    @close="() => removeTag(scope.$index, tagIndex)"
                    style="margin: 2px;"
                  >
                    {{ tag }}
                  </el-tag>
                  <el-input
                    v-if="scope.row.inputVisible"
                    ref="tagInputRef"
                    v-model="scope.row.inputValue"
                    size="small"
                    class="spec-tag-input"
                    @keyup.enter="() => handleTagInputConfirm(scope.$index)"
                    @blur="() => handleTagInputConfirm(scope.$index)"
                  />
                  <el-button
                    v-else
                    size="small"
                    @click="() => showTagInput(scope.$index)"
                  >
                    + 添加
                  </el-button>
                  <span class="spec-tip">
                    单个规格值最多10个字符，如白色，至多添加20个规格值
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="82" align="center" fixed="right">
              <template #default="scope">
                <el-button
                  link
                  type="danger"
                  icon="Delete"
                  @click="removeSpec(scope.$index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 10px;">
            <el-button type="primary" plain icon="Plus" @click="addSpec">添加规格</el-button>
            <span style="color: #909399; font-size: 12px; margin-left: 10px;">
              +添加（{{ itemForm.specs.length }}/2）
            </span>
          </div>
        </el-form-item>

        <!-- SKU列表 -->
        <el-form-item label="SKU列表" v-if="itemForm.skus && itemForm.skus.length > 0">
          <el-table :data="itemForm.skus" border class="sku-table" table-layout="auto" style="width: 100%;">
            <el-table-column label="序号" type="index" width="72" align="center" />
            <el-table-column label="属性" prop="specText" min-width="220" show-overflow-tooltip />
            <el-table-column label="启用状态" width="108" align="center">
              <template #default="scope">
                <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0" />
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <!-- 单品信息 -->
        <el-form-item label="单品信息" prop="singleInfo">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input v-model="itemForm.singlePrice" placeholder="请输入单价">
                <template #append>元</template>
              </el-input>
            </el-col>
          </el-row>
        </el-form-item>

        <!-- 备注 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="备注说明" prop="remark">
              <el-input
                v-model="itemForm.remark"
                type="textarea"
                :rows="3"
                placeholder="请输入备注说明"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelItem">取 消</el-button>
          <el-button type="primary" @click="submitItemForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 采购对话框 -->
    <el-dialog title="选择物品" v-model="selectItemDialogVisible" width="800px" append-to-body>
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input v-model="itemSearchKeyword" placeholder="请输入物品名称" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="searchAvailableItems">搜索</el-button>
        </el-form-item>
      </el-form>

      <!-- 物品列表 -->
      <el-table :data="availableItemList" @expand-change="handleItemExpand" row-key="id" max-height="400">
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
        <el-table-column label="库存" prop="totalStock" width="100" />
      </el-table>

      <div style="margin-top: 10px; color: #909399;">
        已选择：{{ selectedSkuList.length }} 项
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectItemDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmItemSelection">确定了</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 出入库详情对话框 -->
    <el-dialog title="出入库记录详情" v-model="stockDetailVisible" width="1100px" class="stock-detail-dialog" append-to-body>
      <div v-loading="stockDetailLoading" class="stock-detail-panel">
        <div class="detail-actions">
          <el-button
            icon="CircleClose"
            :disabled="stockDetail.recordStatus === 'voided'"
            @click="handleVoidStock(stockDetail)"
          >
            作废记录
          </el-button>
          <el-tag v-if="stockDetail.recordStatus === 'voided'" type="danger">已作废</el-tag>
        </div>

        <div class="detail-heading">
          <div>
            <strong>业务类型：{{ stockDetail.businessTypeLabel || '-' }}</strong>
            <span>创建时间：{{ formatDate(stockDetail.createTime || stockDetail.stockDate) || '-' }}</span>
          </div>
          <el-tag :type="stockDetail.quantity > 0 ? 'success' : 'danger'">
            {{ stockDetail.stockTypeLabel || '-' }} {{ stockDetail.quantity > 0 ? '+' : '' }}{{ stockDetail.quantity || 0 }}
          </el-tag>
        </div>

        <div class="detail-grid">
          <div>
            <label>物品名称</label>
            <span>{{ stockDetail.itemName || '-' }}</span>
          </div>
          <div>
            <label>物品规格</label>
            <span>{{ stockDetail.specText && stockDetail.specText !== '默认' ? stockDetail.specText : '-' }}</span>
          </div>
          <div>
            <label>库存变化</label>
            <span>{{ stockDetail.stockBefore ?? '-' }} -> {{ stockDetail.stockAfter ?? '-' }}</span>
          </div>
          <div>
            <label>角色类型</label>
            <span>{{ stockDetail.roleTypeLabel || '-' }}</span>
          </div>
          <div>
            <label>角色姓名</label>
            <span>{{ stockDetail.roleName || '-' }}</span>
          </div>
          <div>
            <label>经办日期</label>
            <span>{{ formatDate(stockDetail.recordDate || stockDetail.stockDate) || '-' }}</span>
          </div>
          <div>
            <label>经办人</label>
            <span>{{ stockDetail.operator || stockDetail.operatorName || '-' }}</span>
          </div>
          <div>
            <label>流水号</label>
            <span>{{ stockDetail.recordNo || '-' }}</span>
          </div>
          <div>
            <label>备注</label>
            <span>{{ stockDetail.remark || '-' }}</span>
          </div>
        </div>

        <el-divider content-position="left">关联业务</el-divider>
        <el-table :data="stockRelatedRows" border class="stock-detail-table" table-layout="auto">
          <el-table-column label="业务单号" prop="businessNo" min-width="180" show-overflow-tooltip>
            <template #default="scope">
              <el-button
                v-if="scope.row.businessNo && scope.row.saleOrderId"
                link
                type="primary"
                @click="openSaleOrder(scope.row.saleOrderId)"
              >{{ scope.row.businessNo }}</el-button>
              <span v-else-if="scope.row.businessNo">{{ scope.row.businessNo }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="业务类型" prop="businessTypeLabel" width="120" />
          <el-table-column label="业务来源" prop="sourceLabel" width="130" />
          <el-table-column label="经办人" prop="operator" width="120" show-overflow-tooltip />
          <el-table-column label="经办日期" prop="recordDate" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.recordDate) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="创建时间" prop="createTime" width="170">
            <template #default="scope">
              {{ formatDate(scope.row.createTime) || '-' }}
            </template>
          </el-table-column>
        </el-table>

        <template v-if="stockDetail.purchaseOrder">
          <el-divider content-position="left">采购单信息</el-divider>
          <div class="detail-grid">
            <div>
              <label>采购单号</label>
              <span>{{ stockDetail.purchaseOrder.orderNo || '-' }}</span>
            </div>
            <div>
              <label>采购日期</label>
              <span>{{ formatDate(stockDetail.purchaseOrder.purchaseDate) || '-' }}</span>
            </div>
            <div>
              <label>采购状态</label>
              <span>{{ stockDetail.purchaseOrder.statusLabel || '-' }}</span>
            </div>
            <div>
              <label>支付方式</label>
              <span>{{ stockDetail.purchaseOrder.paymentMethodLabel || '-' }}</span>
            </div>
            <div>
              <label>账户</label>
              <span>{{ stockDetail.purchaseOrder.accountName || '-' }}</span>
            </div>
            <div>
              <label>总金额</label>
              <span>¥ {{ stockDetail.purchaseOrder.totalAmount || '0.00' }}</span>
            </div>
          </div>

          <el-table :data="stockDetail.purchaseItems || []" border class="stock-detail-table" table-layout="auto">
            <el-table-column label="物品名称" prop="itemName" min-width="160" show-overflow-tooltip />
            <el-table-column label="物品规格" prop="specText" min-width="140" show-overflow-tooltip />
            <el-table-column label="采购单价" prop="unitPrice" width="120">
              <template #default="scope">¥ {{ scope.row.unitPrice || '0.00' }}</template>
            </el-table-column>
            <el-table-column label="采购数量" prop="quantity" width="110" align="center" />
            <el-table-column label="采购总价" prop="totalAmount" width="120">
              <template #default="scope">¥ {{ scope.row.totalAmount || '0.00' }}</template>
            </el-table-column>
            <el-table-column label="备注" prop="remark" min-width="140" show-overflow-tooltip />
          </el-table>
        </template>
      </div>
    </el-dialog>

    <!-- 销售订单详情 -->
    <el-dialog title="销售订单详情" v-model="saleOrderVisible" width="900px" append-to-body>
      <div v-loading="saleOrderLoading">
        <el-descriptions v-if="saleOrder.order" :column="3" border size="small">
          <el-descriptions-item label="订单号">{{ saleOrder.order.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="订单类型">{{ saleOrder.order.orderTypeName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ saleOrder.order.statusName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学员">{{ saleOrder.order.studentName }}</el-descriptions-item>
          <el-descriptions-item label="家长手机">{{ saleOrder.order.parentPhone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="经办日期">{{ formatDate(saleOrder.order.enrollDate) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="订单总额">¥ {{ saleOrder.order.totalAmount }}</el-descriptions-item>
          <el-descriptions-item label="应收">¥ {{ saleOrder.order.receivableAmount }}</el-descriptions-item>
          <el-descriptions-item label="实收">¥ {{ saleOrder.order.paidAmount }}（欠费 ¥ {{ saleOrder.order.arrearsAmount }}）</el-descriptions-item>
          <el-descriptions-item label="经办人">{{ saleOrder.order.createBy || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ saleOrder.order.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="left">订单明细</el-divider>
        <el-table :data="saleOrder.items || []" border size="small">
          <el-table-column label="类型" prop="itemTypeName" width="70" align="center" />
          <el-table-column label="名称" prop="itemName" min-width="140" show-overflow-tooltip />
          <el-table-column label="规格/定价" prop="specName" min-width="120" show-overflow-tooltip />
          <el-table-column label="数量" prop="quantity" width="70" align="center" />
          <el-table-column label="单价" width="100"><template #default="{ row }">¥ {{ row.unitPrice }}</template></el-table-column>
          <el-table-column label="小计" width="100"><template #default="{ row }">¥ {{ row.subtotalPrice }}</template></el-table-column>
          <el-table-column label="备注" prop="remark" min-width="120" show-overflow-tooltip />
        </el-table>
        <el-divider content-position="left">出库流水</el-divider>
        <el-table :data="saleOrder.stockRecords || []" border size="small">
          <el-table-column label="流水号" prop="recordNo" min-width="160" />
          <el-table-column label="物品" prop="itemName" min-width="120" />
          <el-table-column label="规格" prop="skuName" width="110" />
          <el-table-column label="数量" prop="quantity" width="70" align="center" />
          <el-table-column label="库存变化" width="110" align="center">
            <template #default="{ row }">{{ row.stockBefore }} → {{ row.stockAfter }}</template>
          </el-table-column>
          <el-table-column label="状态" prop="recordStatusLabel" width="80" align="center" />
        </el-table>
      </div>
    </el-dialog>

    <ExcelImportDialog
      v-model="feeImportVisible"
      title="导入费用"
      template-url="ast/inventory/fee/import/template"
      template-name="费用导入模板.xlsx"
      upload-url="/ast/inventory/fee/import"
      :tips="['费用名称不能与已有费用重复（不做覆盖更新）', '关联课程填课程名称，多个用逗号或顿号分隔', '任一行有误则整批不导入']"
      @success="getFeeList"
    />

    <!-- 导入采购单对话框 -->
    <el-dialog title="导入采购" v-model="importPurchaseDialogVisible" width="680px" append-to-body>
      <div class="import-purchase-dialog">
        <div class="import-step">
          <strong>1. 按要求填写模板文件</strong>
          <el-button link type="primary" @click="handleDownloadPurchaseTemplate">下载导入模板</el-button>
        </div>
        <div class="import-step">
          <strong>2. 选择需要导入的文件，并开始导入</strong>
          <el-upload
            ref="purchaseUploadRef"
            accept=".xlsx,.xls"
            :auto-upload="false"
            :limit="1"
            :file-list="importPurchaseFileList"
            :on-change="handlePurchaseFileChange"
            :on-remove="handlePurchaseFileRemove"
          >
            <el-button type="primary" plain icon="Upload">添加文件</el-button>
            <template #tip>
              <div class="el-upload__tip">请使用模板文件，系统会按物品名称和物品规格匹配 SKU。</div>
            </template>
          </el-upload>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importPurchaseDialogVisible = false">取 消</el-button>
          <el-button type="primary" :loading="importPurchaseLoading" @click="submitImportPurchase">导 入</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 采购详情对话框 -->
    <el-dialog title="新建采购" v-model="purchaseDialogVisible" width="1000px" class="stock-form-dialog" append-to-body>
      <el-form ref="purchaseFormRef" :model="purchaseForm" label-width="100px" class="stock-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购日期" prop="purchaseDate">
              <el-date-picker
                v-model="purchaseForm.purchaseDate"
                type="date"
                placeholder="选择日期"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 物品SKU列表 -->
        <el-divider content-position="left">物品明细</el-divider>
        <el-button type="primary" plain icon="Plus" @click="openSelectItemDialog" style="margin-bottom: 10px;">
          选择物品
        </el-button>

        <el-table :data="purchaseForm.items" border class="stock-detail-table" table-layout="auto" style="width: 100%;">
          <el-table-column label="物品名称" prop="itemName" min-width="150" show-overflow-tooltip />
          <el-table-column label="物品规格" prop="specText" min-width="130" show-overflow-tooltip />
          <el-table-column label="单价(元)" width="120">
            <template #default="scope">
              <el-input-number v-model="scope.row.price" :min="0" :precision="2" :controls="false" style="width: 100%;" />
            </template>
          </el-table-column>
          <el-table-column label="采购数量" width="130">
            <template #default="scope">
              <div class="quantity-cell">
                <el-input-number v-model="scope.row.quantity" :min="1" :controls="false" style="width: 100%;" />
                <span class="quantity-stock-tip">库存: {{ scope.row.stock }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="小计(元)" width="110">
            <template #default="scope">
              ¥ {{ (scope.row.price * scope.row.quantity).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="76" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="danger" icon="Delete" @click="removePurchaseItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="text-align: right; margin-top: 10px; font-size: 16px;">
          <span style="font-weight: bold;">总数：{{ purchaseTotalQuantity }}</span>
          <span style="margin-left: 20px; font-weight: bold; color: #ff6700;">
            合计：¥ {{ purchaseTotalAmount }}
          </span>
        </div>

        <!-- 支付信息 -->
        <el-divider content-position="left">支付信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="支付方式" prop="paymentMethod">
              <el-select v-model="purchaseForm.paymentMethod" placeholder="请选择支付方式" style="width: 100%;">
                <el-option label="现金" value="cash" />
                <el-option label="微信" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="银行卡" value="bank" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账户" prop="account">
              <div class="account-select-line">
                <el-select v-model="purchaseForm.account" placeholder="请选择账户">
                  <el-option label="现金账户" value="现金账户" />
                  <el-option label="微信账户" value="微信账户" />
                  <el-option label="支付宝账户" value="支付宝账户" />
                  <el-option label="银行卡账户" value="银行卡账户" />
                </el-select>
                <el-button type="primary" link>设置</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="年度账本" prop="yearBook">
              <el-input v-model="purchaseForm.yearBook" placeholder="选择、2007-2100年" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="采购备注" prop="remark">
              <el-input
                v-model="purchaseForm.remark"
                type="textarea"
                :rows="3"
                maxlength="200"
                show-word-limit
                placeholder="选填，200字以内"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="purchaseDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitPurchase">完 成</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 领用对话框 -->
    <el-dialog title="领用" v-model="receiveDialogVisible" width="900px" class="stock-form-dialog" append-to-body>
      <el-form ref="receiveFormRef" :model="receiveForm" label-width="100px" class="stock-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="领用时间" prop="receiveTime">
              <el-date-picker
                v-model="receiveForm.receiveTime"
                type="datetime"
                placeholder="选择日期时间"
                style="width: 100%;"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="roleType">
              <el-select v-model="receiveForm.roleType" placeholder="请选择角色" style="width: 100%;" @change="handleRoleTypeChange">
                <el-option label="学员" value="student" />
                <el-option label="员工" value="staff" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色名称" prop="roleName">
              <el-select
                v-model="receiveForm.roleName"
                :placeholder="receiveForm.roleType === 'other' ? '请输入' : '请选择'"
                style="width: 100%;"
                filterable
                clearable
                :loading="roleNameLoading"
                :allow-create="receiveForm.roleType === 'other'"
                default-first-option
              >
                <el-option
                  v-for="item in roleNameOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 物品SKU列表 -->
        <el-divider content-position="left">物品明细</el-divider>
        <el-button type="primary" plain icon="Plus" @click="openSelectItemDialogForReceive" style="margin-bottom: 10px;">
          选择物品
        </el-button>

        <el-table :data="receiveForm.items" border class="stock-detail-table" table-layout="auto" style="width: 100%;">
          <el-table-column label="物品名称" prop="itemName" min-width="150" show-overflow-tooltip />
          <el-table-column label="物品规格" prop="specText" min-width="130" show-overflow-tooltip />
          <el-table-column label="当前库存" prop="stock" width="86" align="center" />
          <el-table-column label="领用数量" width="128">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="1"
                :controls="false"
                style="width: 100%;"
              />
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="180">
            <template #default="scope">
              <el-input
                v-model="scope.row.remark"
                type="textarea"
                :rows="2"
                maxlength="200"
                show-word-limit
                placeholder="选填，最多200个字"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="76" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="danger" icon="Delete" @click="removeReceiveItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="text-align: right; margin-top: 10px; font-size: 16px;">
          <span style="font-weight: bold;">总数量：{{ receiveTotalQuantity }}</span>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="receiveDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitReceive">完 成</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 退领对话框 -->
    <el-dialog title="退领" v-model="returnDialogVisible" width="900px" class="stock-form-dialog" append-to-body>
      <el-form ref="returnFormRef" :model="returnForm" label-width="100px" class="stock-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="退领时间" prop="returnTime">
              <el-date-picker
                v-model="returnForm.returnTime"
                type="datetime"
                placeholder="选择日期时间"
                style="width: 100%;"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="roleType">
              <el-select v-model="returnForm.roleType" placeholder="请选择角色" style="width: 100%;" @change="handleReturnRoleTypeChange">
                <el-option label="学员" value="student" />
                <el-option label="员工" value="staff" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色名称" prop="roleName">
              <el-select
                v-model="returnForm.roleName"
                :placeholder="returnForm.roleType === 'other' ? '请输入' : '请选择'"
                style="width: 100%;"
                filterable
                clearable
                :loading="returnRoleNameLoading"
                :allow-create="returnForm.roleType === 'other'"
                default-first-option
              >
                <el-option
                  v-for="item in returnRoleNameOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 物品SKU列表 -->
        <el-divider content-position="left">物品明细</el-divider>
        <el-button type="primary" plain icon="Plus" @click="openSelectItemDialogForReturn" style="margin-bottom: 10px;">
          选择物品
        </el-button>

        <el-table :data="returnForm.items" border class="stock-detail-table" table-layout="auto" style="width: 100%;">
          <el-table-column label="物品名称" prop="itemName" min-width="150" show-overflow-tooltip />
          <el-table-column label="物品规格" prop="specText" min-width="130" show-overflow-tooltip />
          <el-table-column label="当前库存" prop="stock" width="86" align="center" />
          <el-table-column label="退领数量" width="128">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.quantity"
                :min="1"
                :controls="false"
                style="width: 100%;"
              />
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="180">
            <template #default="scope">
              <el-input
                v-model="scope.row.remark"
                type="textarea"
                :rows="2"
                maxlength="200"
                show-word-limit
                placeholder="选填，最多200个字"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="76" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="danger" icon="Delete" @click="removeReturnItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="text-align: right; margin-top: 10px; font-size: 16px;">
          <span style="font-weight: bold;">总数量：{{ returnTotalQuantity }}</span>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="returnDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitReturn">完 成</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 盘点对话框 -->
    <el-dialog title="库存盘点" v-model="inventoryDialogVisible" width="1200px" class="stock-form-dialog" append-to-body>
      <el-form ref="inventoryFormRef" :model="inventoryForm" label-width="100px" class="stock-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="盘点日期" prop="inventoryDate" required>
              <el-date-picker
                v-model="inventoryForm.inventoryDate"
                type="date"
                placeholder="选择盘点日期"
                style="width: 100%;"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="操作人" prop="operator" required>
              <el-input v-model="inventoryForm.operator" placeholder="请输入操作人" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 物品SKU列表 -->
        <el-divider content-position="left">盘点明细</el-divider>
        <el-button type="primary" plain icon="Plus" @click="openSelectItemDialogForInventory" style="margin-bottom: 10px;">
          选择物品
        </el-button>

        <el-table :data="inventoryForm.items" border class="stock-detail-table inventory-detail-table" table-layout="auto" style="width: 100%;" max-height="450">
          <el-table-column label="物品名称" prop="itemName" min-width="140" show-overflow-tooltip />
          <el-table-column label="物品规格" prop="specText" min-width="120" show-overflow-tooltip />
          <el-table-column label="原库存" prop="originalStock" width="82" align="center">
            <template #default="scope">
              <span style="color: #909399;">{{ scope.row.originalStock }}</span>
            </template>
          </el-table-column>
          <el-table-column label="当前库存" width="120" align="center">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.currentStock"
                :min="0"
                :controls="false"
                style="width: 100%;"
                @change="calculateStockChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="库存变动" width="92" align="center">
            <template #default="scope">
              <span
                :style="{
                  color: scope.row.stockChange > 0 ? '#67C23A' : scope.row.stockChange < 0 ? '#F56C6C' : '#909399',
                  fontWeight: 'bold'
                }"
              >
                {{ scope.row.stockChange > 0 ? '+' : '' }}{{ scope.row.stockChange }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150">
            <template #default="scope">
              <el-input
                v-model="scope.row.remark"
                placeholder="请输入备注"
                clearable
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="76" align="center" fixed="right">
            <template #default="scope">
              <el-button link type="danger" icon="Delete" @click="removeInventoryItem(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 15px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
          <el-row :gutter="20">
            <el-col :span="8">
              <div style="font-size: 14px;">
                <span style="color: #606266;">盘点物品数：</span>
                <span style="font-weight: bold; color: #409EFF;">{{ inventoryForm.items.length }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div style="font-size: 14px;">
                <span style="color: #606266;">盘盈数量：</span>
                <span style="font-weight: bold; color: #67C23A;">+{{ inventoryProfitCount }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div style="font-size: 14px;">
                <span style="color: #606266;">盘亏数量：</span>
                <span style="font-weight: bold; color: #F56C6C;">{{ inventoryLossCount }}</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="inventoryDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitInventory">完成盘点</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新建/编辑费用对话框 -->
    <el-dialog :title="feeTitle" v-model="feeDialogVisible" width="600px" append-to-body>
      <el-alert
        title="请添加课程和物品以外的收费项目"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />

      <el-form ref="feeFormRef" :model="feeForm" :rules="feeRules" label-width="100px">
        <el-form-item label="费用名称" prop="feeName">
          <el-input
            v-model="feeForm.feeName"
            placeholder="请输入费用名称，如考试费"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="售卖单价" prop="price">
          <el-input-number
            v-model="feeForm.price"
            :min="0"
            :precision="2"
            :controls="false"
            style="width: 100%;"
            placeholder="请输入"
          >
            <template #append>元</template>
          </el-input-number>
        </el-form-item>

        <el-form-item label="绑定课程">
          <div style="width: 100%;">
            <!-- 已选择的课程标签 -->
            <div v-if="feeForm.courseIds && feeForm.courseIds.length > 0" style="margin-bottom: 10px;">
              <el-tag
                v-for="(courseName, index) in feeForm.courseNames"
                :key="feeForm.courseIds[index]"
                closable
                @close="removeCourse(index)"
                style="margin-right: 8px; margin-bottom: 8px;"
                type="primary"
              >
                {{ courseName }}
              </el-tag>
            </div>

            <!-- 选择课程按钮 -->
            <el-button
              icon="Plus"
              @click="openSelectCourseDialog('fee')"
              style="width: 100%;"
            >
              {{ feeForm.courseIds && feeForm.courseIds.length > 0 ? '继续添加课程' : '选择课程' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="线上售卖">
          <el-switch v-model="feeForm.onlineSale" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="feeDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitFee">保 存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择课程对话框 -->
    <el-dialog title="选择课程" v-model="selectCourseDialogVisible" width="900px" append-to-body>
      <el-input
        v-model="courseSearchKeyword"
        placeholder="请输入课程名称"
        clearable
        style="margin-bottom: 15px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-table
        ref="courseTableRef"
        :data="filteredCourseList"
        border
        max-height="400"
        @selection-change="handleCourseSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="课程名称" prop="courseName" width="200" />
        <el-table-column label="课程类型" prop="courseType" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.courseType === '一对一'" type="success">一对一</el-tag>
            <el-tag v-else type="warning">一对多</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="定价标准" prop="priceStandard" min-width="200" />
      </el-table>

      <div style="margin-top: 15px; color: #909399; font-size: 14px;">
        已选择：<span style="color: #409EFF; font-weight: bold;">{{ selectedCourseCount }}</span> 项
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="selectCourseDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmCourseSelection">选好了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantInventory">
import { nextTick } from 'vue';
import * as inventoryApi from '@/api/assistant/inventory';
import ExcelImportDialog from '@/components/ExcelImportDialog/index.vue';
import { listCourseOptions } from '@/api/assistant/course';
import useUserStore from '@/store/modules/user';

const {
  addFee,
  addItem,
  changeFeeStatus,
  createInventory,
  createPurchase,
  createReceive,
  createReturn,
  delFee,
  delItem,
  getFee,
  getItem,
  getStockRecord,
  importPurchase,
  listAvailableItems,
  listFee,
  listItem,
  listRoleOptions,
  listStockRecord,
  updateFee,
  updateItem,
  voidStockRecord
} = inventoryApi;

const { proxy } = getCurrentInstance();
const userStore = useUserStore();

// Tab相关
const activeTab = ref('item');
const itemSubTab = ref('itemManage'); // 物品子Tab
const showSearch = ref(true);

// 物品列表相关
const itemList = ref([]);
const itemLoading = ref(false);
const itemTotal = ref(0);

// 物品查询参数
const itemQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  itemName: undefined,
  status: ''
});

// 出入库列表相关
const stockList = ref([]);
const stockLoading = ref(false);
const stockTotal = ref(0);
const stockTableKey = ref(0);
const stockItemOptions = ref([]);
const stockSummary = ref({
  currentCount: 0,
  inTotal: 0,
  outTotal: 0,
  netTotal: 0
});
const stockDetailVisible = ref(false);
const stockDetailLoading = ref(false);
const stockDetail = ref({});
const importPurchaseDialogVisible = ref(false);
const importPurchaseLoading = ref(false);
const importPurchaseFileList = ref([]);
const purchaseUploadRef = ref(null);

// 出入库查询参数
const stockQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  keyword: undefined,
  itemNames: [],
  dateRange: [],
  businessType: '', // 业务类型：采购、领用、退领
  stockTypes: ['out', 'in'],
  relatedType: '',
  relatedName: '',
  excludeVoided: true
});

// 物品表单相关
const itemOpen = ref(false);
const itemTitle = ref('');
const itemForm = ref({
  itemName: '',
  itemType: '1',
  itemImages: [],
  imageUrl: '',
  enableStock: 1,
  warningStock: 0,
  onlineSale: 0,
  specs: [],
  skus: [],
  singlePrice: '',
  courseIds: [],
  courseNames: [],
  remark: ''
});
const itemRules = ref({
  itemName: [
    { required: true, message: '物品名称不能为空', trigger: 'blur' }
  ],
  itemType: [
    { required: true, message: '请选择物品类型', trigger: 'change' }
  ]
});

// Tag输入框引用
const tagInputRef = ref(null);

// 选择物品对话框
const selectItemDialogVisible = ref(false);
const itemSearchKeyword = ref('');
const availableItemList = ref([]);
const selectedSkuList = ref([]); // 存储所有选中的SKU

// 采购对话框
const purchaseDialogVisible = ref(false);
const purchaseForm = ref({
  purchaseDate: new Date(),
  items: [],
  paymentMethod: '',
  account: '',
  yearBook: '',
  remark: ''
});

// 计算采购总数量
const purchaseTotalQuantity = computed(() => {
  return purchaseForm.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
});

// 计算采购总金额
const purchaseTotalAmount = computed(() => {
  const total = purchaseForm.value.items.reduce((sum, item) => {
    return sum + (item.price || 0) * (item.quantity || 0);
  }, 0);
  return total.toFixed(2);
});

// 领用对话框
const receiveDialogVisible = ref(false);
const receiveFormRef = ref();
const receiveForm = ref({
  receiveTime: '',
  roleType: '',
  roleName: '',
  items: []
});
const roleNameOptions = ref([]); // 角色名称选项
const roleNameLoading = ref(false);
const currentDialogType = ref(''); // 当前打开的对话框类型：receive/return

// 计算领用总数量
const receiveTotalQuantity = computed(() => {
  return receiveForm.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
});

// 退领对话框
const returnDialogVisible = ref(false);
const returnFormRef = ref();
const returnForm = ref({
  returnTime: '',
  roleType: '',
  roleName: '',
  items: []
});
const returnRoleNameOptions = ref([]); // 退领角色名称选项
const returnRoleNameLoading = ref(false);

// 计算退领总数量
const returnTotalQuantity = computed(() => {
  return returnForm.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
});

// 盘点对话框
const inventoryDialogVisible = ref(false);
const inventoryForm = ref({
  inventoryDate: '',
  operator: '',
  items: []
});

// 计算盘盈数量
const inventoryProfitCount = computed(() => {
  return inventoryForm.value.items.reduce((sum, item) => {
    return sum + (item.stockChange > 0 ? item.stockChange : 0);
  }, 0);
});

// 计算盘亏数量
const inventoryLossCount = computed(() => {
  return inventoryForm.value.items.reduce((sum, item) => {
    return sum + (item.stockChange < 0 ? item.stockChange : 0);
  }, 0);
});

// ==================== 费用管理 ====================
const feeQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  feeName: '',
  status: ''
});
const feeLoading = ref(false);
const feeList = ref([]);
const feeTotal = ref(0);

// 新建/编辑费用对话框
const feeDialogVisible = ref(false);
const feeTitle = ref('');
const feeForm = ref({
  id: null,
  feeName: '',
  price: null,
  onlineSale: 0,
  status: 1,
  courseIds: [],
  courseNames: []
});
const feeRules = {
  feeName: [
    { required: true, message: '请输入费用名称', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入售卖单价', trigger: 'blur' }
  ]
};

// 选择课程对话框
const selectCourseDialogVisible = ref(false);
const courseSearchKeyword = ref('');
const courseList = ref([]);
const selectedCourses = ref([]);
const courseTableRef = ref(null);
const courseSelectTarget = ref('fee');

// 过滤后的课程列表
const filteredCourseList = computed(() => {
  if (!courseSearchKeyword.value) {
    return courseList.value;
  }
  return courseList.value.filter(course =>
    (course.courseName || '').includes(courseSearchKeyword.value)
  );
});

// 已选择课程数量
const selectedCourseCount = computed(() => {
  return selectedCourses.value.length;
});

const feeImportVisible = ref(false);
const saleOrderVisible = ref(false);
const saleOrderLoading = ref(false);
const saleOrder = ref({});

async function openSaleOrder(orderId) {
  saleOrderVisible.value = true;
  saleOrderLoading.value = true;
  saleOrder.value = {};
  try {
    const response = await inventoryApi.getSaleOrder(orderId);
    saleOrder.value = response.data || {};
  } finally {
    saleOrderLoading.value = false;
  }
}

const stockRelatedRows = computed(() => {
  const detail = stockDetail.value || {};
  if (detail.purchaseOrder) {
    return [{
      businessNo: detail.purchaseOrder.orderNo,
      businessTypeLabel: '采购',
      sourceLabel: '采购单',
      operator: detail.purchaseOrder.operatorName || detail.operator || '-',
      recordDate: detail.purchaseOrder.purchaseDate || detail.recordDate,
      createTime: detail.purchaseOrder.createTime || detail.createTime
    }];
  }
  if (detail.saleOrderId) {
    return [{
      businessNo: `销售订单 #${detail.saleOrderId}`,
      saleOrderId: detail.saleOrderId,
      businessTypeLabel: detail.businessTypeLabel || '销售',
      sourceLabel: '报名/续费订单',
      operator: detail.operator || detail.operatorName || '-',
      recordDate: detail.recordDate || detail.stockDate,
      createTime: detail.createTime || detail.stockDate
    }];
  }
  if (detail.businessNo) {
    return [{
      businessNo: detail.businessNo,
      businessTypeLabel: detail.businessTypeLabel || '-',
      sourceLabel: detail.sourceType || '-',
      operator: detail.operator || detail.operatorName || '-',
      recordDate: detail.recordDate || detail.stockDate,
      createTime: detail.createTime || detail.stockDate
    }];
  }
  return [];
});

function cleanQuery(query) {
  const result = {};
  Object.keys(query || {}).forEach(key => {
    const value = query[key];
    if (value !== '' && value !== undefined && value !== null) {
      result[key] = value;
    }
  });
  return result;
}

function formatDate(value, endOfDay = false) {
  if (!value) {
    return undefined;
  }
  const pad = num => String(num).padStart(2, '0');
  if (typeof value === 'string') {
    const rawValue = value.trim();
    const normalizedValue = rawValue.replace('T', ' ').replace(/\.\d+$/, '');
    if (/^\d{4}-\d{2}-\d{2}$/.test(normalizedValue)) {
      return `${normalizedValue} ${endOfDay ? '23:59:59' : '00:00:00'}`;
    }
    if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(normalizedValue)) {
      return normalizedValue.slice(0, 19);
    }
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value).slice(0, 19);
  }
  if (endOfDay) {
    date.setHours(23, 59, 59, 0);
  }
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hour = pad(date.getHours());
  const minute = pad(date.getMinutes());
  const second = pad(date.getSeconds());
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

function buildStockQueryParams() {
  const dateRange = stockQueryParams.value.dateRange || [];
  const stockTypes = stockQueryParams.value.stockTypes || [];
  return cleanQuery({
    ...stockQueryParams.value,
    itemNames: (stockQueryParams.value.itemNames || []).join(','),
    stockType: stockTypes.length === 1 ? stockTypes[0] : undefined,
    stockTypes: undefined,
    beginTime: dateRange[0] ? formatDate(dateRange[0]) : undefined,
    endTime: dateRange[1] ? formatDate(dateRange[1], true) : undefined,
    dateRange: undefined,
    businessType: stockQueryParams.value.businessType || undefined,
    relatedType: stockQueryParams.value.relatedType || undefined,
    relatedName: stockQueryParams.value.relatedName || undefined,
    excludeVoided: stockQueryParams.value.excludeVoided
  });
}

function refreshInventoryViews({ refreshStock = true, refreshItems = true, refreshOptions = false } = {}) {
  nextTick(() => {
    window.setTimeout(() => {
      if (refreshOptions) {
        loadStockItemOptions();
      }
      if (refreshStock) {
        getStockList();
      }
      if (refreshItems) {
        getItemList();
      }
    }, 0);
  });
}

function normalizeNumber(value, fallback = 0) {
  if (value === '' || value === undefined || value === null) {
    return fallback;
  }
  return Number(value);
}

function getValidSpecs() {
  return (itemForm.value.specs || []).filter(spec => spec.name && spec.tags && spec.tags.length > 0).slice(0, 2);
}

function buildSkuPayloads(validSpecs) {
  const fallbackPrice = normalizeNumber(itemForm.value.singlePrice, 0);
  return (itemForm.value.skus || []).map(sku => {
    const skuSpecs = sku.specs || [];
    const spec1Value = sku.spec1Value || sku.spec1_value || skuSpecs[0]?.value || null;
    const spec2Value = sku.spec2Value || sku.spec2_value || skuSpecs[1]?.value || null;
    return {
      skuName: sku.skuName || sku.specText || [spec1Value, spec2Value].filter(Boolean).join(', ') || '默认',
      specText: sku.specText || [spec1Value, spec2Value].filter(Boolean).join(', ') || '默认',
      spec1Value,
      spec2Value,
      price: normalizeNumber(sku.price, fallbackPrice),
      costPrice: normalizeNumber(sku.costPrice, 0),
      stock: normalizeNumber(sku.stock, 0),
      status: normalizeNumber(sku.status, 1),
      specs: skuSpecs.length ? skuSpecs : validSpecs.map((spec, index) => ({
        name: spec.name,
        value: index === 0 ? spec1Value : spec2Value
      })).filter(spec => spec.value)
    };
  });
}

function buildItemPayload() {
  const validSpecs = getValidSpecs();
  return {
    id: itemForm.value.id,
    itemNo: itemForm.value.itemNo || itemForm.value.itemCode,
    itemName: itemForm.value.itemName,
    itemType: normalizeNumber(itemForm.value.itemType, 1),
    defaultPrice: normalizeNumber(itemForm.value.singlePrice || itemForm.value.defaultPrice, 0),
    imageUrl: itemForm.value.imageUrl,
    spec1Name: validSpecs[0]?.name,
    spec1Values: validSpecs[0]?.tags?.join(','),
    spec2Name: validSpecs[1]?.name,
    spec2Values: validSpecs[1]?.tags?.join(','),
    enableStock: itemForm.value.enableStock,
    warningStock: normalizeNumber(itemForm.value.warningStock, 0),
    onlineSale: normalizeNumber(itemForm.value.onlineSale, 0),
    specs: validSpecs,
    skus: buildSkuPayloads(validSpecs),
    courseIds: itemForm.value.courseIds || [],
    courseNames: itemForm.value.courseNames || [],
    status: normalizeNumber(itemForm.value.status, 1),
    remark: itemForm.value.remark
  };
}

function buildItemPayloadFromDetail(detail) {
  const oldForm = itemForm.value;
  itemForm.value = detail;
  const payload = buildItemPayload();
  itemForm.value = oldForm;
  return payload;
}

function normalizeItemForm(data) {
  const specs = data.specs && data.specs.length ? data.specs : [{
    name: '',
    tags: [],
    inputVisible: false,
    inputValue: ''
  }];
  return {
    ...data,
    itemType: String(data.itemType || '1'),
    itemCode: data.itemCode || data.itemNo,
    enableStock: data.enableStock ?? 1,
    warningStock: data.warningStock ?? 0,
    onlineSale: data.onlineSale ?? 0,
    singlePrice: data.singlePrice ?? data.defaultPrice ?? '',
    imageUrl: data.imageUrl || '',
    courseIds: data.courseIds || [],
    courseNames: data.courseNames || (data.courseName ? data.courseName.split('、') : []),
    specs: specs.map(spec => ({
      name: spec.name || '',
      tags: spec.tags || [],
      inputVisible: false,
      inputValue: ''
    })),
    skus: (data.skus || []).map(sku => ({
      ...sku,
      specText: sku.specText || sku.skuName || '默认',
      specs: [
        data.spec1Name && sku.spec1Value ? { name: data.spec1Name, value: sku.spec1Value } : null,
        data.spec2Name && sku.spec2Value ? { name: data.spec2Name, value: sku.spec2Value } : null
      ].filter(Boolean),
      price: normalizeNumber(sku.price, data.defaultPrice || 0),
      stock: normalizeNumber(sku.stock, 0),
      status: normalizeNumber(sku.status, 1)
    }))
  };
}

function buildStockItems(items) {
  return (items || []).map(item => ({
    itemId: item.parentItemId,
    itemName: item.itemName,
    skuId: item.skuId,
    skuName: item.skuName || item.specText,
    specText: item.specText,
    quantity: normalizeNumber(item.quantity, 0),
    price: normalizeNumber(item.price, 0),
    currentStock: item.currentStock,
    actualStock: item.currentStock,
    remark: item.remark
  }));
}

/** Tab切换 */
function handleTabClick(tab) {
  if (tab.props.name === 'item') {
    // 切换到物品Tab时，默认显示物品管理子Tab
    if (itemSubTab.value === 'itemManage') {
      getItemList();
    } else if (itemSubTab.value === 'stockManage') {
      loadStockItemOptions();
      getStockList();
    }
  } else if (tab.props.name === 'fee') {
    // 切换到费用Tab时，加载费用列表
    getFeeList();
  }
}

/** 物品子Tab切换 */
function handleItemSubTabClick(tab) {
  if (tab.props.name === 'itemManage') {
    getItemList();
  } else if (tab.props.name === 'stockManage') {
    loadStockItemOptions();
    getStockList();
  }
}

/** 查询物品列表 */
function getItemList() {
  itemLoading.value = true;
  listItem(cleanQuery({
    ...itemQueryParams.value,
    status: itemQueryParams.value.status === '' ? undefined : Number(itemQueryParams.value.status)
  })).then(response => {
    itemList.value = response.rows || [];
    itemTotal.value = response.total || 0;
  }).finally(() => {
    itemLoading.value = false;
  });
}

/** 搜索物品 */
function handleItemQuery() {
  itemQueryParams.value.pageNum = 1;
  getItemList();
}

/** 重置物品搜索 */
function resetItemQuery() {
  itemQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    itemName: undefined,
    status: ''
  };
  handleItemQuery();
}

/** 添加物品 */
function handleAddItem() {
  resetItemForm();
  itemOpen.value = true;
  itemTitle.value = '新增物品';
}

/** 修改物品 */
function handleUpdateItem(row) {
  resetItemForm();
  getItem(row.id).then(response => {
    itemForm.value = normalizeItemForm(response.data || row);
    itemOpen.value = true;
    itemTitle.value = '修改物品';
  });
}

/** 删除物品 */
function handleDeleteItem(row) {
  proxy.$modal.confirm('是否确认删除物品名称为"' + row.itemName + '"的数据项？').then(() => {
    return delItem(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess('删除成功');
    getItemList();
  });
}

/** 物品状态变化 */
function handleItemStatusChange(row) {
  updateItemRowField(row, 'status', row.status, '状态修改成功');
}

/** 物品库存开关变化 */
function handleItemEnableStockChange(row) {
  updateItemRowField(row, 'enableStock', row.enableStock, '库存开关修改成功');
}

/** 物品线上售卖变化 */
function handleItemOnlineSaleChange(row) {
  updateItemRowField(row, 'onlineSale', row.onlineSale, '线上售卖状态修改成功');
}

function updateItemRowField(row, field, value, successMessage) {
  getItem(row.id).then(response => {
    const detail = normalizeItemForm(response.data || row);
    detail[field] = value;
    return updateItem(buildItemPayloadFromDetail(detail));
  }).then(() => {
    proxy.$modal.msgSuccess(successMessage);
  }).catch(() => {
    row[field] = row[field] === 1 ? 0 : 1;
  });
}

/** 查看出入库记录 */
function handleViewItem(row) {
  // 切换到出入库管理子Tab
  itemSubTab.value = 'stockManage';
  stockQueryParams.value.keyword = row.itemName;
  getStockList();
}

/** 导出物品 */
function handleExport() {
  proxy.download('ast/item/export', cleanQuery({
    ...itemQueryParams.value,
    status: itemQueryParams.value.status === '' ? undefined : Number(itemQueryParams.value.status)
  }), `item_${new Date().getTime()}.xlsx`);
}

/** 重置物品表单 */
function resetItemForm() {
  itemForm.value = {
    id: null,
    itemNo: '',
    itemCode: '',
    itemName: '',
    itemType: '1',
    itemImages: [],
    imageUrl: '',
    enableStock: 1,
    warningStock: 0,
    onlineSale: 0,
    specs: [],
    skus: [],
    singlePrice: '',
    courseIds: [],
    courseNames: [],
    status: 1,
    remark: ''
  };
  // 添加一个默认规格
  itemForm.value.specs.push({
    name: '',
    tags: [],
    inputVisible: false,
    inputValue: ''
  });
}

/** 取消物品 */
function cancelItem() {
  itemOpen.value = false;
  resetItemForm();
}

/** 提交物品表单 */
function submitItemForm() {
  proxy.$refs.itemFormRef.validate(valid => {
    if (valid) {
      const payload = buildItemPayload();
      const request = payload.id ? updateItem(payload) : addItem(payload);
      request.then(() => {
        proxy.$modal.msgSuccess(payload.id ? '修改成功' : '新增成功');
        itemOpen.value = false;
        getItemList();
      });
    }
  });
}

/** 添加规格 */
function addSpec() {
  if (itemForm.value.specs.length >= 2) {
    proxy.$modal.msgWarning('最多只能添加2个规格');
    return;
  }
  itemForm.value.specs.push({
    name: '',
    tags: [],
    inputVisible: false,
    inputValue: ''
  });
}

/** 删除规格 */
function removeSpec(index) {
  itemForm.value.specs.splice(index, 1);
  // 删除规格后自动重新生成SKU
  autoGenerateSKU();
}

/** 显示Tag输入框 */
function showTagInput(specIndex) {
  const spec = itemForm.value.specs[specIndex];
  if (spec.tags.length >= 20) {
    proxy.$modal.msgWarning('单个规格最多只能添加20个规格值');
    return;
  }
  spec.inputVisible = true;
  nextTick(() => {
    // 聚焦到输入框
    const inputs = document.querySelectorAll('.el-input__inner');
    if (inputs && inputs.length > 0) {
      inputs[inputs.length - 1]?.focus();
    }
  });
}

/** 确认Tag输入 */
function handleTagInputConfirm(specIndex) {
  const spec = itemForm.value.specs[specIndex];
  const inputValue = spec.inputValue?.trim();

  if (inputValue) {
    if (inputValue.length > 10) {
      proxy.$modal.msgWarning('单个规格值最多10个字符');
      return;
    }
    if (spec.tags.includes(inputValue)) {
      proxy.$modal.msgWarning('规格值已存在');
      spec.inputValue = '';
      return;
    }
    if (spec.tags.length >= 20) {
      proxy.$modal.msgWarning('单个规格最多只能添加20个规格值');
      spec.inputValue = '';
      return;
    }
    spec.tags.push(inputValue);
    // 自动生成SKU
    autoGenerateSKU();
  }

  spec.inputVisible = false;
  spec.inputValue = '';
}

/** 删除Tag */
function removeTag(specIndex, tagIndex) {
  itemForm.value.specs[specIndex].tags.splice(tagIndex, 1);
  // 删除Tag后自动重新生成SKU
  autoGenerateSKU();
}

/** 规格上移 */
function moveSpecUp(index) {
  if (index === 0) return;
  const temp = itemForm.value.specs[index];
  itemForm.value.specs[index] = itemForm.value.specs[index - 1];
  itemForm.value.specs[index - 1] = temp;
  // 重新生成SKU
  autoGenerateSKU();
}

/** 规格下移 */
function moveSpecDown(index) {
  if (index === itemForm.value.specs.length - 1) return;
  const temp = itemForm.value.specs[index];
  itemForm.value.specs[index] = itemForm.value.specs[index + 1];
  itemForm.value.specs[index + 1] = temp;
  // 重新生成SKU
  autoGenerateSKU();
}

/** 自动生成SKU */
function autoGenerateSKU() {
  // 过滤出有效的规格（有名称且有标签）
  const validSpecs = itemForm.value.specs.filter(s => s.name && s.tags && s.tags.length > 0);

  if (validSpecs.length === 0) {
    itemForm.value.skus = [];
    return;
  }

  // 将规格转换为数组格式
  const specArrays = validSpecs.map(spec => ({
    name: spec.name,
    values: spec.tags
  }));

  // 生成笛卡尔积
  function cartesian(arrays) {
    if (arrays.length === 0) return [[]];
    const [first, ...rest] = arrays;
    const restProduct = cartesian(rest);
    return first.values.flatMap(value =>
      restProduct.map(product => [{ name: first.name, value }, ...product])
    );
  }

  const combinations = cartesian(specArrays);

  // 保留已有SKU的价格和库存信息
  const oldSkuMap = new Map();
  itemForm.value.skus.forEach(sku => {
    oldSkuMap.set(sku.specText, {
      price: sku.price,
      stock: sku.stock,
      status: sku.status
    });
  });

  // 生成新的SKU列表
  itemForm.value.skus = combinations.map((combo, index) => {
    const specText = combo.map(c => c.value).join(', ');
    const oldData = oldSkuMap.get(specText) || { price: 0, stock: 0, status: 1 };

    return {
      id: index + 1,
      specText: specText,
      specs: combo,
      price: oldData.price,
      stock: oldData.stock,
      status: oldData.status
    };
  });
}

// ==================== 出入库管理相关方法 ====================

/** 查询出入库列表 */
function getStockList() {
  stockLoading.value = true;
  listStockRecord(buildStockQueryParams()).then(response => {
    stockTableKey.value += 1;
    stockList.value = response.rows || [];
    stockTotal.value = response.total || 0;
    stockSummary.value = response.summary || {
      currentCount: stockTotal.value,
      inTotal: 0,
      outTotal: 0,
      netTotal: 0
    };
  }).finally(() => {
    stockLoading.value = false;
  });
}

/** 加载出入库物品筛选项 */
function loadStockItemOptions() {
  return listAvailableItems({}).then(response => {
    stockItemOptions.value = response.data || [];
  });
}

/** 搜索出入库 */
function handleStockQuery() {
  stockQueryParams.value.pageNum = 1;
  getStockList();
}

/** 重置出入库搜索 */
function resetStockQuery() {
  stockQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    keyword: undefined,
    itemNames: [],
    dateRange: [],
    businessType: '', // 业务类型
    stockTypes: ['out', 'in'],
    relatedType: '',
    relatedName: '',
    excludeVoided: true
  };
  handleStockQuery();
}

/** 采购 */
function handlePurchase() {
  purchaseDialogVisible.value = true;
  purchaseForm.value = {
    purchaseDate: new Date(),
    items: [],
    paymentMethod: '',
    account: '',
    yearBook: '',
    remark: ''
  };
}

function handlePurchaseCommand(command) {
  if (command === 'import') {
    importPurchaseDialogVisible.value = true;
    importPurchaseFileList.value = [];
    return;
  }
  handlePurchase();
}

/** 领用 */
function handleReceive() {
  receiveDialogVisible.value = true;
  receiveForm.value = {
    receiveTime: formatDate(new Date()),
    roleType: '',
    roleName: '',
    items: []
  };
  roleNameOptions.value = [];
  nextTick(() => {
    receiveFormRef.value?.clearValidate();
  });
}

/** 退领 */
function handleReturn() {
  returnDialogVisible.value = true;
  returnForm.value = {
    returnTime: formatDate(new Date()),
    roleType: '',
    roleName: '',
    items: []
  };
  returnRoleNameOptions.value = [];
  nextTick(() => {
    returnFormRef.value?.clearValidate();
  });
}

/** 盘点 */
function handleInventory() {
  inventoryDialogVisible.value = true;
  inventoryForm.value = {
    inventoryDate: formatDate(new Date()).slice(0, 10),
    operator: '',
    items: []
  };
}

/** 导出出入库 */
function handleStockExport() {
  proxy.download('ast/inventory/stock/export', buildStockQueryParams(), `stock_record_${new Date().getTime()}.xlsx`);
}

/** 查看出入库详情 */
function handleViewStock(row) {
  stockDetailVisible.value = true;
  stockDetailLoading.value = true;
  stockDetail.value = {};
  getStockRecord(row.id).then(response => {
    stockDetail.value = response.data || {};
  }).finally(() => {
    stockDetailLoading.value = false;
  });
}

function handleVoidStock(detail) {
  if (!detail || !detail.id) {
    return;
  }
  proxy.$modal.confirm('确定要作废该出入库记录吗？作废后库存会按该记录数量回滚。').then(() => {
    return voidStockRecord(detail.id);
  }).then(() => {
    proxy.$modal.msgSuccess('作废成功');
    stockDetailVisible.value = false;
    refreshInventoryViews();
  }).catch(() => {});
}

function handleDownloadPurchaseTemplate() {
  proxy.download(
    'ast/inventory/purchase/import/template',
    {},
    `导入物品采购单模板_${new Date().getTime()}.xlsx`
  );
}

function handlePurchaseFileChange(file, fileList) {
  importPurchaseFileList.value = fileList.slice(-1);
}

function handlePurchaseFileRemove(file, fileList) {
  importPurchaseFileList.value = fileList;
}

function submitImportPurchase() {
  const file = importPurchaseFileList.value[0]?.raw;
  if (!file) {
    proxy.$modal.msgWarning('请先添加需要导入的采购单文件');
    return;
  }
  const formData = new FormData();
  formData.append('file', file);
  importPurchaseLoading.value = true;
  importPurchase(formData).then(() => {
    proxy.$modal.msgSuccess('导入成功');
    importPurchaseDialogVisible.value = false;
    importPurchaseFileList.value = [];
    refreshInventoryViews({ refreshOptions: true });
  }).finally(() => {
    importPurchaseLoading.value = false;
  });
}

/** 打开选择物品对话框（采购） */
function openSelectItemDialog() {
  currentDialogType.value = 'purchase';
  selectItemDialogVisible.value = true;
  selectedSkuList.value = []; // 清空之前的选择
  loadAvailableItems();
}

/** 打开选择物品对话框（领用） */
function openSelectItemDialogForReceive() {
  currentDialogType.value = 'receive';
  selectItemDialogVisible.value = true;
  selectedSkuList.value = []; // 清空之前的选择
  loadAvailableItems();
}

/** 打开选择物品对话框（退领） */
function openSelectItemDialogForReturn() {
  currentDialogType.value = 'return';
  selectItemDialogVisible.value = true;
  selectedSkuList.value = []; // 清空之前的选择
  loadAvailableItems();
}

/** 打开选择物品对话框（盘点） */
function openSelectItemDialogForInventory() {
  currentDialogType.value = 'inventory';
  selectItemDialogVisible.value = true;
  selectedSkuList.value = []; // 清空之前的选择
  loadAvailableItems();
}

/** 加载可选物品列表 */
function loadAvailableItems() {
  return listAvailableItems(cleanQuery({ keyword: itemSearchKeyword.value })).then(response => {
    availableItemList.value = response.data || [];
  });
}

/** 搜索可选物品 */
function searchAvailableItems() {
  loadAvailableItems();
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
    skuName: sku.skuName,
    price: sku.price,
    quantity: 1, // 默认数量为1
    stock: sku.stock,
    skuId: sku.id
  }));

  selectedSkuList.value.push(...newSelections);
}

/** 确认选择物品 */
function confirmItemSelection() {
  if (selectedSkuList.value.length === 0) {
    proxy.$modal.msgWarning('请至少选择一个物品规格');
    return;
  }

  // 根据当前对话框类型，将选中的SKU添加到对应表单中
  if (currentDialogType.value === 'purchase') {
    purchaseForm.value.items.push(...selectedSkuList.value);
  } else if (currentDialogType.value === 'receive') {
    receiveForm.value.items.push(...selectedSkuList.value);
  } else if (currentDialogType.value === 'return') {
    returnForm.value.items.push(...selectedSkuList.value);
  } else if (currentDialogType.value === 'inventory') {
    // 盘点需要特殊处理，添加原库存和当前库存字段
    const inventoryItems = selectedSkuList.value.map(sku => ({
      ...sku,
      originalStock: sku.stock, // 原库存
      currentStock: sku.stock,  // 当前库存（默认等于原库存）
      stockChange: 0,           // 库存变动
      remark: ''                // 备注
    }));
    inventoryForm.value.items.push(...inventoryItems);
  }

  selectItemDialogVisible.value = false;
  selectedSkuList.value = [];
}

/** 删除采购物品 */
function removePurchaseItem(index) {
  purchaseForm.value.items.splice(index, 1);
}

/** 提交采购 */
function submitPurchase() {
  if (purchaseForm.value.items.length === 0) {
    proxy.$modal.msgWarning('请选择采购物品');
    return;
  }

  createPurchase({
    purchaseDate: formatDate(purchaseForm.value.purchaseDate),
    paymentMethod: purchaseForm.value.paymentMethod,
    accountName: purchaseForm.value.account,
    yearBook: purchaseForm.value.yearBook,
    remark: purchaseForm.value.remark,
    items: buildStockItems(purchaseForm.value.items)
  }).then(() => {
    proxy.$modal.msgSuccess('采购成功');
    purchaseDialogVisible.value = false;
    refreshInventoryViews();
  });
}

/** 角色类型变化（领用） */
function handleRoleTypeChange(value) {
  receiveForm.value.roleName = '';
  loadRoleNameOptions(value, 'receive');
}

/** 角色类型变化（退领） */
function handleReturnRoleTypeChange(value) {
  returnForm.value.roleName = '';
  loadRoleNameOptions(value, 'return');
}

function normalizeRoleOptions(rows) {
  return (rows || [])
    .map(item => {
      const label = item.label || item.value || item.studentName || item.teacherName || item.name;
      return label ? { label, value: item.value || label } : null;
    })
    .filter(Boolean);
}

function loadRoleNameOptions(roleType, target) {
  const isReceive = target === 'receive';
  const optionsRef = isReceive ? roleNameOptions : returnRoleNameOptions;
  const loadingRef = isReceive ? roleNameLoading : returnRoleNameLoading;
  optionsRef.value = [];
  if (!roleType || roleType === 'other') {
    return Promise.resolve();
  }
  loadingRef.value = true;
  return listRoleOptions(cleanQuery({ roleType })).then(response => {
    optionsRef.value = normalizeRoleOptions(response.data);
  }).finally(() => {
    loadingRef.value = false;
  });
}

/** 删除领用物品 */
function removeReceiveItem(index) {
  receiveForm.value.items.splice(index, 1);
}

/** 提交领用 */
function submitReceive() {
  // 验证必填字段
  if (!receiveForm.value.receiveTime) {
    proxy.$modal.msgWarning('请选择领用时间');
    return;
  }
  if (!receiveForm.value.roleType) {
    proxy.$modal.msgWarning('请选择角色');
    return;
  }
  if (!receiveForm.value.roleName) {
    proxy.$modal.msgWarning('请选择角色名称');
    return;
  }
  if (receiveForm.value.items.length === 0) {
    proxy.$modal.msgWarning('请选择领用物品');
    return;
  }

  createReceive({
    receiveTime: formatDate(receiveForm.value.receiveTime),
    roleType: receiveForm.value.roleType,
    roleName: receiveForm.value.roleName,
    items: buildStockItems(receiveForm.value.items)
  }).then(() => {
    proxy.$modal.msgSuccess('领用成功');
    receiveDialogVisible.value = false;
    refreshInventoryViews();
  });
}

/** 删除退领物品 */
function removeReturnItem(index) {
  returnForm.value.items.splice(index, 1);
}

/** 提交退领 */
function submitReturn() {
  // 验证必填字段
  if (!returnForm.value.returnTime) {
    proxy.$modal.msgWarning('请选择退领时间');
    return;
  }
  if (!returnForm.value.roleType) {
    proxy.$modal.msgWarning('请选择角色');
    return;
  }
  if (!returnForm.value.roleName) {
    proxy.$modal.msgWarning('请选择角色名称');
    return;
  }
  if (returnForm.value.items.length === 0) {
    proxy.$modal.msgWarning('请选择退领物品');
    return;
  }

  createReturn({
    returnTime: formatDate(returnForm.value.returnTime),
    roleType: returnForm.value.roleType,
    roleName: returnForm.value.roleName,
    items: buildStockItems(returnForm.value.items)
  }).then(() => {
    proxy.$modal.msgSuccess('退领成功');
    returnDialogVisible.value = false;
    refreshInventoryViews();
  });
}

/** 计算库存变动 */
function calculateStockChange(row) {
  row.stockChange = (row.currentStock || 0) - (row.originalStock || 0);
}

/** 删除盘点物品 */
function removeInventoryItem(index) {
  inventoryForm.value.items.splice(index, 1);
}

/** 提交盘点 */
function submitInventory() {
  // 验证必填字段
  if (!inventoryForm.value.inventoryDate) {
    proxy.$modal.msgWarning('请选择盘点日期');
    return;
  }
  if (!inventoryForm.value.operator) {
    proxy.$modal.msgWarning('请输入操作人');
    return;
  }
  if (inventoryForm.value.items.length === 0) {
    proxy.$modal.msgWarning('请选择盘点物品');
    return;
  }

  // 检查是否有未填写当前库存的物品
  const unfilledItem = inventoryForm.value.items.find(item =>
    item.currentStock === null || item.currentStock === undefined
  );
  if (unfilledItem) {
    proxy.$modal.msgWarning('请填写所有物品的当前库存');
    return;
  }

  // 统计盘点结果
  const profitItems = inventoryForm.value.items.filter(item => item.stockChange > 0);
  const lossItems = inventoryForm.value.items.filter(item => item.stockChange < 0);
  const normalItems = inventoryForm.value.items.filter(item => item.stockChange === 0);

  let message = `盘点完成！\n`;
  message += `盘点物品：${inventoryForm.value.items.length} 项\n`;
  message += `盘盈：${profitItems.length} 项（+${inventoryProfitCount.value}）\n`;
  message += `盘亏：${lossItems.length} 项（${inventoryLossCount.value}）\n`;
  message += `正常：${normalItems.length} 项`;

  proxy.$modal.confirm(message).then(() => {
    return createInventory({
      inventoryDate: formatDate(inventoryForm.value.inventoryDate),
      operator: inventoryForm.value.operator,
      items: buildStockItems(inventoryForm.value.items)
    });
  }).then(() => {
    proxy.$modal.msgSuccess('盘点成功，库存已更新');
    inventoryDialogVisible.value = false;
    refreshInventoryViews();
  }).catch(() => {});
}

// ==================== 费用管理函数 ====================

/** 获取费用列表 */
function getFeeList() {
  feeLoading.value = true;
  listFee(cleanQuery({
    ...feeQueryParams.value,
    status: feeQueryParams.value.status === '' ? undefined : Number(feeQueryParams.value.status)
  })).then(response => {
    feeList.value = response.rows || [];
    feeTotal.value = response.total || 0;
  }).finally(() => {
    feeLoading.value = false;
  });
}

/** 重置费用查询 */
function resetFeeQuery() {
  feeQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    feeName: '',
    status: ''
  };
  getFeeList();
}

/** 新建费用 */
function handleAddFee() {
  feeTitle.value = '新建费用';
  feeDialogVisible.value = true;
  feeForm.value = {
    id: null,
    feeName: '',
    price: null,
    onlineSale: 0,
    status: 1,
    courseIds: [],
    courseNames: []
  };
}

/** 编辑费用 */
function handleEditFee(row) {
  getFee(row.id).then(response => {
    const detail = response.data || row;
    feeTitle.value = '编辑费用';
    feeDialogVisible.value = true;
    feeForm.value = {
      id: detail.id,
      feeName: detail.feeName,
      price: detail.price ?? detail.amount,
      onlineSale: detail.onlineSale ?? 0,
      status: detail.status,
      courseIds: detail.courseIds || [],
      courseNames: detail.courseNames || (detail.courseName ? detail.courseName.split('、') : [])
    };
  });
}

/** 删除费用 */
function handleDeleteFee(row) {
  proxy.$modal.confirm('确定要删除费用"' + row.feeName + '"吗？').then(() => {
    return delFee(row.id);
  }).then(() => {
    proxy.$modal.msgSuccess('删除成功');
    getFeeList();
  }).catch(() => {});
}

/** 费用状态变化 */
function handleFeeStatusChange(row) {
  const statusText = row.status === 1 ? '启用' : '停用';
  proxy.$modal.confirm('确定要' + statusText + '费用"' + row.feeName + '"吗？').then(() => {
    return changeFeeStatus({ id: row.id, status: row.status });
  }).then(() => {
    proxy.$modal.msgSuccess(statusText + '成功');
  }).catch(() => {
    row.status = row.status === 1 ? 0 : 1;
  });
}

/** 费用线上售卖变化 */
function handleFeeOnlineSaleChange(row) {
  getFee(row.id).then(response => {
    const detail = response.data || row;
    return updateFee({
      id: detail.id,
      feeName: detail.feeName,
      price: normalizeNumber(detail.price ?? detail.amount, 0),
      amount: normalizeNumber(detail.price ?? detail.amount, 0),
      onlineSale: row.onlineSale,
      status: detail.status,
      courseIds: detail.courseIds || [],
      courseNames: detail.courseNames || []
    });
  }).then(() => {
    proxy.$modal.msgSuccess('线上售卖状态修改成功');
  }).catch(() => {
    row.onlineSale = row.onlineSale === 1 ? 0 : 1;
  });
}

/** 提交费用 */
function submitFee() {
  proxy.$refs.feeFormRef.validate(valid => {
    if (valid) {
      const action = feeForm.value.id ? '修改' : '新增';
      const payload = {
        id: feeForm.value.id,
        feeName: feeForm.value.feeName,
        price: normalizeNumber(feeForm.value.price, 0),
        amount: normalizeNumber(feeForm.value.price, 0),
        onlineSale: normalizeNumber(feeForm.value.onlineSale, 0),
        status: feeForm.value.status ?? 1,
        courseIds: feeForm.value.courseIds || [],
        courseNames: feeForm.value.courseNames || []
      };
      const request = payload.id ? updateFee(payload) : addFee(payload);
      request.then(() => {
        proxy.$modal.msgSuccess(action + '成功');
        feeDialogVisible.value = false;
        getFeeList();
      });
    }
  });
}

/** 打开选择课程对话框 */
function getTargetCourseIds() {
  return courseSelectTarget.value === 'item' ? itemForm.value.courseIds : feeForm.value.courseIds;
}

/** 打开选择课程对话框 */
function openSelectCourseDialog(target = 'fee') {
  courseSelectTarget.value = target;
  selectCourseDialogVisible.value = true;
  courseSearchKeyword.value = '';
  selectedCourses.value = [];
  loadCourseList().then(() => {
    const targetCourseIds = getTargetCourseIds() || [];
    nextTick(() => {
      if (courseTableRef.value && targetCourseIds.length > 0) {
        const selectedRows = courseList.value.filter(course =>
          targetCourseIds.includes(course.id)
        );
        selectedRows.forEach(row => {
          courseTableRef.value.toggleRowSelection(row, true);
        });
      }
    });
  });
}

/** 加载课程列表 */
function loadCourseList() {
  return listCourseOptions().then(response => {
    courseList.value = response.data || [];
  });
}

/** 课程选择变化 */
function handleCourseSelectionChange(selection) {
  selectedCourses.value = selection;
}

/** 确认选择课程 */
function confirmCourseSelection() {
  if (!selectedCourses.value || selectedCourses.value.length === 0) {
    proxy.$modal.msgWarning('请至少选择一个课程');
    return;
  }

  const courseIds = selectedCourses.value.map(course => course.id);
  const courseNames = selectedCourses.value.map(course => course.courseName);
  if (courseSelectTarget.value === 'item') {
    itemForm.value.courseIds = courseIds;
    itemForm.value.courseNames = courseNames;
  } else {
    feeForm.value.courseIds = courseIds;
    feeForm.value.courseNames = courseNames;
  }
  selectCourseDialogVisible.value = false;
}

/** 移除单个课程 */
function removeCourse(index) {
  feeForm.value.courseIds.splice(index, 1);
  feeForm.value.courseNames.splice(index, 1);
}

/** 移除物品绑定课程 */
function removeItemCourse(index) {
  itemForm.value.courseIds.splice(index, 1);
  itemForm.value.courseNames.splice(index, 1);
}

/** 清除所有课程 */
function clearCourse() {
  feeForm.value.courseIds = [];
  feeForm.value.courseNames = [];
}

// 初始化
getItemList();
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.item-manage-table {
  width: 100%;
}

.stock-record-table {
  width: 100%;
}

.stock-search-form {
  padding-top: 2px;
}

.stock-action-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  min-height: 34px;
}

.stock-action-buttons {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.stock-action-buttons :deep(.el-button + .el-button) {
  margin-left: 0;
}

.purchase-more-button {
  margin-left: -10px;
  padding-left: 9px;
  padding-right: 9px;
}

.stock-summary-bar {
  align-items: center;
  background: #fff3ea;
  border-radius: 4px;
  color: #606266;
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  line-height: 22px;
  margin: 8px 0 14px;
  padding: 10px 14px;
}

.stock-summary-bar span:first-child {
  font-weight: 600;
}

.item-name-cell {
  display: flex;
  flex-direction: column;
  line-height: 20px;
  min-width: 0;
}

.item-name-cell small {
  color: #909399;
  font-size: 12px;
}

.item-manage-table :deep(.cell) {
  white-space: nowrap;
}

.stock-record-table :deep(.cell) {
  white-space: nowrap;
}

.item-manage-table :deep(.el-button) {
  margin: 0 3px;
}

.stock-record-table :deep(.el-button) {
  margin: 0 3px;
}

.item-form :deep(.el-input),
.item-form :deep(.el-select),
.item-form :deep(.el-input-number),
.item-form :deep(.el-textarea),
.stock-form :deep(.el-input),
.stock-form :deep(.el-select),
.stock-form :deep(.el-input-number),
.stock-form :deep(.el-date-editor),
.stock-form :deep(.el-textarea) {
  width: 100%;
}

.item-form :deep(.el-form-item__content),
.stock-form :deep(.el-form-item__content) {
  min-width: 0;
}

.course-bind-area {
  width: 100%;
  min-width: 0;
}

.spec-table,
.sku-table,
.stock-detail-table {
  max-width: 100%;
}

.spec-table :deep(.cell),
.stock-detail-table :deep(.cell) {
  white-space: normal;
}

.sku-table :deep(.cell) {
  white-space: nowrap;
}

.spec-value-editor {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-width: 0;
  padding: 2px 0;
  width: 100%;
}

.spec-value-editor :deep(.el-tag) {
  max-width: 160px;
}

.spec-tag-input {
  width: 150px;
  flex: 0 0 150px;
}

.spec-tip {
  color: #909399;
  flex: 1 1 240px;
  font-size: 12px;
  line-height: 20px;
  min-width: 200px;
  white-space: normal;
}

.quantity-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quantity-stock-tip {
  color: #909399;
  font-size: 12px;
  line-height: 18px;
}

.account-select-line {
  display: flex;
  gap: 10px;
  min-width: 0;
  width: 100%;
}

.account-select-line :deep(.el-select) {
  flex: 1 1 auto;
  min-width: 0;
}

.stock-detail-panel {
  min-height: 220px;
}

.detail-actions {
  align-items: center;
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.detail-heading {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.detail-heading div {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-heading span {
  color: #606266;
}

.detail-grid {
  border: 1px solid #ebeef5;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 18px;
}

.detail-grid > div {
  border-bottom: 1px solid #ebeef5;
  min-width: 0;
  padding: 14px 18px;
}

.detail-grid > div:nth-last-child(-n + 3) {
  border-bottom: 0;
}

.detail-grid label {
  color: #909399;
  display: block;
  font-size: 13px;
  line-height: 18px;
  margin-bottom: 6px;
}

.detail-grid span {
  color: #303133;
  display: block;
  line-height: 22px;
  overflow-wrap: anywhere;
}

.import-purchase-dialog {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 4px 8px 10px;
}

.import-step {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.import-step strong {
  color: #303133;
  font-size: 15px;
}

:global(.item-form-dialog),
:global(.stock-form-dialog),
:global(.stock-detail-dialog) {
  max-width: calc(100vw - 40px);
}

:global(.item-form-dialog .el-dialog__header),
:global(.item-form-dialog .el-dialog__footer),
:global(.stock-form-dialog .el-dialog__header),
:global(.stock-form-dialog .el-dialog__footer),
:global(.stock-detail-dialog .el-dialog__header),
:global(.stock-detail-dialog .el-dialog__footer) {
  padding-left: 20px;
  padding-right: 20px;
}

:global(.item-form-dialog .el-dialog__body),
:global(.stock-form-dialog .el-dialog__body),
:global(.stock-detail-dialog .el-dialog__body) {
  max-height: calc(100vh - 180px);
  overflow-x: hidden;
  overflow-y: auto;
  padding: 12px 20px 18px;
}

:global(.item-form-dialog .el-row),
:global(.stock-form-dialog .el-row) {
  margin-left: 0 !important;
  margin-right: 0 !important;
}

:global(.item-form-dialog [class*="el-col-"]),
:global(.stock-form-dialog [class*="el-col-"]) {
  padding-left: 0 !important;
  padding-right: 20px !important;
}

:global(.item-form-dialog [class*="el-col-"]:last-child),
:global(.stock-form-dialog [class*="el-col-"]:last-child) {
  padding-right: 0 !important;
}

@media (max-width: 1280px) {
  :global(.item-form-dialog),
  :global(.stock-form-dialog),
  :global(.stock-detail-dialog) {
    width: calc(100vw - 40px) !important;
  }
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-grid > div {
    border-bottom: 1px solid #ebeef5;
  }

  .detail-grid > div:last-child {
    border-bottom: 0;
  }
}
</style>
