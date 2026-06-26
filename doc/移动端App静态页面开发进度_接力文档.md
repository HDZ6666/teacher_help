# 移动端 App 静态页面开发进度（接力文档）

> 最新整理：2026-06-25
> 代码范围：`teacher_help_uniapp` 静态页面
> 开发口径：uni-app + Vue3 + TS，`script setup`，`definePage`，scoped SCSS + rpx，全部 mock 数据，不接 API。

## 1. 当前总览

当前以代码事实为准：

- `teacher_help_uniapp/src/pages.json` 已注册 **54 个页面**。
- `teacher_help_uniapp/src/pages` 下现有 **54 个 `.vue` 页面文件**。
- 当前无“已落盘但未注册”的页面文件。
- 已注册页面均配置 `navigationStyle: custom`，继续按 Stitch 自绘顶部栏风格实现。
- 已接入更多工具入口：课程管理、班级管理、老师管理、教室/场地、物品费用、会员卡、数据概览。
- 当前只做静态高保真页面，未接真实接口、权限、后端业务校验。

当前剩余明确缺口：

- 暂无。场地模块剩余 2 页已补齐并注册，当前移动端静态页口径下 12 个模块全部完成。
- `pages/venue/index.vue`、`pages/venue/schedule.vue` 中指向 `/pages/venue/booking-detail` 的跳转已可达。

## 2. 路由注册清单

### 通用与我的

| 页面 | 对应原型 | 状态 | 说明 |
|---|---|---|---|
| `pages/login/login` | `_54` 登录 | 已注册 | 静态登录页 |
| `pages/index/index` | `_25` 今日工作台 | 已注册 | 5 Tab 首页 |
| `pages/me/me` | `_8` 我的 | 已注册 | 资料卡、快捷入口、功能列表 |
| `pages/me/tools` | `_23` 更多工具 | 已注册 | 高频/教务/经营工具网格 |
| `pages/me/settings` | `_16` 设置 | 已注册 | 通知、账号、安全等设置 |
| `pages/me/business` | `_44` 经营管理 | 已注册 | 经营数据概览 |

> `_28` 班级管理轻入口、`_29` 老师管理轻入口、`_34` 课程管理轻入口已合入 `pages/me/tools` 的工具卡入口，不单独建页。

### 课表与点名

| 页面 | 对应原型 | 状态 | 说明 |
|---|---|---|---|
| `pages/schedule/index` | `_17` 课表首页 | 已注册 | 日期条、视图切换、课程卡 |
| `pages/schedule/course-detail` | `_22` 课次详情 | 已注册 | 课次统计、学员名单、调课/点名入口 |
| `pages/schedule/create` | `_47` 新增排课 | 已注册 | 单次/规则/日历模式；`_55`、`_59` 合并在此页 |
| `pages/schedule/conflict` | `_52` 排课冲突 | 已注册 | 冲突列表与处理动作 |
| `pages/schedule/reschedule` | `_41` 调课 | 已注册 | 调课申请表单 |
| `pages/schedule/detail` | `_14` 点名页 | 已注册 | 点名统计、批量动作、学员状态 |
| `pages/schedule/exception-confirm` | `_5` 点名异常确认 | 已注册 | 异常名单确认态 |
| `pages/schedule/checkin-done` | `_4` 点名完成 | 已注册 | 完成统计与后续动作 |
| `pages/schedule/comment` | `_15` 课后点评 | 已注册 | 点评、作业、课堂照片、发布 |

### 学员与错题本

| 页面 | 对应原型 | 状态 | 说明 |
|---|---|---|---|
| `pages/student/index` | `_3` 学员列表 | 已注册 | 搜索、筛选、学员卡 |
| `pages/student/detail` | `_53` 学员详情、`_32` 联系家长 | 已注册 | 联系家长作为详情内状态承载 |
| `pages/student/add` | `_42` 添加学员 | 已注册 | 当前作为班级添加学员勾选页复用 |
| `pages/student/leave` | `_43` 学员请假 | 已注册 | 请假表单和审批流 |
| `pages/student/enroll` | `_45` 报名续费 | 已注册 | 报名、续费、支付方式 |
| `pages/wrong-question/index` | `_46` 错题本首页 | 已注册 | 统计、拍照上传、最近错题 |
| `pages/wrong-question/upload` | `_31` 拍照上传 | 已注册 | 取景、裁剪、关联学员 |
| `pages/wrong-question/analyzing` | `ai` AI 分析中 | 已注册 | 分析进度 |
| `pages/wrong-question/detail` | `_35` 错题详情 | 已注册 | 解析、错因、知识点 |
| `pages/wrong-question/edit` | `_39` 编辑解析 | 已注册 | AI 解析编辑 |

### 班级、课程、老师

