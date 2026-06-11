<template>
  <div class="month-schedule" :style="{ height: height }">
    <!-- 星期表头 -->
    <div class="month-header">
      <div class="month-header-cell" v-for="label in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']" :key="label">
        {{ label }}
      </div>
    </div>

    <!-- 日期网格 -->
    <div class="month-grid">
      <div
        v-for="day in displayDates"
        :key="day.fullDate"
        class="month-day-cell"
        :class="{
          'other-month': !day.isCurrentMonth,
          'is-today': day.isToday
        }"
      >
        <div class="month-day-header">
          <span class="month-day-number">{{ day.dateObj.getDate() }}</span>
        </div>
        <div class="month-day-courses">
          <!-- 课程列表 -->
          <template v-for="(course, index) in getDisplayCoursesForDate(day.fullDate)" :key="course.id">
            <el-popover
              v-if="index < 3"
              placement="right"
              :width="320"
              trigger="hover"
              :show-after="200"
              popper-class="course-detail-popover"
            >
              <template #reference>
                <div
                  class="month-course-item"
                  :style="{ backgroundColor: course.color || '#5DADE2' }"
                  @click="handleCourseCardClick(course)"
                >
                  <div class="month-course-time">{{ course.timeRange }}</div>
                  <div class="month-course-name">{{ course.name }}</div>
                </div>
              </template>

              <!-- Popover 内容 -->
              <div class="course-detail">
                <div class="detail-header">
                  <div class="detail-title">{{ course.name }}</div>
                  <div class="detail-time">{{ course.date }} {{ course.timeRange }}</div>
                </div>

                <div class="detail-body">
                  <div class="detail-item">
                    <span class="detail-label">授课课程：</span>
                    <span class="detail-value">{{ course.courseName || course.name }}</span>
                  </div>

                  <div class="detail-item">
                    <span class="detail-label">上课老师：</span>
                    <span class="detail-value">{{ course.teacher || '-' }}</span>
                  </div>

                  <div class="detail-item">
                    <span class="detail-label">上课教室：</span>
                    <span class="detail-value">{{ course.classroom || '-' }}</span>
                  </div>

                  <div class="detail-item">
                    <span class="detail-label">上课人数：</span>
                    <span class="detail-value">{{ course.studentCount || course.students || '-' }}</span>
                  </div>

                  <div class="detail-item">
                    <span class="detail-label">学生：</span>
                    <span class="detail-value detail-students" :title="course.studentNames || course.studentList">
                      {{ course.studentNames || course.studentList || '-' }}
                    </span>
                  </div>
                </div>

                <div class="detail-footer">
                  <el-button type="primary" size="small" link @click="handleViewDetail(course)">详情</el-button>
                  <el-button type="warning" size="small" link @click="handleReschedule(course)">调课</el-button>
                  <el-button type="danger" size="small" link @click="handleDelete(course)">删除</el-button>
                </div>
              </div>
            </el-popover>
          </template>

          <!-- 查看更多按钮 -->
          <el-popover
            v-if="getCoursesForDate(day.fullDate).length > 3"
            placement="right"
            :width="320"
            trigger="hover"
            :show-after="200"
            popper-class="course-list-popover"
          >
            <template #reference>
              <div class="month-view-more">
                查看更多 ({{ getCoursesForDate(day.fullDate).length - 3 }})
              </div>
            </template>

            <!-- Popover 内容：显示所有课程列表 -->
            <div class="course-list">
              <div class="course-list-header">
                <div class="list-title">{{ day.fullDate }} 全部课程</div>
                <div class="list-count">共 {{ getCoursesForDate(day.fullDate).length }} 节课</div>
              </div>

              <div class="course-list-body">
                <div
                  v-for="course in getDisplayCoursesForDate(day.fullDate)"
                  :key="course.id"
                  class="course-list-item"
                >
                  <div class="course-list-item-header">
                    <div class="course-color-dot" :style="{ backgroundColor: course.color || '#5DADE2' }"></div>
                    <div class="course-list-name">{{ course.name }}</div>
                    <div class="course-list-time">{{ course.timeRange }}</div>
                  </div>
                  <div class="course-list-item-body">
                    <div class="course-list-info">
                      <span class="info-label">老师：</span>
                      <span class="info-value">{{ course.teacher || '-' }}</span>
                    </div>
                    <div class="course-list-info">
                      <span class="info-label">教室：</span>
                      <span class="info-value">{{ course.classroom || '-' }}</span>
                    </div>
                    <div class="course-list-info">
                      <span class="info-label">人数：</span>
                      <span class="info-value">{{ course.studentCount || course.students || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-popover>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MonthSchedule',
  props: {
    // 课程数据数组
    courses: {
      type: Array,
      default: () => []
    },
    // 组件高度
    height: {
      type: String,
      default: 'calc(100vh - 200px)'
    },
    // 月份（格式：'2025-11' 或 '2025/11'）
    month: {
      type: String,
      default: null
    }
  },
  computed: {
    // 显示的日期数组（包含上月末尾和下月开头的日期，填充完整的周）
    displayDates() {
      const dates = [];
      let targetDate;

      if (this.month) {
        const [year, month] = this.month.replace(/\//g, '-').split('-').map(Number);
        targetDate = new Date(year, month - 1, 1);
      } else {
        targetDate = new Date();
        targetDate.setDate(1);
      }

      const year = targetDate.getFullYear();
      const month = targetDate.getMonth();

      // 获取今天的日期（用于判断是否为当天）
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      // 获取当月第一天是星期几（0-6，周日-周六）
      const firstDay = new Date(year, month, 1);
      const firstDayOfWeek = firstDay.getDay();

      // 计算需要显示的上月日期数量（周一为第一天）
      const daysFromPrevMonth = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

      // 添加上月的日期
      for (let i = daysFromPrevMonth; i > 0; i--) {
        const date = new Date(year, month, 1 - i);
        dates.push({
          dateObj: date,
          fullDate: this.formatDate(date),
          isCurrentMonth: false,
          isToday: date.getTime() === today.getTime()
        });
      }

      // 添加当月的日期
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(year, month, i);
        dates.push({
          dateObj: date,
          fullDate: this.formatDate(date),
          isCurrentMonth: true,
          isToday: date.getTime() === today.getTime()
        });
      }

      // 添加下月的日期，填充到完整的周（35或42天）
      const remainingDays = 42 - dates.length;
      for (let i = 1; i <= remainingDays; i++) {
        const date = new Date(year, month + 1, i);
        dates.push({
          dateObj: date,
          fullDate: this.formatDate(date),
          isCurrentMonth: false,
          isToday: date.getTime() === today.getTime()
        });
      }

      return dates;
    }
  },
  methods: {
    // 格式化日期为 YYYY-MM-DD
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    // 获取指定日期的课程
    getCoursesForDate(dateStr) {
      return this.courses.filter(course => {
        return course.date && course.date.replace(/\//g, '-') === dateStr;
      }).sort((a, b) => {
        // 按开始时间排序
        const aTime = a.startTime || '00:00';
        const bTime = b.startTime || '00:00';
        return aTime.localeCompare(bTime);
      });
    },

    // 获取用于显示的课程（添加时间段格式）
    getDisplayCoursesForDate(dateStr) {
      const courses = this.getCoursesForDate(dateStr);
      return courses.map(course => ({
        ...course,
        timeRange: course.endTime
          ? `${course.startTime}-${course.endTime}`
          : course.startTime || ''
      }));
    },

    // 查看更多课程
    handleViewMore(dateStr) {
      const courses = this.getCoursesForDate(dateStr);
      this.$emit('view-more', { date: dateStr, courses });
    },

    // 点击课程卡片
    handleCourseCardClick(course) {
      this.$emit('view-detail', course);
    },

    // 查看课程详情
    handleViewDetail(course) {
      this.$emit('view-detail', course);
    },

    // 调课
    handleReschedule(course) {
      this.$emit('reschedule', course);
    },

    // 删除课程
    handleDelete(course) {
      this.$emit('delete', course);
    }
  }
};
</script>

<style lang="scss" scoped>
.month-schedule {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  overflow: auto;
}

/* 星期表头 */
.month-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f5f7fa;
  border-bottom: 2px solid #e0e0e0;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.month-header-cell {
  padding: 12px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  border-right: 1px solid #e0e0e0;
}

.month-header-cell:last-child {
  border-right: none;
}

/* 日期网格 */
.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: 220px;
  flex: 1;
  min-height: 0;
}

