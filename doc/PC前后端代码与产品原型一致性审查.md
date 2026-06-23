# PC 前后端代码与产品原型一致性审查

> 最新进度更新：当前代码已经新增并接入班级基础闭环，本文中“班级后端缺失”等早期结论已过期。最新项目进度、测试数据和下一步优先级请以 `doc/当前项目进度结论.md` 为准。

> 核对时间：2026-06-22  
> 核对范围：`doc/产品图片`、`teacher_help_admin`、`teacher_help_service`、`teacher_help_service/logs`  
> 核对原则：本次只做文档审查和文档修正，不修改 PC 前端或后端业务代码。

## 1. 总体结论

当前 `doc/产品图片` 按 9 个 PC 助教业务模块组织：学员管理、班级管理、课表管理、上课记录、课程管理、老师管理、物品费用、会员卡、场地管理。原型目录中没有独立的“家长管理”模块；家长/联系人信息应归入学员管理的联系人能力。

从代码覆盖看，PC 前端 `teacher_help_admin/src/views/assistant` 已有学员、课程、班级、物品费用、课表、上课记录 6 个助教业务入口；会员卡、场地管理暂无对应前端入口。后端已注册教学与物品费用相关 Controller，包括教师、家长基础数据、学生、课程、排课事件、排课考勤、物品、库存/费用；暂无班级、上课记录、会员卡、场地管理的独立 Controller。

完成度判断如下：

| 原型模块 | 原型图片数 | 前端覆盖 | 后端覆盖 | 完成度 | 结论 |
| --- | ---: | --- | --- | --- | --- |
| 学员管理 | 38 | 有 `/assistant/student`、详情、报名页 | 有 `/teach/student`，报名/课程/订单接口处于未提交改动中 | 部分完成 | 列表仍主要是 mock；报名和详情开始接真实接口，但需稳定验证 |
| 班级管理 | 31 | 有列表、详情、点名页 | 未见班级 Controller | 部分完成偏原型 | 页面形态接近原型，但大量 TODO/mock，后端缺口大 |
| 课表管理 | 20 | 有 `/assistant/schedule` | 有 `/teach/schedule/event`、`/teach/schedule/attendance` | 部分完成 | 有基础排课/考勤接口，但 PC 课表页面仍以 mock 为主 |
| 上课记录 | 23 | 有列表、详情、点评、评价页 | 未见 `/assistant/classRecord` 后端 Controller | 部分完成偏原型 | 前端 API 指向不存在的后端路径，页面大量 mock/TODO |
| 课程管理 | 11 | 有 `/assistant/course` | 有 `/teach/course` 与 package 接口 | 基本完成 | 课程、套餐、物品/费用选项链路较完整 |
| 老师管理 | 7 | 无 assistant 老师入口；有 teach/user、teach/teacher 旧页面/API | 有 `/teach/teacher` 基础 CRUD | 部分完成 | 基础教师数据存在，但和原型的老师详情/权限入口未完全对齐 |
| 物品费用 | 15 | 有 `/assistant/inventory` | 有 `/ast/item`、`/ast/inventory`、费用接口 | 基本完成 | 物品、SKU、出入库、费用接口较完整；订单/报名联动仍需验证 |
| 会员卡 | 8 | 无 | 无 | 未完成 | 仅有原型和文档，未见 PC/后端实现 |
| 场地管理 | 15 | 无 | 无 | 未完成 | 仅有原型和文档，未见 PC/后端实现 |

## 2. 原型资源清单

| 目录 | 原型图片 | 附带文件 | 说明 |
| --- | ---: | ---: | --- |
| `1学员管理模块` | 38 | 5 | 含导入模板、导出样例和 `view_all.html` |
| `2班级管理` | 31 | 2 | 含班级导入、签到导出样例 |
| `3课表管理` | 20 | 2 | 含课表导出和签到名单样例 |
| `4上课记录` | 23 | 0 | 全部为原型图片 |
| `5课程管理模块` | 11 | 0 | 全部为原型图片 |
| `6老师管理` | 7 | 0 | 全部为原型图片 |
| `7物品费用` | 15 | 2 | 含采购导入模板和出入库导出样例 |
| `8会员卡` | 8 | 0 | 全部为原型图片 |
| `9场地管理` | 15 | 0 | 全部为原型图片 |