| 页面 | 对应原型 | 状态 | 说明 |
|---|---|---|---|
| `pages/class/index` | `_20` 班级列表 | 已注册 | 班级卡、筛选、快捷操作 |
| `pages/class/detail` | `_48` 班级详情 | 已注册 | 班级信息、学员/课表/点名等 tabs |
| `pages/class/create` | `_10` 新增/编辑班级 | 已注册 | 班级基础信息、课程、容量 |
| `pages/class/upgrade` | `_9` 升班/结业 | 已注册 | 学员升班/结业 |
| `pages/course/index` | `_13` 课程列表 | 已注册 | 课程卡、收费方式、状态 |
| `pages/course/detail` | `_57` 课程详情 | 已注册 | 价格、班级、套餐、规则 |
| `pages/course/create` | `_24` 新增/编辑课程 | 已注册 | 课程字段、收费标准 |
| `pages/course/package` | `_6` 套餐轻入口 | 已注册 | 套餐列表和轻量详情 |
| `pages/teacher/index` | `_58` 老师列表 | 已注册 | 老师卡、筛选、课表入口 |
| `pages/teacher/detail` | `_51` 老师详情 | 已注册 | 资料卡、快捷操作、近期课程 |
| `pages/teacher/create` | `_37` 新增/编辑老师 | 已注册 | 老师资料表单 |
| `pages/teacher/schedule` | `_36` 老师课表 | 已注册 | 老师日期课表 |

### 物品费用、会员卡、场地

| 页面 | 对应原型 | 状态 | 说明 |
|---|---|---|---|
| `pages/item/index` | `_56` 物品费用首页 | 已注册 | 统计、分段、快捷入口 |
| `pages/item/list` | `_38` 物品列表 | 已注册 | 物品卡、库存预警、入库/领用 |
| `pages/item/edit` | `_27` 新增/编辑物品 | 已注册 | 物品资料、价格、库存规则 |
| `pages/item/purchase` | `_7` 采购入库 | 已注册 | 入库表单、金额计算 |
| `pages/item/fee` | `_40` 费用项目 | 已注册 | 费用项目卡片 |
| `pages/item/stock-log` | `_21` 库存流水 | 已注册 | 出入库流水 |
| `pages/member-card/index` | `_2` 会员卡列表 | 已注册 | 会员卡卡片、发放入口 |
| `pages/member-card/detail` | `_12` 会员卡详情 | 已注册 | 卡面、权益、规则 |
| `pages/member-card/grant` | `_49` 发放会员卡 | 已注册 | 发放表单 |
| `pages/member-card/grant-record` | `_19` 发放记录 | 已注册 | 发放记录列表 |
| `pages/member-card/hold-detail` | `_33` 学员持卡详情 | 已注册 | 持卡概要与时间线 |
| `pages/venue/index` | `_26` 场地首页 | 已注册 | 场地卡、预约/锁场入口 |
| `pages/venue/schedule` | `_30` 订场时间表 | 已注册 | 场地时间表 |
| `pages/venue/proxy-booking` | `_11` 代预约 | 已注册 | 代预约表单 |
| `pages/venue/lock` | `_50` 锁场 | 已注册 | 锁定场地表单 |
| `pages/venue/booking-detail` | `_18` 预约详情/核销 | 已注册 | 预约人、场地、金额、取消/订单/核销 |
| `pages/venue/cancel` | `_1` 取消预约 | 已注册 | 退款金额、取消原因、通知用户 |

## 3. 模块完成度

| 模块 | 预期 | 当前 | 结论 |
|---|---:|---:|---|
| 01 登录与今日工作台 | 2 | 2 | 完成 |
| 02 课表与排课 | 7 | 7 | 完成，规则/日历排课合入 `schedule/create` |
| 03 点名与课后 | 4 | 4 | 完成 |
| 04 学员管理 | 5 | 5 | 完成，联系家长合入学员详情 |
| 05 AI 错题本 | 5 | 5 | 完成 |
| 06 我的与更多工具 | 7 | 7 | 完成，轻入口合入更多工具 |
| 07 班级管理 | 5 | 5 | 完成，添加学员复用 `student/add` |
| 08 课程管理 | 4 | 4 | 完成 |
| 09 老师管理 | 4 | 4 | 完成 |
| 10 物品费用 | 6 | 6 | 完成 |
| 11 会员卡 | 5 | 5 | 完成 |
| 12 场地管理 | 6 | 6 | 完成，预约详情/核销与取消预约已补齐 |

## 4. 最新变更记录

### 2026-06-25 场地模块剩余静态页收口

