<template>
  <div class="app-container evaluate-page">
    <!-- 头部 -->
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" @click="goBack">评价学员</el-button>
      <div class="header-actions">
        <el-tooltip content="草稿功能暂未接入后端" placement="bottom">
          <span><el-button disabled>保存草稿</el-button></span>
        </el-tooltip>
        <el-button type="warning" :loading="submitting" :disabled="!studentList.length" @click="handleSubmit">发送</el-button>
      </div>
    </div>

    <!-- 课次信息 -->
    <el-card class="course-info-card">
      <h3>课次信息</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="info-item">{{ classInfo.courseName || '-' }}</div>
          <div class="info-item">上课时间：{{ classInfo.classTime || '-' }}</div>
          <div class="info-item">上课老师：{{ classInfo.teacherName || '-' }}</div>
          <div class="info-item">上课内容：{{ classInfo.content || '-' }}</div>
        </el-col>
        <el-col :span="12">
          <div class="info-item">所属班级：{{ classInfo.className }}</div>
          <div class="info-item">点名时间：{{ classInfo.attendanceTime || '-' }}</div>
          <div class="info-item">点名老师：{{ classInfo.createBy || '-' }}</div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 写评价 -->
    <el-card v-loading="loading" class="evaluate-card">
      <el-alert
        class="mb20"
        type="info"
        :closable="false"
        show-icon
        title="当前保存“课堂表现”“跟课巩固（作业）”两项评分和评价内容；学习态度、动作技巧评分、评价模板、录音/图片/视频附件暂未接入后端，不会保存。"
      />
      <el-empty v-if="!loading && !studentList.length" description="该课次没有待点评的学员" />
      <h3>写评价 <span class="student-count">(给{{ studentList.length }}个学员)</span></h3>

      <!-- Tab切换 -->
      <el-tabs v-model="evaluateMode" class="evaluate-tabs">
        <el-tab-pane label="分开评价学员" name="separate"></el-tab-pane>
        <el-tab-pane label="统一评价学员" name="unified"></el-tab-pane>
      </el-tabs>

      <!-- 评价模板选择 -->
      <div class="template-selector">
        <span>评价模板：</span>
        <el-select v-model="selectedTemplate" placeholder="舞蹈" style="width: 200px" disabled>
          <el-option label="舞蹈" value="dance" />
          <el-option label="体育" value="sports" />
          <el-option label="美术" value="art" />
        </el-select>
        <el-button type="text" class="template-link" disabled>设置评价模板（未接入）</el-button>
      </div>

      <!-- 统一评价模式 -->
      <div v-if="evaluateMode === 'unified'" class="unified-evaluate">
        <!-- 已选学员列表 -->
        <div class="selected-students">
          <span>已选学员：</span>
          <span class="student-names">{{ studentNames }}</span>
        </div>

        <!-- 统一评分区域 -->
        <div class="rating-area">
          <div class="rating-row">
            <div class="rating-item">
              <span class="rating-label">课堂表现：</span>
              <el-rate v-model="unifiedRating.classPerformance" />
            </div>
            <div class="rating-item">
              <span class="rating-label">学习态度（未接入）：</span>
              <el-rate v-model="unifiedRating.learningAttitude" disabled />
            </div>
          </div>
          <div class="rating-row">
            <div class="rating-item">
              <span class="rating-label">动作技巧（未接入）：</span>
              <el-rate v-model="unifiedRating.skillLevel" disabled />
            </div>
            <div class="rating-item">
              <span class="rating-label">跟课巩固（作业）：</span>
              <el-rate v-model="unifiedRating.consolidation" />
            </div>
          </div>
        </div>

        <!-- 统一评价内容 -->
        <div class="evaluate-content">
          <el-tabs v-model="unifiedContentTab">
            <el-tab-pane label="AI点评" name="ai">
              <el-input
                v-model="unifiedComment"
                type="textarea"
                :rows="4"
                placeholder="请输入评价"
                maxlength="500"
                show-word-limit
              />
            </el-tab-pane>
            <el-tab-pane label="常用评语" name="common">
              <div class="common-comments">
                <el-tag
                  v-for="comment in commonComments"
                  :key="comment"
                  class="comment-tag"
                  @click="addUnifiedComment(comment)"
                >
                  {{ comment }}
                </el-tag>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 媒体上传 -->
          <div class="media-upload">
            <div class="upload-item">
              <el-icon><Microphone /></el-icon>
              <span>录音</span>
            </div>
            <div class="upload-item">
              <el-icon><Headset /></el-icon>
              <span>音频</span>
            </div>
            <div class="upload-item">
              <el-icon><Picture /></el-icon>
              <span>图片</span>
            </div>
            <div class="upload-item">
              <el-icon><VideoCamera /></el-icon>
              <span>视频</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分开评价模式 - 学员评价列表 -->
      <div v-else class="student-evaluate-list">
        <div v-for="(student, index) in studentList" :key="student.id" class="student-evaluate-item">
          <div class="student-header">
            <div class="student-info">
              <el-avatar :size="40" :src="student.avatar">{{ (student.studentName || '').charAt(0) }}</el-avatar>
              <div class="student-detail">
                <div class="student-name">{{ student.studentName }}</div>
                <el-tag v-if="student.tag" size="small">{{ student.tag }}</el-tag>
                <div class="student-meta">{{ student.meta }}</div>
              </div>
            </div>
            <el-button type="text" class="skip-btn" @click="handleSkipStudent(index)">暂不评价ta</el-button>
          </div>

          <!-- 评分区域 -->
          <div class="rating-area">
            <div class="rating-row">
              <div class="rating-item">
                <span class="rating-label">课堂表现：</span>
                <el-rate v-model="student.classPerformance" />
              </div>
              <div class="rating-item">
                <span class="rating-label">学习态度（未接入）：</span>
                <el-rate v-model="student.learningAttitude" disabled />
              </div>
            </div>
            <div class="rating-row">
              <div class="rating-item">
                <span class="rating-label">动作技巧（未接入）：</span>
                <el-rate v-model="student.skillLevel" disabled />
              </div>
              <div class="rating-item">
                <span class="rating-label">跟课巩固（作业）：</span>
                <el-rate v-model="student.consolidation" />
              </div>
            </div>
          </div>

          <!-- 评价内容 -->
          <div class="evaluate-content">
            <el-tabs v-model="student.contentTab">
              <el-tab-pane label="AI点评" name="ai">
                <el-input
                  v-model="student.aiComment"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入评价"
                  maxlength="500"
                  show-word-limit
                />
              </el-tab-pane>
              <el-tab-pane label="常用评语" name="common">
                <div class="common-comments">
                  <el-tag
                    v-for="comment in commonComments"
                    :key="comment"
                    class="comment-tag"
                    @click="addCommonComment(student, comment)"
                  >
                    {{ comment }}
                  </el-tag>
                </div>
              </el-tab-pane>
            </el-tabs>

            <!-- 媒体上传 -->
            <div class="media-upload">
              <div class="upload-item">
                <el-icon><Microphone /></el-icon>
                <span>录音</span>
              </div>
              <div class="upload-item">
                <el-icon><Headset /></el-icon>
                <span>音频</span>
              </div>
              <div class="upload-item">
                <el-icon><Picture /></el-icon>
                <span>图片</span>
              </div>
              <div class="upload-item">
                <el-icon><VideoCamera /></el-icon>
                <span>视频</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup name="Evaluate">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAttendanceRecord } from '@/api/assistant/classRecord'