.month-day-cell {
  border-right: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px;
  display: flex;
  flex-direction: column;
  height: 220px;
  background-color: #fff;
  transition: background-color 0.2s;
  overflow: hidden;
}

.month-day-cell:hover {
  background-color: #f9f9f9;
}

/* 当天的样式 */
.month-day-cell.is-today {
  background-color: #ecf5ff;
}

.month-day-cell.is-today:hover {
  background-color: #e1f0ff;
}

.month-day-cell.is-today .month-day-number {
  background-color: #409EFF;
  color: #fff;
}

.month-day-cell.other-month {
  background-color: #fafafa;
}

.month-day-cell.other-month .month-day-number {
  color: #c0c4cc;
}

.month-day-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.month-day-number {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.month-day-courses {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.month-course-item {
  padding: 6px 8px;
  border-radius: 3px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
  display: flex;
  flex-direction: column;
  gap: 2px;
  height: 42px;
  flex-shrink: 0;
}

.month-course-item:hover {
  opacity: 0.9;
  transform: translateX(2px);
}

.month-course-time {
  font-size: 11px;
  opacity: 0.9;
  line-height: 1.2;
}

.month-course-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

/* 查看更多按钮 */
.month-view-more {
  padding: 6px 8px;
  text-align: center;
  font-size: 12px;
  color: #606266;
  background-color: transparent;
  border-radius: 3px;
  cursor: pointer;
  transition: color 0.2s;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: auto;
}

.month-view-more:hover {
  color: #409EFF;
}

/* 课程列表 Popover 样式 */
.course-list {
  .course-list-header {
    padding-bottom: 12px;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 12px;

    .list-title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 4px;
    }

    .list-count {
      font-size: 12px;
      color: #909399;
    }
  }

  .course-list-body {
    max-height: 400px;
    overflow-y: auto;

    .course-list-item {
      padding: 10px;
      border-radius: 4px;
      margin-bottom: 8px;
      background-color: #f5f7fa;
      transition: background-color 0.2s;

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        background-color: #e4e7ed;
      }

      .course-list-item-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .course-color-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .course-list-name {
          font-size: 14px;
          font-weight: 600;
          color: #303133;
          flex: 1;
        }

        .course-list-time {
          font-size: 12px;
          color: #606266;
          flex-shrink: 0;
        }
      }

      .course-list-item-body {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        padding-left: 16px;

        .course-list-info {
          font-size: 12px;
          color: #606266;

          .info-label {
            color: #909399;
          }

          .info-value {
            color: #303133;
          }
        }
      }
    }
  }
}

/* Popover 课程详情样式 */
.course-detail {
  .detail-header {
    padding-bottom: 12px;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 12px;

    .detail-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 6px;
    }

    .detail-time {
      font-size: 13px;
      color: #909399;
    }
  }

  .detail-body {
    .detail-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 10px;
      font-size: 13px;

      &:last-child {
        margin-bottom: 0;
      }

      .detail-label {
        color: #606266;
        min-width: 80px;
        flex-shrink: 0;
      }

      .detail-value {
        color: #303133;
        flex: 1;
        word-break: break-all;
      }

      .detail-students {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        word-break: normal;
        cursor: help;
      }
    }
  }

  .detail-footer {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #e4e7ed;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
}
</style>

<style>
/* Popover 全局样式（不使用 scoped） */
.course-detail-popover {
  padding: 16px !important;
}

.course-list-popover {
  padding: 16px !important;
}
</style>

