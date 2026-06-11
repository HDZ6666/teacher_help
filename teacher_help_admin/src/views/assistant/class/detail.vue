<template>
  <div class="app-container class-detail">
    <!-- 头部导航 -->
    <div class="detail-header">
      <el-page-header @back="goBack" :content="classInfo.className">
        <template #icon>
          <el-icon><ArrowLeft /></el-icon>
        </template>
      </el-page-header>
      <el-button type="warning" class="edit-btn" @click="handleEdit">编辑班级信息</el-button>
    </div>

    <!-- 班级基本信息 -->
    <div class="class-info-card">
      <div class="class-title">
        <span class="class-name">{{ classInfo.className }}</span>
        <el-tag v-if="classInfo.classType === 'system'" type="success" size="small">系统</el-tag>
        <el-tag v-else type="info" size="small">自建</el-tag>
      </div>

      <el-row :gutter="20" class="info-row">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">关联课程：</span>
            <span class="value">{{ classInfo.courseName }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">实际在读人数：</span>
            <span class="value">{{ classInfo.actualStudents }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">班级老师：</span>
            <span class="value">{{ classInfo.teacherName || '待分配' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="info-row">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">人数/容量：</span>
            <span class="value">{{ classInfo.currentStudents }}/{{ classInfo.capacity }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">上课时长：</span>
            <span class="value">{{ classInfo.lessonDuration }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">备注：</span>
            <span class="value">{{ classInfo.remark || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="info-row">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">班级分类：</span>
            <span class="value">{{ classInfo.classCategory || '不指定' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">授课老师：</span>
            <span class="value">{{ classInfo.teacherName || '待分配' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">班级分类：</span>
            <span class="value">
              <el-tag v-if="classInfo.classType === 'system'" type="success" size="small">系统</el-tag>
              <el-tag v-else type="info" size="small">自建</el-tag>
            </span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="info-row">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">默认消耗金额：</span>
            <span class="value">{{ classInfo.defaultConsumption }}元</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">自动分配老师：</span>
            <span class="value">{{ classInfo.autoAssignName ? '开启' : '关闭' }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">允许充值购时：</span>
            <span class="value">{{ classInfo.allowRecharge ? '开启' : '关闭' }}</span>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="detail-tabs">
      <!-- 排课信息 -->
      <el-tab-pane label="排课信息" name="schedule">
        <div class="schedule-toolbar">
          <el-button type="primary" size="small" icon="Plus" @click="handleScheduleClass">排课</el-button>
          <div class="schedule-filters">
            <el-select v-model="scheduleFilter.teachingMethod" placeholder="授课方式" size="small" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="线下" value="offline" />
              <el-option label="线上" value="online" />
            </el-select>
            <el-select v-model="scheduleFilter.status" placeholder="状态" size="small" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
              <el-option label="未开始" value="pending" />
              <el-option label="进行中" value="ongoing" />
              <el-option label="已结束" value="finished" />
            </el-select>
            <span class="period-label" style="margin-left: 20px;">期数</span>
          </div>
        </div>

        <!-- 排课列表 -->
        <el-table
          :data="scheduleList"
          border
          class="schedule-table"
          @selection-change="handleScheduleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="排课方式" prop="teachingMethod" width="120" align="center">
            <template #default="{ row }">
              {{ row.teachingMethod === 'offline' ? '线次 第1次课' : '线上' }}
            </template>
          </el-table-column>
          <el-table-column label="上课日期" prop="classDate" width="150" align="center">
            <template #default="{ row }">
              {{ formatDateWithWeekday(row.classDate) }}
            </template>
          </el-table-column>
          <el-table-column label="授课课程" prop="courseName" min-width="120" align="center" />
          <el-table-column label="上课时间" prop="classTime" width="120" align="center" />
          <el-table-column label="上课教室" prop="classroom" width="120" align="center" />
          <el-table-column label="上课老师" prop="teacherName" width="120" align="center" />
          <el-table-column label="上课内容" prop="content" width="120" align="center" />
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-link type="warning" :underline="false" style="margin-right: 10px;" @click="handleScheduleDetail(row)">
                编辑
              </el-link>
              <el-link type="danger" :underline="false" @click="handleDeleteSchedule(row)">
                删除
              </el-link>
            </template>
          </el-table-column>
        </el-table>

        <!-- 暂无数据提示 -->
        <div v-if="scheduleList.length === 0" class="empty-data">
          <el-empty description="暂无数据" />
        </div>
      </el-tab-pane>

      <!-- 班级成员 -->
      <el-tab-pane label="班级成员" name="members">
        <div class="members-toolbar">
          <el-button type="warning" size="small" @click="handleAddStudent">添加学员</el-button>
          <div class="member-filters">
            <el-button size="small">课程卡续费</el-button>
            <el-button size="small">移出班级</el-button>
          </div>
        </div>

        <!-- 搜索栏 -->
        <div class="member-search-bar">
          <el-input
            v-model="memberSearchKeyword"
            placeholder="请输入学员姓名/手机号"
            clearable
            style="width: 300px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table
          :data="filteredMemberList"
          border
          class="members-table"
          @selection-change="handleMemberSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="姓名" width="100" align="center">
            <template #default="{ row }">
              <el-link type="primary" @click="handleViewStudent(row)">
                {{ row.studentName }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="性别" prop="gender" width="80" align="center">
            <template #default="{ row }">
              {{ row.gender === 'male' ? '男' : '女' }}
            </template>
          </el-table-column>
          <el-table-column label="手机号" prop="phone" width="130" />
          <el-table-column label="消耗方式" width="200">
            <template #default="{ row }">
              <span>课程【{{ row.consumeMethod }}】</span>
              <el-icon style="margin-left: 5px; cursor: pointer;" @click="handleChangeConsumeMethod(row)">
                <ArrowDown />
              </el-icon>
            </template>
          </el-table-column>
          <el-table-column label="剩余数量" width="150" align="center">
            <template #default="{ row }">
              <span v-if="row.remainingType === 'hours'">{{ row.remainingHours }}课时</span>
              <span v-else-if="row.remainingType === 'times'">
                {{ row.remainingTimes }}次
                <span v-if="row.remainingDays">(还剩{{ row.remainingDays }}天到期)</span>
              </span>
              <span v-else>{{ row.remainingAmount }}元</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <el-link type="danger" :underline="false" style="margin-right: 10px;" @click="handleRemoveStudent(row)">
                移除
              </el-link>
              <el-link type="primary" :underline="false" style="margin-right: 10px;" @click="handleTransferClass(row)">
                调班
              </el-link>
              <el-link type="warning" :underline="false" @click="handleLeaveRequest(row)">
                请假
              </el-link>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 点名情况 -->
      <el-tab-pane label="点名情况" name="attendance">
        <!-- 日期导航 -->
        <div class="attendance-header">
          <div class="date-range">
            一周点名情况：{{ attendanceDateRange }}
          </div>
          <div class="date-navigation">
            <el-button size="small" icon="ArrowLeft" @click="handlePreviousWeek">上周</el-button>
            <el-button size="small" @click="handleNextWeek">下周<el-icon style="margin-left: 5px;"><ArrowRight /></el-icon></el-button>
            <el-button type="warning" size="small" style="margin-left: 10px;" @click="handleBatchAttendance">
              一键点名/签到
            </el-button>
          </div>
        </div>

        <!-- 点名列表 -->
        <el-table
          :data="attendanceList"
          border
          class="attendance-table"
        >
          <el-table-column type="index" label="No" width="60" align="center" />
          <el-table-column label="上课时间" prop="classTime" width="200" align="center">
            <template #default="{ row }">
              {{ row.classTime }}
              <el-icon v-if="row.hasVideo" color="#67C23A" style="margin-left: 5px;">
                <VideoCamera />
              </el-icon>
            </template>
          </el-table-column>
          <el-table-column label="授课课程" prop="courseName" width="120" align="center" />
          <el-table-column label="上课教室" prop="classroom" width="120" align="center" />
          <el-table-column label="上课老师" prop="teacherName" width="100" align="center" />
          <el-table-column label="上课内容" prop="content" width="150" align="center" />
          <el-table-column label="点名时间" prop="attendanceTime" width="150" align="center" />
          <el-table-column label="操作" min-width="200" align="center">
            <template #default="{ row }">
              <el-link
                type="warning"
                :underline="false"
                style="margin-right: 10px;"
                @click="handleAttendanceAction(row, 'present')"
              >
                点名
              </el-link>
              <el-link
                type="warning"
                :underline="false"
                style="margin-right: 10px;"
                @click="handleAttendanceAction(row, 'view')"
              >
                调课记录
              </el-link>
              <el-link
                type="warning"
                :underline="false"
                style="margin-right: 10px;"
                @click="handleAttendanceAction(row, 'reschedule')"
              >
                查看详情
              </el-link>
              <el-link
                type="danger"
                :underline="false"
                @click="handleAttendanceAction(row, 'delete')"
              >
                删除
              </el-link>
            </template>
          </el-table-column>
        </el-table>

        <!-- 历史点名情况 -->
        <div class="history-attendance-section">
          <div class="section-title">历史点名情况</div>
          <el-table
            :data="historyAttendanceList"
            border
            class="history-attendance-table"
          >
            <el-table-column type="index" label="No" width="60" align="center" />
            <el-table-column label="上课时间" prop="classTime" width="200" align="center" />
            <el-table-column label="授课课程" prop="courseName" width="120" align="center" />
            <el-table-column label="上课教室" prop="classroom" width="120" align="center" />
            <el-table-column label="上课老师" prop="teacherName" width="100" align="center" />
            <el-table-column label="上课内容" prop="content" width="150" align="center" />
            <el-table-column label="点名状态" prop="status" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.status === 'present'" type="success" size="small">已点名</el-tag>
                <el-tag v-else-if="row.status === 'absent'" type="danger" size="small">缺席</el-tag>
                <el-tag v-else-if="row.status === 'leave'" type="warning" size="small">请假</el-tag>
                <el-tag v-else type="info" size="small">未点名</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="签到审核" prop="checkInStatus" width="100" align="center" />
            <el-table-column label="实到人数" prop="actualCount" width="100" align="center" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 底部提示 -->
    <div class="bottom-tip">
      <p>我们可以进入班级去添加学员</p>
    </div>

    <!-- 调班对话框 -->
    <el-dialog
      title="调至其他班"
      v-model="transferClassDialogVisible"
      width="500px"
      append-to-body
      @close="handleTransferClassDialogClose"
    >
      <el-form :model="transferClassForm" label-width="100px">
        <el-form-item label="目标班级：">
          <el-select
            v-model="transferClassForm.targetClassId"
            placeholder="请选择目标班级"
            filterable
            style="width: 100%;"
          >
            <el-option
              v-for="classItem in availableClassList"
              :key="classItem.id"
              :label="classItem.className"
              :value="classItem.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="transferClassDialogVisible = false">取 消</el-button>
          <el-button type="warning" @click="handleConfirmTransferClass">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加学员对话框 -->
    <el-dialog
      title="添加学员"
      v-model="addStudentDialogVisible"
      width="900px"
      append-to-body
      @close="handleAddStudentDialogClose"
    >
      <!-- Tab切换 -->
      <el-tabs v-model="addStudentActiveTab">
        <!-- 关联在读学员 -->
        <el-tab-pane label="关联在读学员" name="related">
          <div class="student-search-bar">
            <el-input
              v-model="relatedStudentSearch"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 300px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div class="search-filters">
              <span>课程卡类型</span>
              <span style="margin-left: 20px;">所在班级</span>
              <el-icon style="margin-left: 5px;"><Search /></el-icon>
            </div>
          </div>

          <!-- 学员列表 -->
          <el-table
            ref="relatedStudentTableRef"
            :data="filteredRelatedStudents"
            border
            max-height="400"
            @selection-change="handleRelatedStudentSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="学员名称" prop="studentName" width="120" />
            <el-table-column label="性别" prop="gender" width="80" align="center">
              <template #default="{ row }">
                {{ row.gender === 'male' ? '男' : '女' }}
              </template>
            </el-table-column>
            <el-table-column label="手机号" prop="phone" width="130" />
            <el-table-column label="消耗状态" prop="consumeStatus" width="120" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.consumeStatus === 'normal'" type="success" size="small">正常</el-tag>
                <el-tag v-else-if="row.consumeStatus === 'warning'" type="warning" size="small">预警</el-tag>
                <el-tag v-else type="danger" size="small">欠费</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="消耗方式" prop="consumeMethod" min-width="150">
              <template #default="{ row }">
                <el-select
                  v-model="row.selectedConsumeMethod"
                  placeholder="请选择"
                  size="small"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="method in row.consumeMethods"
                    :key="method.value"
                    :label="method.label"
                    :value="method.value"
                  />
                </el-select>
              </template>
            </el-table-column>
          </el-table>

          <div class="selected-count">
            已选择数量：{{ selectedRelatedStudents.length }}人
          </div>
        </el-tab-pane>

        <!-- 充值账户中学员 -->
        <el-tab-pane label="充值账户中学员" name="recharge">
          <div class="student-search-bar">
            <el-input
              v-model="rechargeStudentSearch"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 300px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div class="search-filters">
              <span>所在班级</span>
              <el-icon style="margin-left: 5px;"><Search /></el-icon>
            </div>
          </div>

          <el-table
            ref="rechargeStudentTableRef"
            :data="filteredRechargeStudents"
            border
            max-height="400"
            @selection-change="handleRechargeStudentSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="学员名称" prop="studentName" width="120" />
            <el-table-column label="性别" prop="gender" width="80" align="center">
              <template #default="{ row }">
                {{ row.gender === 'male' ? '男' : '女' }}
              </template>
            </el-table-column>
            <el-table-column label="手机号" prop="phone" width="130" />
            <el-table-column label="剩余课时" prop="remainingHours" width="100" align="center" />
            <el-table-column label="消耗方式" prop="consumeMethod" min-width="150">
              <template #default="{ row }">
                <el-select
                  v-model="row.selectedConsumeMethod"
                  placeholder="请选择"
                  size="small"
                  style="width: 100%;"
                >
                  <el-option label="按课时" value="hours" />
                  <el-option label="按金额" value="amount" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>

          <div class="selected-count">
            已选择数量：{{ selectedRechargeStudents.length }}人
          </div>
        </el-tab-pane>

        <!-- 全员卡学员 -->
        <el-tab-pane label="全员卡学员" name="all">
          <div class="student-search-bar">
            <el-input
              v-model="allStudentSearch"
              placeholder="请输入学员姓名/手机号"
              clearable
              style="width: 300px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <el-table
            ref="allStudentTableRef"
            :data="filteredAllStudents"
            border
            max-height="400"
            @selection-change="handleAllStudentSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="学员名称" prop="studentName" width="120" />
            <el-table-column label="性别" prop="gender" width="80" align="center">
              <template #default="{ row }">
                {{ row.gender === 'male' ? '男' : '女' }}
              </template>
            </el-table-column>
            <el-table-column label="手机号" prop="phone" width="130" />
            <el-table-column label="家长姓名" prop="parentName" min-width="120" />
          </el-table>

          <div class="selected-count">
            已选择数量：{{ selectedAllStudents.length }}人
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addStudentDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleConfirmAddStudents">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑排课对话框 -->
    <el-dialog
      v-model="editScheduleDialogVisible"
      title="编辑排课"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="editScheduleForm" label-width="120px" class="edit-schedule-form">
        <!-- 开始日期 -->
        <el-form-item label="开始日期：" required>
          <el-date-picker
            v-model="editScheduleForm.startDate"
            type="date"
            placeholder="2020-10-26"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>

        <!-- 结束方式 -->
        <el-form-item label="结束方式：" required>
          <el-select v-model="editScheduleForm.endMode" placeholder="不结束" style="width: 100%;">
            <el-option label="不结束" value="never" />
            <el-option label="按日期结束" value="byDate" />
            <el-option label="按次数结束" value="byCount" />
          </el-select>
        </el-form-item>

        <!-- 属性 -->
        <el-form-item label="属性：" required>
          <el-select v-model="editScheduleForm.attribute" placeholder="每周" style="width: 100%;">
            <el-option label="每周" value="weekly" />
            <el-option label="每天" value="daily" />
            <el-option label="隔天" value="everyOtherDay" />
            <el-option label="隔周" value="biweekly" />
          </el-select>
        </el-form-item>

        <!-- 周几上课 -->
        <el-form-item label="周几上课：" required>
          <el-select v-model="editScheduleForm.weekday" placeholder="周一" style="width: 100%;">
            <el-option label="周一" value="1" />
            <el-option label="周二" value="2" />
            <el-option label="周三" value="3" />
            <el-option label="周四" value="4" />
            <el-option label="周五" value="5" />
            <el-option label="周六" value="6" />
            <el-option label="周日" value="7" />
          </el-select>
        </el-form-item>

        <!-- 上课时间 -->
        <el-form-item label="上课时间：" required>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-time-picker
              v-model="editScheduleForm.startTime"
              placeholder="09:00"
              format="HH:mm"
              value-format="HH:mm"
              style="flex: 1;"
            />
            <span>-</span>
            <el-time-picker
              v-model="editScheduleForm.endTime"
              placeholder="10:00"
              format="HH:mm"
              value-format="HH:mm"
              style="flex: 1;"
            />
            <el-link type="warning" :underline="false">设置</el-link>
          </div>
        </el-form-item>

        <!-- 授课课程 -->
        <el-form-item label="授课课程：">
          <el-tooltip content="授课课程信息" placement="top">
            <el-icon style="margin-right: 5px; cursor: help;"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-select v-model="editScheduleForm.courseId" placeholder="暂无课" style="width: calc(100% - 30px);">
            <el-option label="暂无课" :value="null" />
            <el-option
              v-for="course in courseList"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>

        <!-- 上课老师 -->
        <el-form-item label="上课老师：" required>
          <el-select
            v-model="editScheduleForm.teacherId"
            placeholder="请选择老师"
            style="width: 100%;"
            popper-class="teacher-select-dropdown"
          >
            <!-- 自定义下拉头部 -->
            <template #header>
              <div class="teacher-select-header">
                <span class="header-col">姓名</span>
                <span class="header-col">手机号</span>
                <span class="header-col">冲突状态</span>
                <span class="header-col">时段</span>
              </div>
            </template>

            <!-- 自定义选项 -->
            <el-option
              v-for="teacher in teacherList"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            >
              <div class="teacher-option-content">
                <span class="teacher-name">{{ teacher.name }}</span>
                <span class="teacher-phone">{{ teacher.phone || '-' }}</span>
                <span class="teacher-status">
                  <span v-if="teacher.status === 'active'" class="status-dot active"></span>
                  <span class="status-text">空闲</span>
                </span>
                <span class="teacher-action">
                  <el-link type="warning" :underline="false">查看</el-link>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 上课教室 -->
        <el-form-item label="上课教室：" required>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-select
              v-model="editScheduleForm.classroomId"
              placeholder="不指定"
              style="flex: 1;"
              popper-class="classroom-select-dropdown"
            >
              <!-- 自定义下拉头部 -->
              <template #header>
                <div class="classroom-select-header">
                  <span class="header-col">上课教室</span>
                  <span class="header-col">冲突状态</span>
                  <span class="header-col">时段</span>
                </div>
              </template>

              <!-- 自定义选项 -->
              <el-option
                v-for="room in classroomList"
                :key="room.id"
                :label="room.name"
                :value="room.id"
              >
                <div class="classroom-option-content">
                  <span class="classroom-name">{{ room.name }}</span>
                  <span class="classroom-status">
                    <span v-if="room.status === 'available'" class="status-dot available"></span>
                    <span class="status-text">空闲</span>
                  </span>
                  <span class="classroom-action">
                    <el-link type="warning" :underline="false">查看</el-link>
                  </span>
                </div>
              </el-option>
            </el-select>
            <el-link type="warning" :underline="false">设置</el-link>
          </div>
        </el-form-item>

        <!-- 上课内容 -->
        <el-form-item label="上课内容：">
          <el-input
            v-model="editScheduleForm.content"
            type="textarea"
            :rows="3"
            placeholder="最多20字"
            maxlength="20"
            show-word-limit
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editScheduleDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="handleSaveScheduleEdit">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 一键排课对话框 -->
    <el-dialog
      v-model="scheduleDialogVisible"
      title="生成排课"
      width="700px"
      :close-on-click-modal="false"
      @close="handleScheduleDialogClose"
    >
      <el-form :model="scheduleForm" label-width="100px" class="schedule-form">
        <!-- 课程 -->
        <el-form-item label="课程" required>
          <el-select v-model="scheduleForm.courseId" placeholder="美语" style="width: 100%;">
            <el-option
              v-for="course in courseList"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>

        <!-- 班级 -->
        <el-form-item label="班级" required>
          <el-select v-model="scheduleForm.classId" placeholder="书画3班" style="width: 100%;">
            <el-option
              v-for="cls in classList"
              :key="cls.id"
              :label="cls.name"
              :value="cls.id"
            />
          </el-select>
        </el-form-item>

        <!-- 排课方式 -->
        <el-form-item label="排课方式">
          <el-radio-group v-model="scheduleForm.scheduleType">
            <el-radio label="rule">规则排课</el-radio>
            <el-radio label="calendar">日历排课</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 规则排课模式 -->
        <template v-if="scheduleForm.scheduleType === 'rule'">
          <!-- 开始日期 -->
          <el-form-item label="开始日期" required>
            <el-date-picker
              v-model="scheduleForm.startDate"
              type="date"
              placeholder="2024-03-12"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>

          <!-- 重复方式 -->
          <el-form-item label="重复方式">
            <el-radio-group v-model="scheduleForm.repeatMode">
              <el-radio label="daily">每天重复</el-radio>
              <el-radio label="everyOtherDay">隔天重复</el-radio>
              <el-radio label="weekly">每周重复</el-radio>
              <el-radio label="biweekly">隔周重复</el-radio>
            </el-radio-group>
          </el-form-item>
        </template>

        <!-- 日历排课模式 -->
        <template v-if="scheduleForm.scheduleType === 'calendar'">
          <!-- 上课日期 -->
          <el-form-item label="上课日期" required>
            <div style="color: #999; font-size: 12px; margin-bottom: 8px;">
              已选 {{ scheduleForm.selectedDates?.length || 0 }} 天
            </div>
            <div class="calendar-picker-container">
              <div class="calendar-header">
                <el-button
                  text
                  icon="ArrowLeft"
                  @click="changeCalendarMonth(-1)"
                />
                <span class="calendar-month-title">{{ calendarMonthTitle }}</span>
                <el-button
                  text
                  icon="ArrowRight"
                  @click="changeCalendarMonth(1)"
                />
              </div>
              <div class="calendar-body">
                <div class="calendar-weekdays">
                  <div class="weekday">一</div>
                  <div class="weekday">二</div>
                  <div class="weekday">三</div>
                  <div class="weekday">四</div>
                  <div class="weekday">五</div>
                  <div class="weekday">六</div>
                  <div class="weekday">日</div>
                </div>
                <div class="calendar-days">
                  <div
                    v-for="day in calendarDays"
                    :key="day.date"
                    :class="[
                      'calendar-day',
                      {
                        'is-other-month': day.isOtherMonth,
                        'is-selected': isDateSelected(day.date),
                        'is-today': isToday(day.date)
                      }
                    ]"
                    @click="toggleDateSelection(day.date, day.isOtherMonth)"
                  >
                    {{ day.day }}
                  </div>
                </div>
              </div>
            </div>
          </el-form-item>
        </template>

        <!-- 规则排课：每天重复/隔天重复：只显示上课时间 -->
        <template v-if="scheduleForm.scheduleType === 'rule' && (scheduleForm.repeatMode === 'daily' || scheduleForm.repeatMode === 'everyOtherDay')">
          <el-form-item label="上课时间">
            <div class="time-range">
              <el-time-picker
                v-model="scheduleForm.startTime"
                placeholder="开始时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 140px;"
              />
              <span style="margin: 0 10px;">~</span>
              <el-time-picker
                v-model="scheduleForm.endTime"
                placeholder="结束时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 140px;"
              />
              <el-link type="warning" :underline="false" style="margin-left: 15px;">
                选择常用时间段
              </el-link>
            </div>
          </el-form-item>
        </template>

        <!-- 规则排课：每周重复/隔周重复：显示星期和上课时间，支持动态添加 -->
        <template v-if="scheduleForm.scheduleType === 'rule' && (scheduleForm.repeatMode === 'weekly' || scheduleForm.repeatMode === 'biweekly')">
          <el-form-item label="">
            <div class="weekly-schedule-container">
              <div class="weekly-schedule-header">
                <span class="header-label">星期</span>
                <span class="header-label">上课时间</span>
              </div>

              <div
                v-for="(slot, index) in scheduleForm.weeklyTimeSlots"
                :key="index"
                class="weekly-time-slot"
              >
                <el-select
                  v-model="slot.weekday"
                  placeholder="周一"
                  style="width: 120px;"
                >
                  <el-option label="周一" value="1" />
                  <el-option label="周二" value="2" />
                  <el-option label="周三" value="3" />
                  <el-option label="周四" value="4" />
                  <el-option label="周五" value="5" />
                  <el-option label="周六" value="6" />
                  <el-option label="周日" value="7" />
                </el-select>

                <div class="time-range-inline">
                  <el-time-picker
                    v-model="slot.startTime"
                    placeholder="08:00"
                    format="HH:mm"
                    value-format="HH:mm"
                    style="width: 110px;"
                  />
                  <span style="margin: 0 8px;">~</span>
                  <el-time-picker
                    v-model="slot.endTime"
                    placeholder="09:00"
                    format="HH:mm"
                    value-format="HH:mm"
                    style="width: 110px;"
                  />
                </div>

                <el-link
                  type="warning"
                  :underline="false"
                  style="margin-left: 10px;"
                >
                  选择常用时间段
                </el-link>

                <el-button
                  v-if="scheduleForm.weeklyTimeSlots.length > 1"
                  type="danger"
                  text
                  icon="Delete"
                  @click="removeWeeklyTimeSlot(index)"
                  style="margin-left: 10px;"
                />
              </div>

              <el-button
                type="warning"
                text
                @click="addWeeklyTimeSlot"
                style="margin-top: 10px;"
              >
                + 添加
              </el-button>
            </div>
          </el-form-item>
        </template>

        <!-- 日历排课：上课时间 -->
        <template v-if="scheduleForm.scheduleType === 'calendar'">
          <el-form-item label="上课时间">
            <div class="time-range">
              <el-time-picker
                v-model="scheduleForm.startTime"
                placeholder="开始时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 140px;"
              />
              <span style="margin: 0 10px;">~</span>
              <el-time-picker
                v-model="scheduleForm.endTime"
                placeholder="结束时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 140px;"
              />
              <el-link type="warning" :underline="false" style="margin-left: 15px;">
                选择常用时间段
              </el-link>
            </div>
          </el-form-item>
        </template>

        <!-- 规则排课：结束方式 -->
        <template v-if="scheduleForm.scheduleType === 'rule'">
          <!-- 结束方式 -->
          <el-form-item label="结束方式">
            <el-radio-group v-model="scheduleForm.endMode">
              <el-radio label="byDate">按日期结束</el-radio>
              <el-radio label="byCount">按次数结束</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 排课次数 -->
          <el-form-item label="排课次数" required v-if="scheduleForm.endMode === 'byCount'">
            <el-input-number
              v-model="scheduleForm.scheduleCount"
              :min="1"
              :max="100"
              controls-position="right"
              style="width: 150px;"
            />
            <div style="margin-top: 5px; color: #999; font-size: 12px;">
              预计最后一次排课日期为{{ predictedEndDate }}
            </div>
          </el-form-item>

          <!-- 结束日期 -->
          <el-form-item label="结束日期" required v-if="scheduleForm.endMode === 'byDate'">
            <el-date-picker
              v-model="scheduleForm.endDate"
              type="date"
              placeholder="请选择结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>
        </template>

        <!-- 上课老师 -->
        <el-form-item label="上课老师">
          <el-select
            v-model="scheduleForm.teacherId"
            placeholder="请选择老师"
            style="width: 200px;"
            popper-class="teacher-select-dropdown"
          >
            <!-- 自定义下拉头部 -->
            <template #header>
              <div class="teacher-select-header">
                <span class="header-col">姓名</span>
                <span class="header-col">手机号</span>
                <span class="header-col">冲突状态</span>
                <span class="header-col">时段</span>
              </div>
            </template>

            <!-- 自定义选项 -->
            <el-option
              v-for="teacher in teacherList"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            >
              <div class="teacher-option-content">
                <span class="teacher-name">{{ teacher.name }}</span>
                <span class="teacher-phone">{{ teacher.phone || '-' }}</span>
                <span class="teacher-status">
                  <span v-if="teacher.status === 'active'" class="status-dot active"></span>
                  <span class="status-text">空闲</span>
                </span>
                <span class="teacher-action">
                  <el-link type="warning" :underline="false">查看</el-link>
                </span>
              </div>
            </el-option>
          </el-select>
          <el-button type="warning" text style="margin-left: 10px;">新增</el-button>
        </el-form-item>

        <!-- 上课教室 -->
        <el-form-item label="上课教室">
          <el-select
            v-model="scheduleForm.classroomId"
            placeholder="不指定"
            style="width: 200px;"
            popper-class="classroom-select-dropdown"
          >
            <!-- 自定义下拉头部 -->
            <template #header>
              <div class="classroom-select-header">
                <span class="header-col">上课教室</span>
                <span class="header-col">冲突状态</span>
                <span class="header-col">时段</span>
              </div>
            </template>

            <!-- 自定义选项 -->
            <el-option
              v-for="room in classroomList"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            >
              <div class="classroom-option-content">
                <span class="classroom-name">{{ room.name }}</span>
                <span class="classroom-status">
                  <span v-if="room.status === 'available'" class="status-dot available"></span>
                  <span class="status-text">空闲</span>
                </span>
                <span class="classroom-action">
                  <el-link type="warning" :underline="false">查看</el-link>
                </span>
              </div>
            </el-option>
          </el-select>
          <el-button type="warning" text style="margin-left: 10px;">新增</el-button>
        </el-form-item>

        <!-- 上课内容 -->
        <el-form-item label="上课内容">
          <el-input
            v-model="scheduleForm.content"
            type="textarea"
            :rows="3"
            placeholder="最多20字"
            maxlength="20"
            show-word-limit
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="scheduleDialogVisible = false">取 消</el-button>
          <el-button type="warning" @click="handleConfirmSchedule">生成排课</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 未排课直接点名对话框 -->
    <el-dialog
      v-model="directAttendanceDialogVisible"
      title="爵士舞1班"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form :model="directAttendanceForm" label-width="100px" class="direct-attendance-form">
        <!-- 上课日期 -->
        <el-form-item label="上课日期" required>
          <el-date-picker
            v-model="directAttendanceForm.classDate"
            type="date"
            placeholder="2020-11-17"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 200px;"
          />
        </el-form-item>

        <!-- 二课时间 -->
        <el-form-item label="二课时间" required>
          <div class="time-range-group">
            <el-time-picker
              v-model="directAttendanceForm.startTime"
              placeholder="05:00"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 120px;"
            />
            <span style="margin: 0 10px;">~</span>
            <el-time-picker
              v-model="directAttendanceForm.endTime"
              placeholder="05:01"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 120px;"
            />
          </div>
        </el-form-item>

        <!-- 授课课程 -->
        <el-form-item label="授课课程" required>
          <el-select v-model="directAttendanceForm.courseId" placeholder="爵士舞" style="width: 200px;">
            <el-option
              v-for="course in courseList"
              :key="course.id"
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>

        <!-- 上课老师 -->
        <el-form-item label="上课老师">
          <el-select
            v-model="directAttendanceForm.teacherId"
            placeholder="选择"
            style="width: 200px;"
            popper-class="teacher-select-dropdown"
          >
            <!-- 自定义下拉头部 -->
            <template #header>
              <div class="teacher-select-header">
                <span class="header-col">姓名</span>
                <span class="header-col">手机号</span>
                <span class="header-col">冲突状态</span>
                <span class="header-col">时段</span>
              </div>
            </template>

            <!-- 自定义选项 -->
            <el-option
              v-for="teacher in teacherList"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            >
              <div class="teacher-option-content">
                <span class="teacher-name">{{ teacher.name }}</span>
                <span class="teacher-phone">{{ teacher.phone || '-' }}</span>
                <span class="teacher-status">
                  <span v-if="teacher.status === 'active'" class="status-dot active"></span>
                  <span class="status-text">空闲</span>
                </span>
                <span class="teacher-action">
                  <el-link type="warning" :underline="false">查看</el-link>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 授课课时 -->
        <el-form-item label="授课课时">
          <el-input-number
            v-model="directAttendanceForm.lessonHours"
            :min="1"
            :max="10"
            controls-position="right"
            style="width: 150px;"
          />
        </el-form-item>

        <!-- 上课教室 -->
        <el-form-item label="上课教室">
          <el-select
            v-model="directAttendanceForm.classroomId"
            placeholder="不指定"
            style="width: 200px;"
            popper-class="classroom-select-dropdown"
          >
            <!-- 自定义下拉头部 -->
            <template #header>
              <div class="classroom-select-header">
                <span class="header-col">上课教室</span>
                <span class="header-col">冲突状态</span>
                <span class="header-col">时段</span>
              </div>
            </template>

            <!-- 自定义选项 -->
            <el-option
              v-for="room in classroomList"
              :key="room.id"
              :label="room.name"
              :value="room.id"
            >
              <div class="classroom-option-content">
                <span class="classroom-name">{{ room.name }}</span>
                <span class="classroom-status">
                  <span v-if="room.status === 'available'" class="status-dot available"></span>
                  <span class="status-text">空闲</span>
                </span>
                <span class="classroom-action">
                  <el-link type="warning" :underline="false">查看</el-link>
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 上课内容 -->
        <el-form-item label="上课内容">
          <el-input
            v-model="directAttendanceForm.content"
            type="textarea"
            :rows="3"
            placeholder="最多20字"
            maxlength="20"
            show-word-limit
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="directAttendanceDialogVisible = false">取 消</el-button>
          <el-button type="warning" @click="handleConfirmDirectAttendance">完成点名</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="ClassDetail">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowLeft, ArrowRight, Search, ArrowDown, Warning, Delete, QuestionFilled, VideoCamera } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();

// 班级ID
const classId = ref(route.params.id || route.query.id);

// 当前Tab
const activeTab = ref('schedule');

// 班级信息
const classInfo = ref({
  id: 1,
  className: '书画3班',
  classType: 'system',
  courseName: '书画课程-1',
  actualStudents: 0,
  currentStudents: 0,
  capacity: 0,
  lessonDuration: '0分钟',
  teacherName: '待分配',
  remark: '',
  classCategory: '不指定',
  defaultConsumption: 50.00,
  autoAssignName: 0,
  allowRecharge: 1
});

// 排课筛选
const scheduleFilter = ref({
  teachingMethod: '',
  status: ''
});

// 排课列表
const scheduleList = ref([]);
const selectedSchedules = ref([]);

// 班级成员列表
const memberList = ref([]);
const memberSearchKeyword = ref('');
const selectedMembers = ref([]);

// 点名情况相关数据
const attendanceDateRange = ref('2020/11/16 - 2020/11/22');
const currentWeekStart = ref(new Date('2020-11-16'));
const attendanceList = ref([]);
const historyAttendanceList = ref([]);

// 未排课直接点名对话框
const directAttendanceDialogVisible = ref(false);
const directAttendanceForm = ref({
  classDate: '',           // 上课日期
  startTime: '05:00',      // 开始时间
  endTime: '05:01',        // 结束时间
  courseId: null,          // 授课课程ID
  teacherId: null,         // 上课老师ID
  lessonHours: 1,          // 授课课时
  classroomId: null,       // 上课教室ID
  content: ''              // 上课内容
});

// 过滤后的成员列表
const filteredMemberList = computed(() => {
  if (!memberSearchKeyword.value) {
    return memberList.value;
  }
  return memberList.value.filter(member =>
    member.studentName.includes(memberSearchKeyword.value) ||
    member.phone.includes(memberSearchKeyword.value)
  );
});

// 调班对话框
const transferClassDialogVisible = ref(false);
const transferClassForm = ref({
  studentId: null,
  studentName: '',
  targetClassId: null
});

// 可选择的班级列表
const availableClassList = ref([
  { id: 1, className: '书画大班' },
  { id: 2, className: '书画2班' },
  { id: 3, className: '爱笑美术班' }
]);

// 编辑排课对话框
const editScheduleDialogVisible = ref(false);
const editScheduleForm = ref({
  id: null,                 // 排课ID
  startDate: '',            // 开始日期
  endMode: 'never',         // 结束方式：never-不结束, byDate-按日期, byCount-按次数
  attribute: 'weekly',      // 属性：weekly-每周, daily-每天, everyOtherDay-隔天, biweekly-隔周
  weekday: '1',             // 周几上课
  startTime: '09:00',       // 开始时间
  endTime: '10:00',         // 结束时间
  courseId: null,           // 授课课程ID
  teacherId: null,          // 上课老师ID
  classroomId: null,        // 上课教室ID
  content: ''               // 上课内容
});

// 排课对话框
const scheduleDialogVisible = ref(false);
const scheduleForm = ref({
  courseId: null,           // 课程ID
  classId: null,            // 班级ID
  scheduleType: 'rule',     // 排课方式：rule-规则排课, calendar-日历排课
  startDate: '',            // 开始日期
  repeatMode: 'weekly',     // 重复方式：daily-每天, everyOtherDay-隔天, weekly-每周, biweekly-隔周
  startTime: '08:00',       // 开始时间（每天重复/隔天重复使用）
  endTime: '09:00',         // 结束时间（每天重复/隔天重复使用）
  weeklyTimeSlots: [        // 每周时间段列表（每周重复/隔周重复使用）
    { weekday: '1', startTime: '08:00', endTime: '09:00' }
  ],
  endMode: 'byCount',       // 结束方式：byDate-按日期, byCount-按次数
  scheduleCount: 1,         // 排课次数
  endDate: '',              // 结束日期
  teacherId: null,          // 上课老师ID
  classroomId: null,        // 上课教室ID
  content: '',              // 上课内容
  selectedDates: []         // 日历排课选中的日期列表
});

// 日历相关数据
const currentCalendarMonth = ref(new Date());
const calendarDays = ref([]);

// 日历月份标题
const calendarMonthTitle = computed(() => {
  const year = currentCalendarMonth.value.getFullYear();
  const month = currentCalendarMonth.value.getMonth() + 1;
  return `${year}年${String(month).padStart(2, '0')}月`;
});

// 课程列表
const courseList = ref([
  { id: 1, name: '美语' },
  { id: 2, name: '书画课程-1' },
  { id: 3, name: '数学课程' }
]);

// 班级列表
const classList = ref([
  { id: 1, name: '书画3班' },
  { id: 2, name: '书画大班' },
  { id: 3, name: '爱笑美术班' }
]);

// 老师列表
const teacherList = ref([
  { id: 1, name: '本班老师', phone: '', status: 'active', isDefault: true },
  { id: 2, name: '叶老师', phone: '185****3771', status: 'active', isDefault: false },
  { id: 3, name: '校区老师', phone: '', status: 'active', isDefault: false },
  { id: 4, name: '齐', phone: '176****9625', status: 'active', isDefault: false },
  { id: 5, name: '黄老师', phone: '173****9071', status: 'active', isDefault: false }
]);

// 教室列表
const classroomList = ref([
  { id: 0, name: '不指定', status: 'available', isDefault: true },
  { id: 1, name: '万达A馆', status: 'available', isDefault: false },
  { id: 2, name: '教室2', status: 'available', isDefault: false },
  { id: 3, name: '教室1', status: 'available', isDefault: false },
  { id: 4, name: '益普国际3号教室', status: 'available', isDefault: false }
]);

// 预计结束日期
const predictedEndDate = computed(() => {
  if (scheduleForm.value.endMode === 'byCount' && scheduleForm.value.scheduleCount > 0 && scheduleForm.value.startDate) {
    const startDate = new Date(scheduleForm.value.startDate);
    let daysToAdd = 0;

    // 根据重复方式计算天数
    switch (scheduleForm.value.repeatMode) {
      case 'daily':
        daysToAdd = scheduleForm.value.scheduleCount - 1;
        break;
      case 'everyOtherDay':
        daysToAdd = (scheduleForm.value.scheduleCount - 1) * 2;
        break;
      case 'weekly':
        daysToAdd = (scheduleForm.value.scheduleCount - 1) * 7;
        break;
      case 'biweekly':
        daysToAdd = (scheduleForm.value.scheduleCount - 1) * 14;
        break;
    }

    const endDate = new Date(startDate.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
    return endDate.toISOString().split('T')[0];
  }
  return '2024-03-18';
});

// 添加学员对话框
const addStudentDialogVisible = ref(false);
const addStudentActiveTab = ref('related');

// 关联在读学员
const relatedStudentSearch = ref('');
const relatedStudentList = ref([
  {
    id: 1,
    studentName: '佳劲',
    gender: 'male',
    phone: '13757110431',
    consumeStatus: 'normal',
    consumeMethods: [
      { label: '黄琦', value: 'huangqi' }
    ],
    selectedConsumeMethod: 'huangqi'
  },
  {
    id: 2,
    studentName: '李会',
    gender: 'female',
    phone: '13757110431',
    consumeStatus: 'normal',
    consumeMethods: [
      { label: '黄琦', value: 'huangqi' }
    ],
    selectedConsumeMethod: 'huangqi'
  },
  {
    id: 3,
    studentName: '天天',
    gender: 'male',
    phone: '18004662607',
    consumeStatus: 'warning',
    consumeMethods: [
      { label: '班费', value: 'class_fee' }
    ],
    selectedConsumeMethod: 'class_fee'
  },
  {
    id: 4,
    studentName: '小佳',
    gender: 'female',
    phone: '13311111112',
    consumeStatus: 'normal',
    consumeMethods: [
      { label: '黄琦', value: 'huangqi' }
    ],
    selectedConsumeMethod: 'huangqi'
  },
  {
    id: 5,
    studentName: '张小燕',
    gender: 'female',
    phone: '16111111111',
    consumeStatus: 'danger',
    consumeMethods: [
      { label: '班费', value: 'class_fee' }
    ],
    selectedConsumeMethod: 'class_fee'
  }
]);
const selectedRelatedStudents = ref([]);

// 充值账户中学员
const rechargeStudentSearch = ref('');
const rechargeStudentList = ref([
  {
    id: 6,
    studentName: '王小明',
    gender: 'male',
    phone: '13800138001',
    remainingHours: 20,
    selectedConsumeMethod: 'hours'
  },
  {
    id: 7,
    studentName: '李小红',
    gender: 'female',
    phone: '13800138002',
    remainingHours: 15,
    selectedConsumeMethod: 'hours'
  }
]);
const selectedRechargeStudents = ref([]);

// 全员卡学员
const allStudentSearch = ref('');
const allStudentList = ref([
  {
    id: 8,
    studentName: '赵小刚',
    gender: 'male',
    phone: '13800138003',
    parentName: '赵父'
  },
  {
    id: 9,
    studentName: '孙小丽',
    gender: 'female',
    phone: '13800138004',
    parentName: '孙父'
  }
]);
const selectedAllStudents = ref([]);

// 过滤后的学员列表
const filteredRelatedStudents = computed(() => {
  if (!relatedStudentSearch.value) {
    return relatedStudentList.value;
  }
  return relatedStudentList.value.filter(student =>
    student.studentName.includes(relatedStudentSearch.value) ||
    student.phone.includes(relatedStudentSearch.value)
  );
});

const filteredRechargeStudents = computed(() => {
  if (!rechargeStudentSearch.value) {
    return rechargeStudentList.value;
  }
  return rechargeStudentList.value.filter(student =>
    student.studentName.includes(rechargeStudentSearch.value) ||
    student.phone.includes(rechargeStudentSearch.value)
  );
});

const filteredAllStudents = computed(() => {
  if (!allStudentSearch.value) {
    return allStudentList.value;
  }
  return allStudentList.value.filter(student =>
    student.studentName.includes(allStudentSearch.value) ||
    student.phone.includes(allStudentSearch.value)
  );
});

/** 格式化日期显示星期 */
function formatDateWithWeekday(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const weekday = weekdays[date.getDay()];
  return `${dateStr} (${weekday})`;
}

/** 返回 */
function goBack() {
  router.back();
}

/** 编辑班级 */
function handleEdit() {
  router.push({
    path: '/assistant/class',
    query: { action: 'edit', id: classId.value }
  });
}

/** 排课选择变化 */
function handleScheduleSelectionChange(selection) {
  selectedSchedules.value = selection;
}

/** 查看排课详情/编辑 */
function handleScheduleDetail(row) {
  console.log('编辑排课', row);

  // 填充编辑表单数据
  editScheduleForm.value = {
    id: row.id || null,
    startDate: row.classDate || '',
    endMode: 'never',
    attribute: 'weekly',
    weekday: '1',
    startTime: row.classTime ? row.classTime.split('-')[0] : '09:00',
    endTime: row.classTime ? row.classTime.split('-')[1] : '10:00',
    courseId: row.courseId || null,
    teacherId: row.teacherId || null,
    classroomId: row.classroomId || null,
    content: row.content || ''
  };

  // 打开编辑弹窗
  editScheduleDialogVisible.value = true;
}

/** 保存排课编辑 */
function handleSaveScheduleEdit() {
  // 验证必填项
  if (!editScheduleForm.value.startDate) {
    ElMessage.warning('请选择开始日期');
    return;
  }

  if (!editScheduleForm.value.startTime || !editScheduleForm.value.endTime) {
    ElMessage.warning('请选择上课时间');
    return;
  }

  if (!editScheduleForm.value.teacherId) {
    ElMessage.warning('请选择上课老师');
    return;
  }

  // TODO: 调用API保存编辑
  console.log('保存排课编辑', editScheduleForm.value);
  ElMessage.success('保存成功');
  editScheduleDialogVisible.value = false;
  getScheduleList();
}

/** 删除排课 */
function handleDeleteSchedule(row) {
  ElMessageBox.confirm(
    `确认删除该排课吗？删除后将无法恢复。`,
    '删除排课',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // TODO: 调用API删除排课
    console.log('删除排课', row);
    ElMessage.success('删除成功');
    getScheduleList();
  }).catch(() => {
    ElMessage.info('已取消操作');
  });
}

/** 打开排课对话框 */
function handleScheduleClass() {
  scheduleDialogVisible.value = true;
  // 重置表单，设置默认值
  const today = new Date();
  scheduleForm.value = {
    courseId: courseList.value[0]?.id || null,
    classId: classId.value,
    scheduleType: 'rule',
    startDate: today.toISOString().split('T')[0],
    repeatMode: 'weekly',
    startTime: '08:00',
    endTime: '09:00',
    weeklyTimeSlots: [
      { weekday: '1', startTime: '08:00', endTime: '09:00' }
    ],
    endMode: 'byCount',
    scheduleCount: 1,
    endDate: '',
    teacherId: null,
    classroomId: null,
    content: '',
    selectedDates: []
  };
  // 初始化日历
  currentCalendarMonth.value = new Date();
  generateCalendarDays();
}

/** 添加每周时间段 */
function addWeeklyTimeSlot() {
  scheduleForm.value.weeklyTimeSlots.push({
    weekday: '1',
    startTime: '08:00',
    endTime: '09:00'
  });
}

/** 删除每周时间段 */
function removeWeeklyTimeSlot(index) {
  if (scheduleForm.value.weeklyTimeSlots.length > 1) {
    scheduleForm.value.weeklyTimeSlots.splice(index, 1);
  }
}

/** 生成日历天数 */
function generateCalendarDays() {
  const year = currentCalendarMonth.value.getFullYear();
  const month = currentCalendarMonth.value.getMonth();

  // 获取当月第一天
  const firstDay = new Date(year, month, 1);
  // 获取当月最后一天
  const lastDay = new Date(year, month + 1, 0);

  // 获取第一天是星期几 (0-6, 0是周日)
  let firstDayOfWeek = firstDay.getDay();
  // 转换为周一为第一天 (1-7, 1是周一)
  firstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek;

  const days = [];

  // 添加上个月的日期
  const prevMonthLastDay = new Date(year, month, 0).getDate();
  for (let i = firstDayOfWeek - 1; i > 0; i--) {
    const day = prevMonthLastDay - i + 1;
    const date = new Date(year, month - 1, day);
    days.push({
      day,
      date: formatDate(date),
      isOtherMonth: true
    });
  }

  // 添加当月的日期
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i);
    days.push({
      day: i,
      date: formatDate(date),
      isOtherMonth: false
    });
  }

  // 添加下个月的日期，补齐到42天(6周)
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i);
    days.push({
      day: i,
      date: formatDate(date),
      isOtherMonth: true
    });
  }

  calendarDays.value = days;
}

/** 格式化日期为 YYYY-MM-DD */
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/** 切换日历月份 */
function changeCalendarMonth(offset) {
  const newDate = new Date(currentCalendarMonth.value);
  newDate.setMonth(newDate.getMonth() + offset);
  currentCalendarMonth.value = newDate;
  generateCalendarDays();
}

/** 判断日期是否被选中 */
function isDateSelected(date) {
  return scheduleForm.value.selectedDates?.includes(date);
}

/** 判断是否是今天 */
function isToday(date) {
  const today = new Date();
  return date === formatDate(today);
}

/** 切换日期选择 */
function toggleDateSelection(date, isOtherMonth) {
  if (isOtherMonth) {
    return; // 不允许选择其他月份的日期
  }

  if (!scheduleForm.value.selectedDates) {
    scheduleForm.value.selectedDates = [];
  }

  const index = scheduleForm.value.selectedDates.indexOf(date);
  if (index > -1) {
    // 已选中，取消选择
    scheduleForm.value.selectedDates.splice(index, 1);
  } else {
    // 未选中，添加选择
    scheduleForm.value.selectedDates.push(date);
  }

  // 排序日期
  scheduleForm.value.selectedDates.sort();
}

/** 确认排课 */
function handleConfirmSchedule() {
  // 验证表单
  if (!scheduleForm.value.courseId) {
    ElMessage.warning('请选择课程');
    return;
  }

  if (!scheduleForm.value.classId) {
    ElMessage.warning('请选择班级');
    return;
  }

  // 规则排课验证
  if (scheduleForm.value.scheduleType === 'rule') {
    if (!scheduleForm.value.startDate) {
      ElMessage.warning('请选择开始日期');
      return;
    }

    // 验证上课时间
    if (scheduleForm.value.repeatMode === 'daily' || scheduleForm.value.repeatMode === 'everyOtherDay') {
      // 每天重复/隔天重复：验证单个时间段
      if (!scheduleForm.value.startTime || !scheduleForm.value.endTime) {
        ElMessage.warning('请选择上课时间');
        return;
      }
    } else if (scheduleForm.value.repeatMode === 'weekly' || scheduleForm.value.repeatMode === 'biweekly') {
      // 每周重复/隔周重复：验证每周时间段列表
      if (!scheduleForm.value.weeklyTimeSlots || scheduleForm.value.weeklyTimeSlots.length === 0) {
        ElMessage.warning('请添加至少一个上课时间段');
        return;
      }

      for (let i = 0; i < scheduleForm.value.weeklyTimeSlots.length; i++) {
        const slot = scheduleForm.value.weeklyTimeSlots[i];
        if (!slot.weekday || !slot.startTime || !slot.endTime) {
          ElMessage.warning(`请完善第${i + 1}个时间段信息`);
          return;
        }
      }
    }

    if (scheduleForm.value.endMode === 'byCount' && !scheduleForm.value.scheduleCount) {
      ElMessage.warning('请输入排课次数');
      return;
    }

    if (scheduleForm.value.endMode === 'byDate' && !scheduleForm.value.endDate) {
      ElMessage.warning('请选择结束日期');
      return;
    }
  }

  // 日历排课验证
  if (scheduleForm.value.scheduleType === 'calendar') {
    if (!scheduleForm.value.selectedDates || scheduleForm.value.selectedDates.length === 0) {
      ElMessage.warning('请在日历中选择上课日期');
      return;
    }

    if (!scheduleForm.value.startTime || !scheduleForm.value.endTime) {
      ElMessage.warning('请选择上课时间');
      return;
    }
  }

  // TODO: 调用API生成排课
  console.log('生成排课', scheduleForm.value);
  ElMessage.success('排课生成成功');
  scheduleDialogVisible.value = false;
  getScheduleList();
}

/** 关闭排课对话框 */
function handleScheduleDialogClose() {
  // 重置表单
  scheduleForm.value = {
    courseId: null,
    classId: null,
    scheduleType: 'rule',
    startDate: '',
    repeatMode: 'weekly',
    startTime: '08:00',
    endTime: '09:00',
    weeklyTimeSlots: [
      { weekday: '1', startTime: '08:00', endTime: '09:00' }
    ],
    endMode: 'byCount',
    scheduleCount: 1,
    endDate: '',
    teacherId: null,
    classroomId: null,
    content: '',
    selectedDates: []
  };
}

/** 添加学员 */
function handleAddStudent() {
  addStudentDialogVisible.value = true;
  addStudentActiveTab.value = 'related';
  // 清空之前的选择
  selectedRelatedStudents.value = [];
  selectedRechargeStudents.value = [];
  selectedAllStudents.value = [];
}

/** 关联在读学员选择变化 */
function handleRelatedStudentSelectionChange(selection) {
  selectedRelatedStudents.value = selection;
}

/** 充值账户学员选择变化 */
function handleRechargeStudentSelectionChange(selection) {
  selectedRechargeStudents.value = selection;
}

/** 全员卡学员选择变化 */
function handleAllStudentSelectionChange(selection) {
  selectedAllStudents.value = selection;
}

/** 确认添加学员 */
function handleConfirmAddStudents() {
  let totalSelected = 0;
  let studentsToAdd = [];

  // 收集所有选中的学员
  if (addStudentActiveTab.value === 'related') {
    totalSelected = selectedRelatedStudents.value.length;
    studentsToAdd = selectedRelatedStudents.value.map(s => ({
      ...s,
      source: 'related'
    }));
  } else if (addStudentActiveTab.value === 'recharge') {
    totalSelected = selectedRechargeStudents.value.length;
    studentsToAdd = selectedRechargeStudents.value.map(s => ({
      ...s,
      source: 'recharge'
    }));
  } else if (addStudentActiveTab.value === 'all') {
    totalSelected = selectedAllStudents.value.length;
    studentsToAdd = selectedAllStudents.value.map(s => ({
      ...s,
      source: 'all'
    }));
  }

  if (totalSelected === 0) {
    ElMessage.warning('请至少选择一个学员');
    return;
  }

  // TODO: 调用API添加学员到班级
  console.log('添加学员到班级', studentsToAdd);

  ElMessage.success(`成功添加 ${totalSelected} 名学员`);
  addStudentDialogVisible.value = false;

  // 刷新班级成员列表
  getMemberList();
}

/** 添加学员对话框关闭 */
function handleAddStudentDialogClose() {
  relatedStudentSearch.value = '';
  rechargeStudentSearch.value = '';
  allStudentSearch.value = '';
  selectedRelatedStudents.value = [];
  selectedRechargeStudents.value = [];
  selectedAllStudents.value = [];
}

/** 成员选择变化 */
function handleMemberSelectionChange(selection) {
  selectedMembers.value = selection;
}

/** 上一周 */
function handlePreviousWeek() {
  const newDate = new Date(currentWeekStart.value);
  newDate.setDate(newDate.getDate() - 7);
  currentWeekStart.value = newDate;
  updateAttendanceDateRange();
  getAttendanceList();
}

/** 下一周 */
function handleNextWeek() {
  const newDate = new Date(currentWeekStart.value);
  newDate.setDate(newDate.getDate() + 7);
  currentWeekStart.value = newDate;
  updateAttendanceDateRange();
  getAttendanceList();
}

/** 更新日期范围显示 */
function updateAttendanceDateRange() {
  const startDate = new Date(currentWeekStart.value);
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 6);

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
  };

  attendanceDateRange.value = `${formatDate(startDate)} - ${formatDate(endDate)}`;
}

/** 一键点名/签到 */
function handleBatchAttendance() {
  // 打开未排课直接点名对话框
  handleOpenDirectAttendance();
}

/** 点名操作 */
function handleAttendanceAction(row, action) {
  switch (action) {
    case 'present':
      ElMessage.success(`已为"${row.studentName}"点名`);
      // TODO: 调用API更新点名状态
      getAttendanceList();
      break;
    case 'view':
      ElMessage.info('调课记录功能开发中');
      break;
    case 'reschedule':
      ElMessage.info('查看详情功能开发中');
      break;
    case 'delete':
      ElMessageBox.confirm(
        '确认删除该点名记录吗？',
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        ElMessage.success('删除成功');
        getAttendanceList();
      }).catch(() => {
        ElMessage.info('已取消操作');
      });
      break;
  }
}

/** 获取点名列表 */
function getAttendanceList() {
  // TODO: 调用API获取点名列表
  setTimeout(() => {
    attendanceList.value = [
      {
        id: 1,
        classTime: '2020-11-16(周一) 08:00-09:00',
        hasVideo: true,
        courseName: '爵士课',
        classroom: '爵士舞练习班',
        teacherName: '孟吉',
        content: '基础训练',
        attendanceTime: '--'
      },
      {
        id: 2,
        classTime: '2020-11-16(周一) 13:00-14:00',
        hasVideo: true,
        courseName: '爵士课',
        classroom: '',
        teacherName: '孟吉',
        content: '',
        attendanceTime: '--'
      },
      {
        id: 3,
        classTime: '2020-11-17(周二) 17:20-19:20',
        hasVideo: false,
        courseName: '爵士课',
        classroom: '',
        teacherName: '忠贞',
        content: '舞蹈编排',
        attendanceTime: '2020-11-17 17:20'
      }
    ];

    historyAttendanceList.value = [
      {
        id: 1,
        classTime: '2020-11-10(周二) 08:00-09:00',
        courseName: '爵士课',
        classroom: '爵士舞练习班',
        teacherName: '孟吉',
        content: '基础训练',
        status: 'present',
        checkInStatus: '已审核',
        actualCount: '1/1'
      },
      {
        id: 2,
        classTime: '2020-11-09(周一) 13:00-14:00',
        courseName: '爵士课',
        classroom: '爵士舞练习班',
        teacherName: '孟吉',
        content: '舞蹈编排',
        status: 'present',
        checkInStatus: '已审核',
        actualCount: '1/1'
      },
      {
        id: 3,
        classTime: '2020-11-03(周二) 17:20-19:20',
        courseName: '爵士课',
        classroom: '爵士舞练习班',
        teacherName: '忠贞',
        content: '成品舞练习',
        status: 'present',
        checkInStatus: '已审核',
        actualCount: '1/1'
      }
    ];
  }, 300);
}

/** 打开未排课直接点名对话框 */
function handleOpenDirectAttendance() {
  const today = new Date();
  directAttendanceForm.value = {
    classDate: today.toISOString().split('T')[0],
    startTime: '05:00',
    endTime: '05:01',
    courseId: courseList.value[0]?.id || null,
    teacherId: null,
    lessonHours: 1,
    classroomId: null,
    content: ''
  };

  directAttendanceDialogVisible.value = true;
}

/** 确认直接点名 */
function handleConfirmDirectAttendance() {
  // 验证必填项
  if (!directAttendanceForm.value.classDate) {
    ElMessage.warning('请选择上课日期');
    return;
  }

  if (!directAttendanceForm.value.startTime || !directAttendanceForm.value.endTime) {
    ElMessage.warning('请选择上课时间');
    return;
  }

  if (!directAttendanceForm.value.courseId) {
    ElMessage.warning('请选择授课课程');
    return;
  }

  console.log('直接点名数据', {
    form: directAttendanceForm.value
  });

  // TODO: 调用API保存点名数据
  ElMessage.success('点名完成');
  directAttendanceDialogVisible.value = false;

  // 刷新点名列表
  getAttendanceList();
}

/** 查看学员 */
function handleViewStudent(row) {
  console.log('查看学员', row);
  // TODO: 跳转到学员详情页
  ElMessage.info('学员详情功能开发中');
}

/** 移除学员 */
function handleRemoveStudent(row) {
  ElMessageBox.confirm(
    `确认将学员"${row.studentName}"从该班级移除吗？移除后该学员将不再属于此班级。`,
    '移除学员',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // TODO: 调用API移除学员
    ElMessage.success('移除成功');
    getMemberList();
  }).catch(() => {
    ElMessage.info('已取消操作');
  });
}

/** 调班 */
function handleTransferClass(row) {
  // 打开调班对话框
  transferClassForm.value = {
    studentId: row.id,
    studentName: row.studentName,
    targetClassId: null
  };
  transferClassDialogVisible.value = true;
}

/** 确认调班 */
function handleConfirmTransferClass() {
  if (!transferClassForm.value.targetClassId) {
    ElMessage.warning('请选择目标班级');
    return;
  }

  const targetClass = availableClassList.value.find(
    c => c.id === transferClassForm.value.targetClassId
  );

  ElMessageBox.confirm(
    `确认将学员"${transferClassForm.value.studentName}"调到"${targetClass.className}"吗？`,
    '确认调班',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // TODO: 调用API执行调班
    console.log('调班', transferClassForm.value);
    ElMessage.success('调班成功');
    transferClassDialogVisible.value = false;
    getMemberList();
  }).catch(() => {
    ElMessage.info('已取消操作');
  });
}

/** 调班对话框关闭 */
function handleTransferClassDialogClose() {
  transferClassForm.value = {
    studentId: null,
    studentName: '',
    targetClassId: null
  };
}

/** 请假 */
function handleLeaveRequest(row) {
  ElMessageBox.prompt(
    `为学员"${row.studentName}"申请请假`,
    '请假',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入请假原因',
      inputType: 'textarea'
    }
  ).then(({ value }) => {
    if (!value) {
      ElMessage.warning('请输入请假原因');
      return;
    }
    // TODO: 调用API提交请假申请
    ElMessage.success('请假申请已提交');
  }).catch(() => {
    ElMessage.info('已取消操作');
  });
}

/** 修改消耗方式 */
function handleChangeConsumeMethod(row) {
  console.log('修改消耗方式', row);
  ElMessage.info('修改消耗方式功能开发中');
}

/** 获取班级详情 */
function getClassDetail() {
  // TODO: 调用API获取班级详情
  console.log('获取班级详情', classId.value);
}

/** 获取排课列表 */
function getScheduleList() {
  // TODO: 调用API获取排课列表
  setTimeout(() => {
    scheduleList.value = [
      {
        id: 1,
        teachingMethod: 'offline',
        classDate: '2024-03-18',
        courseName: '美语',
        courseId: 1,
        classTime: '08:00-09:00',
        classroom: '教室A',
        classroomId: 1,
        teacherName: '张老师',
        teacherId: 1,
        content: ''
      },
      {
        id: 2,
        teachingMethod: 'offline',
        classDate: '2024-03-25',
        courseName: '美语',
        courseId: 1,
        classTime: '08:00-09:00',
        classroom: '教室A',
        classroomId: 1,
        teacherName: '张老师',
        teacherId: 1,
        content: ''
      },
      {
        id: 3,
        teachingMethod: 'offline',
        classDate: '2024-04-01',
        courseName: '美语',
        courseId: 1,
        classTime: '08:00-09:00',
        classroom: '教室A',
        classroomId: 1,
        teacherName: '张老师',
        teacherId: 1,
        content: ''
      },
      {
        id: 4,
        teachingMethod: 'offline',
        classDate: '2024-04-08',
        courseName: '美语',
        courseId: 1,
        classTime: '08:00-09:00',
        classroom: '教室A',
        classroomId: 1,
        teacherName: '张老师',
        teacherId: 1,
        content: ''
      }
    ];
  }, 300);
}

/** 获取班级成员 */
function getMemberList() {
  // TODO: 调用API获取班级成员
  memberList.value = [
    {
      id: 1,
      studentName: '李会',
      gender: 'female',
      phone: '13757110431',
      consumeMethod: '黄琦',
      remainingType: 'hours',
      remainingHours: 9,
      status: 'active'
    },
    {
      id: 2,
      studentName: '天天',
      gender: 'male',
      phone: '18004662607',
      consumeMethod: '班费',
      remainingType: 'times',
      remainingTimes: 23,
      remainingDays: 93,
      expiryDate: '2024-03-03',
      status: 'active'
    },
    {
      id: 3,
      studentName: '小佳',
      gender: 'female',
      phone: '13311111112',
      consumeMethod: '黄琦',
      remainingType: 'hours',
      remainingHours: 0,
      status: 'active'
    },
    {
      id: 4,
      studentName: '张小燕',
      gender: 'female',
      phone: '16111111111',
      consumeMethod: '班费',
      remainingType: 'hours',
      remainingHours: 0,
      status: 'active'
    }
  ];
}

onMounted(() => {
  // 如果URL中有tab参数，则切换到对应的Tab
  if (route.query.tab) {
    activeTab.value = route.query.tab;
  }

  getClassDetail();
  getScheduleList();
  getMemberList();
  getAttendanceList();
  updateAttendanceDateRange();
});
</script>

<style scoped lang="scss">
.class-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;

    .edit-btn {
      margin-left: auto;
    }
  }

  .class-info-card {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;

    .class-title {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;

      .class-name {
        color: #303133;
      }
    }

    .info-row {
      margin-bottom: 15px;

      .info-item {
        .label {
          color: #909399;
          font-size: 14px;
        }

        .value {
          color: #303133;
          font-size: 14px;
          margin-left: 5px;
        }
      }
    }
  }

  .detail-tabs {
    background: #fff;
    padding: 20px;
    border-radius: 4px;

    .schedule-toolbar,
    .members-toolbar {
      margin-bottom: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .schedule-filters,
      .member-filters {
        display: flex;
        align-items: center;
        gap: 10px;

        .period-label {
          color: #606266;
          font-size: 14px;
        }
      }
    }

    .member-search-bar {
      margin-bottom: 15px;
    }

    .empty-data {
      padding: 40px 0;
      text-align: center;
    }
  }

  .bottom-tip {
    margin-top: 30px;
    padding: 20px;
    background: #fff7e6;
    border-radius: 4px;
    text-align: center;

    p {
      margin: 0;
      color: #ff6600;
      font-size: 16px;
      font-weight: bold;
    }
  }

  // 添加学员对话框样式
  .student-search-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    .search-filters {
      display: flex;
      align-items: center;
      color: #606266;
      font-size: 14px;
    }
  }

  .selected-count {
    margin-top: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
    color: #606266;
    font-size: 14px;
  }

  // 编辑排课对话框样式
  .edit-schedule-form {
    :deep(.el-form-item__label) {
      font-weight: normal;
      color: #606266;
    }
  }

  // 排课对话框样式
  .schedule-form {
    .time-range {
      display: flex;
      align-items: center;
    }

    .time-range-inline {
      display: flex;
      align-items: center;
    }

    .weekly-schedule-container {
      width: 100%;
      border: 1px solid #DCDFE6;
      border-radius: 4px;
      padding: 16px;
      background: #FAFAFA;

      .weekly-schedule-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #EBEEF5;

        .header-label {
          color: #606266;
          font-size: 14px;
          font-weight: 500;

          &:first-child {
            width: 120px;
          }

          &:last-child {
            margin-left: 10px;
          }
        }
      }

      .weekly-time-slot {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        padding: 8px;
        background: #fff;
        border-radius: 4px;

        &:last-of-type {
          margin-bottom: 0;
        }
      }

      .el-button {
        margin-top: 8px;
      }
    }

    .schedule-notice {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      background: #FFF7E6;
      border-radius: 4px;
      color: #E6A23C;
      font-size: 14px;
      margin-top: 20px;
    }
  }

  // 点名情况样式
  .attendance-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 4px;

    .date-range {
      font-size: 14px;
      color: #303133;
      font-weight: 500;
    }

    .date-navigation {
      display: flex;
      align-items: center;
      gap: 10px;
    }
  }

  .attendance-table {
    margin-bottom: 30px;
  }

  .history-attendance-section {
    margin-top: 40px;

    .section-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #E6A23C;
    }

    .history-attendance-table {
      margin-top: 15px;
    }
  }

  // 未排课直接点名对话框样式
  .direct-attendance-form {
    :deep(.el-form-item__label) {
      font-weight: normal;
      color: #606266;
    }

    .time-range-group {
      display: flex;
      align-items: center;
    }
  }

  // 日历选择器样式
  .calendar-picker-container {
    border: 1px solid #DCDFE6;
    border-radius: 4px;
    padding: 12px;
    background: #fff;

    .calendar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid #EBEEF5;

      .calendar-month-title {
        font-size: 16px;
        font-weight: 500;
        color: #303133;
      }
    }

    .calendar-body {
      .calendar-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        margin-bottom: 8px;

        .weekday {
          text-align: center;
          padding: 8px 0;
          font-size: 14px;
          font-weight: 500;
          color: #606266;
        }
      }

      .calendar-days {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;

        .calendar-day {
          aspect-ratio: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
          border: 1px solid transparent;

          &:not(.is-other-month):hover {
            background: #F5F7FA;
            border-color: #E6A23C;
          }

          &.is-other-month {
            color: #C0C4CC;
            cursor: not-allowed;
          }

          &.is-selected {
            background: #E6A23C;
            color: #fff;
            font-weight: 500;

            &:hover {
              background: #D89E3A;
            }
          }

          &.is-today {
            border-color: #E6A23C;
            font-weight: 500;

            &:not(.is-selected) {
              color: #E6A23C;
            }
          }
        }
      }
    }
  }
}
</style>

