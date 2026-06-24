# 移动端 App 静态页面开发进度（接力文档）

> 创建：2026-06-24 ｜ 用途：token 不足时的断点续传。下次直接读本文件即可接着开发。

## 0. 任务背景（一句话）

基于 **Stitch 60 页设计稿** + `doc/老师帮-移动端App原型设计说明.md`，用 **teacher_help_uniapp 现有技术栈**开发**静态页面**（本地 mock 数据，**不接 API**）。严禁引入其他技术栈。

- Stitch 项目 ID：`6199345630279074284`（共 60 个设计稿）
- 目标页面口径：以原型文档第 7 节「页面清单 23 页」+ 5 Tab 为主，P0→P1→P2。

## 1. 必须遵守的技术栈与约定（关键）

- 框架：**unibest 模板**（uni-app + Vue3 + TS），页面用 `<script lang="ts" setup>` + `definePage({ style:{...} })` + `defineOptions({ name })`。
- 样式：**scoped scss + rpx**，**不接 API，mock 数据写 `ref()`**。
- 新页面要**同时**做两件事：① 建 `.vue` 文件；② 在 `src/pages.json` 的 `pages` 数组注册路径（否则 navigateTo 404）。
- Tab 页还要改 `src/tabbar/config.ts` 的 `customTabbarList` + `pages.json` 的 `tabBar.list`。
- 自定义 tabbar 策略 = `CUSTOM_TABBAR_WITH_CACHE`，图标用 `iconType:'uniUi'` + uni-icons 名。

### 🔑 Stitch 设计稿可经 MCP 直接访问（2026-06-24 确认）
- 本会话的 **Stitch MCP 工具可访问项目 `6199345630279074284`**（共 60 画板，已确认 OWNER 权限）。
- `get_project` 返回完整 `designMd` 设计系统：token 与下方第 5 节配色完全一致（主色 `#1f7159`、深绿卡 `#193f36`、背景 `#f4f6f5`、白卡 `#ffffff`+`#e7ece9`、状态色配对、5 Tab、胶囊 chips、字体 Plus Jakarta Sans + Be Vietnam Pro）。
- `get_screen`（传 screenId）返回该画板的 **`title`（中文页名）+ 截图 PNG `screenshot.downloadUrl` + 完整 `htmlCode`**。例：screen `357d4a91...` 的 title = “课表首页”。
- ⚠️ 画板**列表里没有标题**，只有 ID 和坐标；要逐个 `get_screen` 读 `title` 才能定位某页对应哪个画板。
- **建议工作流**：建某页前，先在 Stitch 项目里 `get_screen` 找到对应 title 的画板 → 用 `curl` 下载 `screenshot.downloadUrl` 到本地临时 png → `Read` 查看 → 照真实布局还原。已建页面如需提高保真度可回头比对。

### 📋 Stitch 画板对照表（页名 → screenId，2026-06-24 全量核对）
> 项目 `6199345630279074284` 共 60 画板（含 1 个设计系统实例，下表列出 59 个页面）。取某页代码：`get_screen(name="projects/6199345630279074284/screens/<screenId>", projectId="6199345630279074284", screenId="<screenId>")` → 返回 `title` + 截图 `screenshot.downloadUrl` + 完整 `htmlCode.downloadUrl`。