import { addComment, batchComment, listPendingCommentStudents } from '@/api/teach/comment'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const submitting = ref(false)

// 评价模式
const evaluateMode = ref('unified')

// 选中的模板（评价模板暂未接入后端）
const selectedTemplate = ref('dance')

// 课次信息（来自 /teach/class-record/attendance/{id}）
const classInfo = ref({})

// 待点评学员列表（来自 /teach/comment/pending）
const studentList = ref([])

// 统一评价 - 评分
const unifiedRating = ref({
  classPerformance: 0,
  learningAttitude: 0,
  skillLevel: 0,
  consolidation: 0
})

// 统一评价 - 内容Tab
const unifiedContentTab = ref('ai')

// 统一评价 - 评价内容
const unifiedComment = ref('')

// 常用评语
const commonComments = ref([
  '表现优秀',
  '积极主动',
  '需要加强',
  '进步明显',
  '认真听讲',
  '课堂活跃'
])

// 计算学员名称列表
const studentNames = computed(() => {
  return studentList.value.map(s => s.studentName).join('、')
})

// 添加常用评语（分开评价）
function addCommonComment(student, comment) {
  if (student.aiComment) {
    student.aiComment += '，' + comment
  } else {
    student.aiComment = comment
  }
}

// 添加常用评语（统一评价）
function addUnifiedComment(comment) {
  if (unifiedComment.value) {
    unifiedComment.value += '，' + comment
  } else {
    unifiedComment.value = comment
  }
}