图片合计 168 张，目录文件合计 179 个。

## 3. 模块明细

### 3.1 学员管理：部分完成

原型覆盖在读学员列表、导入导出、分配跟进人、分配学管师、报名/续费、选择课程/物品/费用、收据、报读情况、转课、停课、结课、详情页、消费记录、上课记录、跟进记录、持有卡等。

前端现状：

- 路由：`/assistant/student`、`/assistant/student/detail/:id`、`/assistant/student/enroll/:id`。
- `student/index.vue` 仍存在 `mockData`、`setTimeout` 和多处“功能开发中”，列表和批量操作不能视为正式完成。
- `student/detail.vue` 已引入 `getStudent`、`getStudentCourses`、`getStudentOrders`。
- `student/enroll.vue` 已引入 `getStudent`、`getStudentCourses`、`submitStudentEnroll`，并读取课程套餐、可售物品和费用。

后端现状：

- `teach_student_controller.py` 已有 `/teach/student/list`、详情、增删改、导出、`/teach/student/enroll`、`/{student_id}/courses`、`/{student_id}/orders`。
- 报名订单、订单明细、学员课程账户相关 DAO/Service/DO 文件当前是未跟踪文件，属于新增但尚未纳入稳定版本的实现。
- `/teach/parent` 是家长/联系人基础数据接口，不代表独立“家长管理”原型模块。

一致性判断：学员基础档案和报名闭环正在接入真实后端，但前端列表、导入、批量处理、转课/停课/结课、收据和详情多 Tab 仍未完全闭环。当前应标记为“部分完成”，不应标记为已完成。

### 3.2 班级管理：部分完成偏原型

原型覆盖班级列表、新建/导入、批量关联课程、批量升班、批量结业、一对一班课、班级详情、课程详情、班级学员、排课、点名、请假、历史点名。

前端现状：

- 路由：`/assistant/class`、`/assistant/class/detail/:id`、`/assistant/class/attendance/:id`。
- `class/index.vue`、`class/detail.vue`、`class/attendance.vue` 页面结构较完整，但存在大量 `mockData`、`setTimeout`、`TODO`、“功能开发中”。
- 未发现班级页面引用正式 `@/api` 模块。

后端现状：

- 当前 `module_teach/controller` 未见班级管理 Controller。
- 后端已注册的排课/考勤接口可作为班级后续联动基础，但不能替代班级实体、班级成员、班级排课、班级点名完整后端。

一致性判断：前端更接近“高保真业务原型”，后端缺少班级主业务。当前不能视为正式完成。

### 3.3 课表管理：部分完成

原型覆盖时间课表日/周/月视图、老师课表、教室课表、班级课表、悬浮弹窗、课次详情、编辑课程、添加临时学员、学生请假、学生调课、删除课次、导出课表/签到名单。

前端现状：

- 路由：`/assistant/schedule`。
- `schedule/index.vue` 覆盖多种视图，但仍大量使用 `mockCourses`，并有“约课/导出/打印/课表设置/调课”等功能开发中提示。
- 未发现页面直接引用 `@/api/teach/schedule`。

后端现状：

- 已有 `/teach/schedule/event` 的列表、详情、新增、编辑、删除、日历事件、导出。
- 已有 `/teach/schedule/attendance` 的考勤列表、签到、手动考勤、统计。

一致性判断：后端有基础排课和考勤能力，但 PC 课表页面尚未和真实接口打通，且原型中的临时学员、请假、调课、删除课次、导出图片等交互未闭环。

### 3.4 上课记录：部分完成偏原型

原型覆盖点名记录、点名详情、课后点评、统一/批量点评、撤销点评、请假申请、缺课补课、缺课提醒、超时未点名、标记已补等。

前端现状：

- 路由：`/assistant/classRecord`、详情、点评、评价页。
- `classRecord/index.vue`、`detail.vue`、`comment.vue`、`evaluate.vue` 存在大量 mock/TODO。
- `src/api/assistant/classRecord.js` 指向 `/assistant/classRecord/*` 路径。

后端现状：

