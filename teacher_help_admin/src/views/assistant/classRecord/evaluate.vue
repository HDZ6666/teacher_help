<template>
  <div class="app-container evaluate-page">
    <!-- 头部 -->
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" @click="goBack">评价学员</el-button>
      <div class="header-actions">
        <el-button>保存草稿</el-button>
        <el-button type="warning" @click="handleSubmit">发送</el-button>
      </div>
    </div>

    <!-- 课次信息 -->
    <el-card class="course-info-card">
      <h3>课次信息</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="info-item">托展训练周六9:00——10:00</div>
          <div class="info-item">上课时间：{{ classInfo.classTime }}</div>
          <div class="info-item">上课老师：{{ classInfo.teacher }}</div>
          <div class="info-item">上课内容：</div>
        </el-col>
        <el-col :span="12">
          <div class="info-item">所属班级：{{ classInfo.className }}</div>
          <div class="info-item">点名时间：{{ classInfo.attendanceTime }}</div>
          <div class="info-item">点名老师：{{ classInfo.attendanceTeacher }}</div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 写评价 -->
    <el-card class="evaluate-card">
      <h3>写评价 <span class="student-count">(给{{ studentList.length }}个学员)</span></h3>

      <!-- Tab切换 -->
      <el-tabs v-model="evaluateMode" class="evaluate-tabs">
        <el-tab-pane label="分开评价学员" name="separate"></el-tab-pane>
        <el-tab-pane label="统一评价学员" name="unified"></el-tab-pane>
      </el-tabs>

      <!-- 评价模板选择 -->
      <div class="template-selector">
        <span>评价模板：</span>
        <el-select v-model="selectedTemplate" placeholder="舞蹈" style="width: 200px">
          <el-option label="舞蹈" value="dance" />
          <el-option label="体育" value="sports" />
          <el-option label="美术" value="art" />
        </el-select>
        <el-button type="text" class="template-link">设置评价模板</el-button>
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
              <span class="rating-label">学习态度：</span>
              <el-rate v-model="unifiedRating.learningAttitude" />
            </div>
          </div>
          <div class="rating-row">
            <div class="rating-item">
              <span class="rating-label">动作技巧：</span>
              <el-rate v-model="unifiedRating.skillLevel" />
            </div>
            <div class="rating-item">
              <span class="rating-label">跟课巩固：</span>
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
              <el-avatar :size="40" :src="student.avatar">{{ student.studentName.charAt(0) }}</el-avatar>
              <div class="student-detail">
                <div class="student-name">{{ student.studentName }}</div>
                <el-tag v-if="student.tag" size="small">{{ student.tag }}</el-tag>
                <div class="student-meta">{{ student.meta }}</div>
              </div>
            </div>
            <el-button type="text" class="skip-btn">暂不评价ta</el-button>
          </div>

          <!-- 评分区域 -->
          <div class="rating-area">
            <div class="rating-row">
              <div class="rating-item">
                <span class="rating-label">课堂表现：</span>
                <el-rate v-model="student.classPerformance" />
              </div>
              <div class="rating-item">
                <span class="rating-label">学习态度：</span>
                <el-rate v-model="student.learningAttitude" />
              </div>
            </div>
            <div class="rating-row">
              <div class="rating-item">
                <span class="rating-label">动作技巧：</span>
                <el-rate v-model="student.skillLevel" />
              </div>
              <div class="rating-item">
                <span class="rating-label">跟课巩固：</span>
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

const route = useRoute()
const router = useRouter()

// 评价模式
const evaluateMode = ref('unified')

// 选中的模板
const selectedTemplate = ref('dance')

// 课次信息
const classInfo = ref({
  classTime: '2025-11-03 10:00 - 11:30',
  teacher: '叶老师',
  className: '拓展训练班',
  attendanceTime: '2025-11-05 14:53',
  attendanceTeacher: '黄老师'
})

// 学员列表
const studentList = ref([
  {
    id: 1,
    studentName: '宁宁',
    avatar: '',
    tag: '刷新',
    meta: '',
    classPerformance: 0,
    learningAttitude: 0,
    skillLevel: 0,
    consolidation: 0,
    contentTab: 'ai',
    aiComment: ''
  },
  {
    id: 2,
    studentName: '西西',
    avatar: '',
    tag: '刷新',
    meta: '未到2次后，无法发送到家长端',
    classPerformance: 0,
    learningAttitude: 0,
    skillLevel: 0,
    consolidation: 0,
    contentTab: 'ai',
    aiComment: ''
  }
])

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

// 返回上一页
function goBack() {
  router.back()
}

// 提交评价
function handleSubmit() {
  if (evaluateMode.value === 'unified') {
    // 统一评价模式验证
    if (!unifiedRating.value.classPerformance || !unifiedRating.value.learningAttitude ||
        !unifiedRating.value.skillLevel || !unifiedRating.value.consolidation) {
      ElMessage.warning('请完成所有评分项')
      return
    }
    if (!unifiedComment.value) {
      ElMessage.warning('请输入评价内容')
      return
    }
  } else {
    // 分开评价模式验证
    const unrated = studentList.value.filter(s =>
      !s.classPerformance || !s.learningAttitude || !s.skillLevel || !s.consolidation || !s.aiComment
    )

    if (unrated.length > 0) {
      ElMessage.warning('请完成所有学员的评价')
      return
    }
  }

  ElMessage.success('评价提交成功')
  // TODO: 调用API提交评价
  setTimeout(() => {
    router.back()
  }, 1000)
}

// 组件挂载时获取数据
onMounted(() => {
  const recordId = route.params.id
  const studentIds = route.query.studentIds
  console.log('课程ID:', recordId)
  console.log('学员IDs:', studentIds)
  // TODO: 根据ID获取课程和学员数据
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

