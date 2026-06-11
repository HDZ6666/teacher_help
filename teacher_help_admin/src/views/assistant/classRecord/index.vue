<template>
  <div class="app-container">
    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- 点名记录Tab -->
      <el-tab-pane label="点名记录" name="attendance">
        <!-- 搜索栏 -->
        <el-form :model="queryParams" ref="queryRef" :inline="true" label-width="80px">
          <el-form-item label="上课日期" style="width: 308px">
            <el-date-picker
              v-model="dateRange"
              value-format="YYYY-MM-DD"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="合并日期" prop="mergeDate">
            <el-date-picker
              v-model="queryParams.mergeDate"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select
              v-model="queryParams.classId"
              placeholder="请选择班级"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in classList"
                :key="item.id"
                :label="item.className"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="授课课程" prop="courseId">
            <el-select
              v-model="queryParams.courseId"
              placeholder="请选择课程"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in courseList"
                :key="item.id"
                :label="item.courseName"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="上课老师" prop="teacherId">
            <el-select
              v-model="queryParams.teacherId"
              placeholder="请选择老师"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in teacherList"
                :key="item.id"
                :label="item.teacherName"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="课程类型" prop="courseType">
            <el-select
              v-model="queryParams.courseType"
              placeholder="请选择类型"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select
              v-model="queryParams.status"
              placeholder="请选择状态"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Plus" @click="handleAdd">新增</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleExport">导出</el-button>
          </el-col>
          <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
        </el-row>

        <!-- 数据表格 -->
        <el-table v-loading="loading" :data="recordList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="点名时间" align="center" prop="attendanceTime" width="180" sortable>
            <template #default="scope">
              <span>{{ parseTime(scope.row.attendanceTime, '{y}-{m}-{d} {h}:{i}') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="班级名称" align="center" prop="className" width="150" />
          <el-table-column label="授课课程" align="center" prop="courseName" width="150" />
          <el-table-column label="上课时间" align="center" width="200">
            <template #default="scope">
              <span>{{ scope.row.startTime }} - {{ scope.row.endTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课老师" align="center" prop="teacherName" width="100" />
          <el-table-column label="授课时长" align="center" prop="duration" width="100">
            <template #default="scope">
              <span>{{ scope.row.duration }}分钟</span>
            </template>
          </el-table-column>
          <el-table-column label="应到人数" align="center" prop="expectedCount" width="100" />
          <el-table-column label="实到人数" align="center" prop="actualCount" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.actualCount < scope.row.expectedCount ? 'warning' : 'success'">
                {{ scope.row.actualCount }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="课程名额" align="center" prop="capacity" width="100" />
          <el-table-column label="课程合计" align="center" prop="totalAmount" width="120">
            <template #default="scope">
              <span>¥{{ scope.row.totalAmount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课教室" align="center" prop="classroom" width="120" />
          <el-table-column label="操作" align="center" width="250" fixed="right">
            <template #default="scope">
              <el-button type="primary" link size="small" @click="handleDetail(scope.row)">详情</el-button>
              <el-button type="warning" link size="small" @click="handleComment(scope.row)">点评记录</el-button>
              <el-button type="success" link size="small" @click="handleEdit(scope.row)">调课</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </el-tab-pane>

      <!-- 超时未点Tab -->
      <el-tab-pane label="超时未点" name="overtime">
        <!-- 搜索栏 -->
        <el-form :model="overtimeQueryParams" ref="overtimeQueryRef" :inline="true" label-width="80px">
          <el-form-item label="上课日期" style="width: 308px">
            <el-date-picker
              v-model="overtimeDateRange"
              value-format="YYYY-MM-DD"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select
              v-model="overtimeQueryParams.classId"
              placeholder="请选择班级"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in classList"
                :key="item.id"
                :label="item.className"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleOvertimeQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetOvertimeQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Warning" @click="handleBatchRemind">批量提醒</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleOvertimeExport">导出</el-button>
          </el-col>
        </el-row>

        <!-- 数据表格 -->
        <el-table v-loading="overtimeLoading" :data="overtimeList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="上课时间" align="center" width="180" sortable>
            <template #default="scope">
              <span>{{ scope.row.classDate }} {{ scope.row.classTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="班级名称" align="center" prop="className" width="150" />
          <el-table-column label="上课老师" align="center" prop="teacherName" width="100" />
          <el-table-column label="授课课程" align="center" prop="courseName" width="150" />
          <el-table-column label="上课教室" align="center" prop="classroom" width="120" />
          <el-table-column label="上课内容" align="center" prop="classContent" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="scope">
              <el-button type="warning" link size="small" @click="handleRemind(scope.row)">去点名</el-button>
              <el-button type="primary" link size="small" @click="handleOvertimeDetail(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="overtimeTotal > 0"
          :total="overtimeTotal"
          v-model:page="overtimeQueryParams.pageNum"
          v-model:limit="overtimeQueryParams.pageSize"
          @pagination="getOvertimeList"
        />
      </el-tab-pane>

      <!-- 缺课补课Tab -->
      <el-tab-pane label="缺课补课" name="makeup">
        <!-- 搜索栏 -->
        <el-form :model="makeupQueryParams" ref="makeupQueryRef" :inline="true" label-width="100px">
          <el-form-item label="搜索学员">
            <el-input
              v-model="makeupQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 240px"
              @keyup.enter="handleMakeupQuery"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select
              v-model="makeupQueryParams.classId"
              placeholder="请选择班级"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in classList"
                :key="item.id"
                :label="item.className"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="上课日期" style="width: 308px">
            <el-date-picker
              v-model="makeupDateRange"
              value-format="YYYY-MM-DD"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            ></el-date-picker>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleMakeupQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetMakeupQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Bell" @click="handleBatchNotify">开课提醒</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleMakeupExport">导出</el-button>
          </el-col>
        </el-row>

        <!-- 数据表格 -->
        <el-table v-loading="makeupLoading" :data="makeupList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="学员姓名" align="center" prop="studentName" width="120" />
          <el-table-column label="手机号" align="center" prop="phone" width="130" />
          <el-table-column label="班级名称" align="center" prop="className" width="150" />
          <el-table-column label="上课时间" align="center" width="180">
            <template #default="scope">
              <span>{{ scope.row.classDate }} {{ scope.row.classTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课老师" align="center" prop="teacherName" width="100" />
          <el-table-column label="课程" align="center" prop="courseName" width="120" />
          <el-table-column label="缺课状态" align="center" prop="makeupStatus" width="120">
            <template #default="scope">
              <el-tag :type="getMakeupStatusType(scope.row.makeupStatus)">
                {{ scope.row.makeupStatus }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="消耗方式" align="center" prop="consumeType" width="120" />
          <el-table-column label="应扣课数" align="center" prop="shouldDeduct" width="100" />
          <el-table-column label="实扣课数" align="center" prop="actualDeduct" width="100" />
          <el-table-column label="补课状态" align="center" prop="madeupStatus" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.madeupStatus" type="success">已补课</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="补课详情" align="center" prop="makeupDetail" width="100">
            <template #default="scope">
              <span>{{ scope.row.makeupDetail || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上课内容" align="center" prop="classContent" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" align="center" width="200" fixed="right">
            <template #default="scope">
              <el-button type="warning" link size="small" icon="Bell" @click="handleNotifyMakeup(scope.row)">提醒补课</el-button>
              <el-button type="primary" link size="small" icon="Edit" @click="handleMarkMadeup(scope.row)">标记已补</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="makeupTotal > 0"
          :total="makeupTotal"
          v-model:page="makeupQueryParams.pageNum"
          v-model:limit="makeupQueryParams.pageSize"
          @pagination="getMakeupList"
        />
      </el-tab-pane>

      <!-- 缺课提醒Tab -->
      <el-tab-pane label="缺课提醒" name="absence">
        <!-- 搜索栏 -->
        <el-form :model="absenceQueryParams" ref="absenceQueryRef" :inline="true" label-width="100px">
          <el-form-item label="搜索学员">
            <el-input
              v-model="absenceQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 240px"
              @keyup.enter="handleAbsenceQuery"
            />
          </el-form-item>
          <el-form-item label="所在班级" prop="classId">
            <el-select
              v-model="absenceQueryParams.classId"
              placeholder="请选择班级"
              clearable
              style="width: 200px"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="item in classList"
                :key="item.id"
                :label="item.className"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="未到次数" style="width: 308px">
            <el-row :gutter="10">
              <el-col :span="11">
                <el-input v-model="absenceQueryParams.minAbsences" placeholder="最小值" clearable />
              </el-col>
              <el-col :span="2" style="text-align: center">-</el-col>
              <el-col :span="11">
                <el-input v-model="absenceQueryParams.maxAbsences" placeholder="最大值" clearable />
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleAbsenceQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetAbsenceQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="warning" plain icon="Bell" @click="handleBatchRemindAbsence">提醒</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleAbsenceExport">导出</el-button>
          </el-col>
          <right-toolbar @queryTable="getAbsenceList" />
        </el-row>

        <!-- 提醒说明 -->
        <el-alert
          title="别忘记提示学员示今天之前的课程进行点名哦！"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 10px"
        />

        <!-- 提醒规则说明 -->
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 10px"
        >
          <template #title>
            <div>
              提醒规则说明：距离最近一次课程结束后，未到课数≥2次提醒班级，未到课数≥3次提醒家长
            </div>
          </template>
        </el-alert>

        <!-- 数据表格 -->
        <el-table v-loading="absenceLoading" :data="absenceList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="学员" align="center" prop="studentName" width="100" />
          <el-table-column label="手机号" align="center" prop="phone" width="130" />
          <el-table-column label="所在班级" align="center" prop="className" width="150" />
          <el-table-column label="未到次数" align="center" prop="absenceCount" width="100" />
          <el-table-column label="应扣次数" align="center" prop="shouldDeduct" width="100" />
          <el-table-column label="未上课数" align="center" prop="missedClasses" width="100" />
          <el-table-column label="限制人" align="center" prop="restrictedBy" width="100">
            <template #default="scope">
              <span>{{ scope.row.restrictedBy || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="学管师" align="center" prop="advisor" width="100">
            <template #default="scope">
              <span>{{ scope.row.advisor || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="上次提醒时间" align="center" prop="lastRemindTime" width="160">
            <template #default="scope">
              <span>{{ scope.row.lastRemindTime || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150" fixed="right">
            <template #default="scope">
              <el-button type="warning" link size="small" icon="Bell" @click="handleRemindAbsence(scope.row)">提醒</el-button>
              <el-button type="primary" link size="small" icon="Edit" @click="handleMarkReminded(scope.row)">不再提醒</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="absenceTotal > 0"
          :total="absenceTotal"
          v-model:page="absenceQueryParams.pageNum"
          v-model:limit="absenceQueryParams.pageSize"
          @pagination="getAbsenceList"
        />
      </el-tab-pane>

      <!-- 请假申请Tab -->
      <el-tab-pane label="请假申请" name="leave">
        <!-- 搜索栏 -->
        <el-form :model="leaveQueryParams" ref="leaveQueryRef" :inline="true" label-width="80px">
          <el-form-item label="搜索学员" prop="studentKeyword">
            <el-input
              v-model="leaveQueryParams.studentKeyword"
              placeholder="请输入学员姓名/手机号/课程"
              clearable
              style="width: 240px"
              @keyup.enter="handleLeaveQuery"
            />
          </el-form-item>
          <el-form-item label="处理状态" prop="status">
            <el-select
              v-model="leaveQueryParams.status"
              placeholder="请选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已同意" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item label="申请时间" style="width: 308px">
            <el-date-picker
              v-model="leaveApplyDateRange"
              value-format="YYYY-MM-DD"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="结束时间" style="width: 308px">
            <el-date-picker
              v-model="leaveEndDateRange"
              value-format="YYYY-MM-DD"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            ></el-date-picker>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="Search" @click="handleLeaveQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetLeaveQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <el-row :gutter="10" class="mb8">
          <el-col :span="1.5">
            <el-button type="primary" plain icon="Check" @click="handleBatchApprove">批量同意按钮</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="info" plain icon="Document" @click="handleLeaveReceipt">请假收据</el-button>
          </el-col>
          <el-col :span="1.5">
            <el-button type="success" plain icon="Download" @click="handleLeaveExport">导出</el-button>
          </el-col>
          <right-toolbar @queryTable="getLeaveList" />
        </el-row>

        <!-- 数据表格 -->
        <el-table v-loading="leaveLoading" :data="leaveList" border>
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="申请学员" align="center" width="150">
            <template #default="scope">
              <div style="display: flex; align-items: center; justify-content: center;">
                <el-avatar :size="32" style="margin-right: 8px;">
                  {{ scope.row.studentName.charAt(0) }}
                </el-avatar>
                <div style="text-align: left;">
                  <div>{{ scope.row.studentName }}</div>
                  <div style="color: #999; font-size: 12px;">{{ scope.row.phone }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="课程时间" align="center" prop="courseTime" width="180" />
          <el-table-column label="申请时间" align="center" prop="applyTime" width="180" />
          <el-table-column label="请假类型" align="center" prop="leaveType" width="100" />
          <el-table-column label="请假原因" align="center" prop="leaveReason" width="100">
            <template #default="scope">
              <span>{{ scope.row.leaveReason || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="处理时间" align="center" prop="handleTime" width="180" />
          <el-table-column label="处理状态" align="center" prop="status" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'approved'" type="success">已同意</el-tag>
              <el-tag v-else-if="scope.row.status === 'rejected'" type="danger">已拒绝</el-tag>
              <el-tag v-else type="warning">待处理</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="100" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleLeaveDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <pagination
          v-show="leaveTotal > 0"
          :total="leaveTotal"
          v-model:page="leaveQueryParams.pageNum"
          v-model:limit="leaveQueryParams.pageSize"
          @pagination="getLeaveList"
        />
      </el-tab-pane>

    </el-tabs>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="点名记录详情" width="800px" append-to-body>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="班级名称">{{ currentRecord.className }}</el-descriptions-item>
        <el-descriptions-item label="授课课程">{{ currentRecord.courseName }}</el-descriptions-item>
        <el-descriptions-item label="上课老师">{{ currentRecord.teacherName }}</el-descriptions-item>
        <el-descriptions-item label="上课教室">{{ currentRecord.classroom }}</el-descriptions-item>
        <el-descriptions-item label="上课时间" :span="2">
          {{ currentRecord.startTime }} - {{ currentRecord.endTime }}
        </el-descriptions-item>
        <el-descriptions-item label="授课时长">{{ currentRecord.duration }}分钟</el-descriptions-item>
        <el-descriptions-item label="应到人数">{{ currentRecord.expectedCount }}</el-descriptions-item>
        <el-descriptions-item label="实到人数">{{ currentRecord.actualCount }}</el-descriptions-item>
        <el-descriptions-item label="课程合计">¥{{ currentRecord.totalAmount }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="ClassRecord">
import { parseTime } from '@/utils/ruoyi'
import { useRouter } from 'vue-router'

const { proxy } = getCurrentInstance()
const router = useRouter()

// 当前激活的Tab
const activeTab = ref('attendance')
const loading = ref(false)
const showSearch = ref(true)
const recordList = ref([])
const total = ref(0)
const dateRange = ref([])
const detailDialogVisible = ref(false)
const currentRecord = ref({})

// 超时未点Tab数据
const overtimeLoading = ref(false)
const overtimeList = ref([])
const overtimeTotal = ref(0)
const overtimeDateRange = ref([])
const overtimeQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  classId: '',
  teacherId: ''
})

// 缺课补课Tab数据
const makeupLoading = ref(false)
const makeupList = ref([])
const makeupTotal = ref(0)
const makeupDateRange = ref([])
const makeupQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  classId: ''
})

// 缺课提醒Tab数据
const absenceLoading = ref(false)
const absenceList = ref([])
const absenceTotal = ref(0)
const absenceQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  classId: '',
  minAbsences: '',
  maxAbsences: ''
})

// 请假申请Tab数据
const leaveLoading = ref(false)
const leaveList = ref([])
const leaveTotal = ref(0)
const leaveQueryParams = ref({
  pageNum: 1,
  pageSize: 10,
  studentKeyword: '',
  status: ''
})
const leaveApplyDateRange = ref([])
const leaveEndDateRange = ref([])

// 下拉选项数据
const classList = ref([])
const courseList = ref([])
const teacherList = ref([])

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  mergeDate: null,
  classId: '',
  courseId: '',
  teacherId: '',
  courseType: '',
  status: ''
})

/** 查询点名记录列表 */
function getList() {
  loading.value = true
  // 模拟数据
  setTimeout(() => {
    recordList.value = generateMockData()
    total.value = 50
    loading.value = false
  }, 500)
}

/** 生成模拟数据 */
function generateMockData() {
  const mockData = []
  const classNames = ['街舞1班', '中国舞2班', '现代舞3班', '民族舞4班']
  const courseNames = ['街舞基础', '中国舞进阶', '现代舞初级', '民族舞高级']
  const teacherNames = ['孟吉', '忠贞', '庆庆', '李老师']
  const classrooms = ['教室A101', '教室B202', '教室C303', '舞蹈室1']

  for (let i = 0; i < 10; i++) {
    const expectedCount = 10 + Math.floor(Math.random() * 10)
    const actualCount = expectedCount - Math.floor(Math.random() * 3)
    const duration = 90
    const pricePerStudent = 208.42

    mockData.push({
      id: i + 1,
      attendanceTime: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
      className: classNames[i % 4],
      courseName: courseNames[i % 4],
      startTime: '10:00',
      endTime: '11:30',
      teacherName: teacherNames[i % 4],
      duration: duration,
      expectedCount: expectedCount,
      actualCount: actualCount,
      capacity: expectedCount,
      totalAmount: (actualCount * pricePerStudent).toFixed(2),
      classroom: classrooms[i % 4]
    })
  }

  return mockData
}

/** Tab切换 */
function handleTabClick(tab) {
  console.log('切换到Tab:', tab.props.name)
  if (tab.props.name === 'attendance') {
    getList()
  } else if (tab.props.name === 'overtime') {
    getOvertimeList()
  } else if (tab.props.name === 'makeup') {
    getMakeupList()
  } else if (tab.props.name === 'absence') {
    getAbsenceList()
  } else if (tab.props.name === 'leave') {
    getLeaveList()
  }
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = []
  queryParams.value = {
    pageNum: 1,
    pageSize: 10,
    mergeDate: null,
    classId: '',
    courseId: '',
    teacherId: '',
    courseType: '',
    status: ''
  }
  getList()
}

/** 新增按钮操作 */
function handleAdd() {
  proxy.$modal.msgInfo('新增功能开发中')
}

/** 导出按钮操作 */
function handleExport() {
  proxy.$modal.msgInfo('导出功能开发中')
}

/** 查看详情 */
function handleDetail(row) {
  // 跳转到详情页面
  router.push({
    name: 'ClassRecordDetail',
    params: { id: row.id }
  })
}

/** 点评记录 */
function handleComment(row) {
  // 跳转到点评详情页面
  router.push({
    name: 'CommentDetail',
    params: { id: row.id }
  })
}

/** 调课操作 */
function handleEdit(row) {
  proxy.$modal.msgInfo('调课功能开发中')
}

/** 删除操作 */
function handleDelete(row) {
  proxy.$modal.confirm('是否确认删除该点名记录？').then(() => {
    proxy.$modal.msgSuccess('删除成功')
    getList()
  }).catch(() => {})
}

/** 初始化下拉选项数据 */
function initSelectOptions() {
  // 模拟班级数据
  classList.value = [
    { id: 1, className: '街舞1班' },
    { id: 2, className: '中国舞2班' },
    { id: 3, className: '现代舞3班' },
    { id: 4, className: '民族舞4班' }
  ]

  // 模拟课程数据
  courseList.value = [
    { id: 1, courseName: '街舞基础' },
    { id: 2, courseName: '中国舞进阶' },
    { id: 3, courseName: '现代舞初级' },
    { id: 4, courseName: '民族舞高级' }
  ]

  // 模拟教师数据
  teacherList.value = [
    { id: 1, teacherName: '孟吉' },
    { id: 2, teacherName: '忠贞' },
    { id: 3, teacherName: '庆庆' },
    { id: 4, teacherName: '李老师' }
  ]
}

/** 查询超时未点列表 */
function getOvertimeList() {
  overtimeLoading.value = true
  // 模拟数据
  setTimeout(() => {
    overtimeList.value = generateOvertimeMockData()
    overtimeTotal.value = 30
    overtimeLoading.value = false
  }, 500)
}

/** 生成超时未点模拟数据 */
function generateOvertimeMockData() {
  const mockData = []
  const classNames = ['托管训练班A班00-10:00', '蓝球U6班', '演2', '英语一班', '蓝球基础班']
  const courseNames = ['托管训练', '蓝球课', '舞蹈', '英语', '蓝球基础']
  const teacherNames = ['叶老师', '黄老师', '齐', '叶老师', '叶老师']
  const classrooms = ['-', '蓝球课', '教室1', '万达4楼', '-']
  const contents = ['-', '-', '-', '-', '测试']
  const dates = ['2025-11-07', '2025-11-07', '2025-11-06', '2025-11-06', '2025-11-06']
  const times = ['10:00-11:30', '09:00-10:00', '23:35-23:40', '14:40-19:45', '10:00-11:30']

  for (let i = 0; i < 10; i++) {
    const idx = i % 5
    mockData.push({
      id: i + 1,
      classId: idx + 1, // 添加班级ID，用于跳转到点名页面
      classDate: dates[idx],
      classTime: times[idx],
      className: classNames[idx],
      teacherName: teacherNames[idx],
      courseName: courseNames[idx],
      classroom: classrooms[idx],
      classContent: contents[idx],
      status: 'overtime'
    })
  }

  return mockData
}

/** 超时未点搜索 */
function handleOvertimeQuery() {
  overtimeQueryParams.value.pageNum = 1
  getOvertimeList()
}

/** 超时未点重置 */
function resetOvertimeQuery() {
  overtimeDateRange.value = []
  overtimeQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    classId: '',
    teacherId: ''
  }
  getOvertimeList()
}

/** 批量提醒 */
function handleBatchRemind() {
  proxy.$modal.msgInfo('批量提醒功能开发中')
}

/** 超时未点导出 */
function handleOvertimeExport() {
  proxy.$modal.msgInfo('导出功能开发中')
}

/** 去点名 */
function handleRemind(row) {
  // 跳转到班级点名页面
  if (row.classId) {
    router.push({
      name: 'ClassAttendance',
      params: { id: row.classId }
    })
  } else {
    proxy.$modal.msgError('无法获取班级信息')
  }
}

/** 超时未点详情 */
function handleOvertimeDetail(row) {
  currentRecord.value = { ...row }
  detailDialogVisible.value = true
}

// ==================== 缺课补课Tab方法 ====================

/** 查询缺课补课列表 */
function getMakeupList() {
  makeupLoading.value = true
  const params = { ...makeupQueryParams.value }
  if (makeupDateRange.value && makeupDateRange.value.length === 2) {
    params.startDate = makeupDateRange.value[0]
    params.endDate = makeupDateRange.value[1]
  }

  // 模拟数据
  setTimeout(() => {
    makeupList.value = [
      {
        id: 1,
        studentName: '林蔓',
        phone: '188****9695',
        className: '杭州训练营A3-00...',
        classDate: '2025-11-03',
        classTime: '10:00~11:30',
        teacherName: '叶老师',
        courseName: '未到',
        makeupStatus: '【托班训练】',
        consumeType: '课程',
        shouldDeduct: '1课时',
        actualDeduct: '0课时',
        madeupStatus: false,
        makeupDetail: '',
        classContent: ''
      },
      {
        id: 2,
        studentName: '蔡子慧',
        phone: '134****0512',
        className: '杭州训练营A3-00...',
        classDate: '2025-11-03',
        classTime: '10:00~11:30',
        teacherName: '叶老师',
        courseName: '请假',
        makeupStatus: '【托班训练】',
        consumeType: '课程',
        shouldDeduct: '1课时',
        actualDeduct: '0课时',
        madeupStatus: false,
        makeupDetail: '',
        classContent: ''
      },
      {
        id: 3,
        studentName: '蒋韵成',
        phone: '164****6465',
        className: '杭州训练营A3-00...',
        classDate: '2025-11-03',
        classTime: '10:00~11:30',
        teacherName: '叶老师',
        courseName: '请假',
        makeupStatus: '【托班训练】',
        consumeType: '课程',
        shouldDeduct: '1课时',
        actualDeduct: '0课时',
        madeupStatus: false,
        makeupDetail: '',
        classContent: ''
      }
    ]
    makeupTotal.value = 3
    makeupLoading.value = false
  }, 500)
}

/** 搜索按钮操作 */
function handleMakeupQuery() {
  makeupQueryParams.value.pageNum = 1
  getMakeupList()
}

/** 重置按钮操作 */
function resetMakeupQuery() {
  makeupDateRange.value = []
  makeupQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    studentKeyword: '',
    classId: ''
  }
  getMakeupList()
}

/** 获取缺课状态标签类型 */
function getMakeupStatusType(status) {
  const typeMap = {
    '【托班训练】': 'warning',
    '【试听训练】': 'info',
    '【正课训练】': 'danger'
  }
  return typeMap[status] || 'info'
}

/** 提醒补课 */
function handleNotifyMakeup(row) {
  proxy.$modal.confirm(`确认要提醒学员"${row.studentName}"补课吗？`).then(() => {
    // TODO: 调用提醒接口
    proxy.$modal.msgSuccess('提醒成功')
  }).catch(() => {})
}

/** 批量提醒 */
function handleBatchNotify() {
  proxy.$modal.msgWarning('请选择要提醒的学员')
}

/** 标记已补课 */
function handleMarkMadeup(row) {
  proxy.$modal.confirm(`确认要标记学员"${row.studentName}"已补课吗？`).then(() => {
    // TODO: 调用标记接口
    proxy.$modal.msgSuccess('标记成功')
    getMakeupList()
  }).catch(() => {})
}

/** 导出缺课补课记录 */
function handleMakeupExport() {
  proxy.download('assistant/classRecord/makeup/export', {
    ...makeupQueryParams.value
  }, `缺课补课记录_${new Date().getTime()}.xlsx`)
}

// ==================== 缺课提醒Tab方法 ====================

/** 查询缺课提醒列表 */
function getAbsenceList() {
  absenceLoading.value = true
  const params = { ...absenceQueryParams.value }

  // 模拟数据
  setTimeout(() => {
    absenceList.value = [
      {
        id: 1,
        studentName: '二分',
        phone: '123****8855',
        className: '测2',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 121,
        restrictedBy: '演示专用',
        advisor: '',
        lastRemindTime: ''
      },
      {
        id: 2,
        studentName: '美好梦',
        phone: '186****7279',
        className: '蓝球队班',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 92,
        restrictedBy: '齐',
        advisor: '黄老师',
        lastRemindTime: ''
      },
      {
        id: 3,
        studentName: '宁宁',
        phone: '187****5892',
        className: '蓝球队班、测2',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 92,
        restrictedBy: '演示专用',
        advisor: '',
        lastRemindTime: ''
      },
      {
        id: 4,
        studentName: '西西',
        phone: '186****5205',
        className: '蓝球队班',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 92,
        restrictedBy: '演示专用',
        advisor: '',
        lastRemindTime: ''
      },
      {
        id: 5,
        studentName: '来二',
        phone: '152****6231',
        className: '蓝球队班',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 92,
        restrictedBy: '齐老师',
        advisor: '',
        lastRemindTime: ''
      },
      {
        id: 6,
        studentName: '周雨彤',
        phone: '188****6151',
        className: '',
        absenceCount: 0,
        shouldDeduct: 0,
        missedClasses: 168,
        restrictedBy: '',
        advisor: '',
        lastRemindTime: ''
      }
    ]
    absenceTotal.value = 6
    absenceLoading.value = false
  }, 500)
}

/** 搜索按钮操作 */
function handleAbsenceQuery() {
  absenceQueryParams.value.pageNum = 1
  getAbsenceList()
}

/** 重置按钮操作 */
function resetAbsenceQuery() {
  absenceQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    studentKeyword: '',
    classId: '',
    minAbsences: '',
    maxAbsences: ''
  }
  getAbsenceList()
}

/** 提醒缺课学员 */
function handleRemindAbsence(row) {
  proxy.$modal.confirm(`确认要提醒学员"${row.studentName}"吗？`).then(() => {
    // TODO: 调用提醒接口
    proxy.$modal.msgSuccess('提醒成功')
  }).catch(() => {})
}

/** 批量提醒缺课 */
function handleBatchRemindAbsence() {
  proxy.$modal.msgWarning('请选择要提醒的学员')
}

/** 标记不再提醒 */
function handleMarkReminded(row) {
  proxy.$modal.confirm(`确认要标记学员"${row.studentName}"不再提醒吗？`).then(() => {
    // TODO: 调用标记接口
    proxy.$modal.msgSuccess('标记成功')
    getAbsenceList()
  }).catch(() => {})
}

/** 导出缺课提醒记录 */
function handleAbsenceExport() {
  proxy.download('assistant/classRecord/absence/export', {
    ...absenceQueryParams.value
  }, `缺课提醒记录_${new Date().getTime()}.xlsx`)
}

// ==================== 请假申请Tab方法 ====================

/** 查询请假申请列表 */
function getLeaveList() {
  leaveLoading.value = true
  const params = { ...leaveQueryParams.value }
  if (leaveApplyDateRange.value && leaveApplyDateRange.value.length === 2) {
    params.applyStartDate = leaveApplyDateRange.value[0]
    params.applyEndDate = leaveApplyDateRange.value[1]
  }
  if (leaveEndDateRange.value && leaveEndDateRange.value.length === 2) {
    params.endStartDate = leaveEndDateRange.value[0]
    params.endEndDate = leaveEndDateRange.value[1]
  }

  // 模拟数据
  setTimeout(() => {
    leaveList.value = [
      {
        id: 1,
        studentName: '刘少明',
        phone: '152****9134',
        courseTime: '2025-03-02 15:00~16:30',
        applyTime: '2025-02-28 16:55',
        leaveType: '病假',
        leaveReason: '-',
        handleTime: '2025-02-28 16:55',
        status: 'approved'
      },
      {
        id: 2,
        studentName: '顾思雯',
        phone: '186****8566',
        courseTime: '2024-12-24 15:00~16:30',
        applyTime: '2024-12-24 21:12',
        leaveType: '病假',
        leaveReason: '-',
        handleTime: '2024-12-24 21:12',
        status: 'approved'
      },
      {
        id: 3,
        studentName: '刘少明',
        phone: '152****9134',
        courseTime: '2024-12-17 15:00~16:30',
        applyTime: '2024-12-16 16:55',
        leaveType: '病假',
        leaveReason: '-',
        handleTime: '2024-12-24 18:15',
        status: 'approved'
      },
      {
        id: 4,
        studentName: '蔡',
        phone: '150****5683',
        courseTime: '2024-11-02 15:00~16:30',
        applyTime: '2024-10-31 19:18',
        leaveType: '事假',
        leaveReason: '-',
        handleTime: '2024-10-31 19:18',
        status: 'approved'
      },
      {
        id: 5,
        studentName: '君见',
        phone: '136****8161',
        courseTime: '2024-10-30 15:00~16:30',
        applyTime: '2024-10-30 20:34',
        leaveType: '事假',
        leaveReason: '-',
        handleTime: '2024-10-30 20:34',
        status: 'approved'
      },
      {
        id: 6,
        studentName: '蔡',
        phone: '150****5683',
        courseTime: '2024-11-01 15:00~16:30',
        applyTime: '2024-10-30 20:29',
        leaveType: '事假',
        leaveReason: '-',
        handleTime: '2024-10-30 20:29',
        status: 'approved'
      },
      {
        id: 7,
        studentName: '鲁',
        phone: '123****8999',
        courseTime: '2024-10-31 15:00~16:30',
        applyTime: '2024-10-30 20:10',
        leaveType: '事假',
        leaveReason: '-',
        handleTime: '2024-10-30 20:10',
        status: 'approved'
      },
      {
        id: 8,
        studentName: '刘少明',
        phone: '152****9134',
        courseTime: '2024-10-18 15:00~16:30',
        applyTime: '2024-10-14 17:20',
        leaveType: '病假',
        leaveReason: '-',
        handleTime: '2024-10-14 17:20',
        status: 'approved'
      }
    ]
    leaveTotal.value = 8
    leaveLoading.value = false
  }, 500)
}

/** 搜索按钮操作 */
function handleLeaveQuery() {
  leaveQueryParams.value.pageNum = 1
  getLeaveList()
}

/** 重置按钮操作 */
function resetLeaveQuery() {
  leaveApplyDateRange.value = []
  leaveEndDateRange.value = []
  leaveQueryParams.value = {
    pageNum: 1,
    pageSize: 10,
    studentKeyword: '',
    status: ''
  }
  getLeaveList()
}

/** 批量同意 */
function handleBatchApprove() {
  proxy.$modal.msgWarning('请选择要同意的请假申请')
}

/** 请假收据 */
function handleLeaveReceipt() {
  proxy.$modal.msgInfo('请假收据功能开发中')
}

/** 查看详情 */
function handleLeaveDetail(row) {
  proxy.$modal.msgInfo('查看详情功能开发中')
}

/** 导出请假申请记录 */
function handleLeaveExport() {
  proxy.download('assistant/classRecord/leave/export', {
    ...leaveQueryParams.value
  }, `请假申请记录_${new Date().getTime()}.xlsx`)
}

// 组件挂载时初始化
onMounted(() => {
  initSelectOptions()
  getList()
})
</script>

<style scoped lang="scss">
.tab-content-placeholder {
  padding: 60px 0;
  text-align: center;
}

.mb8 {
  margin-bottom: 8px;
}
</style>