- 当前后端未注册 `/assistant/classRecord` Controller。
- 已有 `/teach/schedule/attendance` 基础考勤接口，但不覆盖上课记录原型中的点评、请假、补课、缺课提醒、超时未点名等完整业务。

一致性判断：前端原型较完整，但后端路径缺失，当前不能进入正式联调。

### 3.5 课程管理：基本完成

原型覆盖课程列表、新建课程、按月收费、套餐列表、新增套餐、选择课程、选择物品、选择费用、套餐价格和优惠配置。

前端现状：

- 路由：`/assistant/course`。
- `course/index.vue` 引用 `@/api/assistant/course` 和 `@/api/assistant/inventory`。
- 前端 API 指向 `/teach/course`、`/teach/course/package`，并能读取可售物品、费用。

后端现状：

- `teach_course_controller.py` 注册 `/teach/course`。
- 覆盖课程列表、详情、增删改、批量新增、启停、删除、导出、课程选项、套餐列表、套餐详情、套餐新增/编辑/启停/删除。
- 权限主要使用 `teach:course:*`，套餐复用课程权限。

一致性判断：课程与套餐主链路和原型匹配度高，是当前完成度较高的模块。后续主要补细节测试、字典状态和报名订单联动。

### 3.6 老师管理：部分完成

原型覆盖老师列表、老师详情、老师本月课时/已上课时/授课班级、签到列表、老师权限和角色选择。

前端现状：

- `assistant` 路由下暂无老师管理入口。
- `src/api/teach/teacher.js` 存在教师列表、详情、增删改、导出、课程、学生、统计接口封装。
- `views/teach/user`、`views/teach/student`、`views/teach/parent` 属于较早的 teach 基础管理页面，不等同于当前 9 模块 assistant 原型入口。

后端现状：

- `teacher_controller.py` 注册 `/teach/teacher`，覆盖教师基础 CRUD 和导出。
- 前端 API 中的 `/teach/teacher/{teacher_id}/courses`、`students`、`stats` 是否存在对应后端路由需另行补齐核对；当前 Controller 扫描只看到基础 CRUD 和导出。
- 老师权限原型更多依赖系统角色/权限能力，尚未看到和老师业务页完整融合。

一致性判断：教师基础数据后端存在，但 assistant 老师管理原型入口、详情统计、权限配置联动尚未完整落地。

### 3.7 物品费用：基本完成

原型覆盖物品管理、新增/编辑物品、SKU、售卖单价、库存预警、绑定课程、采购入库、导入采购订单、领用、领退、盘点、出入库详情、关联订单、费用列表和新建费用。

前端现状：

- 路由：`/assistant/inventory`。
- `inventory/index.vue` 引用 `@/api/assistant/inventory` 与课程选项。
- API 覆盖 `/ast/item`、`/ast/inventory/item/{id}/skus`、`/ast/inventory/items/options`、`/ast/inventory/stock/list`、采购导入、领用、领退、盘点、费用列表/详情/增删改/启停。

后端现状：

- `ast_item_controller.py` 注册 `/ast/item`，覆盖物品 CRUD 和导出。
- `ast_inventory_controller.py` 注册 `/ast/inventory`，覆盖 SKU、可售物品、角色选项、库存记录、详情、作废、导出、采购、导入、模板、领用、领退、盘点、费用管理。
- 当前未提交的学员报名 Service 中已开始和库存销售出库联动，但尚需整体联调验证。

一致性判断：物品费用自身管理链路较完整，和原型匹配度高。剩余重点是报名订单、财务收款、关联订单详情等跨模块闭环。

### 3.8 会员卡：未完成

原型覆盖卡列表、新建课程卡、新建场地折扣卡、关联课程、卡详情、发放记录、操作记录。

前端现状：

- 当前 `assistant` 路由下没有会员卡入口。
- 未见 `views/assistant/memberCard` 或同类目录。

后端现状：

- 未见会员卡相关 Controller、Service、DAO、DO。

一致性判断：当前仅有原型和文档，应标记为未完成。不要把学员详情中的“持有卡”展示误判为会员卡模块已完成。

### 3.9 场地管理：未完成

