<template>
  <div class="app-container" v-loading="loading">
    <!-- 返回按钮 -->
    <el-page-header @back="goBack" class="mb20">
      <template #content>
        <span class="text-large font-600 mr-3">点评详情</span>
      </template>
    </el-page-header>

    <!-- 课程基本信息（来自 /teach/class-record/attendance/{id}） -->
    <el-card class="mb20">
      <div class="course-header">
        <h2>{{ classInfo.className || '-' }} {{ classInfo.startTime }}~{{ classInfo.endTime }}</h2>
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
              <span>{{ classInfo.teacherName || '-' }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">上课教室：</span>
              <span>{{ classInfo.classroom || '-' }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 点评列表 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <!-- 已点评Tab - 左右布局（来自 /teach/comment/list?attendanceId=&status=1） -->
        <el-tab-pane :label="`已点评(${commentedStudents.length})`" name="commented">
          <div v-if="commentedStudents.length" class="comment-container">
            <!-- 左侧学员列表 -->
            <div class="student-list">
              <div
                v-for="student in commentedStudents"
                :key="student.studentId"
                class="student-item"
                :class="{ active: selectedStudentId === student.studentId }"
                @click="selectStudent(student)"
              >
                <el-avatar :size="40">{{ (student.studentName || '?').charAt(0) }}</el-avatar>
                <div class="student-detail">
                  <div class="student-name">{{ student.studentName }}</div>
                  <div class="student-meta">收到评价 {{ student.comments.length }}条</div>
                </div>
              </div>
            </div>

            <!-- 右侧点评详情 -->
            <div class="comment-detail">
              <div v-if="selectedStudent" class="detail-content">
                <div class="detail-header">
                  <h3>评价详情 <span class="comment-count">(收到评价 {{ selectedStudent.comments.length }}条)</span></h3>
                </div>

                <div v-for="comment in selectedStudent.comments" :key="comment.id" class="comment-card">
                  <div class="comment-header">
                    <div class="author-info">
                      <el-avatar :size="32">{{ (comment.teacherName || comment.createBy || '师').charAt(0) }}</el-avatar>
                      <div class="author-detail">
                        <div class="author-name">{{ comment.teacherName || comment.createBy || '-' }}</div>
                        <el-tag size="small" type="success">{{ commentTypeLabel(comment.commentType) }}</el-tag>
                      </div>
                    </div>
                    <div class="comment-time">
                      {{ parseTime(comment.createTime, '{y}-{m}-{d} {h}:{i}') }}
                      <el-button
                        link
                        type="danger"
                        icon="Delete"
                        v-hasPermi="['teach:comment:remove']"
                        @click="handleRevoke(comment)"
                      >撤销</el-button>
                    </div>
                  </div>

                  <!-- 后端目前只保存两个评分维度：课堂表现(performanceScore)、跟课巩固(homeworkScore) -->
                  <div class="rating-section">
                    <div class="rating-row">
                      <div class="rating-item">
                        <span class="rating-label">课堂表现：</span>
                        <el-rate :model-value="comment.performanceScore || 0" disabled />
                      </div>
                      <div class="rating-item">
                        <span class="rating-label">跟课巩固：</span>
                        <el-rate :model-value="comment.homeworkScore || 0" disabled />
                      </div>
                    </div>
                  </div>

                  <div class="comment-text">{{ comment.commentContent }}</div>
                </div>
              </div>
              <el-empty v-else description="请选择学员查看点评详情" :image-size="100" />
            </div>
          </div>
          <el-empty v-else description="本次课暂无点评" :image-size="100" />
        </el-tab-pane>

        <!-- 未点评Tab - 表格列表（来自 /teach/comment/pending?attendance_id=） -->
        <el-tab-pane :label="`未点评(${uncommentedStudents.length})`" name="uncommented">
          <el-button
            type="warning"
            class="mb20"
            :disabled="!uncommentedStudents.length"
            v-hasPermi="['teach:comment:add']"
            @click="handleBatchEvaluate"
          >{{ selectedPending.length ? `批量点评(${selectedPending.length})` : '全部点评' }}</el-button>

          <el-table :data="uncommentedStudents" border @selection-change="handlePendingSelection">
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="学员" prop="studentName" align="center">
              <template #default="scope">
                <div class="student-cell">
                  <el-avatar :size="32">{{ (scope.row.studentName || '?').charAt(0) }}</el-avatar>
                  <div class="student-info">
                    <div class="name">{{ scope.row.studentName }}</div>
                    <el-tag v-if="scope.row.attendanceStatusName" size="small">{{ scope.row.attendanceStatusName }}</el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="150">
              <template #default="scope">
                <el-button
                  type="warning"
                  link
                  v-hasPermi="['teach:comment:add']"
                  @click="handleEvaluate(scope.row)"
                >去评价</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup name="CommentDetail">
import { ref, computed, getCurrentInstance, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAttendanceRecord } from '@/api/assistant/classRecord'
import { delComment, listComment, listPendingCommentStudents } from '@/api/teach/comment'

const { proxy } = getCurrentInstance()
const route = useRoute()
const router = useRouter()

const COMMENT_TYPE_LABELS = { single: '单独点评', unified: '统一点评', batch: '批量点评' }
// 一次课的点评数量有限，一次取完；超过时提示用户
const COMMENT_PAGE_SIZE = 200

const loading = ref(false)
const activeTab = ref('commented')
const classInfo = ref({})
const comments = ref([])
const uncommentedStudents = ref([])
const selectedStudentId = ref(null)
const selectedPending = ref([])

const attendanceId = computed(() => route.params.id)

// 已点评学员：按学员聚合点评记录
const commentedStudents = computed(() => {
  const map = new Map()
  comments.value.forEach(comment => {
    if (!map.has(comment.studentId)) {
      map.set(comment.studentId, { studentId: comment.studentId, studentName: comment.studentName, comments: [] })
    }
    map.get(comment.studentId).comments.push(comment)
  })
  return Array.from(map.values())
})

const selectedStudent = computed(() => {
  return commentedStudents.value.find(item => item.studentId === selectedStudentId.value) || null
})

function commentTypeLabel(type) {
  return COMMENT_TYPE_LABELS[type] || '点评'
}

function selectStudent(student) {
  selectedStudentId.value = student.studentId
}

function handlePendingSelection(selection) {
  selectedPending.value = selection
}

/** 加载课次信息、已点评记录、未点评学员 */
function loadData() {
  if (!attendanceId.value) {
    return
  }
  loading.value = true
  Promise.all([
    getAttendanceRecord(attendanceId.value),
    listComment({ attendanceId: attendanceId.value, status: 1, pageNum: 1, pageSize: COMMENT_PAGE_SIZE }),
    listPendingCommentStudents(attendanceId.value)
  ])
    .then(([recordRes, commentRes, pendingRes]) => {
      classInfo.value = recordRes.data || {}
      comments.value = commentRes.rows || []
      if ((commentRes.total || 0) > comments.value.length) {
        proxy.$modal.msgWarning(`点评较多，仅展示前${comments.value.length}条`)
      }
      uncommentedStudents.value = pendingRes.data || []
      const stillExists = commentedStudents.value.some(item => item.studentId === selectedStudentId.value)
      if (!stillExists) {
        selectedStudentId.value = commentedStudents.value.length ? commentedStudents.value[0].studentId : null
      }
      if (!commentedStudents.value.length && uncommentedStudents.value.length) {
        activeTab.value = 'uncommented'
      }
    })
    .finally(() => {
      loading.value = false
    })
}

/** 撤销点评 */
function handleRevoke(comment) {
  proxy.$modal
    .confirm(`确认撤销对“${comment.studentName}”的这条点评吗？`)
    .then(() => delComment(comment.id))
    .then(() => {
      proxy.$modal.msgSuccess('撤销成功')
      loadData()
    })
    .catch(() => {})
}

// 去评价（单个学员）
function handleEvaluate(row) {
  router.push({
    name: 'EvaluateStudent',
    params: { id: attendanceId.value },
    query: { studentIds: row.studentId }
  })
}

// 批量点评：有勾选时只评勾选的学员，否则评全部未点评学员
function handleBatchEvaluate() {
  const source = selectedPending.value.length ? selectedPending.value : uncommentedStudents.value
  router.push({
    name: 'EvaluateStudent',
    params: { id: attendanceId.value },
    query: { studentIds: source.map(item => item.studentId).join(',') }
  })
}

// 返回上一页
function goBack() {
  router.back()
}

onMounted(() => {
  loadData()
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