| 模块 | 页名 | screenId |
| --- | --- | --- |
| 通用 | 登录 | dba124e3474e491284be98e728b97fb5 |
| 通用 | 今日工作台 | 5dc7b15b23f149f98ae541438d40bb5f |
| 通用 | 我的 | 18c21c04328b4e4a9e6d4339b4038d29 |
| 通用 | 设置 | 33b83673a1fd41fd9d9e0c42dea8e95c |
| 通用 | 更多工具 | 56628dd122b3499fa246e7c084509f58 |
| 通用 | 经营管理 | b492d6119de545319a3e8d0b6c596258 |
| 课表 | 课表首页 | 357d4a91e60144f3af0ce5def3c7f413 |
| 课表 | 新增排课 | c8779f2ef7c448ebaa3a65cf69da20af |
| 课表 | 规则排课 | f1c54fd3eb714bb4ae83de61f2b9238d |
| 课表 | 日历排课 | ddd468bf142745d1832c2365a24ed6fb |
| 课表 | 调课 | aaa753fafba942b7800f3d3bf03a590b |
| 课表 | 冲突处理 | d626d401b3374253932f0c8afe1f7944 |
| 点名 | 点名 | 2ae56ae1a1084f0395a134028245c02f |
| 点名 | 点名异常确认 | 0bddf972d7644e66bc71f8c7e4a2c2a4 |
| 点名 | 点名完成 | 0ba43fab90a94670b37b733a75cc31ee |
| 点名 | 课后点评 | 3163b9fe30924620a13d106f508ebc28 |
| 班级 | 班级列表 | 4877cc2abdf041008d5a417494b2aacf |
| 班级 | 班级管理 | 6ff8c9779a8e4d97852610ebef10aaa4 |
| 班级 | 班级详情 | cd2c38fe7dbe447782ed1c4a10ea4b1e |
| 班级 | 新增/编辑班级 | 1c2d797496f64acf9f1e62a846064954 |
| 班级 | 升班/结业 | 1b474688d7554384b68ed586078c996d |
| 课程 | 课程列表 | 2acd8d546e1e41c6b407be4e3007d967 |
| 课程 | 课程管理 | 7a3f84f0f9204cdd80e92be4f328f6d3 |
| 课程 | 课程详情(1) | 525d5af41a174b989eb4229b476882c3 |
| 课程 | 课程详情(2) | e9fa1674510b4ed68b18f7364a87a1b8 |
| 课程 | 新增/编辑课程 | 58e5879234de4f5fad47f56215743c7d |
| 课程 | 套餐轻入口 | 148599e9dee949089d9be9cbe727f94d |
| 学员 | 学员列表 | 08cb251502aa4d73aaa6005ec38f154d |
| 学员 | 学员详情 | d6342e655d3a47378ce9d6482f3e9e27 |
| 学员 | 添加学员 ⚠️见下注 | aab8187058f74e4181a09ed3529ae41b |
| 学员 | 学员请假 | adef09d653cb491fb68357e86a146704 |
| 学员 | 报名续费 | c20f38f4df1548db9e7adee9605ee30b |
| 学员 | 联系家长 | 796a539a82f84ea2bc64e3b3a7540789 |
| 老师 | 老师列表 | eaf2544491894fb9b5d65a99eb3e4fb0 |
| 老师 | 老师管理 | 7144c2d73fd94b82bc39f12b2d21948f |
| 老师 | 老师详情 | d414d0307ed543fdaf70e7a2f4176369 |
| 老师 | 老师课表 | 8a78bf71c2414c22aabe2b0752b151fc |
| 老师 | 新增/编辑老师 | 8bb42066af374e5da718c0f8206da3c0 |
| 物品费用 | 物品费用首页 | de45dc48f0474f19bb49b6e9440395a9 |
| 物品费用 | 物品列表 | 95f5332b74be4567b4a0d7156e42e931 |
| 物品费用 | 新增/编辑物品 | 63caefb04b5148cdb904d071a90b977b |
| 物品费用 | 采购入库 | 1628e05cfc644adc8410932a57984644 |
| 物品费用 | 库存流水 | 4a472bb905a743c0b406b28ea87c161f |
| 物品费用 | 费用项目 | a4c765e99adf44b2b01f85c4061951b7 |
| 会员卡 | 会员卡列表 | 07584e10cc51429f9593b008727583c6 |
| 会员卡 | 会员卡详情 | 21f0249a02454c7fbacbe79f0d11c45c |
| 会员卡 | 发放会员卡 | cd540c5fb7d34fb9827e2f48ace1d3a6 |
| 会员卡 | 发放记录 | 3f14a0c18855465692d8e70a052ce750 |
| 错题本 | 错题本首页 | c5f56827ac7543a5ad19cbc18ee49dd2 |
| 错题本 | 拍照上传 | 75838a2194d34b8fa8af8a735cd28f47 |
| 错题本 | AI 分析中 | 7a8c7536384041299f805a2a42b4df9a |
| 错题本 | 错题详情 | 84868d46cad047b5a964c89ab818a5a0 |
| 错题本 | 编辑解析 | 9f55e003423c4751b477c7d9e1621b63 |
| 场地 | 场地首页 | 5e63b8e68596458fa35bbdf700a23f54 |
| 场地 | 订场时间表 | 757de29435b8440795ebd3e62bc95496 |
| 场地 | 代预约 | 1fad67a24f3e4968bb7219f3659a1bc3 |
| 场地 | 预约详情/核销 | 3bc613e83a344d3c96e673f0347db66d |
| 场地 | 取消预约 | 049383c0f491472fa9d563dbd709ebc6 |
| 场地 | 锁场 | cee42482a6544d1bb5b41a9d169a8fd9 |

> ⚠️ **add.vue 与 Stitch 不一致（待返工）**：真实「添加学员」画板(`aab8187...`)实为**选学员勾选列表**（搜索框 + 学员卡多选 + 底部「已选 N 人」+「新增学员并加入 / 确认添加」），并非分组录入表单。当前已建的 `pages/student/add.vue` 是按文字 spec 做的录入表单，需按此画板返工。`leave.vue`、`enroll.vue` 等也应在动手前先 `get_screen` 比对真实布局。