原型覆盖场馆/场地列表、新建场馆、新建场地、配置可预约星期和时间、订场管理、锁定、代预订、预定记录、详情、核销、取消预定。

前端现状：

- 当前 `assistant` 路由下没有场地管理入口。
- 未见 `views/assistant/venue` 或同类目录。

后端现状：

- 未见场地、场馆、订场、预订记录相关 Controller、Service、DAO、DO。

一致性判断：当前仅有原型和文档，应标记为未完成。

## 4. 路由与接口对照

### 4.1 PC 前端 assistant 路由

当前 `teacher_help_admin/src/router/index.js` 中的助教业务路由：

- `/assistant/student`
- `/assistant/student/detail/:id`
- `/assistant/student/enroll/:id`
- `/assistant/course`
- `/assistant/class`
- `/assistant/class/detail/:id`
- `/assistant/class/attendance/:id`
- `/assistant/inventory`
- `/assistant/schedule`
- `/assistant/classRecord`
- `/assistant/classRecord/detail/:id`
- `/assistant/classRecord/comment/:id`
- `/assistant/classRecord/evaluate/:id`

缺失的原型入口：

- 老师管理 assistant 入口缺失。
- 会员卡入口缺失。
- 场地管理入口缺失。

### 4.2 后端已注册业务 Controller

当前 `teacher_help_service/server.py` 注册的教学和物品费用业务 Controller：

- `/teach/teacher`
- `/teach/parent`
- `/teach/student`
- `/teach/course`
- `/teach/schedule/event`
- `/teach/schedule/attendance`
- `/ast/item`
- `/ast/inventory`

缺失的原型后端能力：

- 班级管理独立后端。
- 上课记录独立后端，尤其是 `/assistant/classRecord/*` 对应 Controller。
- 会员卡后端。
- 场地管理后端。

## 5. 日志结论

已查看 `teacher_help_service/logs` 最新日志。`2026-06-22_error.log` 显示：

- 后端服务启动成功。
- 数据库连接成功。
- Redis 连接成功。
- 登录、获取用户信息、获取路由成功。
- 课程列表、套餐列表、课程选项、可售物品、费用列表、学员课程、学员订单接口有成功调用记录。
- 未看到 `Traceback`、`ERROR`、`Exception`。
- 反复出现的 warning 为学员详情接口提示“学生不存在”，发生在访问学员详情/报名相关页面时，更像是联调用的学生 ID 或测试数据不存在，需要后续用真实数据验证。

## 6. 后续优先级建议

1. 先稳定学员报名闭环：确认未提交的报名订单/课程账户/库存出库后端文件是否要纳入版本，并补充数据库表、菜单权限、真实数据联调。
2. 补班级管理后端：班级、班级成员、班级排课、班级点名是课表和上课记录的基础。
3. 打通课表页面真实接口：将 `assistant/schedule` 从 mock 数据切到 `/teach/schedule/event` 和考勤接口。
4. 重建上课记录后端路径：要么补 `/assistant/classRecord/*` Controller，要么调整前端 API 到统一的 `/teach/...` 路径。
5. 对齐老师管理入口：决定老师管理是否进入 assistant 9 模块导航，并补详情统计和权限联动。
6. 会员卡、场地管理按“新模块”规划：先补数据库设计和后端模型，再做 PC 页面和接口。

## 7. 本次不改代码的说明

当前工作区存在学员报名相关前后端未提交改动，包括：

- `teacher_help_admin/src/api/teach/student.js`
- `teacher_help_admin/src/views/assistant/student/detail.vue`
- `teacher_help_admin/src/views/assistant/student/enroll.vue`
- `teacher_help_service/module_teach/controller/teach_student_controller.py`
- `teacher_help_service/module_teach/entity/vo/teach_student_vo.py`
- `teacher_help_service/module_teach/dao/teach_enrollment_dao.py`
- `teacher_help_service/module_teach/entity/do/teach_enrollment_order_do.py`
- `teacher_help_service/module_teach/service/teach_enrollment_service.py`

这些改动涉及真实业务闭环，且当前任务要求先核对完成进度、未完成的先不要改代码。因此本次只新增和修正文档，不覆盖、不回滚、不继续编辑上述代码文件。
