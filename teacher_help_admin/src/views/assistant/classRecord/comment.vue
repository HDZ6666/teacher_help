<template>
  <div class="app-container">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" class="mb20">
      <template #content>
        <span class="text-large font-600 mr-3">点评详情</span>
      </template>
    </el-page-header>

    <!-- 课程基本信息 -->
    <el-card class="mb20">
      <div class="course-header">
        <h2>{{ classInfo.className }} {{ classInfo.startTime }}~{{ classInfo.endTime }}</h2>
      </div>

      <div class="course-info">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <span class="label">上课时间：</span>
              <span>{{ classInfo.classDate }} {{ classInfo.startTime }}~{{ classInfo.endTime }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">授课老师：</span>
              <span>{{ classInfo.teacherName }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">上课教室：</span>
              <span>{{ classInfo.classroom }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 点评列表 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 已点评Tab - 左右布局 -->
        <el-tab-pane label="已点评(1)" name="commented">
          <div class="comment-container">
            <!-- 左侧学员列表 -->
            <div class="student-list">
              <div
                v-for="student in commentedStudents"
                :key="student.id"
                class="student-item"
                :class="{ active: selectedStudent?.id === student.id }"
                @click="selectStudent(student)"
              >
                <el-avatar :size="40" :src="student.avatar">{{ student.studentName.charAt(0) }}</el-avatar>
                <div class="student-detail">
                  <div class="student-name">
                    {{ student.studentName }}
                    <el-tag v-if="student.commentCount > 0" size="small">刷新</el-tag>
                  </div>
                  <div class="student-meta">收到评价 {{ student.commentCount }}条 0</div>
                </div>
              </div>
            </div>

            <!-- 右侧点评详情 -->
            <div class="comment-detail">
              <div v-if="selectedStudent" class="detail-content">
                <div class="detail-header">
                  <h3>评价详情 <span class="comment-count">(收到评价 {{ selectedStudent.commentCount }}条 0)</span></h3>
                  <div class="header-actions">
                    <el-button type="text" icon="Share">分享</el-button>
                    <el-button type="text" icon="Edit">编辑</el-button>
                    <el-button type="text" icon="Delete">删除</el-button>
                  </div>
                </div>

                <div class="comment-card">
                  <div class="comment-header">
                    <div class="author-info">
                      <el-avatar :size="32">{{ selectedStudent.commentAuthor.charAt(0) }}</el-avatar>
                      <div class="author-detail">
                        <div class="author-name">{{ selectedStudent.commentAuthor }}</div>
                        <el-tag size="small" type="success">学校名称</el-tag>
                      </div>
                    </div>
                    <div class="comment-time">{{ selectedStudent.commentTime }}</div>
                  </div>

                  <div class="rating-section">
                    <div class="rating-row">
                      <div class="rating-item">
                        <span class="rating-label">课堂表现：</span>
                        <el-rate v-model="selectedStudent.classPerformance" disabled />
                      </div>
                      <div class="rating-item">
                        <span class="rating-label">学习态度：</span>
                        <el-rate v-model="selectedStudent.learningAttitude" disabled />
                      </div>
                    </div>
                    <div class="rating-row">
                      <div class="rating-item">
                        <span class="rating-label">动作技巧：</span>
                        <el-rate v-model="selectedStudent.skillLevel" disabled />
                      </div>
                      <div class="rating-item">
                        <span class="rating-label">跟课巩固：</span>
                        <el-rate v-model="selectedStudent.consolidation" disabled />
                      </div>
                    </div>
                  </div>

                  <div class="comment-text">{{ selectedStudent.commentText }}</div>

                  <div class="comment-footer">
                    <el-avatar :size="32">U</el-avatar>
                    <el-input
                      v-model="selectedStudent.replyText"
                      type="textarea"
                      :rows="3"
                      placeholder="输入评论内容，200字以内"
                      maxlength="200"
                      show-word-limit
                      class="reply-input"
                    />
                  </div>
                  <div class="send-area">
                    <el-button type="warning" class="send-btn">发送</el-button>
                    <div class="footer-tip">你还未设置显示在家长端的老师名称 <span class="link-text">去设置></span></div>
                  </div>
                </div>
              </div>
              <el-empty v-else description="请选择学员查看点评详情" :image-size="100" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 未点评Tab - 表格列表 -->
        <el-tab-pane label="未点评(1)" name="uncommented">
          <el-button type="warning" class="mb20" @click="handleBatchEvaluate">批量点评</el-button>

          <el-table :data="uncommentedStudents" border>
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="学员" prop="studentName" align="center">
              <template #default="scope">
                <div class="student-cell">
                  <el-avatar :size="32" :src="scope.row.avatar">{{ scope.row.studentName.charAt(0) }}</el-avatar>
                  <div class="student-info">
                    <div class="name">{{ scope.row.studentName }}</div>
                    <el-tag v-if="scope.row.tag" size="small">{{ scope.row.tag }}</el-tag>
                    <div class="meta">{{ scope.row.meta }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="150">
              <template #default="scope">
                <el-button type="warning" link @click="handleEvaluate(scope.row)">去评价</el-button>
              </template>
            </el-table-column>
          </el-table>

          <pagination
            v-show="uncommentedTotal > 0"
            v-model:page="uncommentedQueryParams.pageNum"
            v-model:limit="uncommentedQueryParams.pageSize"
            :total="uncommentedTotal"
            @pagination="getUncommentedList"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup name="CommentDetail">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 当前激活的tab
const activeTab = ref('commented')

// 当前选中的学员
const selectedStudent = ref(null)

// 课程基本信息
const classInfo = ref({
  className: '拓展训练周六9:00',
  classDate: '2025-11-03',
  startTime: '10:00',
  endTime: '11:30',
  teacherName: '拓展训练',
  classroom: '叶老师'
})

// 已点评学员列表
const commentedStudents = ref([
  {
    id: 1,
    studentName: '刘少岁',
    avatar: '',
    commentCount: 1,
    commentAuthor: 'HDZ',
    commentTime: '2025-11-07 17:03',
    classPerformance: 5,
    learningAttitude: 5,
    skillLevel: 5,
    consolidation: 5,
    commentText: '满大大测试',
    replyText: ''
  }
])

// 未点评学员列表
const uncommentedStudents = ref([
  {
    id: 2,
    studentName: '方炜冉',
    avatar: '',
    tag: '刷新',
    meta: '未到2次后，无法发送到家长端'
  }
])

const uncommentedTotal = ref(1)
const uncommentedQueryParams = ref({
  pageNum: 1,
  pageSize: 10
})

// 选择学员
function selectStudent(student) {
  selectedStudent.value = student
}

// 获取未点评学员列表
function getUncommentedList() {
  // TODO: 调用API获取未点评学员列表
  console.log('获取未点评学员列表')
}

// 去评价（单个学员）
function handleEvaluate(row) {
  // 跳转到评价页面，传递学员ID
  router.push({
    name: 'EvaluateStudent',
    params: { id: route.params.id },
    query: { studentIds: row.id }
  })
}

// 批量点评
function handleBatchEvaluate() {
  // 获取所有未点评学员的ID
  const studentIds = uncommentedStudents.value.map(s => s.id).join(',')
  router.push({
    name: 'EvaluateStudent',
    params: { id: route.params.id },
    query: { studentIds }
  })
}

// 返回上一页
function goBack() {
  router.back()
}

// 组件挂载时获取详情数据
onMounted(() => {
  const recordId = route.params.id
  console.log('点名记录ID:', recordId)
  // TODO: 根据ID获取点评数据

  // 默认选中第一个学员
  if (commentedStudents.value.length > 0) {
    selectedStudent.value = commentedStudents.value[0]
  }
})
</script>

<style scoped lang="scss">
.course-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;

  h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.course-info {
  .info-item {
    line-height: 32px;

    .label {
      color: #909399;
      margin-right: 8px;
    }
  }
}

.mb20 {
  margin-bottom: 20px;
}

.comment-container {
  display: flex;
  gap: 20px;
  min-height: 500px;

  // 左侧学员列表
  .student-list {
    width: 280px;
    border-right: 1px solid #ebeef5;
    padding-right: 20px;

    .student-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.3s;
      margin-bottom: 8px;

      &:hover {
        background-color: #f5f7fa;
      }

      &.active {
        background-color: #ecf5ff;
        border: 1px solid #409eff;
      }

      .student-detail {
        flex: 1;

        .student-name {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 5px;
        }

        .student-meta {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  // 右侧点评详情
  .comment-detail {
    flex: 1;
    padding-left: 20px;

    .detail-content {
      .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #ebeef5;

        h3 {
          margin: 0;
          font-size: 16px;
          color: #303133;

          .comment-count {
            font-size: 14px;
            color: #909399;
            font-weight: normal;
          }
        }

        .header-actions {
          display: flex;
          gap: 10px;
        }
      }

      .comment-card {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 20px;

        .comment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;

          .author-info {
            display: flex;
            align-items: center;
            gap: 10px;

            .author-detail {
              display: flex;
              align-items: center;
              gap: 8px;

              .author-name {
                font-weight: 500;
                color: #303133;
              }
            }
          }

          .comment-time {
            color: #909399;
            font-size: 14px;
          }
        }

        .rating-section {
          margin-bottom: 20px;

          .rating-row {
            display: flex;
            gap: 40px;
            margin-bottom: 12px;

            &:last-child {
              margin-bottom: 0;
            }

            .rating-item {
              display: flex;
              align-items: center;
              gap: 8px;
              flex: 1;

              .rating-label {
                color: #606266;
                font-size: 14px;
                white-space: nowrap;
              }
            }
          }
        }

        .comment-text {
          color: #303133;
          font-size: 14px;
          line-height: 1.6;
          margin-bottom: 20px;
          padding: 15px;
          background-color: #fff;
          border-radius: 4px;
        }

        .comment-footer {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 15px;

          .reply-input {
            flex: 1;
          }
        }

        .send-area {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .send-btn {
            margin-right: auto;
          }

          .footer-tip {
            color: #909399;
            font-size: 12px;

            .link-text {
              color: #409eff;
              cursor: pointer;

              &:hover {
                text-decoration: underline;
              }
            }
          }
        }
      }
    }
  }
}

// 未点评Tab样式
.student-cell {
  display: flex;
  align-items: center;
  gap: 10px;

  .student-info {
    text-align: left;

    .name {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
    }

    .meta {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }
}
</style>

