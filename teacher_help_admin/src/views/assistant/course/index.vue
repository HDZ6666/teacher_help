<template>
  <div class="app-container">
    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- 课程Tab -->
      <el-tab-pane label="课程" name="course">
        <!-- 搜索栏 -->
        <el-form :model="courseQueryParams" ref="courseQueryRef" :inline="true" v-show="showSearch" label-width="68px">
          <el-form-item label="课程名称" prop="courseName">
            <el-input
              v-model="courseQueryParams.courseName"
              placeholder="请输入课程名称"
              clearable
              @keyup.enter="handleCourseQuery"
            />
          </el-form-item>
          <el-form-item label="课程类型" prop="courseType">
            <el-select v-model="courseQueryParams.courseType" placeholder="请选择课程类型" clearable>
              <el-option label="一对多" value="1" />
              <el-option label="一对一" value="2" />
            </el-select>
          </el-form-item>
          <el-form-item label="年级" prop="grade">
            <el-select v-model="courseQueryParams.grade" placeholder="请选择年级" clearable>
              <el-option label="一年级" value="1" />
              <el-option label="二年级" value="2" />
              <el-option label="三年级" value="3" />
              <el-option label="四年级" value="4" />
              <el-option label="五年级" value="5" />
              <el-option label="六年级" value="6" />
              <el-option label="初一" value="7" />
              <el-option label="初二" value="8" />
              <el-option label="初三" value="9" />
              <el-option label="高一" value="10" />
              <el-option label="高二" value="11" />
              <el-option label="高三" value="12" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleCourseQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetCourseQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button
              type="primary"
              plain
              icon="Plus"
              @click="handleAddCourse"
            >新增课程</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="success"
              plain
              icon="Edit"
              :disabled="courseSingle"
              @click="handleUpdateCourse"
            >修改</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="danger"
              plain
              icon="Delete"
              :disabled="courseMultiple"
              @click="handleDeleteCourse"
            >删除</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button
              type="warning"
              plain
              icon="Download"
              @click="handleExportCourse"
            >导出</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getCourseList"></right-toolbar>
        </el-row>

        <!-- 课程列表 -->
        <el-table v-loading="courseLoading" :data="courseList" @selection-change="handleCourseSelectionChange">
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="课程名称" align="center" prop="courseName" width="150" />
          <el-table-column label="类型" align="center" prop="courseType" width="100">
            <template #default="scope">
              {{ scope.row.courseType === '1' ? '一对多' : '一对一' }}
            </template>
          </el-table-column>
          <el-table-column label="收费方式" align="center" prop="chargeType" width="200">
            <template #default="scope">
              <div v-if="scope.row.chargeByClass">
                <div>按课时({{ scope.row.classPrices[0]?.totalPrice }}元/课时)</div>
              </div>
              <div v-if="scope.row.chargeByMonth">
                <div v-for="(item, index) in scope.row.monthPrices" :key="index">
                  {{ item.name }}({{ item.totalPrice }}元/{{ item.quantity }}个月)
                </div>
              </div>
              <div v-if="scope.row.chargeByDay">
                <div v-for="(item, index) in scope.row.dayPrices" :key="index">
                  {{ item.name }}({{ item.totalPrice }}元/{{ item.quantity }}天)
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="年级标签" align="center" prop="gradeLabel" width="100" />
          <el-table-column label="在读学员数" align="center" prop="studentCount" width="100" />
          <el-table-column label="启用状态" align="center" prop="status" width="100">
            <template #default="scope">
              <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0" />
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
            <template #default="scope">
              <el-button link type="primary" icon="Edit" @click="handleUpdateCourse(scope.row)">编辑</el-button>
              <el-button link type="primary" icon="Delete" @click="handleDeleteCourse(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="courseTotal > 0"
          :total="courseTotal"
          v-model:page="courseQueryParams.pageNum"
          v-model:limit="courseQueryParams.pageSize"
          @pagination="getCourseList"
        />
      </el-tab-pane>

      <!-- 套餐Tab -->
      <el-tab-pane label="套餐" name="package">
        <!-- 搜索栏 -->
        <el-form :model="packageQueryParams" ref="packageQueryRef" :inline="true" v-show="showSearch" label-width="68px">
          <el-form-item label="套餐名称" prop="packageName">
            <el-input
              v-model="packageQueryParams.packageName"
              placeholder="请输入套餐名称"
              clearable
              @keyup.enter="handlePackageQuery"
            />
          </el-form-item>
          <el-form-item label="启用状态" prop="status">
            <el-radio-group v-model="packageQueryParams.status">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="1">启用</el-radio-button>
              <el-radio-button label="0">停用</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handlePackageQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetPackageQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button
              type="primary"
              plain
              icon="Plus"
              @click="handleAddPackage"
            >添加套餐</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getPackageList"></right-toolbar>
        </el-row>

        <!-- 套餐列表 -->
        <el-table v-loading="packageLoading" :data="packageList">
          <el-table-column label="套餐名称" align="center" prop="packageName" width="200" />
          <el-table-column label="套价" align="center" prop="totalPrice" width="150">
            <template #default="scope">
              ¥ {{ scope.row.totalPrice }}
            </template>
          </el-table-column>
          <el-table-column label="启用状态" align="center" prop="status" width="100">
            <template #default="scope">
              <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0" />
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
            <template #default="scope">
              <el-button link type="primary" icon="Edit" @click="handleUpdatePackage(scope.row)">编辑</el-button>
              <el-button link type="primary" icon="Delete" @click="handleDeletePackage(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="packageTotal > 0"
          :total="packageTotal"
          v-model:page="packageQueryParams.pageNum"
          v-model:limit="packageQueryParams.pageSize"
          @pagination="getPackageList"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 新增/修改课程对话框 -->
    <el-dialog :title="courseTitle" v-model="courseOpen" width="800px" append-to-body destroy-on-close>
      <el-form ref="courseFormRef" :model="courseForm" :rules="courseRules" label-width="100px">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-form-item label="课程名称" prop="courseName">
          <el-input v-model="courseForm.courseName" placeholder="请输入课程名称" maxlength="50" />
        </el-form-item>

        <el-form-item label="课程类型" prop="courseType">
          <el-radio-group v-model="courseForm.courseType">
            <el-radio label="1">一对多</el-radio>
            <el-radio label="2">一对一</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="年级" prop="grade">
          <el-select v-model="courseForm.grade" placeholder="请选择年级" style="width: 200px;">
            <el-option label="一年级" value="1" />
            <el-option label="二年级" value="2" />
            <el-option label="三年级" value="3" />
            <el-option label="四年级" value="4" />
            <el-option label="五年级" value="5" />
            <el-option label="六年级" value="6" />
            <el-option label="初一" value="7" />
            <el-option label="初二" value="8" />
            <el-option label="初三" value="9" />
            <el-option label="高一" value="10" />
            <el-option label="高二" value="11" />
            <el-option label="高三" value="12" />
          </el-select>
          <el-link type="primary" style="margin-left: 10px;">选择设置</el-link>
        </el-form-item>

        <el-form-item label="科目" prop="subject">
          <el-select v-model="courseForm.subject" placeholder="请选择科目" style="width: 200px;">
            <el-option label="语文" value="1" />
            <el-option label="数学" value="2" />
            <el-option label="英语" value="3" />
            <el-option label="物理" value="4" />
            <el-option label="化学" value="5" />
            <el-option label="生物" value="6" />
            <el-option label="政治" value="7" />
            <el-option label="历史" value="8" />
            <el-option label="地理" value="9" />
          </el-select>
          <el-link type="primary" style="margin-left: 10px;">选择设置</el-link>
        </el-form-item>

        <el-form-item label="学期" prop="semester">
          <el-select v-model="courseForm.semester" placeholder="请选择学期" style="width: 200px;">
            <el-option label="春季" value="1" />
            <el-option label="夏季" value="2" />
            <el-option label="秋季" value="3" />
            <el-option label="冬季" value="4" />
          </el-select>
        </el-form-item>

        <el-form-item label="课表颜色" prop="scheduleColor">
          <div style="display: flex; gap: 10px; align-items: center;">
            <div 
              v-for="color in colorOptions" 
              :key="color"
              @click="courseForm.scheduleColor = color"
              :style="{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: color,
                cursor: 'pointer',
                border: courseForm.scheduleColor === color ? '2px solid #409EFF' : '2px solid transparent'
              }"
            ></div>
            <span style="color: #999;">...</span>
          </div>
        </el-form-item>

        <!-- 收费方式 -->
        <el-divider content-position="left">收费方式</el-divider>

        <!-- 按课时收费 -->
        <el-form-item label="按课时收费">
          <el-switch v-model="courseForm.chargeByClass" />
        </el-form-item>

        <div v-if="courseForm.chargeByClass" style="margin-left: 100px; margin-bottom: 20px;">
          <el-alert
            title="【温馨提示】为方便您设定更灵活的价格体系，建议您在在标准中添加/或编辑数量为1的单价价目表~"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          />
          
          <div style="margin-bottom: 10px;">
            <span style="font-weight: bold;">扣课时规则：</span>
            <el-radio-group v-model="courseForm.classDeductRule" style="margin-left: 10px;">
              <el-radio label="1">满课最多扣除时</el-radio>
              <el-radio label="2">扣1</el-radio>
              <el-radio label="3">不扣</el-radio>
              <el-radio label="4">部分免扣</el-radio>
            </el-radio-group>
          </div>

          <div style="margin-bottom: 10px;">
            <span style="font-weight: bold;">未到差异扣除时：</span>
            <el-radio-group v-model="courseForm.classAbsenceRule" style="margin-left: 10px;">
              <el-radio label="1">扣1</el-radio>
              <el-radio label="2">不扣</el-radio>
            </el-radio-group>
          </div>

          <el-alert
            title="【温馨提示】为方便您设定更灵活的价格体系，建议您在在标准中添加/或编辑数量为1的单价价目表~"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          />

          <div style="margin-bottom: 10px; font-weight: bold;">定价标准：</div>
          <el-table :data="courseForm.classPrices" border style="width: 100%;">
            <el-table-column label="名称" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.name" placeholder="单价" />
              </template>
            </el-table-column>
            <el-table-column label="数量(课时)" width="150">
              <template #default="scope">
                <el-input-number v-model="scope.row.quantity" :min="1" controls-position="right" style="width: 100%;" />
              </template>
            </el-table-column>
            <el-table-column label="总价(元)" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.totalPrice" placeholder="请输入" />
              </template>
            </el-table-column>
            <el-table-column label="单价(元/课时)" width="150">
              <template #default="scope">
                <span>{{ scope.row.quantity > 0 ? (scope.row.totalPrice / scope.row.quantity).toFixed(2) : '自动计算' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button link type="danger" @click="removeClassPrice(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button link type="primary" icon="Plus" @click="addClassPrice" style="margin-top: 10px;">添加(1/10)</el-button>
        </div>

        <!-- 按月收费 -->
        <el-form-item label="按月收费">
          <el-switch v-model="courseForm.chargeByMonth" />
        </el-form-item>

        <div v-if="courseForm.chargeByMonth" style="margin-left: 100px; margin-bottom: 20px;">
          <el-alert
            title="【温馨提示】为方便您设定更灵活的价格体系，建议您在在标准中添加/或编辑数量为1的单价价目表~"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          />

          <div style="margin-bottom: 10px; font-weight: bold;">定价标准：</div>
          <el-table :data="courseForm.monthPrices" border style="width: 100%;">
            <el-table-column label="名称" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.name" placeholder="单价" />
              </template>
            </el-table-column>
            <el-table-column label="数量(月)" width="150">
              <template #default="scope">
                <el-input-number v-model="scope.row.quantity" :min="1" controls-position="right" style="width: 100%;" />
              </template>
            </el-table-column>
            <el-table-column label="总价(元)" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.totalPrice" placeholder="请输入" />
              </template>
            </el-table-column>
            <el-table-column label="单价(元/月)" width="150">
              <template #default="scope">
                <span>{{ scope.row.quantity > 0 ? (scope.row.totalPrice / scope.row.quantity).toFixed(2) : '自动计算' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button link type="danger" @click="removeMonthPrice(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button link type="primary" icon="Plus" @click="addMonthPrice" style="margin-top: 10px;">添加(1/10)</el-button>
        </div>

        <!-- 按天收费 -->
        <el-form-item label="按天收费">
          <el-switch v-model="courseForm.chargeByDay" />
        </el-form-item>

        <div v-if="courseForm.chargeByDay" style="margin-left: 100px; margin-bottom: 20px;">
          <el-alert
            title="【温馨提示】为方便您设定更灵活的价格体系，建议您在在标准中添加/或编辑数量为1的单价价目表~"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          />

          <div style="margin-bottom: 10px; font-weight: bold;">定价标准：</div>
          <el-table :data="courseForm.dayPrices" border style="width: 100%;">
            <el-table-column label="名称" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.name" placeholder="单价" />
              </template>
            </el-table-column>
            <el-table-column label="数量(天)" width="150">
              <template #default="scope">
                <el-input-number v-model="scope.row.quantity" :min="1" controls-position="right" style="width: 100%;" />
              </template>
            </el-table-column>
            <el-table-column label="总价(元)" width="150">
              <template #default="scope">
                <el-input v-model="scope.row.totalPrice" placeholder="请输入" />
              </template>
            </el-table-column>
            <el-table-column label="单价(元/天)" width="150">
              <template #default="scope">
                <span>{{ scope.row.quantity > 0 ? (scope.row.totalPrice / scope.row.quantity).toFixed(2) : '自动计算' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button link type="danger" @click="removeDayPrice(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button link type="primary" icon="Plus" @click="addDayPrice" style="margin-top: 10px;">添加(1/10)</el-button>
        </div>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>
        
        <el-form-item label="备注" prop="remark">
          <el-input v-model="courseForm.remark" type="textarea" :rows="3" placeholder="请输入备注" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelCourse">取 消</el-button>
          <el-button type="primary" @click="submitCourseForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加/修改套餐对话框 -->
    <el-dialog :title="packageTitle" v-model="packageOpen" width="900px" append-to-body>
      <el-form ref="packageFormRef" :model="packageForm" :rules="packageRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="套餐名称" prop="packageName">
              <el-input v-model="packageForm.packageName" placeholder="请输入套餐名称" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="packageForm.remark" placeholder="请输入备注" maxlength="200" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 选择课程 -->
        <el-divider content-position="left">
          <span style="font-size: 14px; font-weight: bold;">选择课程</span>
        </el-divider>
        <el-form-item>
          <el-button type="primary" plain icon="Plus" @click="openCourseDialog">选择课程</el-button>
          <el-table :data="packageForm.courses" style="margin-top: 10px;" max-height="200">
            <el-table-column label="课程名称" prop="courseName" />
            <el-table-column label="课程类型" prop="courseType" width="100">
              <template #default="scope">
                {{ scope.row.courseType === '1' ? '一对多' : '一对一' }}
              </template>
            </el-table-column>
            <el-table-column label="定价标准" prop="pricingName" width="150" />
            <el-table-column label="操作" width="80">
              <template #default="scope">
                <el-button link type="danger" icon="Delete" @click="removeCourse(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <!-- 选择物品 -->
        <el-divider content-position="left">
          <span style="font-size: 14px; font-weight: bold;">选择物品</span>
        </el-divider>
        <el-form-item>
          <el-button type="primary" plain icon="Plus" @click="openItemDialog">选择物品</el-button>
          <el-table :data="packageForm.items" style="margin-top: 10px;" max-height="200">
            <el-table-column label="物品名称" prop="itemName" />
            <el-table-column label="单价" prop="price" width="120">
              <template #default="scope">
                ¥ {{ scope.row.price }}
              </template>
            </el-table-column>
            <el-table-column label="库存" prop="stock" width="100" />
            <el-table-column label="操作" width="80">
              <template #default="scope">
                <el-button link type="danger" icon="Delete" @click="removeItem(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <!-- 选择费用 -->
        <el-divider content-position="left">
          <span style="font-size: 14px; font-weight: bold;">选择费用</span>
        </el-divider>
        <el-form-item>
          <el-button type="primary" plain icon="Plus" @click="openFeeDialog">选择费用</el-button>
          <el-table :data="packageForm.fees" style="margin-top: 10px;" max-height="200">
            <el-table-column label="费用名称" prop="feeName" />
            <el-table-column label="单价" prop="price" width="120">
              <template #default="scope">
                ¥ {{ scope.row.price }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="scope">
                <el-button link type="danger" icon="Delete" @click="removeFee(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <!-- 套餐总价 -->
        <el-row :gutter="20">
          <el-col :span="24" style="text-align: right; padding-right: 20px;">
            <span style="font-size: 16px; font-weight: bold; color: #ff6700;">
              套餐价：¥ {{ calculatePackageTotal }}
            </span>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelPackage">取 消</el-button>
          <el-button type="primary" @click="submitPackageForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择课程对话框 -->
    <el-dialog title="选择课程" v-model="courseDialogVisible" width="800px" append-to-body>
      <el-form :inline="true">
        <el-form-item label="课程名称">
          <el-input v-model="courseSearchName" placeholder="请输入课程名称" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="searchCourseList">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="availableCourseList" @selection-change="handleDialogCourseSelectionChange" max-height="400">
        <el-table-column type="selection" width="55" />
        <el-table-column label="课程名称" prop="courseName" />
        <el-table-column label="课程类型" prop="courseType" width="100">
          <template #default="scope">
            {{ scope.row.courseType === '1' ? '一对多' : '一对一' }}
          </template>
        </el-table-column>
        <el-table-column label="定价标准" prop="pricingName" width="200" />
      </el-table>
      <div style="margin-top: 10px; color: #909399;">
        已选择：{{ selectedCourses.length }} 项
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="courseDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmCourseSelection">确定了</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择物品对话框 -->
    <el-dialog title="选择物品" v-model="itemDialogVisible" width="700px" append-to-body>
      <el-form :inline="true">
        <el-form-item label="物品名称">
          <el-input v-model="itemSearchName" placeholder="请输入物品名称" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="searchItemList">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="availableItemList" @selection-change="handleItemSelectionChange" max-height="400">
        <el-table-column type="selection" width="55" />
        <el-table-column label="物品名称" prop="itemName" />
        <el-table-column label="单价" prop="price" width="120">
          <template #default="scope">
            ¥ {{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column label="库存" prop="stock" width="100" />
      </el-table>
      <div style="margin-top: 10px; color: #909399;">
        已选择：{{ selectedItems.length }} 项
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="itemDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmItemSelection">确定了</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 选择费用对话框 -->
    <el-dialog title="选择费用" v-model="feeDialogVisible" width="700px" append-to-body>
      <el-form :inline="true">
        <el-form-item label="费用名称">
          <el-input v-model="feeSearchName" placeholder="请输入费用名称" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="searchFeeList">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="availableFeeList" @selection-change="handleFeeSelectionChange" max-height="400">
        <el-table-column type="selection" width="55" />
        <el-table-column label="费用名称" prop="feeName" />
        <el-table-column label="单价" prop="price" width="120">
          <template #default="scope">
            ¥ {{ scope.row.price }}
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 10px; color: #909399;">
        已选择：{{ selectedFees.length }} 项
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="feeDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="confirmFeeSelection">确定了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantCourse">
import { Plus } from '@element-plus/icons-vue';

const { proxy } = getCurrentInstance();

// Tab相关
const activeTab = ref('course');

// 课程列表相关
const courseList = ref([]);
const courseLoading = ref(false);
const courseTotal = ref(0);
const showSearch = ref(true);
const courseSingle = ref(true);
const courseMultiple = ref(true);
const courseIds = ref([]);

// 课程查询参数
const courseQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  courseName: undefined,
  courseType: undefined,
  grade: undefined
});

// 课程表单相关
const courseOpen = ref(false);
const courseTitle = ref('');
const courseForm = ref({});
const courseRules = ref({
  courseName: [
    { required: true, message: '课程名称不能为空', trigger: 'blur' }
  ],
  courseType: [
    { required: true, message: '请选择课程类型', trigger: 'change' }
  ],
  grade: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请选择科目', trigger: 'change' }
  ]
});

// 课表颜色选项
const colorOptions = ref([
  '#409EFF',
  '#FFA500',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#9C27B0'
]);

// 套餐列表相关
const packageList = ref([]);
const packageLoading = ref(false);
const packageTotal = ref(0);

// 套餐查询参数
const packageQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  packageName: undefined,
  status: ''
});

// 套餐表单相关
const packageOpen = ref(false);
const packageTitle = ref('');
const packageForm = ref({
  packageName: '',
  remark: '',
  courses: [],
  items: [],
  fees: []
});
const packageRules = ref({
  packageName: [
    { required: true, message: '套餐名称不能为空', trigger: 'blur' }
  ]
});

// 选择课程对话框
const courseDialogVisible = ref(false);
const courseSearchName = ref('');
const availableCourseList = ref([]);
const selectedCourses = ref([]);

// 选择物品对话框
const itemDialogVisible = ref(false);
const itemSearchName = ref('');
const availableItemList = ref([]);
const selectedItems = ref([]);

// 选择费用对话框
const feeDialogVisible = ref(false);
const feeSearchName = ref('');
const availableFeeList = ref([]);
const selectedFees = ref([]);

/** 查询课程列表 */
function getCourseList() {
  courseLoading.value = true;
  // 模拟数据
  setTimeout(() => {
    courseList.value = [
      {
        id: 1,
        courseName: '小学数学999',
        courseType: '1',
        gradeLabel: '一对多',
        studentCount: 1,
        status: 1,
        chargeByClass: true,
        classPrices: [{ name: '单价', quantity: 1, totalPrice: 200 }]
      },
      {
        id: 2,
        courseName: '托管0322',
        courseType: '2',
        gradeLabel: '一对多',
        studentCount: 1,
        status: 1,
        chargeByMonth: true,
        monthPrices: [
          { name: '单价', quantity: 1, totalPrice: 1500 },
          { name: '套餐', quantity: 3, totalPrice: 1666 },
          { name: '半年', quantity: 6, totalPrice: 4500 },
          { name: '套餐', quantity: 12, totalPrice: 8000 }
        ]
      }
    ];
    courseTotal.value = 2;
    courseLoading.value = false;
  }, 500);
}

/** Tab切换 */
function handleTabClick(tab) {
  if (tab.props.name === 'course') {
    getCourseList();
  } else if (tab.props.name === 'package') {
    getPackageList();
  }
}

/** 搜索按钮操作 */
function handleCourseQuery() {
  courseQueryParams.value.pageNum = 1;
  getCourseList();
}

/** 重置按钮操作 */
function resetCourseQuery() {
  proxy.$refs.courseQueryRef.resetFields();
  handleCourseQuery();
}

/** 多选框选中数据 */
function handleCourseSelectionChange(selection) {
  courseIds.value = selection.map(item => item.id);
  courseSingle.value = selection.length !== 1;
  courseMultiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAddCourse() {
  resetCourseForm();
  courseOpen.value = true;
  courseTitle.value = '新增课程';
}

/** 修改按钮操作 */
function handleUpdateCourse(row) {
  resetCourseForm();
  const id = row.id || courseIds.value[0];
  // 模拟获取详情
  courseForm.value = {
    id: id,
    courseName: row.courseName,
    courseType: row.courseType,
    grade: '1',
    subject: '2',
    semester: '1',
    scheduleColor: '#409EFF',
    chargeByClass: row.chargeByClass || false,
    chargeByMonth: row.chargeByMonth || false,
    chargeByDay: row.chargeByDay || false,
    classDeductRule: '1',
    classAbsenceRule: '1',
    classPrices: row.classPrices || [],
    monthPrices: row.monthPrices || [],
    dayPrices: row.dayPrices || [],
    remark: ''
  };
  courseOpen.value = true;
  courseTitle.value = '修改课程';
}

/** 删除按钮操作 */
function handleDeleteCourse(row) {
  const ids = row.id || courseIds.value;
  proxy.$modal.confirm('是否确认删除选中的课程？').then(() => {
    proxy.$modal.msgSuccess('删除成功');
    getCourseList();
  });
}

/** 导出按钮操作 */
function handleExportCourse() {
  proxy.$modal.msgSuccess('导出功能开发中...');
}

/** 表单重置 */
function resetCourseForm() {
  courseForm.value = {
    id: undefined,
    courseName: '',
    courseType: '1',
    grade: undefined,
    subject: undefined,
    semester: undefined,
    scheduleColor: '#409EFF',
    chargeByClass: false,
    chargeByMonth: false,
    chargeByDay: false,
    classDeductRule: '1',
    classAbsenceRule: '1',
    classPrices: [{ name: '单价', quantity: 1, totalPrice: '' }],
    monthPrices: [{ name: '单价', quantity: 1, totalPrice: '' }],
    dayPrices: [{ name: '单价', quantity: 1, totalPrice: '' }],
    remark: ''
  };
  proxy.$refs.courseFormRef?.resetFields();
}

/** 取消按钮 */
function cancelCourse() {
  courseOpen.value = false;
  resetCourseForm();
}

/** 提交按钮 */
function submitCourseForm() {
  proxy.$refs.courseFormRef.validate(valid => {
    if (valid) {
      if (courseForm.value.id) {
        proxy.$modal.msgSuccess('修改成功');
      } else {
        proxy.$modal.msgSuccess('新增成功');
      }
      courseOpen.value = false;
      getCourseList();
    }
  });
}

/** 添加课时价格 */
function addClassPrice() {
  if (courseForm.value.classPrices.length >= 10) {
    proxy.$modal.msgWarning('最多只能添加10条定价标准');
    return;
  }
  courseForm.value.classPrices.push({ name: '', quantity: 1, totalPrice: '' });
}

/** 删除课时价格 */
function removeClassPrice(index) {
  courseForm.value.classPrices.splice(index, 1);
}

/** 添加月价格 */
function addMonthPrice() {
  if (courseForm.value.monthPrices.length >= 10) {
    proxy.$modal.msgWarning('最多只能添加10条定价标准');
    return;
  }
  courseForm.value.monthPrices.push({ name: '', quantity: 1, totalPrice: '' });
}

/** 删除月价格 */
function removeMonthPrice(index) {
  courseForm.value.monthPrices.splice(index, 1);
}

/** 添加天价格 */
function addDayPrice() {
  if (courseForm.value.dayPrices.length >= 10) {
    proxy.$modal.msgWarning('最多只能添加10条定价标准');
    return;
  }
  courseForm.value.dayPrices.push({ name: '', quantity: 1, totalPrice: '' });
}

/** 删除天价格 */
function removeDayPrice(index) {
  courseForm.value.dayPrices.splice(index, 1);
}

// ==================== 套餐管理相关方法 ====================

/** 查询套餐列表 */
function getPackageList() {
  packageLoading.value = true;
  // 模拟数据
  setTimeout(() => {
    packageList.value = [
      {
        id: 1,
        packageName: '钢琴全套',
        totalPrice: 1900.00,
        status: 1
      },
      {
        id: 2,
        packageName: '全天',
        totalPrice: 4800.00,
        status: 1
      },
      {
        id: 3,
        packageName: '4节课2套',
        totalPrice: 4900.00,
        status: 1
      },
      {
        id: 4,
        packageName: '4节包',
        totalPrice: 4000.00,
        status: 1
      },
      {
        id: 5,
        packageName: '开学送出套餐',
        totalPrice: 6800.00,
        status: 1
      },
      {
        id: 6,
        packageName: 'PWMA钢琴入门套餐PWMA钢琴出证班',
        totalPrice: 42600.00,
        status: 1
      }
    ];
    packageTotal.value = 6;
    packageLoading.value = false;
  }, 500);
}

/** 搜索套餐 */
function handlePackageQuery() {
  packageQueryParams.value.pageNum = 1;
  getPackageList();
}

/** 重置套餐搜索 */
function resetPackageQuery() {
  packageQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    packageName: undefined,
    status: ''
  };
  handlePackageQuery();
}

/** 添加套餐 */
function handleAddPackage() {
  resetPackageForm();
  packageOpen.value = true;
  packageTitle.value = '添加套餐';
}

/** 修改套餐 */
function handleUpdatePackage(row) {
  resetPackageForm();
  packageForm.value = { ...row };
  packageOpen.value = true;
  packageTitle.value = '修改套餐';
}

/** 删除套餐 */
function handleDeletePackage(row) {
  proxy.$modal.confirm('是否确认删除套餐名称为"' + row.packageName + '"的数据项？').then(() => {
    proxy.$modal.msgSuccess('删除成功');
    getPackageList();
  });
}

/** 重置套餐表单 */
function resetPackageForm() {
  packageForm.value = {
    packageName: '',
    remark: '',
    courses: [],
    items: [],
    fees: []
  };
}

/** 取消套餐 */
function cancelPackage() {
  packageOpen.value = false;
  resetPackageForm();
}

/** 提交套餐表单 */
function submitPackageForm() {
  proxy.$refs.packageFormRef.validate(valid => {
    if (valid) {
      if (packageForm.value.id) {
        proxy.$modal.msgSuccess('修改成功');
      } else {
        proxy.$modal.msgSuccess('新增成功');
      }
      packageOpen.value = false;
      getPackageList();
    }
  });
}

/** 计算套餐总价 */
const calculatePackageTotal = computed(() => {
  let total = 0;

  // 计算课程价格
  packageForm.value.courses?.forEach(course => {
    if (course.price) {
      total += parseFloat(course.price);
    }
  });

  // 计算物品价格
  packageForm.value.items?.forEach(item => {
    if (item.price) {
      total += parseFloat(item.price);
    }
  });

  // 计算费用价格
  packageForm.value.fees?.forEach(fee => {
    if (fee.price) {
      total += parseFloat(fee.price);
    }
  });

  return total.toFixed(2);
});

// ==================== 选择课程相关方法 ====================

/** 打开选择课程对话框 */
function openCourseDialog() {
  courseDialogVisible.value = true;
  loadAvailableCourses();
}

/** 加载可选课程列表 */
function loadAvailableCourses() {
  // 模拟数据 - 从课程列表中获取，并展开定价标准
  const allCourses = [];

  // 课程1：小学数学999
  allCourses.push({
    id: 1,
    courseName: '小学数学999',
    courseType: '1',
    pricingName: '单价(1200元/课时) 单-1课',
    price: 1200
  });

  // 课程2：托管0322 - 展开多个定价标准
  allCourses.push({
    id: 2,
    courseName: '托管0322',
    courseType: '2',
    pricingName: '单价(1500元/月)',
    price: 1500
  });
  allCourses.push({
    id: 3,
    courseName: '托管0322',
    courseType: '2',
    pricingName: '套餐(1500元/月) 单-3月',
    price: 1500
  });
  allCourses.push({
    id: 4,
    courseName: '托管0322',
    courseType: '2',
    pricingName: '半年(1200元/月) 单-6月',
    price: 1200
  });

  // 添加更多模拟课程
  allCourses.push({
    id: 5,
    courseName: '幼儿托班',
    courseType: '1',
    pricingName: '单价(1500元/月)',
    price: 1500
  });
  allCourses.push({
    id: 6,
    courseName: '少儿英语',
    courseType: '1',
    pricingName: '单价(200元/课时) 单-1课',
    price: 200
  });

  availableCourseList.value = allCourses;
}

/** 搜索课程 */
function searchCourseList() {
  loadAvailableCourses();
  if (courseSearchName.value) {
    availableCourseList.value = availableCourseList.value.filter(item =>
      item.courseName.includes(courseSearchName.value)
    );
  }
}

/** 课程选择变化（对话框） */
function handleDialogCourseSelectionChange(selection) {
  selectedCourses.value = selection;
}

/** 确认选择课程 */
function confirmCourseSelection() {
  // 添加选中的课程到套餐中（去重）
  selectedCourses.value.forEach(course => {
    const exists = packageForm.value.courses.some(c =>
      c.id === course.id && c.pricingName === course.pricingName
    );
    if (!exists) {
      packageForm.value.courses.push({ ...course });
    }
  });
  courseDialogVisible.value = false;
  selectedCourses.value = [];
}

/** 移除课程 */
function removeCourse(index) {
  packageForm.value.courses.splice(index, 1);
}

// ==================== 选择物品相关方法 ====================

/** 打开选择物品对话框 */
function openItemDialog() {
  itemDialogVisible.value = true;
  loadAvailableItems();
}

/** 加载可选物品列表 */
function loadAvailableItems() {
  // 模拟数据
  availableItemList.value = [
    { id: 1, itemName: '物理自然笔', price: 150.00, stock: 56 },
    { id: 2, itemName: '中包', price: 100.00, stock: 2 },
    { id: 3, itemName: '古筝耳朵校区', price: 1999.00, stock: 215 },
    { id: 4, itemName: '古筝耳朵校区', price: 1999.00, stock: 139 },
    { id: 5, itemName: '工作服', price: 69.00, stock: 155 },
    { id: 6, itemName: '教材', price: 100.00, stock: 12 },
    { id: 7, itemName: '教材', price: 100.00, stock: 0 },
    { id: 8, itemName: '教材', price: 90.00, stock: 2 }
  ];
}

/** 搜索物品 */
function searchItemList() {
  loadAvailableItems();
  if (itemSearchName.value) {
    availableItemList.value = availableItemList.value.filter(item =>
      item.itemName.includes(itemSearchName.value)
    );
  }
}

/** 物品选择变化 */
function handleItemSelectionChange(selection) {
  selectedItems.value = selection;
}

/** 确认选择物品 */
function confirmItemSelection() {
  // 添加选中的物品到套餐中（去重）
  selectedItems.value.forEach(item => {
    const exists = packageForm.value.items.some(i => i.id === item.id);
    if (!exists) {
      packageForm.value.items.push({ ...item });
    }
  });
  itemDialogVisible.value = false;
  selectedItems.value = [];
}

/** 移除物品 */
function removeItem(index) {
  packageForm.value.items.splice(index, 1);
}

// ==================== 选择费用相关方法 ====================

/** 打开选择费用对话框 */
function openFeeDialog() {
  feeDialogVisible.value = true;
  loadAvailableFees();
}

/** 加载可选费用列表 */
function loadAvailableFees() {
  // 模拟数据
  availableFeeList.value = [
    { id: 1, feeName: '产证', price: 20000.00 },
    { id: 2, feeName: '广告1', price: 10000.00 },
    { id: 3, feeName: '教育中心', price: 0.00 },
    { id: 4, feeName: '教育中心天', price: 1500.00 },
    { id: 5, feeName: '少年宫考级', price: 20000.00 },
    { id: 6, feeName: '艺考考级', price: 10000.00 },
    { id: 7, feeName: '监不到费用', price: 199.00 },
    { id: 8, feeName: 'b站抽奖费', price: 150.00 }
  ];
}

/** 搜索费用 */
function searchFeeList() {
  loadAvailableFees();
  if (feeSearchName.value) {
    availableFeeList.value = availableFeeList.value.filter(item =>
      item.feeName.includes(feeSearchName.value)
    );
  }
}

/** 费用选择变化 */
function handleFeeSelectionChange(selection) {
  selectedFees.value = selection;
}

/** 确认选择费用 */
function confirmFeeSelection() {
  // 添加选中的费用到套餐中（去重）
  selectedFees.value.forEach(fee => {
    const exists = packageForm.value.fees.some(f => f.id === fee.id);
    if (!exists) {
      packageForm.value.fees.push({ ...fee });
    }
  });
  feeDialogVisible.value = false;
  selectedFees.value = [];
}

/** 移除费用 */
function removeFee(index) {
  packageForm.value.fees.splice(index, 1);
}

// 初始化
getCourseList();
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>