- 新增 `teacher_help_uniapp/src/pages/venue/booking-detail.vue`，对应 Stitch `_18`：展示预约人、手机号、场地、日期时间、支付金额、预约来源、订单编号、地图入口；底部提供“取消预约、查看订单、核销”，核销后显示核销时间和操作人。
- 新增 `teacher_help_uniapp/src/pages/venue/cancel.vue`，对应 Stitch `_1`：展示取消规则、目标预约、退款金额、取消原因、补充说明、通知用户开关；底部提供“确认取消”和“返回”。
- 已在 `teacher_help_uniapp/src/pages.json` 注册上述 2 个页面，场地模块从 4/6 更新为 6/6。
- 代码事实校验：`pages.json` 已注册 54 页，`src/pages` 下 `.vue` 文件 54 个；无已落盘未注册页面，无注册但缺失文件。
- 页面层 API 扫描：`rg "@/api|fetch\(|axios|request\(" teacher_help_uniapp/src/pages` 未命中，仍保持静态 mock 口径。
- `pnpm type-check` 当前因 `node_modules` 缺失、`vue-tsc` 不存在而无法完成，需安装依赖后复跑。

### 2026-06-25 Claude 后阶段复核（收口前历史）

- 本次复核发现 Claude 新增的是后端真实库/技术债分析文档：`doc/数据库真实结构与后端技术债核查_2026-06-25.md`。
- `teacher_help_uniapp` 页面事实未新增：仍为 **52 个注册页面**、**52 个 `.vue` 页面文件**。
- 当前仍无已落盘但未注册的移动端页面。
- 场地模块缺口不变：仍缺 `pages/venue/booking-detail.vue`（`_18`）和 `pages/venue/cancel.vue`（`_1`）。

### 2026-06-25 uniapp 当前代码变更审计

本次按 `teacher_help_uniapp` 当前工作区逐模块检查，结论如下：

- `package.json`：Node engine 已从 `>=22` 放宽为 `>=20`。
- `pages.json`：由原来少量基础页面扩展为 **54 个自绘导航页面**，`index/login/me/schedule/student/wrong-question` 原有页面也统一设置或保持 `navigationStyle: custom`。
- 原有 tracked 页面被高保真静态化/重写：`index`、`login`、`me`、`schedule`、`student`、`wrong-question` 下共 20+ 个页面大幅改动，移除了页面层真实 API 依赖，改为本地 mock 数据。
- 新增 untracked 模块目录：`class`、`course`、`item`、`member-card`、`teacher`、`venue`，以及 `me/tools.vue`、`me/settings.vue`、`me/business.vue`、`schedule/comment.vue`、`schedule/exception-confirm.vue`、`student/enroll.vue`。
- 页面层 API 扫描：`teacher_help_uniapp/src/pages` 下未命中 `@/api`、`fetch(`、`axios`、`request(`；`src/http`、`src/store` 仍保留 unibest 模板接口能力，不影响当前静态页口径。
- 页面跳转扫描：扫描到的 `navigateTo/switchTab` 目标均已注册或为当前模块内已补齐页面。

#### 逐模块代码变更说明

| 模块 | 当前页面 | 本轮代码体现的主要变化 | 跳转/风险 |
|---|---:|---|---|
| 登录与今日 | 2 | `login/login` 改为静态登录体验；`index/index` 改为今日工作台，包含校区切换、统计、快捷动作、今日课程和待办。 | 登录按钮跳首页；今日课程可跳点名。 |
| 我的与工具 | 4 | `me/me` 改为资料卡、快捷数据、功能列表；新增 `tools/settings/business`，更多工具接入课程、班级、老师、场地、物品、会员卡、数据概览。 | `me/tools` 的收费记录仍是待开发 toast；其余主要入口可达。 |
| 课表与排课 | 9 | `schedule/index/create/detail/course-detail/conflict/reschedule/checkin-done` 大幅静态化；新增 `comment` 和 `exception-confirm`。 | 新增排课、课程详情、调课、点名、异常确认、点评链路已串起。 |
| 学员管理 | 5 | `student/index/detail/add/leave` 静态高保真重做；新增 `student/enroll`。详情页承载联系家长状态，添加学员页复用为班级选学员。 | 学员列表→详情/请假/添加，详情→请假/报名续费可达。 |
| AI 错题本 | 5 | 首页、上传、分析中、详情、编辑解析均改为 AI 错题静态流程。 | 首页→上传/分析/详情，详情→编辑，上传→分析可达。 |
| 班级管理 | 4 | 新增班级列表、详情、创建、升班结业；列表含学员/排课/点名/详情，详情含学员/课表/点名/请假/设置 tabs。 | 班级模块预期 5 页中 `_42` 添加学员复用 `student/add`。 |
| 课程管理 | 4 | 新增课程列表、详情、新增编辑、套餐轻入口；保留课程颜色、收费方式、价格、班级、套餐、规则等移动端轻量管理口径。 | 课程列表→详情/编辑，详情→编辑可达。 |
| 老师管理 | 4 | 新增老师列表、详情、新增编辑、老师课表；详情有课表/联系/排课/编辑快捷操作。 | 老师课表复用排课调课和点名页面。 |
| 物品费用 | 6 | 新增物品费用首页、物品列表、新增编辑、采购入库、费用项目、库存流水；示例文案已中文化。 | 物品费用内列表/费用/库存/入库/编辑可达。 |
| 会员卡 | 5 | 新增会员卡列表、详情、发放、发放记录、学员持卡详情。 | 列表→详情/发放，详情→发放/发放记录，记录→持卡详情可达。 |
| 场地管理 | 6/6 | 新增场地首页、订场时间表、代预约、锁场、预约详情/核销、取消预约。 | `venue/index`、`venue/schedule` 指向 `booking-detail` 的跳转已可达；详情页可进入取消预约。 |

