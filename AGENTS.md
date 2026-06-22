# AI 项目协作规范

本文件是所有 AI 助手进入本项目后的工作入口。修改代码前必须先阅读并遵守本文规则，确保后续改动和项目既有风格一致。

## 必读顺序

1. 先读 `doc/老师帮-项目介绍.md`，了解项目定位、整体结构和技术栈。
2. 再读 `doc/老师帮-后台功能结构图.md`，了解 PC 管理后台功能边界。
3. 做具体模块前，阅读对应模块总结报告，例如 `05_课程管理模块总结报告.md`、`07_物品费用模块总结报告.md`。
4. 做页面或交互前，查看 `doc/产品图片/<对应模块>` 下的原型截图。
5. 做数据库、实体、接口前，查看 `doc/数据库设计` 和相关 SQL。
6. 排查运行问题前，查看 `teacher_help_service/logs` 下最新日志。

## 项目结构

- 前端：`teacher_help_admin`，Vue 3 + Vite + Element Plus + RuoYi-Vue3 风格。
- 后端：`teacher_help_service`，FastAPI + SQLAlchemy async + Redis + RuoYi-FastAPI 风格。
- 产品文档和原型：`doc`。
- 后端运行日志：`teacher_help_service/logs`。
- AI 任务记录：`log`。

## 修改前规则

1. 必须先执行 `git status --short`，确认工作区状态。
2. 不要覆盖、回滚或格式化用户已有未提交修改。
3. 找同类模块作为参照后再写代码，例如学生、课程、课表、物品费用模块。
4. 不做无关重构，不改无关文件，不大范围格式化。
5. 不因为终端中文乱码就修改中文文案。编辑中文文件前先确认原文件编码和实际内容。
6. 修改接口前确认前端 API、后端 `APIRouter(prefix=...)`、权限标识和字段命名是否一致。

## 前端风格

1. 保持 RuoYi 后台管理系统风格：查询表单、工具栏、表格、分页、弹窗或抽屉。
2. 页面放在 `src/views/...`，接口封装放在 `src/api/...`。
3. 优先使用 Element Plus、`right-toolbar`、`pagination`、`dict-tag`、`v-hasPermi`、全局 `proxy.$modal`、`resetForm` 等既有能力。
4. 优先复用同类页面写法，不重新设计整体交互。
5. 前端字段使用 camelCase，并和后端 VO 输出保持一致。
6. 按钮权限使用 `v-hasPermi="['module:resource:action']"`。
7. 不引入新的 UI 库，不大改全局样式。
8. 不做营销页、卡片堆叠式改版。后台页面以高效管理、信息密度和稳定交互为主。

## 后端风格

1. 保持 Controller -> Service -> DAO -> Entity 分层。
2. Controller 只处理路由、依赖注入、权限声明、参数接收和响应封装。
3. Service 处理业务校验、事务提交/回滚、数据组装和业务异常。
4. DAO 只处理 SQLAlchemy 查询和持久化。
5. Entity 分为 `entity/do` 数据库实体和 `entity/vo` 请求/响应模型。
6. 路由使用 `APIRouter(prefix=...)`。
7. 登录态使用 `LoginService.get_current_user`。
8. 接口权限使用 `CheckUserInterfaceAuth`。
9. 增删改、导入导出等操作使用 `@Log`。
10. 响应统一使用 `ResponseUtil.success`、`ResponseUtil.failure`、`ResponseUtil.streaming`。
11. 分页统一使用 `PageUtil` / `PageResponseModel`。
12. 数据库字段使用 snake_case，接口字段通过 VO 或工具转换为 camelCase。
13. Python 代码遵守 `teacher_help_service/ruff.toml`：行宽 120，字符串优先单引号。

## 日志和排错

1. 后端启动日志、接口日志在 `teacher_help_service/logs/YYYY-MM-DD_error.log`。
2. 后端错误和 warning 查看 `teacher_help_service/logs/backend.err.log`。
3. 日志格式包含时间、trace_id、级别、模块、函数、行号和消息。
4. 当前项目曾出现 Pydantic alias warning，修改 VO 时要特别注意 `Field`、alias 和 camelCase 输出方式。
5. 最终回复中应说明查看到的关键日志结论，不能只说“看过日志”。

## 验收要求

1. 前端修改后优先运行 `pnpm build`，或说明无法运行的原因。
2. 后端修改后至少运行语法检查、相关测试或启动验证，或说明无法运行的原因。
3. 接口改动要说明路径、权限标识、请求字段和响应字段。
4. 页面改动要说明参考了哪个原型截图或已有页面。
5. 修复问题时要说明根因、改动点和验证结果。
6. 无法完成时要明确阻塞原因，不要留下半成品而不说明。

## 禁止事项

1. 禁止覆盖未提交改动。
2. 禁止跳过文档和原型直接设计功能。
3. 禁止把业务逻辑写进 Controller。
4. 禁止绕过统一响应格式。
5. 禁止随意新增技术栈或 UI 库。
6. 禁止大范围格式化无关文件。
7. 禁止把模拟数据当成正式后端逻辑，除非任务明确要求并在结果中说明。
8. 禁止在未确认影响范围时修改全局配置、权限体系、路由守卫或数据库初始化逻辑。

## 推荐工作流程

1. 查看 `git status --short`。
2. 阅读本文和任务相关文档、原型、日志。
3. 找到同类前端页面、API 文件、后端 Controller、Service、DAO、VO、DO 作为参照。
4. 小范围修改代码。
5. 运行可行的验证命令。
6. 总结改动文件、验证结果、残余风险。
