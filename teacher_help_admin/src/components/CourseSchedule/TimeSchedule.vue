<template>
  <div class="time-schedule" :style="{ height: height }">
    <!-- 左上角空白占位，显示"时间" -->
    <div class="corner-cell">
      <div class="corner-label">时间</div>
      <!-- 底部显示当前滚动位置对应的时间 -->
      <div class="corner-time">{{ currentScrollTime }}</div>
    </div>

    <!-- 星期表头（固定顶部） -->
    <div class="week-header" ref="weekHeader">
      <div class="week-header-inner" :style="{ width: totalWidth + 'px' }">
        <div
          v-for="day in displayDates"
          :key="day.value"
          class="week-header-cell"
          :class="{ 'is-today': day.isToday }"
          :style="{
            width: actualColumnWidths[day.value] + 'px',
            left: columnPositions[day.value] + 'px'
          }"
        >
          <div class="week-day-name">{{ day.label }}</div>
          <div class="week-day-date">{{ day.date }}</div>
        </div>
      </div>
    </div>

    <!-- 主内容区域（可滚动） -->
    <div class="schedule-main" ref="scheduleMain">
      <div class="schedule-content" :style="{ width: (80 + totalWidth) + 'px' }">
        <!-- 时间轴列（固定左侧，但跟随垂直滚动） -->
        <div class="time-column">
          <div
            v-for="hour in 24"
            :key="hour"
            class="time-cell"
            :style="{ height: cellHeight + 'px' }"
          >
            <!-- 时间标签显示在单元格底部边框上 -->
            <span class="time-label-bottom">
              {{ formatHour(hour) }}
            </span>
          </div>
        </div>

        <!-- 课程网格容器 -->
        <div class="schedule-grid" :style="{ width: totalWidth + 'px', height: (24 * cellHeight) + 'px' }">
          <!-- 背景网格线 -->
          <div class="grid-background">
            <div
              v-for="day in displayDates"
              :key="`col-${day.value}`"
              class="grid-column"
              :class="{ 'is-today': day.isToday }"
              :style="{
                width: actualColumnWidths[day.value] + 'px',
                left: columnPositions[day.value] + 'px'
              }"
            >
              <div
                v-for="hour in 24"
                :key="`cell-${day.value}-${hour}`"
                class="grid-cell"
                :style="{ height: cellHeight + 'px' }"
              ></div>
            </div>
          </div>

          <!-- 课程卡片层 -->
          <div class="courses-layer" :style="{
            height: (24 * cellHeight) + 'px',
            width: totalWidth + 'px'
          }">
            <el-popover
              v-for="course in processedCourses"
              :key="course.id"
              placement="right"
              :width="320"
              trigger="hover"
              :show-after="200"
              popper-class="course-detail-popover"
            >
              <template #reference>
                <div
                  class="course-card"
                  :style="getCourseStyle(course)"
                  @click="handleCourseCardClick(course)"
                >
                  <div class="course-time">{{ course.timeRange }}</div>
                  <div class="course-name">{{ course.name }}</div>
                  <div class="course-info" v-if="course.teacher">
                    <div>{{ course.teacher }}</div>
                    <div v-if="course.classroom">{{ course.classroom }}</div>
                  </div>
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TimeSchedule',
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
    // 每小时单元格高度（像素）
    cellHeight: {
      type: Number,
      default: 60
    },
    // 视图模式：'day' | 'week'
    viewMode: {
      type: String,
      default: 'week',
      validator: (value) => ['day', 'week'].includes(value)
    },
    // 日期数组
    // 日视图：传入1个日期 ['2025-11-07']
    // 周视图：传入7个日期 ['2025-11-03', '2025-11-04', ...]
    dates: {
      type: Array,
      default: null
    },
    // 起始日期（兼容旧版本）
    startDate: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      // 当前滚动位置对应的时间
      currentScrollTime: '00:00',
      // 容器宽度（用于计算最小宽度）
      containerWidth: 0
    };
  },
  computed: {
    // 显示的日期数组
    displayDates() {
      // 优先使用 dates 参数
      if (this.dates && this.dates.length > 0) {
        return this.dates.map((dateStr, index) => {
          const date = new Date(dateStr.replace(/\//g, '-'));
          date.setHours(0, 0, 0, 0);
          return this.formatDateObject(date, index);
        });
      }

      // 根据视图模式生成日期
      if (this.viewMode === 'day') {
        return this.generateDayDate();
      } else {
        return this.generateWeekDates();
      }
    },

    // 星期几到列号的映射（1-7 对应周一到周日）
    weekDays() {
      const days = {};
      this.displayDates.forEach(day => {
        days[day.dayOfWeek] = day;
      });
      return days;
    },

    // 日期字符串到列号的映射
    dateToColumnMap() {
      const map = {};
      this.displayDates.forEach(day => {
        map[day.fullDate] = day.dayOfWeek;
      });
      return map;
    },

    // 处理后的课程数据（添加位置、尺寸等信息）
    processedCourses() {
      return this.courses
        .filter(course => {
          // 过滤出在显示日期范围内的课程
          const courseDate = course.date ? course.date.replace(/\//g, '-') : null;
          return courseDate && this.dateToColumnMap[courseDate];
        })
        .map(course => {
          const startMinutes = this.timeToMinutes(course.startTime);
          const endMinutes = this.timeToMinutes(course.endTime);
          const duration = endMinutes - startMinutes;
          const courseDate = course.date.replace(/\//g, '-');
          const dayOfWeek = this.dateToColumnMap[courseDate];

          return {
            ...course,
            startMinutes,
            endMinutes,
            duration,
            dayOfWeek,
            timeRange: `${course.startTime}-${course.endTime}`
          };
        });
    },

    // 计算每天同一时间段的最大课程数（用于确定列宽）
    maxCoursesPerDay() {
      const maxCourses = {};
      
      // 初始化每天的最大课程数为1
      for (let i = 1; i <= 7; i++) {
        maxCourses[i] = 1;
      }

      // 按天分组课程
      const coursesByDay = {};
      this.processedCourses.forEach(course => {
        if (!coursesByDay[course.dayOfWeek]) {
          coursesByDay[course.dayOfWeek] = [];
        }
        coursesByDay[course.dayOfWeek].push(course);
      });

      // 计算每天的最大并发课程数
      Object.keys(coursesByDay).forEach(dayOfWeek => {
        const courses = coursesByDay[dayOfWeek];
        let max = 1;

        // 检查每个时间点的课程数
        for (let i = 0; i < courses.length; i++) {
          let concurrent = 1;
          const current = courses[i];

          for (let j = 0; j < courses.length; j++) {
            if (i !== j) {
              const other = courses[j];
              // 检查时间是否重叠
              if (current.startMinutes < other.endMinutes && current.endMinutes > other.startMinutes) {
                concurrent++;
              }
            }
          }

          max = Math.max(max, concurrent);
        }

        maxCourses[dayOfWeek] = max;
      });

      return maxCourses;
    },

    // 计算每列的宽度（单位：px）
    columnWidths() {
      const widths = {};
      const courseWidth = 150; // 每个课程卡片宽度
      const gap = 10; // 课程之间的间距
      const padding = 50; // 额外留白

      // 根据实际显示的日期数量来计算
      this.displayDates.forEach(day => {
        const dayOfWeek = day.dayOfWeek;
        const maxCourses = this.maxCoursesPerDay[dayOfWeek] || 1;
        // 宽度 = 课程数 × 课程宽度 + (课程数 - 1) × 间距 + 留白
        const width = maxCourses * courseWidth + (maxCourses - 1) * gap + padding;
        widths[dayOfWeek] = width;
        widths[day.value] = width; // 同时使用 value 作为键
      });

      return widths;
    },

    // 计算总宽度
    totalWidth() {
      let total = 0;
      // 只累加实际显示的列
      this.displayDates.forEach(day => {
        total += this.columnWidths[day.dayOfWeek] || 0;
      });
      
      // 确保总宽度至少是容器宽度（减去时间轴的80px）
      const minWidth = this.containerWidth > 0 ? this.containerWidth - 80 : 0;
      return Math.max(total, minWidth);
    },

    // 计算实际每列的宽度（考虑容器最小宽度后的调整）
    actualColumnWidths() {
      const widths = { ...this.columnWidths };

      // 计算原始总宽度
      let originalTotal = 0;
      this.displayDates.forEach(day => {
        originalTotal += widths[day.dayOfWeek] || 0;
      });

      // 如果原始总宽度小于容器宽度，需要按比例扩展每列
      const minWidth = this.containerWidth > 0 ? this.containerWidth - 80 : 0;
      if (originalTotal < minWidth && originalTotal > 0) {
        const scale = minWidth / originalTotal;
        this.displayDates.forEach(day => {
          const dayOfWeek = day.dayOfWeek;
          const scaledWidth = Math.floor(widths[dayOfWeek] * scale);
          widths[dayOfWeek] = scaledWidth;
          widths[day.value] = scaledWidth; // 同时使用 value 作为键
        });
      }

      return widths;
    },

    // 计算每列的起始位置
    columnPositions() {
      const positions = {};
      let currentPos = 0;

      // 按照 displayDates 的顺序计算位置，使用实际宽度
      this.displayDates.forEach(day => {
        const dayOfWeek = day.dayOfWeek;
        positions[dayOfWeek] = currentPos;
        positions[day.value] = currentPos; // 同时使用 value 作为键
        currentPos += this.actualColumnWidths[dayOfWeek] || 0;
      });

      return positions;
    }
  },

  mounted() {
    this.$nextTick(() => {
      const scheduleMain = this.$refs.scheduleMain;
      if (scheduleMain) {
        scheduleMain.addEventListener('scroll', this.handleScroll);
        // 获取容器宽度
        this.updateContainerWidth();
      }

      // 监听窗口大小变化
      window.addEventListener('resize', this.handleResize);
    });
  },

  beforeUnmount() {
    const scheduleMain = this.$refs.scheduleMain;
    if (scheduleMain) {
      scheduleMain.removeEventListener('scroll', this.handleScroll);
    }
    window.removeEventListener('resize', this.handleResize);
  },

  methods: {
    // 格式化日期对象为统一格式
    formatDateObject(date, index) {
      const weekLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      const dayOfWeek = date.getDay(); // 0-6 (周日-周六)
      const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 转换为 0-6 (周一-周日)

      // 判断是否为今天
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const isToday = date.getTime() === today.getTime();

      return {
        value: index + 1,
        label: weekLabels[adjustedDay],
        date: `${date.getMonth() + 1}/${String(date.getDate()).padStart(2, '0')}`,
        fullDate: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
        dayOfWeek: dayOfWeek === 0 ? 7 : dayOfWeek, // 1-7 (周一-周日)
        dateObj: date,
        isToday: isToday
      };
    },

    // 生成日视图日期（1天）
    generateDayDate() {
      let date;
      if (this.startDate) {
        date = new Date(this.startDate.replace(/\//g, '-'));
      } else {
        date = new Date();
      }
      date.setHours(0, 0, 0, 0);
      return [this.formatDateObject(date, 0)];
    },

    // 生成周视图日期（7天）
    generateWeekDates() {
      const days = [];
      let startDate;

      if (this.startDate) {
        startDate = new Date(this.startDate.replace(/\//g, '-'));
      } else {
        // 默认使用当前周的周一
        startDate = new Date();
        const dayOfWeek = startDate.getDay();
        const diff = startDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
        startDate.setDate(diff);
      }

      startDate.setHours(0, 0, 0, 0);

      for (let i = 0; i < 7; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        days.push(this.formatDateObject(date, i));
      }

      return days;
    },

    // 格式化小时显示（00:00 格式）
    formatHour(hour) {
      return `${String(hour).padStart(2, '0')}:00`;
    },

    // 将时间字符串转换为分钟数（从00:00开始）
    timeToMinutes(timeStr) {
      if (!timeStr) return 0;
      const [hours, minutes] = timeStr.split(':').map(Number);
      return hours * 60 + minutes;
    },

    // 获取课程卡片的样式
    getCourseStyle(course) {
      const top = (course.startMinutes / 60) * this.cellHeight;
      const height = (course.duration / 60) * this.cellHeight;
      const left = this.columnPositions[course.dayOfWeek] || 0;

      // 计算该时间段内有多少并发课程
      const concurrentCourses = this.processedCourses.filter(c =>
        c.dayOfWeek === course.dayOfWeek &&
        c.startMinutes < course.endMinutes &&
        c.endMinutes > course.startMinutes
      );

      // 按开始时间排序，确定当前课程的索引
      concurrentCourses.sort((a, b) => a.startMinutes - b.startMinutes || a.id - b.id);
      const index = concurrentCourses.findIndex(c => c.id === course.id);

      // 固定课程卡片宽度为150px
      const cardWidth = 150;
      const gap = 10; // 课程之间的间距
      const leftOffset = left + 10 + (index * (cardWidth + gap)); // 10px 是左padding

      return {
        top: `${top}px`,
        height: `${height}px`,
        left: `${leftOffset}px`,
        width: `${cardWidth}px`,
        backgroundColor: course.color || '#5DADE2',
        position: 'absolute',
        zIndex: 10
      };
    },

    // 处理滚动事件，同步表头和更新时间显示
    handleScroll(e) {
      const scrollLeft = e.target.scrollLeft;
      const scrollTop = e.target.scrollTop;

      // 同步表头的水平滚动
      const weekHeaderInner = this.$el.querySelector('.week-header-inner');
      if (weekHeaderInner) {
        weekHeaderInner.style.transform = `translateX(-${scrollLeft}px)`;
      }

      // 根据垂直滚动距离计算当前时间
      this.updateScrollTime(scrollTop);
    },

    // 根据滚动距离更新时间显示
    updateScrollTime(scrollTop) {
      const totalMinutes = (scrollTop / this.cellHeight) * 60;
      const hours = Math.floor(totalMinutes / 60);
      const minutes = Math.floor(totalMinutes % 60);
      this.currentScrollTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    },

    // 更新容器宽度
    updateContainerWidth() {
      const scheduleMain = this.$refs.scheduleMain;
      if (scheduleMain) {
        this.containerWidth = scheduleMain.clientWidth;
      }
    },

    // 处理窗口大小变化
    handleResize() {
      this.updateContainerWidth();
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
.time-schedule {
  position: relative;
  display: grid;
  grid-template-columns: 80px 1fr;
  grid-template-rows: 60px 1fr;
  overflow: hidden;
  background-color: #fff;
  border: 1px solid #e0e0e0;
}

/* 左上角占位单元格 */
.corner-cell {
  grid-column: 1;
  grid-row: 1;
  background-color: #f5f7fa;
  border-right: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #606266;
  position: relative;
  z-index: 100;
}

.corner-label {
  font-size: 14px;
}

/* 左上角底部的时间显示 */
.corner-time {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translate(-50%, 50%);
  background-color: #f5f7fa;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: #409EFF;
  white-space: nowrap;
  z-index: 60;
  z-index: 1;
}

/* 星期表头（固定顶部，可水平滚动） */
.week-header {
  grid-column: 2;
  grid-row: 1;
  overflow: hidden;
  position: relative;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e0e0e0;
  z-index: 20;
}

.week-header-inner {
  position: relative;
  height: 100%;
  transition: transform 0.05s ease-out;
}

.week-header-cell {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e0e0e0;
  box-sizing: border-box;
}

/* 当天的表头样式 */
.week-header-cell.is-today {
  background-color: #ecf5ff;
}

.week-header-cell.is-today .week-day-name {
  color: #409EFF;
}

.week-header-cell.is-today .week-day-date {
  color: #409EFF;
  font-weight: 600;
}

.week-day-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.week-day-date {
  font-size: 12px;
  color: #909399;
}

/* 主内容区域（可滚动） */
.schedule-main {
  grid-column: 1 / -1;
  grid-row: 2;
  overflow: auto;
  position: relative;
}

.schedule-content {
  position: relative;
  min-height: 100%;
}

/* 时间轴列（固定左侧） */
.time-column {
  position: sticky;
  left: 0;
  width: 80px;
  background-color: #fafafa;
  border-right: 1px solid #e0e0e0;
  z-index: 50;
  float: left;
}

.time-cell {
  position: relative;
  border-bottom: 1px solid #e0e0e0;
  box-sizing: border-box;
}

/* 时间标签显示在单元格底部边框上 */
.time-label-bottom {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translate(-50%, 50%);
  background-color: #fafafa;
  padding: 0 8px;
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

/* 课程网格容器 */
.schedule-grid {
  position: relative;
  margin-left: 80px;
  height: 100%;
}

/* 背景网格线 */
.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.grid-column {
  position: absolute;
  top: 0;
  height: 100%;
  border-right: 1px solid #e0e0e0;
  box-sizing: border-box;
}

/* 当天的网格列背景色 */
.grid-column.is-today {
  background-color: #f0f9ff;
}

.grid-cell {
  border-bottom: 1px solid #f0f0f0;
  box-sizing: border-box;
}

/* 课程卡片层 */
.courses-layer {
  position: relative;
  pointer-events: none;
}

.course-card {
  pointer-events: auto;
  border-radius: 4px;
  padding: 8px;
  color: #fff;
  font-size: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s, transform 0.2s;
}

.course-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
  z-index: 40 !important;
}

.course-time {
  font-size: 11px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.course-name {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-info {
  font-size: 11px;
  opacity: 0.85;
  line-height: 1.4;
}

.course-info div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
</style>