#### 当前代码事实校验

- 已注册页面：54。
- `.vue` 页面文件：54。
- 已落盘但未注册页面：0。
- 注册但缺失文件：0。
- 非 `navigationStyle: custom` 页面：0。
- 未落盘但被跳转引用：0。

### 2026-06-25 路由与文档收口

- 将已落盘但未注册的 12 个页面补入 `pages.json`：
  - `pages/item/index`
  - `pages/item/list`
  - `pages/item/edit`
  - `pages/item/purchase`
  - `pages/item/fee`
  - `pages/item/stock-log`
  - `pages/venue/index`
  - `pages/venue/schedule`
  - `pages/venue/proxy-booking`
  - `pages/venue/lock`
  - `pages/me/settings`
  - `pages/me/business`
- `pages/me/tools.vue` 已接入：
  - 物品费用 → `/pages/item/index`
  - 教室/场地 → `/pages/venue/index`
  - 数据概览 → `/pages/me/business`
- `pages/me/me.vue` 的“通知设置”已接入 `/pages/me/settings`。
- 已将过程进度文档内容合并到本文件，并删除：
  - `doc/移动端_进度_老师.md`
  - `doc/移动端_进度_会员卡.md`
  - `doc/移动端_进度_物品费用.md`

## 5. 验证方式

每次接力完成后至少执行：

```powershell
node -e "const fs=require('fs'); const p=JSON.parse(fs.readFileSync('teacher_help_uniapp/src/pages.json','utf8')).pages; console.log(p.length)"
```

```powershell
rg "@/api|fetch\(|axios|request\(" teacher_help_uniapp/src/pages
```

```powershell
pnpm type-check
```

当前环境因缺少 `node_modules` 导致 `vue-tsc` 不存在，`pnpm type-check` 需要先安装依赖后复跑。`teacher_help_uniapp/package.json` 的 Node 要求已放宽为 `>=20`，如安装依赖时启用严格 engines，建议使用 Node 20.19+。

## 6. 下一步

当前静态页清单已全部补齐。下一步建议：

1. 安装 `teacher_help_uniapp` 依赖后复跑 `pnpm type-check` / 构建。
2. 启动 H5 或小程序预览，逐页人工核对 Stitch 原型视觉一致性。
3. 进入接口接入阶段前，先冻结当前静态页清单和页面跳转表，避免后续联调时范围漂移。

## 7. 全量原型一致性核对 + 修正（2026-06-26）

54 个页面用 6 个子 agent 并行逐页对照 `mobile-promete/stitch_/<目录>` 核对：✅一致 35 / 🟡小差异 18 / 🔴大差异 1。随后用 3 个 fix agent 并行修正（文件不重叠，未碰 pages.json/tools.vue）：

- 🔴 `schedule/reschedule.vue` → 重写对齐 `_41`：原课程深色卡只留课名+日期+时间；新课程安排=新日期/新时间双列+任课老师/上课教室下拉+调课原因+通知开关；底部「检查冲突/确认调课」。
- 🟡 `student/add.vue` 勾选框选中色 蓝→绿 `#005842`（对齐 `_42`）。
- 🟡 `item/list.vue` 顶部搜索图标改为搜索行为（不再误跳编辑），编辑入口归卡片按钮（对齐 `_38`）。
- 🟡 `class/detail.vue` 快捷操作 5→4 格（添加学员/新增排课/去点名/班级请假），姓名对齐 `_48`。
- 🟡 `item/index.vue` 移除 `_56` 没有的多余快捷按钮区。
- ✅ `wrong-question/index.vue` 审计确认已对齐 `_46`（2×2 Bento + 拍照/相册双按钮）。

**判定为合理适配、有意保留（未改）**：子页省略底部全局 TabBar；列表缩略图/封面/地图用 CSS 占位代替真实图片；子页用「返回」顶栏代替原型品牌/汉堡栏；`me/me` 为用户自定版；`course/detail` 非价格 Tab 占位、`class/create` 下拉降级为选择行等轻量化。

> 结论：除上述合理适配外，全部页面结构已与 Stitch 原型对齐。