// 暂不评价某个学员
function handleSkipStudent(index) {
  studentList.value.splice(index, 1)
}

// 返回上一页
function goBack() {
  router.back()
}

/** 加载课次信息和待点评学员 */
function loadData() {
  const attendanceId = route.params.id
  if (!attendanceId) {
    return
  }
  const selectedIds = String(route.query.studentIds || '')
    .split(',')
    .filter(Boolean)
  loading.value = true
  Promise.all([getAttendanceRecord(attendanceId), listPendingCommentStudents(attendanceId)])
    .then(([recordRes, pendingRes]) => {
      classInfo.value = recordRes.data || {}
      const pending = pendingRes.data || []
      const matched = pending.filter(item => selectedIds.includes(String(item.studentId)))
      // 传入的学员ID与待点评名单匹配不上时，展示该课次全部待点评学员
      const source = matched.length ? matched : pending
      studentList.value = source.map(item => ({
        ...item,
        id: item.studentId,
        avatar: '',
        tag: item.attendanceStatusName,
        meta: '',
        classPerformance: 0,
        learningAttitude: 0,
        skillLevel: 0,
        consolidation: 0,
        contentTab: 'ai',
        aiComment: ''
      }))
    })
    .finally(() => {
      loading.value = false
    })
}

// 提交评价：统一评价调用 /teach/comment/batch，分开评价逐个调用 /teach/comment
function handleSubmit() {
  if (!studentList.value.length) {
    ElMessage.warning('没有可点评的学员')
    return
  }
  const attendanceId = Number(route.params.id)
  if (evaluateMode.value === 'unified') {
    if (!unifiedRating.value.classPerformance || !unifiedRating.value.consolidation) {
      ElMessage.warning('请完成课堂表现和跟课巩固评分')
      return
    }
    if (!unifiedComment.value) {
      ElMessage.warning('请输入评价内容')
      return
    }
    submitting.value = true
    batchComment({
      attendanceId,
      classId: classInfo.value.classId,
      studentIds: studentList.value.map(s => s.studentId),
      performanceScore: unifiedRating.value.classPerformance,
      homeworkScore: unifiedRating.value.consolidation,
      commentContent: unifiedComment.value,
      commentType: 'unified'
    })
      .then(res => {
        ElMessage.success(res.msg || '点评发布成功')
        router.back()
      })
      .finally(() => {
        submitting.value = false
      })
    return
  }

  const unrated = studentList.value.filter(s => !s.classPerformance || !s.consolidation || !s.aiComment)
  if (unrated.length > 0) {
    ElMessage.warning('请完成所有学员的评分和评价内容')
    return
  }
  submitting.value = true
  const tasks = studentList.value.map(student =>
    addComment({
      attendanceId,
      attendanceDetailId: student.attendanceDetailId,
      classId: student.classId,
      studentId: student.studentId,
      studentName: student.studentName,
      performanceScore: student.classPerformance,
      homeworkScore: student.consolidation,
      commentContent: student.aiComment,
      commentType: 'single'
    })
      .then(() => ({ ok: true }))
      .catch(() => ({ ok: false, name: student.studentName }))
  )
  Promise.all(tasks)
    .then(results => {
      const failed = results.filter(item => !item.ok)
      if (failed.length) {
        ElMessage.error(`以下学员点评发布失败：${failed.map(item => item.name).join('、')}`)
        loadData()
        return
      }
      ElMessage.success('点评发布成功')
      router.back()
    })
    .finally(() => {
      submitting.value = false
    })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.evaluate-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px 20px;
    background-color: #fff;
    border-radius: 4px;

    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .course-info-card {
    margin-bottom: 20px;

    h3 {
      margin: 0 0 15px 0;
      font-size: 16px;
      color: #303133;
    }

    .info-item {
      line-height: 28px;
      color: #606266;
      font-size: 14px;
    }
  }

  .evaluate-card {
    h3 {
      margin: 0 0 20px 0;
      font-size: 16px;
      color: #303133;

      .student-count {
        font-size: 14px;
        color: #909399;
        font-weight: normal;
      }
    }

    .evaluate-tabs {
      margin-bottom: 20px;
    }

    .template-selector {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 30px;

      .template-link {
        color: #ff9800;
      }
    }

    // 统一评价模式
    .unified-evaluate {
      .selected-students {
        padding: 15px;
        background-color: #f5f7fa;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 14px;
        color: #606266;

        .student-names {
          color: #303133;
          font-weight: 500;
        }
      }

      .rating-area {
        margin-bottom: 20px;

        .rating-row {
          display: flex;
          gap: 60px;
          margin-bottom: 15px;

          .rating-item {
            display: flex;
            align-items: center;
            gap: 10px;

            .rating-label {
              color: #606266;
              font-size: 14px;
              white-space: nowrap;
            }
          }
        }
      }

      .evaluate-content {
        .common-comments {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          padding: 10px 0;

          .comment-tag {
            cursor: pointer;

            &:hover {
              background-color: #ecf5ff;
              border-color: #409eff;
            }
          }
        }

        .media-upload {
          display: flex;
          gap: 40px;
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #ebeef5;

          .upload-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            color: #909399;
            font-size: 14px;

            &:hover {
              color: #409eff;
            }

            .el-icon {
              font-size: 24px;
            }
          }
        }
      }
    }

    .student-evaluate-list {
      .student-evaluate-item {
        border: 1px solid #ebeef5;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;

        .student-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;

          .student-info {
            display: flex;
            align-items: center;
            gap: 12px;

            .student-detail {
              .student-name {
                font-size: 16px;
                font-weight: 500;
                color: #303133;
                margin-bottom: 4px;
                display: flex;
                align-items: center;
                gap: 8px;
              }

              .student-meta {
                font-size: 12px;
                color: #909399;
                margin-top: 4px;
              }
            }
          }

          .skip-btn {
            color: #ff9800;
          }
        }

        .rating-area {
          margin-bottom: 20px;

          .rating-row {
            display: flex;
            gap: 60px;
            margin-bottom: 15px;

            .rating-item {
              display: flex;
              align-items: center;
              gap: 10px;

              .rating-label {
                color: #606266;
                font-size: 14px;
                white-space: nowrap;
              }
            }
          }
        }

        .evaluate-content {
          .common-comments {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding: 10px 0;

            .comment-tag {
              cursor: pointer;
              
              &:hover {
                background-color: #ecf5ff;
                border-color: #409eff;
              }
            }
          }

          .media-upload {
            display: flex;
            gap: 40px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ebeef5;

            .upload-item {
              display: flex;
              flex-direction: column;
              align-items: center;
              gap: 5px;
              cursor: pointer;
              color: #909399;
              font-size: 14px;

              &:hover {
                color: #409eff;
              }

              .el-icon {
                font-size: 24px;
              }
            }
          }
        }
      }
    }
  }
}
</style>