<!-- 全局样式：老师选择器下拉框 -->
<style lang="scss">
.teacher-select-dropdown {
  .teacher-select-header {
    display: grid;
    grid-template-columns: 100px 120px 80px 80px;
    padding: 8px 12px;
    background: #F5F7FA;
    border-bottom: 1px solid #EBEEF5;
    font-size: 13px;
    color: #606266;
    font-weight: 500;

    .header-col {
      text-align: left;

      &:first-child {
        padding-left: 8px;
      }
    }
  }

  .el-select-dropdown__item {
    height: auto;
    padding: 0;

    &.selected {
      background: #FFF7E6;

      .teacher-option-content {
        .teacher-name {
          color: #E6A23C;
        }
      }
    }

    &:hover {
      background: #F5F7FA;
    }
  }

  .teacher-option-content {
    display: grid;
    grid-template-columns: 100px 120px 80px 80px;
    padding: 12px;
    align-items: center;
    font-size: 14px;

    .teacher-name {
      color: #303133;
      padding-left: 8px;
    }

    .teacher-phone {
      color: #606266;
    }

    .teacher-status {
      display: flex;
      align-items: center;
      gap: 6px;

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;

        &.active {
          background: #67C23A;
        }

        &.busy {
          background: #F56C6C;
        }
      }

      .status-text {
        color: #606266;
        font-size: 13px;
      }
    }

    .teacher-action {
      .el-link {
        font-size: 13px;
      }
    }
  }
}