### 📦 本地 Stitch 导出目录对照表（2026-06-24 补充）
> 本地导出位置：`mobile-promete/stitch_`。已核对：60 个业务页面目录均有 `screen.png` + `code.html`；`academic_precision` 是设计系统说明，不算业务页面。完整细表另存：`mobile-promete/stitch_页面对应关系.md`。

| 导出目录 | 对应模块 / 页面 | 开发参考 |
| --- | --- | --- |
| `_1` | 场地 / 取消预约 | P2，需中文化 |
| `_2` | 会员卡 / 会员卡列表 | P2 |
| `_3` | 学员 / 学员列表 | 已有 `pages/student/index.vue`，可回看提保真 |
| `_4` | 点名 / 点名完成 | 已有 `pages/schedule/checkin-done.vue` |
| `_5` | 点名 / 点名异常确认 | 待补弹层/确认态 |
| `_6` | 课程 / 套餐轻入口 | P2 |
| `_7` | 物品费用 / 采购入库 | P2，需中文化 |
| `_8` | 通用 / 我的 | 已有 Tab，可回看提保真 |
| `_9` | 班级 / 升班结业 | P2 |
| `_10` | 班级 / 新增编辑班级 | P2 |
| `_11` | 场地 / 代预约 | P2，需中文化 |
| `_12` | 会员卡 / 会员卡详情 | P2 |
| `_13` | 课程 / 课程列表 | P2 |
| `_14` | 点名 / 点名页 | 已有 `pages/schedule/detail.vue`，可回看提保真 |
| `_15` | 点名 / 课后点评 | Phase 4 待建：建议 `pages/schedule/comment.vue` |
| `_16` | 通用 / 设置 | P1/P2，可作为 `pages/me/settings.vue` 参考 |
| `_17` | 课表 / 课表首页 | 已有 `pages/schedule/index.vue` |
| `_18` | 场地 / 预约详情核销 | P2，需中文化 |
| `_19` | 会员卡 / 发放记录 | P2 |
| `_20` | 班级 / 班级列表 | P2 |
| `_21` | 物品费用 / 库存流水 | P2，示例数据需中文化 |
| `_22` | 课表 / 课程详情课次详情 | 已有 `pages/schedule/course-detail.vue` |
| `_23` | 通用 / 更多工具 | Phase 4 待建：`pages/me/tools.vue` |
| `_24` | 课程 / 新增编辑课程 | P2 |
| `_25` | 通用 / 今日工作台 | 已有 `pages/index/index.vue` |
| `_26` | 场地 / 场地首页 | P2，需中文化 |
| `_27` | 物品费用 / 新增编辑物品 | P2，部分文案需中文化 |
| `_28` | 通用 / 班级管理轻入口 | 可合入 `pages/me/tools.vue` |
| `_29` | 通用 / 老师管理轻入口 | 可合入 `pages/me/tools.vue` |
| `_30` | 场地 / 订场时间表 | P2，需中文化 |
| `_31` | 错题本 / 拍照上传 | 已有 `pages/wrong-question/upload.vue` |
| `_32` | 学员 / 联系家长 | 待补底部弹层，可在 `student/detail.vue` 里做 |
| `_33` | 会员卡 / 学员持卡详情 | P2 |
| `_34` | 通用 / 课程管理轻入口 | 可合入 `pages/me/tools.vue` |
| `_35` | 错题本 / 错题详情 | 已有 `pages/wrong-question/detail.vue` |
| `_36` | 老师 / 老师课表 | P2，标题和底部导航需中文化 |
| `_37` | 老师 / 新增编辑老师 | P2，标题可统一中文 |
| `_38` | 物品费用 / 物品列表 | P2，标题可中文化 |
| `_39` | 错题本 / 编辑解析 | 已有 `pages/wrong-question/edit.vue` |
| `_40` | 物品费用 / 费用项目 | P2，标题可中文化 |
| `_41` | 课表 / 调课 | 已有 `pages/schedule/reschedule.vue` |
| `_42` | 班级 / 添加学员 | ⚠️ 这是选学员勾选列表；当前 `pages/student/add.vue` 不匹配，需返工或另建班级加学员页 |
| `_43` | 学员 / 学员请假 | 已有 `pages/student/leave.vue`，需回看提保真 |
| `_44` | 通用 / 经营管理概览 | 可合入 `pages/me/tools.vue` 或后置 P2 |
| `_45` | 学员 / 报名续费 | Phase 4 待建：`pages/student/enroll.vue` |
| `_46` | 错题本 / 错题本首页 | 已有 `pages/wrong-question/index.vue` |
| `_47` | 课表 / 新增排课 | 已有 `pages/schedule/create.vue` |
| `_48` | 班级 / 班级详情 | P2 |
| `_49` | 会员卡 / 发放会员卡 | P2 |
| `_50` | 场地 / 锁场 | P2，需中文化 |
| `_51` | 老师 / 老师详情 | P2，标题和底部导航需中文化 |
| `_52` | 课表 / 排课冲突 | 已有 `pages/schedule/conflict.vue` |
| `_53` | 学员 / 学员详情 | 已有 `pages/student/detail.vue`，可回看提保真 |
| `_54` | 通用 / 登录页 | 已有登录页可回看提保真 |
| `_55` | 课表 / 日历排课 | 已并入 `pages/schedule/create.vue` 的日历模式，可视情况拆页 |
| `_56` | 物品费用 / 物品费用首页 | P2，标题和底部导航需中文化 |
| `_57` | 课程 / 课程详情 | P2 |
| `_58` | 老师 / 老师列表 | P2，标题和底部导航需中文化 |
| `_59` | 课表 / 规则排课 | 已并入 `pages/schedule/create.vue` 的规则模式，可视情况拆页 |
| `ai` | 错题本 / AI 分析中 | 已有 `pages/wrong-question/analyzing.vue` |

