<template>
  <div class="course-schedule-wrapper">
    <!-- 月视图 -->
    <MonthSchedule
      v-if="viewMode === 'month'"
      :courses="courses"
      :height="height"
      :month="month"
      @view-detail="$emit('view-detail', $event)"
      @reschedule="$emit('reschedule', $event)"
      @delete="$emit('delete', $event)"
    />

    <!-- 日视图和周视图 -->
    <TimeSchedule
      v-else
      :courses="courses"
      :height="height"
      :cell-height="cellHeight"
      :view-mode="viewMode"
      :dates="dates"
      :start-date="startDate"
      @view-detail="$emit('view-detail', $event)"
      @reschedule="$emit('reschedule', $event)"
      @delete="$emit('delete', $event)"
    />
  </div>
</template>

<script>
import TimeSchedule from './TimeSchedule.vue';
import MonthSchedule from './MonthSchedule.vue';

export default {
  name: 'CourseSchedule',
  components: {
    TimeSchedule,
    MonthSchedule
  },
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
    // 视图模式：'day' | 'week' | 'month'
    viewMode: {
      type: String,
      default: 'week',
      validator: (value) => ['day', 'week', 'month'].includes(value)
    },
    // 日期数组（优先级最高）
    // 日视图：传入1个日期 ['2025-11-07']
    // 周视图：传入7个日期 ['2025-11-03', '2025-11-04', ...]
    // 月视图：不需要传，会根据 month 自动计算
    dates: {
      type: Array,
      default: null
    },
    // 月份（仅月视图使用，格式：'2025-11' 或 '2025/11'）
    month: {
      type: String,
      default: null
    },
    // 起始日期（兼容旧版本，当 dates 和 month 都未提供时使用）
    // 周视图：默认为当前周的周一
    // 日视图：默认为今天
    startDate: {
      type: String,
      default: null // 格式：'2025-11-03' 或 '2025/11/03'
    }
  }
};
</script>

<style scoped>
.course-schedule-wrapper {
  width: 100%;
  height: 100%;
}
</style>