/* 教室选择器下拉框样式 */
.classroom-select-dropdown {
  .classroom-select-header {
    display: grid;
    grid-template-columns: 150px 100px 80px;
    padding: 8px 12px;
    background: #F5F7FA;
    border-bottom: 1px solid #EBEEF5;
    font-size: 13px;
    color: #606266;
    font-weight: 500;

    .header-col {
      text-align: left;

      &:first-child {
        padding-left: 8px;
      }
    }
  }

  .el-select-dropdown__item {
    height: auto;
    padding: 0;

    &.selected {
      background: #FFF7E6;

      .classroom-option-content {
        .classroom-name {
          color: #E6A23C;
        }
      }
    }

    &:hover {
      background: #F5F7FA;
    }
  }

  .classroom-option-content {
    display: grid;
    grid-template-columns: 150px 100px 80px;
    padding: 12px;
    align-items: center;
    font-size: 14px;

    .classroom-name {
      color: #303133;
      padding-left: 8px;
    }

    .classroom-status {
      display: flex;
      align-items: center;
      gap: 6px;

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;

        &.available {
          background: #67C23A;
        }

        &.occupied {
          background: #F56C6C;
        }
      }

      .status-text {
        color: #606266;
        font-size: 13px;
      }
    }

    .classroom-action {
      .el-link {
        font-size: 13px;
      }
    }
  }
}
</style>

