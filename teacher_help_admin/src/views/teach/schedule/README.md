# 排课管理模块

## 功能概述

排课管理模块是老师帮后台管理系统的核心功能之一，基于 FullCalendar 实现，提供直观的日历视图来管理课程安排。

## 主要功能

### 1. 日历视图
- **月视图 (dayGridMonth)**: 查看整月的课程安排
- **周视图 (timeGridWeek)**: 查看一周的详细课程时间表
- **日视图 (timeGridDay)**: 查看单日的课程安排
- **列表视图 (listWeek)**: 以列表形式查看一周的课程

### 2. 课程管理
- **新增排课**: 
  - 点击"新增排课"按钮或直接在日历上选择时间段
  - 填写教师、课程、时间、地点等信息
  - 系统自动检测时间冲突
  
- **编辑排课**:
  - 点击日历上的课程事件查看详情
  - 在详情对话框中点击"编辑"按钮
  - 或直接拖拽课程事件调整时间
  - 或拖拽事件边缘调整课程时长

- **删除排课**:
  - 点击课程事件查看详情
  - 在详情对话框中点击"删除"按钮

### 3. 搜索筛选
- 按教师筛选课程
- 按课程筛选
- 按状态筛选（已安排/进行中/已完成/已取消）

### 4. 状态管理
课程状态用不同颜色标识：
- **灰色**: 已安排
- **橙色**: 进行中
- **绿色**: 已完成
- **红色**: 已取消

### 5. 交互功能
- **拖拽调整**: 直接拖拽课程事件到新的时间位置
- **调整时长**: 拖拽事件边缘调整课程时长
- **点击查看**: 点击课程事件查看详细信息
- **日期导航**: 使用工具栏按钮切换日期和视图

## 技术实现

### 依赖包
```json
{
  "@fullcalendar/core": "^6.1.19",
  "@fullcalendar/vue3": "^6.1.19",
  "@fullcalendar/daygrid": "^6.1.19",
  "@fullcalendar/timegrid": "^6.1.19",
  "@fullcalendar/interaction": "^6.1.19",
  "@fullcalendar/list": "^6.1.19"
}
```

### API接口

#### 1. 获取日历事件
```javascript
GET /teach/schedule/calendar/events
参数: {
  teacherId: number,  // 教师ID（可选）
  courseId: number,   // 课程ID（可选）
  status: number      // 状态（可选）
}
返回: {
  code: 200,
  data: [
    {
      id: 1,
      teacherId: 1,
      teacherName: "张老师",
      courseId: 1,
      courseName: "数学",
      startTime: "2025-01-15 09:00:00",
      endTime: "2025-01-15 10:30:00",
      location: "教室A101",
      status: 1,
      remark: "备注信息",
      createTime: "2025-01-10 10:00:00"
    }
  ]
}
```

#### 2. 新增排课
```javascript
POST /teach/schedule
参数: {
  teacherId: number,
  courseId: number,
  startTime: string,
  endTime: string,
  location: string,
  status: number,
  remark: string
}
```

#### 3. 更新排课
```javascript
PUT /teach/schedule
参数: {
  id: number,
  teacherId: number,
  courseId: number,
  startTime: string,
  endTime: string,
  location: string,
  status: number,
  remark: string
}
```

#### 4. 更新排课时间（拖拽）
```javascript
PUT /teach/schedule/updateTime
参数: {
  id: number,
  startTime: string,
  endTime: string
}
```

#### 5. 删除排课
```javascript
DELETE /teach/schedule/{id}
```

#### 6. 检查时间冲突
```javascript
POST /teach/schedule/checkConflict
参数: {
  teacherId: number,
  startTime: string,
  endTime: string,
  id: number  // 编辑时传入，新增时不传
}
返回: {
  code: 200,
  data: {
    hasConflict: boolean,
    message: string
  }
}
```

#### 7. 获取教师列表
```javascript
GET /teach/teacher/simple/list
返回: {
  code: 200,
  data: [
    { id: 1, teacherName: "张老师" }
  ]
}
```

#### 8. 获取课程列表
```javascript
GET /teach/course/simple/list
参数: {
  teacherId: number  // 可选，筛选指定教师的课程
}
返回: {
  code: 200,
  data: [
    { id: 1, courseName: "数学", teacherId: 1 }
  ]
}
```

## 使用说明

### 1. 添加菜单权限
在系统管理 -> 菜单管理中添加以下菜单：
- 菜单名称: 排课管理
- 路由地址: /teach/schedule
- 组件路径: teach/schedule/index
- 权限标识: teach:schedule:list

### 2. 添加按钮权限
- teach:schedule:event:add - 新增排课
- teach:schedule:event:edit - 编辑排课
- teach:schedule:event:remove - 删除排课
- teach:schedule:event:export - 导出排课
- teach:schedule:query - 查询排课

### 3. 后端实现要点
- 实现上述API接口
- 时间冲突检测逻辑
- 课程状态管理
- 数据权限控制（教师只能管理自己的课程）

## 注意事项

1. **时区处理**: 确保前后端时间格式统一，建议使用 ISO 8601 格式
2. **权限控制**: 根据用户角色限制可操作的数据范围
3. **性能优化**: 大量数据时考虑分页加载或按时间范围加载
4. **移动端适配**: FullCalendar 支持响应式设计，但需要测试移动端体验

## 后续优化方向

1. **周期性排课**: 支持创建重复课程（如每周一、三、五）
2. **课程模板**: 保存常用的课程安排模板
3. **批量操作**: 批量调整、批量删除课程
4. **提醒功能**: 课前提醒教师和学生
5. **统计分析**: 课程统计、教师工作量统计
6. **导入导出**: Excel 批量导入导出课程安排
7. **打印功能**: 打印课程表