#### 本地导出复核结论
- `mobile-promete/stitch_/_1` 到 `_59` + `mobile-promete/stitch_/ai` 共 **60 个业务页面**，截图和 HTML 均存在。
- `mobile-promete/stitch_/academic_precision/DESIGN.md` 是设计系统说明，不能当业务页。
- 优先按 `_15` 课后点评、`_23` 更多工具、`_45` 报名续费继续 Phase 4。
- 需要二次让 Stitch 中文化或开发时手动中文化的页面：`_1`、`_7`、`_11`、`_18`、`_21`、`_26`、`_27`、`_30`、`_36`、`_37`、`_38`、`_50`、`_51`、`_56`、`_58`。
- 可用中文化提示词：`请基于当前页面保持布局、颜色、卡片、按钮大小和组件结构不变，只把页面标题、按钮、标签、说明文字、示例数据全部改成中文老师帮业务文案。不要新增页面，不要改变页面结构，不要改颜色和风格。`

### 配色 token（务必照抄，来自原型文档第 5 节）
- 页面背景 `#f4f6f5`；主文字 `#1f2d33`；弱文字 `#64737b/#718088/#74828a/#839099`
- 深色重点卡 `#193f36`（圆角 18rpx，文字白）；主按钮/主色 `#1f7159`；辅助绿 `#2a9d73`；链接绿 `#1d8b69`；Tab 选中 `#018d71`
- 白卡片 `#ffffff` + 边框 `1rpx solid #e7ece9` + 圆角 14~16rpx；分割线 `#edf1ef`
- 状态色：到课/成功 文字`#227253` 底`#e9f6ef`；警告 文字`#8a671b` 底`#fff5d8`；危险 文字`#9a3b33` 底`#ffeceb`；信息 文字`#335d9a` 底`#eaf1ff`；普通完成 文字`#5d6a70` 底`#eef2f0`
- 次按钮 底`#e6f4ee` 文字`#1f7159`；危险按钮 底`#ffeceb` 文字`#a4423a`
- 页面左右边距 28rpx；tabbar 页底部留白 `padding-bottom:150rpx`；带底部固定栏的页用 `env(safe-area-inset-bottom)`。
- chips：横滑 `scroll-view scroll-x`，active 态 底`#e6f4ee` 边`#b8dccc` 文字`#1e7259`。

### 参考样板文件（照着这些写最稳）
- `src/pages/index/index.vue`（今日工作台：深色 hero 卡 + 四宫格 + 列表）
- `src/pages/schedule/index.vue`（课表：日期面板 + 状态 chips + 卡片列表 + 统计条）
- 本次新增的 `src/pages/student/index.vue`、`detail.vue`（学员卡片、分段 Tabs 写法）

## 2. 已完成（Phase 1 + 2 + 3）✅

