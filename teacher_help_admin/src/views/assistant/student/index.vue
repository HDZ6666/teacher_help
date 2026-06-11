<template>
  <div class="app-container">
    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="mb8">
      <el-tab-pane label="在读学员" name="active"></el-tab-pane>
      <el-tab-pane label="报读情况" name="enrollment"></el-tab-pane>
    </el-tabs>

    <!-- 在读学员Tab的搜索栏 -->
    <el-form v-if="activeTab === 'active'" :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="学员姓名" prop="studentName">
        <el-input
          v-model="queryParams.studentName"
          placeholder="请输入学员姓名"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="学员来源" prop="source">
        <el-select v-model="queryParams.source" placeholder="请选择学员来源" clearable style="width: 200px">
          <el-option label="线上推广" value="线上推广" />
          <el-option label="线下推广" value="线下推广" />
          <el-option label="老学员推荐" value="老学员推荐" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 报读情况Tab的搜索栏 -->
    <el-form v-if="activeTab === 'enrollment'" :model="enrollmentQueryParams" ref="enrollmentQueryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="学员姓名" prop="studentName">
        <el-input
          v-model="enrollmentQueryParams.studentName"
          placeholder="请输入学员姓名"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="报读课程" prop="courseName">
        <el-input
          v-model="enrollmentQueryParams.courseName"
          placeholder="请输入报读课程"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="结课状态" prop="courseStatus">
        <el-select v-model="enrollmentQueryParams.courseStatus" placeholder="请选择结课状态" clearable style="width: 200px">
          <el-option label="在读" value="在读" />
          <el-option label="已结课" value="已结课" />
          <el-option label="暂停" value="暂停" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 在读学员Tab的操作按钮栏 -->
    <el-row v-if="activeTab === 'active'" :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
        >新增学员</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="User"
          :disabled="multiple"
          @click="handleAssignFollower"
        >分配跟进人</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="UserFilled"
          :disabled="multiple"
          @click="handleAssignAdvisor"
        >分配学管师</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Upload"
          @click="handleImport"
        >导入学员</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
        >批量删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 报读情况Tab的操作按钮栏 -->
    <el-row v-if="activeTab === 'enrollment'" :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="UserFilled"
          :disabled="multiple"
          @click="handleAssignAdvisor"
        >分配学管师</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Upload"
          @click="handleImportEnrollment"
        >导入报读信息</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-dropdown @command="handleMoreAction">
          <el-button type="default" plain>
            更多操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="batchUpdate">批量更新</el-dropdown-item>
              <el-dropdown-item command="batchDelete">批量删除</el-dropdown-item>
              <el-dropdown-item command="exportDetail">导出详情</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 在读学员Tab的数据表格 -->
    <el-table
      v-if="activeTab === 'active'"
      v-loading="loading"
      :data="studentList"
      @selection-change="handleSelectionChange"
      border
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="学员姓名" align="center" prop="studentName" width="100" fixed="left">
        <template #default="scope">
          <el-link type="primary" @click="handleViewDetail(scope.row)">{{ scope.row.studentName }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="手机号" align="center" prop="phone" width="120" />
      <el-table-column label="绑卡状态" align="center" prop="cardStatus" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.cardStatus === 1 ? 'success' : 'info'">
            {{ scope.row.cardStatus === 1 ? '已绑卡' : '未绑卡' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="人脸采集" align="center" prop="faceStatus" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.faceStatus === 1 ? 'success' : 'warning'">
            {{ scope.row.faceStatus === 1 ? '已采集' : '未采集' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="学员来源" align="center" prop="source" width="120" />
      <el-table-column label="年龄" align="center" prop="age" width="80" />
      <el-table-column label="出生日期" align="center" prop="birthday" width="120" />
      <el-table-column label="所在班级" align="center" prop="className" width="120" />
      <el-table-column label="年级" align="center" prop="grade" width="100" />
      <el-table-column label="学校" align="center" prop="school" width="150" show-overflow-tooltip />
      <el-table-column label="标签" align="center" prop="tags" width="150">
        <template #default="scope">
          <el-tag
            v-for="tag in scope.row.tags"
            :key="tag"
            size="small"
            style="margin-right: 5px"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="国外手机号" align="center" prop="foreignPhone" width="140" />
      <el-table-column label="体重(kg)" align="center" prop="weight" width="100" />
      <el-table-column label="身份证号" align="center" prop="idCard" width="180" show-overflow-tooltip />
      <el-table-column label="跟进人" align="center" prop="follower" width="100" />
      <el-table-column label="学管师" align="center" prop="advisor" width="100" />
      <el-table-column label="学员创建人" align="center" prop="creator" width="120" />
      <el-table-column label="创建时间" align="center" prop="createTime" width="160" />
      <el-table-column label="操作" align="center" width="150" fixed="right" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 报读情况Tab的数据表格 -->
    <el-table
      v-if="activeTab === 'enrollment'"
      v-loading="loading"
      :data="enrollmentList"
      @selection-change="handleSelectionChange"
      border
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="学员姓名" align="center" prop="studentName" width="100" fixed="left" />
      <el-table-column label="手机号" align="center" prop="phone" width="120" />
      <el-table-column label="报读课程" align="center" prop="courseName" width="150" show-overflow-tooltip />
      <el-table-column label="所在班级" align="center" prop="className" width="120" />
      <el-table-column label="购买数量" align="center" prop="purchaseCount" width="100" />
      <el-table-column label="赠送数量" align="center" prop="giftCount" width="100" />
      <el-table-column label="已消耗数量" align="center" prop="consumedCount" width="110" />
      <el-table-column label="退转数量" align="center" prop="refundCount" width="100" />
      <el-table-column label="剩余数量" align="center" prop="remainingCount" width="100">
        <template #default="scope">
          <span :style="{ color: scope.row.remainingCount <= 5 ? 'red' : '' }">
            {{ scope.row.remainingCount }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="课消金额" align="center" prop="consumedAmount" width="120">
        <template #default="scope">
          ¥{{ scope.row.consumedAmount }}
        </template>
      </el-table-column>
      <el-table-column label="剩余课消金额" align="center" prop="remainingAmount" width="130">
        <template #default="scope">
          ¥{{ scope.row.remainingAmount }}
        </template>
      </el-table-column>
      <el-table-column label="到期日期" align="center" prop="expireDate" width="120" />
      <el-table-column label="缺课次数" align="center" prop="absenceCount" width="100" />
      <el-table-column label="跟进人" align="center" prop="follower" width="100" />
      <el-table-column label="学管师" align="center" prop="advisor" width="100" />
      <el-table-column label="操作" align="center" width="150" fixed="right" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="View" @click="handleViewDetail(scope.row)">查看</el-button>
          <el-button link type="primary" icon="Edit" @click="handleEditEnrollment(scope.row)">编辑</el-button>
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

    <!-- 添加或修改学员对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="头像" prop="avatar">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :auto-upload="false"
                :on-change="handleAvatarChange"
              >
                <img v-if="form.avatar" :src="form.avatar" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学生姓名" prop="studentName">
              <el-input v-model="form.studentName" placeholder="请输入学生姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-row :gutter="10">
                <el-col :span="16">
                  <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
                </el-col>
                <el-col :span="8">
                  <el-select v-model="form.phoneRelation" placeholder="关系">
                    <el-option label="妈妈" value="妈妈" />
                    <el-option label="爸爸" value="爸爸" />
                    <el-option label="奶奶" value="奶奶" />
                    <el-option label="爷爷" value="爷爷" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-col>
              </el-row>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio label="未知">未知</el-radio>
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄/生日" prop="ageType">
              <el-radio-group v-model="form.ageType">
                <el-radio label="age">年龄</el-radio>
                <el-radio label="birthday">出生日期</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="form.ageType === 'age'">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="form.age" :min="1" :max="100" />
              <span style="margin-left: 10px">岁</span>
              <el-input-number v-model="form.ageMonth" :min="0" :max="11" style="margin-left: 10px" />
              <span style="margin-left: 10px">月</span>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="form.ageType === 'birthday'">
            <el-form-item label="出生日期" prop="birthday">
              <el-date-picker
                v-model="form.birthday"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="就读学校" prop="school">
              <el-input v-model="form.school" placeholder="请输入就读学校" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前年级" prop="grade">
              <el-select v-model="form.grade" placeholder="请选择年级" style="width: 100%">
                <el-option label="一年级" value="一年级" />
                <el-option label="二年级" value="二年级" />
                <el-option label="三年级" value="三年级" />
                <el-option label="四年级" value="四年级" />
                <el-option label="五年级" value="五年级" />
                <el-option label="六年级" value="六年级" />
                <el-option label="初一" value="初一" />
                <el-option label="初二" value="初二" />
                <el-option label="初三" value="初三" />
                <el-option label="高一" value="高一" />
                <el-option label="高二" value="高二" />
                <el-option label="高三" value="高三" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学号" prop="studentNo">
              <el-input v-model="form.studentNo" placeholder="请输入学号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="国外手机号" prop="foreignPhone">
              <el-input v-model="form.foreignPhone" placeholder="请输入(最多50字)" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体重" prop="weight">
              <el-input v-model="form.weight" placeholder="请输入(最多50字)" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="form.idCard" placeholder="请输入(最多50字)" maxlength="50" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 联系信息 -->
        <el-divider content-position="left">联系信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="主要联系人" prop="mainContact">
              <el-row :gutter="10">
                <el-col :span="8">
                  <el-select v-model="form.mainContactRelation" placeholder="关系">
                    <el-option label="妈妈" value="妈妈" />
                    <el-option label="爸爸" value="爸爸" />
                    <el-option label="奶奶" value="奶奶" />
                    <el-option label="爷爷" value="爷爷" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-col>
                <el-col :span="16">
                  <el-input v-model="form.mainContactPhone" placeholder="请输入手机号" maxlength="11" />
                </el-col>
              </el-row>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-for="(contact, index) in form.backupContacts" :key="index">
            <el-form-item :label="'备用' + (index + 1)">
              <el-row :gutter="10">
                <el-col :span="8">
                  <el-select v-model="contact.relation" placeholder="关系">
                    <el-option label="妈妈" value="妈妈" />
                    <el-option label="爸爸" value="爸爸" />
                    <el-option label="奶奶" value="奶奶" />
                    <el-option label="爷爷" value="爷爷" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-col>
                <el-col :span="14">
                  <el-input v-model="contact.phone" placeholder="请输入手机号" maxlength="11" />
                </el-col>
                <el-col :span="2">
                  <el-button type="danger" icon="Delete" circle @click="removeBackupContact(index)" />
                </el-col>
              </el-row>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label=" " label-width="120px">
              <el-button type="primary" plain icon="Plus" @click="addBackupContact">添加备用联系人</el-button>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="家庭住址" prop="address">
              <el-input v-model="form.address" placeholder="请输入家庭住址" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学员来源" prop="source">
              <el-select v-model="form.source" placeholder="请选择学员来源" style="width: 100%">
                <el-option label="线上推广" value="线上推广" />
                <el-option label="线下推广" value="线下推广" />
                <el-option label="老学员推荐" value="老学员推荐" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="跟进人" prop="follower">
              <el-select v-model="form.follower" placeholder="请选择跟进人" style="width: 100%">
                <el-option label="李老师" value="李老师" />
                <el-option label="王老师" value="王老师" />
                <el-option label="赵老师" value="赵老师" />
                <el-option label="孙老师" value="孙老师" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学员创建人" prop="creator">
              <el-select v-model="form.creator" placeholder="请选择学员创建人" style="width: 100%">
                <el-option label="管理员" value="管理员" />
                <el-option label="李老师" value="李老师" />
                <el-option label="王老师" value="王老师" />
                <el-option label="张老师" value="张老师" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学管师" prop="advisor">
              <el-select v-model="form.advisor" placeholder="请选择学管师" style="width: 100%">
                <el-option label="王老师" value="王老师" />
                <el-option label="李老师" value="李老师" />
                <el-option label="赵老师" value="赵老师" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="标签" prop="tags">
              <el-select
                v-model="form.tags"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请选择标签（可输入新增）"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tagOptions"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
              <el-button type="text" @click="openTagManager" style="margin-left: 10px">标签管理</el-button>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancel">取 消</el-button>
          <el-button type="primary" @click="submitForm">保 存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 标签管理对话框 -->
    <el-dialog title="标签管理" v-model="tagManagerOpen" width="500px" append-to-body>
      <el-alert
        title="标签管理提示"
        type="warning"
        description="此区域内无标签，添加新标签后，其他也可见可用，删除时请谨慎"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      <el-input
        v-model="newTag"
        placeholder="请输入新标签"
        style="margin-bottom: 20px"
      >
        <template #append>
          <el-button @click="addNewTag">添加标签</el-button>
        </template>
      </el-input>
      <div class="tag-list">
        <el-tag
          v-for="tag in tagOptions"
          :key="tag"
          closable
          @close="removeTag(tag)"
          style="margin-right: 10px; margin-bottom: 10px"
        >
          {{ tag }}
        </el-tag>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="tagManagerOpen = false">取 消</el-button>
          <el-button type="primary" @click="tagManagerOpen = false">完 成</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 分配跟进人对话框 -->
    <el-dialog title="分配跟进人" v-model="assignFollowerOpen" width="700px" append-to-body>
      <el-input
        v-model="followerSearchName"
        placeholder="搜索跟进人姓名"
        prefix-icon="Search"
        style="margin-bottom: 20px"
        clearable
      />
      <el-table
        :data="filteredFollowerList"
        @row-click="handleFollowerRowClick"
        highlight-current-row
        max-height="400"
      >
        <el-table-column width="55">
          <template #default="scope">
            <el-radio v-model="selectedFollowerId" :label="scope.row.id">&nbsp;</el-radio>
          </template>
        </el-table-column>
        <el-table-column label="跟进人" prop="name" />
        <el-table-column label="手机号" prop="phone" />
        <el-table-column label="已分配在读学员" prop="assignedCount" align="center" />
      </el-table>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="assignFollowerOpen = false">取 消</el-button>
          <el-button type="primary" @click="confirmAssignFollower">确认分配</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 分配学管师对话框 -->
    <el-dialog title="分配学管师" v-model="assignAdvisorOpen" width="700px" append-to-body>
      <el-input
        v-model="advisorSearchName"
        placeholder="搜索学管师姓名"
        prefix-icon="Search"
        style="margin-bottom: 20px"
        clearable
      />
      <el-table
        :data="filteredAdvisorList"
        @row-click="handleAdvisorRowClick"
        highlight-current-row
        max-height="400"
      >
        <el-table-column width="55">
          <template #default="scope">
            <el-radio v-model="selectedAdvisorId" :label="scope.row.id">&nbsp;</el-radio>
          </template>
        </el-table-column>
        <el-table-column label="学管师" prop="name" />
        <el-table-column label="手机号" prop="phone" />
        <el-table-column label="已分配在读学员" prop="assignedCount" align="center" />
      </el-table>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="assignAdvisorOpen = false">取 消</el-button>
          <el-button type="primary" @click="confirmAssignAdvisor">确认分配</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="AssistantStudent">
import { ArrowDown, Plus, Delete } from '@element-plus/icons-vue';

const { proxy } = getCurrentInstance();

const activeTab = ref('active'); // 当前激活的Tab
const studentList = ref([]); // 在读学员列表
const enrollmentList = ref([]); // 报读情况列表
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const tagManagerOpen = ref(false); // 标签管理弹窗
const newTag = ref(""); // 新标签
const tagOptions = ref(["优秀", "活跃", "进步", "需关注"]); // 标签选项

// 分配跟进人相关
const assignFollowerOpen = ref(false); // 分配跟进人弹窗
const followerSearchName = ref(""); // 跟进人搜索关键词
const selectedFollowerId = ref(null); // 选中的跟进人ID
const followerList = ref([]); // 跟进人列表

// 分配学管师相关
const assignAdvisorOpen = ref(false); // 分配学管师弹窗
const advisorSearchName = ref(""); // 学管师搜索关键词
const selectedAdvisorId = ref(null); // 选中的学管师ID
const advisorList = ref([]); // 学管师列表

// 查询参数
const data = reactive({
  form: {
    avatar: null,
    studentName: null,
    phone: null,
    phoneRelation: "妈妈",
    gender: "未知",
    ageType: "age",
    age: null,
    ageMonth: null,
    birthday: null,
    school: null,
    grade: null,
    studentNo: null,
    foreignPhone: null,
    weight: null,
    idCard: null,
    mainContactRelation: "妈妈",
    mainContactPhone: null,
    backupContacts: [],
    address: null,
    source: null,
    follower: null,
    creator: null,
    advisor: null,
    tags: [],
    remark: null
  },
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    studentName: null,
    source: null
  },
  enrollmentQueryParams: {
    pageNum: 1,
    pageSize: 10,
    studentName: null,
    courseName: null,
    courseStatus: null
  },
  rules: {
    studentName: [
      { required: true, message: "学员姓名不能为空", trigger: "blur" }
    ],
    phone: [
      { required: true, message: "手机号不能为空", trigger: "blur" },
      { pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/, message: "请输入正确的手机号码", trigger: "blur" }
    ]
  }
});

const { queryParams, enrollmentQueryParams, form, rules } = toRefs(data);

/** 过滤后的跟进人列表 */
const filteredFollowerList = computed(() => {
  if (!followerSearchName.value) {
    return followerList.value;
  }
  return followerList.value.filter(item =>
    item.name.includes(followerSearchName.value)
  );
});

/** 过滤后的学管师列表 */
const filteredAdvisorList = computed(() => {
  if (!advisorSearchName.value) {
    return advisorList.value;
  }
  return advisorList.value.filter(item =>
    item.name.includes(advisorSearchName.value)
  );
});

/** Tab切换处理 */
function handleTabChange(tab) {
  activeTab.value = tab;
  getList();
}

/** 查询学员列表 */
function getList() {
  loading.value = true;

  if (activeTab.value === 'active') {
    // 在读学员模拟数据
    setTimeout(() => {
      const mockData = [
        {
          id: 1,
          studentName: "张三",
          phone: "13800138001",
          cardStatus: 1,
          faceStatus: 1,
          source: "线上推广",
          age: 12,
          birthday: "2012-05-15",
          className: "初一(3)班",
          grade: "初一",
          school: "北京市第一中学",
          tags: ["优秀", "活跃"],
          foreignPhone: "+1-234-567-8901",
          weight: 45.5,
          idCard: "110101201205150011",
          follower: "李老师",
          advisor: "王老师",
          creator: "管理员",
          createTime: "2024-01-15 10:30:00"
        },
        {
          id: 2,
          studentName: "李四",
          phone: "13900139002",
          cardStatus: 0,
          faceStatus: 1,
          source: "老学员推荐",
          age: 13,
          birthday: "2011-08-20",
          className: "初二(1)班",
          grade: "初二",
          school: "北京市第二中学",
          tags: ["进步"],
          foreignPhone: "",
          weight: 48.0,
          idCard: "110101201108200022",
          follower: "赵老师",
          advisor: "王老师",
          creator: "张老师",
          createTime: "2024-02-10 14:20:00"
        },
        {
          id: 3,
          studentName: "王五",
          phone: "13700137003",
          cardStatus: 1,
          faceStatus: 0,
          source: "线下推广",
          age: 11,
          birthday: "2013-03-10",
          className: "六年级(2)班",
          grade: "六年级",
          school: "北京市实验小学",
          tags: ["需关注"],
          foreignPhone: "",
          weight: 42.0,
          idCard: "110101201303100033",
          follower: "孙老师",
          advisor: "李老师",
          creator: "管理员",
          createTime: "2024-03-05 09:15:00"
        }
      ];

      studentList.value = mockData;
      total.value = mockData.length;
      loading.value = false;
    }, 500);
  } else if (activeTab.value === 'enrollment') {
    // 报读情况模拟数据
    setTimeout(() => {
      const mockEnrollmentData = [
        {
          id: 1,
          studentName: "张三",
          phone: "13800138001",
          courseName: "数学提高班",
          className: "初一(3)班",
          purchaseCount: 40,
          giftCount: 4,
          consumedCount: 20,
          refundCount: 0,
          remainingCount: 24,
          consumedAmount: 4000,
          remainingAmount: 4800,
          expireDate: "2025-06-30",
          absenceCount: 2,
          follower: "李老师",
          advisor: "王老师"
        },
        {
          id: 2,
          studentName: "李四",
          phone: "13900139002",
          courseName: "英语强化班",
          className: "初二(1)班",
          purchaseCount: 30,
          giftCount: 3,
          consumedCount: 28,
          refundCount: 0,
          remainingCount: 5,
          consumedAmount: 5600,
          remainingAmount: 1000,
          expireDate: "2025-03-15",
          absenceCount: 1,
          follower: "赵老师",
          advisor: "王老师"
        },
        {
          id: 3,
          studentName: "王五",
          phone: "13700137003",
          courseName: "语文阅读班",
          className: "六年级(2)班",
          purchaseCount: 50,
          giftCount: 5,
          consumedCount: 15,
          refundCount: 2,
          remainingCount: 38,
          consumedAmount: 3000,
          remainingAmount: 7600,
          expireDate: "2025-12-31",
          absenceCount: 0,
          follower: "孙老师",
          advisor: "李老师"
        }
      ];

      enrollmentList.value = mockEnrollmentData;
      total.value = mockEnrollmentData.length;
      loading.value = false;
    }, 500);
  }
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    id: null,
    avatar: null,
    studentName: null,
    phone: null,
    phoneRelation: "妈妈",
    gender: "未知",
    ageType: "age",
    age: null,
    ageMonth: null,
    birthday: null,
    school: null,
    grade: null,
    studentNo: null,
    foreignPhone: null,
    weight: null,
    idCard: null,
    mainContactRelation: "妈妈",
    mainContactPhone: null,
    backupContacts: [],
    address: null,
    source: null,
    follower: null,
    creator: null,
    advisor: null,
    tags: [],
    remark: null
  };
  proxy.resetForm("formRef");
}

/** 头像上传处理 */
function handleAvatarChange(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    form.value.avatar = e.target.result;
  };
  reader.readAsDataURL(file.raw);
}

/** 添加备用联系人 */
function addBackupContact() {
  form.value.backupContacts.push({
    relation: "爸爸",
    phone: ""
  });
}

/** 删除备用联系人 */
function removeBackupContact(index) {
  form.value.backupContacts.splice(index, 1);
}

/** 打开标签管理 */
function openTagManager() {
  tagManagerOpen.value = true;
}

/** 添加新标签 */
function addNewTag() {
  if (newTag.value && !tagOptions.value.includes(newTag.value)) {
    tagOptions.value.push(newTag.value);
    newTag.value = "";
    proxy.$modal.msgSuccess("标签添加成功");
  } else if (tagOptions.value.includes(newTag.value)) {
    proxy.$modal.msgWarning("标签已存在");
  } else {
    proxy.$modal.msgWarning("请输入标签名称");
  }
}

/** 删除标签 */
function removeTag(tag) {
  const index = tagOptions.value.indexOf(tag);
  if (index > -1) {
    tagOptions.value.splice(index, 1);
    proxy.$modal.msgSuccess("标签删除成功");
  }
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加学员";
}

/** 分配跟进人按钮操作 */
function handleAssignFollower() {
  if (ids.value.length === 0) {
    proxy.$modal.msgWarning("请选择要分配的学员");
    return;
  }

  // 初始化跟进人列表（模拟数据）
  followerList.value = [
    { id: 0, name: "待分配", phone: "-", assignedCount: 332 },
    { id: 1, name: "李老师", phone: "130****2483", assignedCount: 45 },
    { id: 2, name: "王老师", phone: "150****9773", assignedCount: 38 },
    { id: 3, name: "赵老师", phone: "138****5621", assignedCount: 52 },
    { id: 4, name: "孙老师", phone: "186****7894", assignedCount: 29 }
  ];

  selectedFollowerId.value = null;
  followerSearchName.value = "";
  assignFollowerOpen.value = true;
}

/** 跟进人行点击 */
function handleFollowerRowClick(row) {
  selectedFollowerId.value = row.id;
}

/** 确认分配跟进人 */
function confirmAssignFollower() {
  if (selectedFollowerId.value === null) {
    proxy.$modal.msgWarning("请选择跟进人");
    return;
  }

  const follower = followerList.value.find(item => item.id === selectedFollowerId.value);

  // 模拟分配操作
  setTimeout(() => {
    proxy.$modal.msgSuccess(`已成功将 ${ids.value.length} 名学员分配给 ${follower.name}`);
    assignFollowerOpen.value = false;
    getList();
  }, 300);
}

/** 分配学管师按钮操作 */
function handleAssignAdvisor() {
  if (ids.value.length === 0) {
    proxy.$modal.msgWarning("请选择要分配的学员");
    return;
  }

  // 初始化学管师列表（模拟数据）
  advisorList.value = [
    { id: 0, name: "待分配", phone: "-", assignedCount: 332 },
    { id: 1, name: "迅优文化（黄老师）", phone: "130****2483", assignedCount: 1 },
    { id: 2, name: "甘泉", phone: "150****9773", assignedCount: 21 },
    { id: 3, name: "张老师", phone: "138****5621", assignedCount: 15 },
    { id: 4, name: "刘老师", phone: "186****7894", assignedCount: 28 }
  ];

  selectedAdvisorId.value = null;
  advisorSearchName.value = "";
  assignAdvisorOpen.value = true;
}

/** 学管师行点击 */
function handleAdvisorRowClick(row) {
  selectedAdvisorId.value = row.id;
}

/** 确认分配学管师 */
function confirmAssignAdvisor() {
  if (selectedAdvisorId.value === null) {
    proxy.$modal.msgWarning("请选择学管师");
    return;
  }

  const advisor = advisorList.value.find(item => item.id === selectedAdvisorId.value);

  // 模拟分配操作
  setTimeout(() => {
    proxy.$modal.msgSuccess(`已成功将 ${ids.value.length} 名学员分配给 ${advisor.name}`);
    assignAdvisorOpen.value = false;
    getList();
  }, 300);
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  if (activeTab.value === 'active') {
    proxy.resetForm("queryRef");
  } else {
    proxy.resetForm("enrollmentQueryRef");
  }
  handleQuery();
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  single.value = selection.length !== 1;
  multiple.value = !selection.length;
}

/** 导入学员 */
function handleImport() {
  proxy.$modal.msgSuccess("导入学员功能开发中...");
}

/** 导入报读信息 */
function handleImportEnrollment() {
  proxy.$modal.msgSuccess("导入报读信息功能开发中...");
}

/** 更多操作 */
function handleMoreAction(command) {
  switch (command) {
    case 'batchUpdate':
      proxy.$modal.msgSuccess("批量更新功能开发中...");
      break;
    case 'batchDelete':
      handleDelete();
      break;
    case 'exportDetail':
      proxy.$modal.msgSuccess("导出详情功能开发中...");
      break;
  }
}

/** 编辑报读信息 */
function handleEditEnrollment(row) {
  proxy.$modal.msgSuccess(`编辑学员 ${row.studentName} 的报读信息，功能开发中...`);
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const studentId = row.id || ids.value[0];

  // 模拟获取详情数据
  const student = studentList.value.find(item => item.id === studentId);
  if (student) {
    form.value = { ...student };
    open.value = true;
    title.value = "修改学员";
  }
}

/** 查看学员详情 */
function handleViewDetail(row) {
  proxy.$router.push(`/assistant/student/detail/${row.id}`);
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["studentRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        // 模拟修改操作
        proxy.$modal.msgSuccess("修改成功");
        open.value = false;
        getList();
      } else {
        // 模拟新增操作
        proxy.$modal.msgSuccess("新增成功");
        open.value = false;
        getList();
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const studentIds = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除学员编号为"' + studentIds + '"的数据项？').then(function() {
    // 模拟删除操作
    proxy.$modal.msgSuccess("删除成功");
    getList();
  }).catch(() => {});
}

/** 导出按钮操作 */
function handleExport() {
  proxy.$modal.confirm('是否确认导出所有学员数据项？').then(function() {
    proxy.$modal.msgSuccess("导出成功");
  }).catch(() => {});
}

// 初始化加载数据
getList();
</script>

<style scoped lang="scss">
.avatar-uploader {
  display: inline-block;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-uploader .avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
}

.avatar-uploader .avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.tag-list {
  min-height: 100px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>


