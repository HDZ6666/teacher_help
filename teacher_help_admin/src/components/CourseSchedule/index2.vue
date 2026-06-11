<template>
  <div class="course-schedule" :style="{ height: height }">
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
          v-for="day in weekDays"
          :key="day.value"
          class="week-header-cell"
          :style="{
            width: columnWidths[day.value] + 'px',
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
        <div class="schedule-grid" :style="{ width: totalWidth + 'px' }">
          <!-- 背景网格线 -->
          <div class="grid-background">
            <div
              v-for="day in weekDays"
              :key="`col-${day.value}`"
              class="grid-column"
              :style="{
                width: columnWidths[day.value] + 'px',
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
            <div
              v-for="course in processedCourses"
              :key="course.id"
              class="course-card"
              :style="getCourseStyle(course)"
            >
              <div class="course-time">{{ course.timeRange }}</div>
              <div class="course-name">{{ course.name }}</div>
              <div class="course-info" v-if="course.teacher">
                {{ course.teacher }}
              </div>
              <div class="course-info" v-if="course.classroom">
                {{ course.classroom }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseSchedule',
  data() {
    return {
      // 当前滚动位置对应的时间
      currentScrollTime: '00:00'
    };
  },
  props: {
    // 课程数据数组
    courses: {
      type: Array,
      default: () => [],
      // 每个课程对象格式：
      // {
      //   id: 1,
      //   name: '数学',
      //   startTime: '14:00', // 格式：HH:mm
      //   endTime: '19:45',
      //   date: '2025-11-03', // 课程日期（YYYY-MM-DD 或 YYYY/MM/DD 格式）
      //   dayOfWeek: 1, // (可选) 1-7 代表周一到周日，如果提供了 date 则自动计算
      //   teacher: '张老师',
      //   classroom: '教室1',
      //   color: '#5DADE2' // 可选，默认蓝色
      // }
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
    // 起始日期（周的第一天，默认为当前周的周一）
    startDate: {
      type: String,
      default: null // 格式：'2025-11-03' 或 '2025/11/03'
    }
  },
  computed: {
    // 计算周的起始日期（周一）
    weekStartDate() {
      if (this.startDate) {
        return new Date(this.startDate.replace(/\//g, '-'));
      }

      // 默认使用当前周的周一
      const today = new Date();
      const dayOfWeek = today.getDay(); // 0 (周日) 到 6 (周六)
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // 计算到周一的偏移
      const monday = new Date(today);
      monday.setDate(today.getDate() + diff);
      monday.setHours(0, 0, 0, 0);
      return monday;
    },

    // 生成星期数据（包含日期）
    weekDays() {
      const days = [];
      const weekLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

      for (let i = 0; i < 7; i++) {
        const date = new Date(this.weekStartDate);
        date.setDate(this.weekStartDate.getDate() + i);

        days.push({
          value: i + 1, // 1-7
          label: weekLabels[i],
          date: `${date.getMonth() + 1}/${String(date.getDate()).padStart(2, '0')}`, // MM/DD
          fullDate: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}` // YYYY-MM-DD
        });
      }

      return days;
    },

    // 日期到列索引的映射
    dateToColumnMap() {
      const map = {};
      this.weekDays.forEach(day => {
        map[day.fullDate] = day.value;
      });
      return map;
    },

    // 处理课程数据，添加列索引和冲突检测
    processedCourses() {
      // 第一步：转换课程数据，计算 dayOfWeek
      const coursesWithDay = this.courses.map(course => {
        // 如果课程有 date 字段，使用日期计算列索引
        let dayOfWeek = course.dayOfWeek;

        if (course.date) {
          const normalizedDate = course.date.replace(/\//g, '-');
          dayOfWeek = this.dateToColumnMap[normalizedDate];

          if (!dayOfWeek) {
            console.warn(`课程 "${course.name}" 的日期 "${course.date}" 不在当前周范围内`);
            return null; // 不在当前周的课程不显示
          }
        }

        const startMinutes = this.timeToMinutes(course.startTime);
        const endMinutes = this.timeToMinutes(course.endTime);
        const duration = endMinutes - startMinutes;

        return {
          ...course,
          dayOfWeek,
          startMinutes,
          endMinutes,
          duration,
          timeRange: `${course.startTime}-${course.endTime}`,
          columnIndex: 0,
          totalColumns: 1
        };
      }).filter(course => course !== null); // 过滤掉不在当前周的课程

      // 第二步：按天分组并检测冲突
      const coursesByDay = {};
      coursesWithDay.forEach(course => {
        const day = course.dayOfWeek;
        if (!coursesByDay[day]) {
          coursesByDay[day] = [];
        }
        coursesByDay[day].push(course);
      });

      // 第三步：为每一天的课程分配列位置
      Object.keys(coursesByDay).forEach(day => {
        const dayCourses = coursesByDay[day];
        dayCourses.sort((a, b) => a.startMinutes - b.startMinutes);

        const groups = [];

        dayCourses.forEach(course => {
          let foundGroup = false;

          for (let group of groups) {
            const hasOverlap = group.some(other => {
              return !(other.endMinutes <= course.startMinutes || other.startMinutes >= course.endMinutes);
            });

            if (hasOverlap) {
              group.push(course);
              foundGroup = true;
              break;
            }
          }

          if (!foundGroup) {
            groups.push([course]);
          }
        });

        groups.forEach(group => {
          const totalColumns = group.length;
          group.forEach((course, index) => {
            course.columnIndex = index;
            course.totalColumns = totalColumns;
          });
        });
      });

      return coursesWithDay;
    },

    // 计算每天的最大课程并发数（用于确定列宽）
    maxCoursesPerDay() {
      const maxCourses = {};

      // 初始化每天的最大并发数为1
      for (let i = 1; i <= 7; i++) {
        maxCourses[i] = 1;
      }

      // 使用 processedCourses（已经处理过日期映射）
      const coursesByDay = {};
      this.processedCourses.forEach(course => {
        const day = course.dayOfWeek;
        if (!day) return; // 跳过没有 dayOfWeek 的课程

        if (!coursesByDay[day]) {
          coursesByDay[day] = [];
        }
        coursesByDay[day].push({
          startMinutes: course.startMinutes,
          endMinutes: course.endMinutes
        });
      });

      // 计算每天的最大并发课程数
      Object.keys(coursesByDay).forEach(day => {
        const dayCourses = coursesByDay[day];
        const groups = [];

        dayCourses.forEach(course => {
          let foundGroup = false;

          for (let group of groups) {
            const hasOverlap = group.some(other => {
              return !(other.endMinutes <= course.startMinutes || other.startMinutes >= course.endMinutes);
            });

            if (hasOverlap) {
              group.push(course);
              foundGroup = true;
              break;
            }
          }

          if (!foundGroup) {
            groups.push([course]);
          }
        });

        // 找出最大的组大小
        const maxGroupSize = Math.max(...groups.map(g => g.length), 1);
        maxCourses[day] = maxGroupSize;
      });

      return maxCourses;
    },

    // 计算每列的宽度（单位：px）
    columnWidths() {
      const widths = {};
      const courseWidth = 150; // 每个课程卡片宽度
      const gap = 10; // 课程之间的间距
      const padding = 50; // 额外留白

      for (let i = 1; i <= 7; i++) {
        const maxCourses = this.maxCoursesPerDay[i];
        // 宽度 = 课程数 × 课程宽度 + (课程数 - 1) × 间距 + 留白
        widths[i] = maxCourses * courseWidth + (maxCourses - 1) * gap + padding;
      }

      return widths;
    },

    // 计算总宽度
    totalWidth() {
      let total = 0;
      for (let i = 1; i <= 7; i++) {
        total += this.columnWidths[i];
      }
      return total;
    },

    // 计算每列的起始位置
    columnPositions() {
      const positions = {};
      let currentPos = 0;

      for (let i = 1; i <= 7; i++) {
        positions[i] = currentPos;
        currentPos += this.columnWidths[i];
      }

      return positions;
    }
  },
  mounted() {
    // 监听主内容区域的滚动，同步表头的水平滚动
    this.$nextTick(() => {
      const scheduleMain = this.$refs.scheduleMain;
      if (scheduleMain) {
        scheduleMain.addEventListener('scroll', this.handleScroll);
      }

      // 调试信息
      console.log('=== CourseSchedule Debug Info ===');
      console.log('Courses count:', this.courses.length);
      console.log('Processed courses count:', this.processedCourses.length);
      console.log('weekDays:', this.weekDays);
      console.log('dateToColumnMap:', this.dateToColumnMap);
      console.log('maxCoursesPerDay:', this.maxCoursesPerDay);
      console.log('columnWidths:', this.columnWidths);
      console.log('totalWidth:', this.totalWidth);
      console.log('columnPositions:', this.columnPositions);
      console.log('Content width:', 80 + this.totalWidth);

      // 检查滚动容器
      if (scheduleMain) {
        setTimeout(() => {
          console.log('scheduleMain scrollWidth:', scheduleMain.scrollWidth);
          console.log('scheduleMain clientWidth:', scheduleMain.clientWidth);
          console.log('scheduleMain offsetWidth:', scheduleMain.offsetWidth);
          console.log('Can scroll?', scheduleMain.scrollWidth > scheduleMain.clientWidth);

          const scheduleContent = scheduleMain.querySelector('.schedule-content');
          if (scheduleContent) {
            console.log('scheduleContent offsetWidth:', scheduleContent.offsetWidth);
            console.log('scheduleContent scrollWidth:', scheduleContent.scrollWidth);
          }

          const scheduleGrid = scheduleMain.querySelector('.schedule-grid');
          if (scheduleGrid) {
            console.log('scheduleGrid offsetWidth:', scheduleGrid.offsetWidth);
          }
        }, 100);
      }
    });
  },

  beforeUnmount() {
    const scheduleMain = this.$refs.scheduleMain;
    if (scheduleMain) {
      scheduleMain.removeEventListener('scroll', this.handleScroll);
    }
  },

  methods: {
    // 处理滚动事件，同步表头和更新时间显示
    handleScroll(e) {
      const scrollLeft = e.target.scrollLeft;
      const scrollTop = e.target.scrollTop;

      // 同步表头的水平滚动
      const weekHeaderInner = this.$el.querySelector('.week-header-inner');
      if (weekHeaderInner) {
        // 使用 transform 来移动表头内容，实现同步滚动
        weekHeaderInner.style.transform = `translateX(-${scrollLeft}px)`;
      }

      // 根据垂直滚动距离计算当前时间
      this.updateScrollTime(scrollTop);
    },

    // 根据滚动距离更新时间显示
    updateScrollTime(scrollTop) {
      // 计算滚动位置对应的小时数(分钟)
      const totalMinutes = (scrollTop / this.cellHeight) * 60;
      const hours = Math.floor(totalMinutes / 60);
      const minutes = Math.floor(totalMinutes % 60);

      // 格式化为 HH:mm
      this.currentScrollTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    },

    // 格式化小时显示（00:00 格式）
    formatHour(hour) {
      return `${String(hour).padStart(2, '0')}:00`;
    },

    // 将时间字符串转换为分钟数（从00:00开始）
    timeToMinutes(timeStr) {
      const [hours, minutes] = timeStr.split(':').map(Number);
      return hours * 60 + minutes;
    },

    // 计算课程卡片的样式
    getCourseStyle(course) {
      const { dayOfWeek, startMinutes, duration, color, columnIndex } = course;

      // 计算垂直位置（top）：从00:00开始的分钟数
      const top = (startMinutes / 60) * this.cellHeight;

      // 计算高度：持续时间对应的像素高度
      const height = (duration / 60) * this.cellHeight;

      // 固定课程卡片宽度和间距
      const cardWidth = 150; // px
      const gap = 10; // 课程之间的间距

      // 计算水平位置：列起始位置 + (卡片索引 × (卡片宽度 + 间距))
      const columnStart = this.columnPositions[dayOfWeek];
      const left = columnStart + columnIndex * (cardWidth + gap);

      return {
        top: `${top}px`,
        left: `${left}px`,
        width: `${cardWidth}px`,
        height: `${height}px`,
        backgroundColor: color || '#5DADE2',
        padding: '8px 12px'
      };
    }
  }
};
</script>

<style scoped>
.course-schedule {
  position: relative;
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr); /* 时间列宽度 + 内容区域（允许溢出） */
  grid-template-rows: 60px 1fr; /* 表头高度 + 内容区域 */
  overflow: hidden;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

/* 左上角空白单元格 */
.corner-cell {
  grid-column: 1;
  grid-row: 1;
  background-color: #f5f7fa;
  border-right: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  left: 0;
  z-index: 30;
  position: relative;
}

/* 左上角的"时间"标签居中显示 */
.corner-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  font-weight: 600;
  color: #303133;
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
  z-index: 1;
}

/* 星期表头（固定顶部） */
.week-header {
  grid-column: 2;
  grid-row: 1;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 20;
  overflow: hidden; /* 隐藏滚动条 */
  height: 60px;
}

/* 表头内部容器（可滚动） */
.week-header-inner {
  position: relative;
  height: 100%;
  min-width: 100%;
}

.week-header-cell {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-right: 1px solid #e0e0e0;
  box-sizing: border-box;
}

.week-header-cell:last-child {
  border-right: none;
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
  grid-column: 1 / 3; /* 横跨两列 */
  grid-row: 2;
  position: relative;
  overflow-x: auto; /* 明确启用横向滚动 */
  overflow-y: auto; /* 明确启用纵向滚动 */
}

/* 内容包装器 */
.schedule-content {
  position: relative;
  min-height: 100%;
  display: flex; /* 使用flex布局替代float */
  min-width: max-content; /* 确保内容不会被压缩 */
}

/* 时间轴列（固定左侧，跟随垂直滚动） */
.time-column {
  position: sticky;
  left: 0;
  width: 80px;
  flex-shrink: 0; /* 防止收缩 */
  background-color: #fafafa;
  border-right: 1px solid #e0e0e0;
  z-index: 10;
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
  color: #606266;
  white-space: nowrap;
  z-index: 1;
}

/* 课程网格容器 */
.schedule-grid {
  flex-shrink: 0; /* 防止收缩，保持固定宽度 */
  position: relative;
  min-height: 100%;
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

.grid-column:last-child {
  border-right: none;
}

.grid-cell {
  border-bottom: 1px solid #e0e0e0;
  box-sizing: border-box;
}

/* 课程卡片层 */
.courses-layer {
  position: relative;
  width: 100%;
  min-height: 100%;
}

.course-card {
  position: absolute;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: #fff;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.course-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  z-index: 5;
}

.course-time {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  opacity: 0.95;
}

.course-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.course-info {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 2px;
}

/* 滚动条样式优化 */
.schedule-main::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.schedule-main::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 4px;
}

.schedule-main::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

.schedule-main::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}
</style>