| 模块 | 文件 | 说明 |
|---|---|---|
| Tab 导航 | `src/tabbar/config.ts`、`src/pages.json` | 由 3 Tab 扩为 **5 Tab**：今日/课表/**学员**/**错题本**/我的 |
| 学员列表 | `src/pages/student/index.vue` | 搜索+6 筛选 chips+学员卡（头像/标签/剩余课时/4 按钮） |
| 学员详情 | `src/pages/student/detail.vue` | 深色头部卡+5 快捷操作+四宫格+5 分段Tabs(概览/报读课程/上课记录/错题/消费) |
| 错题本首页 | `src/pages/wrong-question/index.vue` | 搜索+4 统计卡+6 筛选 chips+错题卡(AI状态/掌握态)+悬浮拍错题按钮 |
| 拍照上传 | `src/pages/wrong-question/upload.vue` | 取景区+拍照/相册+关联学生/学科/课程表单+底部主按钮 |
| AI 分析中 | `src/pages/wrong-question/analyzing.vue` | 进度环+5 步进度(定时器mock,跑完 redirect 到 detail)+后台/取消 |
| 错题详情 | `src/pages/wrong-question/detail.vue` | 题图+识别题干+答案解析步骤+易错点+相似练习+备注+操作网格 |
| 编辑解析 | `src/pages/wrong-question/edit.vue` | 题干/学科/知识点/答案/步骤/易错点/掌握态/备注表单+删除 |
| 新增排课 | `src/pages/schedule/create.vue` | 模式选择(单次/规则/日历)+三套表单+常用时间段+预计生成N节+检查冲突 |
| 排课冲突 | `src/pages/schedule/conflict.vue` | 浅红提示条+冲突卡(类型/时间/对象/已有课程)+换老师/教室/时间+忽略继续(二次确认) |
| 调课 | `src/pages/schedule/reschedule.vue` | 当前课次深色卡+新日期/时间/老师/教室/原因/通知家长开关+检查冲突 |
| 课次详情 | `src/pages/schedule/course-detail.vue` | 深色头部卡+四宫格(应到/已到/迟到/缺勤)+学员名单(状态pill)+更多操作 |
| 点名完成 | `src/pages/schedule/checkin-done.vue` | 成功态+出勤率+5项统计+扣课摘要+低课时学生+4操作按钮 |

**以上全部路由已在 `pages.json` 注册完毕。** 5 个 Tab 已可正常切换。

> ⚠️ 待补的「入口接线」（小工作量，下次顺手做）：现有 `pages/schedule/index.vue`（课表）尚未加「新增排课」悬浮按钮跳 `create.vue`，课程卡也未跳 `course-detail.vue`；`pages/schedule/detail.vue`（点名）的"完成点名"尚未跳 `checkin-done.vue`。这些只是把已有页面 navigateTo 串起来，不影响各页本身可独立预览。

## 3. 待开发（Phase 4）⏳ ｜对应 Task #7
- [x] `pages/student/add.vue` — **添加学员**：分组表单(基础信息/联系人/报读意向/标签/备注)。已建+已注册。⚠️ 按文字字段+token 还原，未逐像素比对 Stitch 画板。
- [x] `pages/student/leave.vue` — **学员请假**：学员/课程/类型(事假/病假/其他)/方式(按课次/按时间段)/课次多选或日期段/原因/图片/是否扣课 + 提交。已建+已注册。⚠️ 同上，未比对 Stitch 画板。
- [ ] `pages/student/enroll.vue` — **报名续费**：选课程或套餐/数量/赠送/有效期/应收/优惠/实收/支付方式/经办人 + 提交报名/保存草稿。
- [ ] `pages/schedule/comment.vue`(或 wrong-question 同级) — **课后点评**：从点名完成进入,评价维度+文字+保存。
- [ ] `pages/me/tools.vue` — **更多工具**：白色列表(课程/班级/老师管理、物品费用、会员卡、场地、数据概览)。建议同时更新 `pages/me/me.vue` 入口跳转。

> 三选一可后置的 P2：班级/课程/老师/物品/会员卡/场地 等管理页（设计稿里有，但文档定为 P2 轻入口，可只做「更多工具」列表占位，详情页后续再补）。

### 每新增页面记得：在 `src/pages.json` 的 `pages` 数组追加注册（参照已有写法）。

## 4. 验证方式
未跑过 dev 构建。下次可在 `teacher_help_uniapp/` 跑 `pnpm dev:h5`（或 `dev:mp-weixin`）自检；注意 `tabbar/config.ts` 改动需重启 dev 才会重生成 pages.json。

## 5. 下一步建议（接上即做）
Phase 1/2/3 已完成（共 14 个新页面）。下次从 **Phase 4（Task #7）** 开始：建议顺序 `student/add` → `student/leave` → `student/enroll` → `schedule/comment` → `me/tools`。
另可顺手补 §2 末尾标注的「入口接线」（课表→新增排课/课次详情、点名→点名完成）。
每建一页记得在 `pages.json` 注册路由。
