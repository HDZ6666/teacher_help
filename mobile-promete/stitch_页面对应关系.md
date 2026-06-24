# Stitch 导出页面对应关系

本文件用于把 `mobile-promete/stitch_` 导出的页面目录，对应回 `mobile-promete/00-12` 提示词中的模块和页面。

## 总体结论

- 原提示词预计生成页面 / 状态：60 个。
- Stitch 实际导出页面：60 个，其中 `_1` 到 `_59` 是页面目录，`ai` 是单独导出的“AI 分析中”页面。
- `academic_precision` 是 Stitch 导出的设计系统说明，不是业务页面。
- 所有预期页面都能在导出目录中找到对应项。
- 部分页面被 Stitch 生成为英文界面或使用了英文示例数据，已在“备注”中标记，建议后续单独要求 Stitch 中文化。

## 使用方式

1. 按“模块”和“预期页面”查找你要核对的页面。
2. 打开“实际截图”查看视觉图。
3. 打开“实际 HTML”查看 Stitch 生成的源码页面。
4. 如果备注里写了“需中文化”，可以把对应页面截图或 HTML 重新发给 Stitch，要求“保持布局不变，只把文案、示例数据和按钮全部改成中文老师帮业务文案”。

## 完整对应表

| 模块 | 预期页面 | 实际目录 | 实际标题 | 实际截图 | 实际 HTML | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 01 登录与今日工作台 | 登录页 | `_54` | 老师帮 - 登录 | [screen.png](stitch_/_54/screen.png) | [code.html](stitch_/_54/code.html) | 匹配 |
| 01 登录与今日工作台 | 今日工作台 | `_25` | 今日工作台 - 老师帮 | [screen.png](stitch_/_25/screen.png) | [code.html](stitch_/_25/code.html) | 匹配 |
| 02 课表与排课 | 课表首页 | `_17` | 我的课表 | [screen.png](stitch_/_17/screen.png) | [code.html](stitch_/_17/code.html) | 匹配，标题可改为“课表” |
| 02 课表与排课 | 课程详情 / 课次详情 | `_22` | 课程详情 | [screen.png](stitch_/_22/screen.png) | [code.html](stitch_/_22/code.html) | 匹配 |
| 02 课表与排课 | 新增排课入口 | `_47` | 新增排课 | [screen.png](stitch_/_47/screen.png) | [code.html](stitch_/_47/code.html) | 匹配 |
| 02 课表与排课 | 规则排课 | `_59` | 规则排课 | [screen.png](stitch_/_59/screen.png) | [code.html](stitch_/_59/code.html) | 匹配 |
| 02 课表与排课 | 日历排课 | `_55` | 日历排课 | [screen.png](stitch_/_55/screen.png) | [code.html](stitch_/_55/code.html) | 匹配 |
| 02 课表与排课 | 排课冲突 | `_52` | 冲突处理 | [screen.png](stitch_/_52/screen.png) | [code.html](stitch_/_52/code.html) | 匹配 |
| 02 课表与排课 | 调课页 | `_41` | 调课申请 | [screen.png](stitch_/_41/screen.png) | [code.html](stitch_/_41/code.html) | 匹配，标题可改为“调课” |
| 03 点名与课后 | 点名页 | `_14` | 点名页 - 老师帮 | [screen.png](stitch_/_14/screen.png) | [code.html](stitch_/_14/code.html) | 匹配 |
| 03 点名与课后 | 点名异常确认 | `_5` | 点名异常确认 | [screen.png](stitch_/_5/screen.png) | [code.html](stitch_/_5/code.html) | 匹配 |
| 03 点名与课后 | 点名完成页 | `_4` | 点名完成 | [screen.png](stitch_/_4/screen.png) | [code.html](stitch_/_4/code.html) | 匹配 |
| 03 点名与课后 | 课后点评 | `_15` | 课后点评 | [screen.png](stitch_/_15/screen.png) | [code.html](stitch_/_15/code.html) | 匹配 |
| 04 学员管理 | 学员列表 | `_3` | 学员列表 - 老师帮 | [screen.png](stitch_/_3/screen.png) | [code.html](stitch_/_3/code.html) | 匹配 |
| 04 学员管理 | 学员详情 | `_53` | 学员详情 - 张子涵 | [screen.png](stitch_/_53/screen.png) | [code.html](stitch_/_53/code.html) | 匹配 |
| 04 学员管理 | 报名 / 续费 | `_45` | 报名续费 - 老师帮 | [screen.png](stitch_/_45/screen.png) | [code.html](stitch_/_45/code.html) | 匹配 |
| 04 学员管理 | 学员请假 | `_43` | 学员请假 | [screen.png](stitch_/_43/screen.png) | [code.html](stitch_/_43/code.html) | 匹配 |
| 04 学员管理 | 联系家长 | `_32` | 联系家长 - 底层 | [screen.png](stitch_/_32/screen.png) | [code.html](stitch_/_32/code.html) | 匹配，属于底部弹层状态 |
| 05 AI 错题本 | 错题本首页 | `_46` | 错题本 | [screen.png](stitch_/_46/screen.png) | [code.html](stitch_/_46/code.html) | 匹配 |
| 05 AI 错题本 | 拍照上传 | `_31` | 拍照上传 | [screen.png](stitch_/_31/screen.png) | [code.html](stitch_/_31/code.html) | 匹配 |
| 05 AI 错题本 | AI 分析中 | `ai` | AI 分析中 | [screen.png](stitch_/ai/screen.png) | [code.html](stitch_/ai/code.html) | 匹配，唯一非编号页面目录 |
| 05 AI 错题本 | 错题详情 | `_35` | 错题详情 | [screen.png](stitch_/_35/screen.png) | [code.html](stitch_/_35/code.html) | 匹配 |
| 05 AI 错题本 | 编辑解析 | `_39` | 编辑解析 | [screen.png](stitch_/_39/screen.png) | [code.html](stitch_/_39/code.html) | 匹配 |
| 06 我的与更多工具 | 我的页 | `_8` | 我的 - 老师帮 | [screen.png](stitch_/_8/screen.png) | [code.html](stitch_/_8/code.html) | 匹配 |
| 06 我的与更多工具 | 更多工具页 | `_23` | 更多工具 | [screen.png](stitch_/_23/screen.png) | [code.html](stitch_/_23/code.html) | 匹配 |
| 06 我的与更多工具 | 课程管理轻入口 | `_34` | 课程管理 | [screen.png](stitch_/_34/screen.png) | [code.html](stitch_/_34/code.html) | 匹配 |
| 06 我的与更多工具 | 班级管理轻入口 | `_28` | 班级管理 | [screen.png](stitch_/_28/screen.png) | [code.html](stitch_/_28/code.html) | 匹配 |
| 06 我的与更多工具 | 老师管理轻入口 | `_29` | 老师管理轻入口 | [screen.png](stitch_/_29/screen.png) | [code.html](stitch_/_29/code.html) | 匹配 |
| 06 我的与更多工具 | 经营管理轻入口 | `_44` | 经营管理概览 | [screen.png](stitch_/_44/screen.png) | [code.html](stitch_/_44/code.html) | 匹配 |
| 06 我的与更多工具 | 设置页 | `_16` | 设置 - 教育管理系统 | [screen.png](stitch_/_16/screen.png) | [code.html](stitch_/_16/code.html) | 匹配，标题建议改成“设置 - 老师帮” |
| 07 班级管理 | 班级列表 | `_20` | 班级 | [screen.png](stitch_/_20/screen.png) | [code.html](stitch_/_20/code.html) | 匹配 |
| 07 班级管理 | 班级详情 | `_48` | 班级详情 | [screen.png](stitch_/_48/screen.png) | [code.html](stitch_/_48/code.html) | 匹配 |
| 07 班级管理 | 新增 / 编辑班级 | `_10` | 创建班级 | [screen.png](stitch_/_10/screen.png) | [code.html](stitch_/_10/code.html) | 匹配 |
| 07 班级管理 | 添加学员 | `_42` | 添加学生 | [screen.png](stitch_/_42/screen.png) | [code.html](stitch_/_42/code.html) | 匹配，标题建议统一成“添加学员” |
| 07 班级管理 | 升班 / 结业 | `_9` | 学员升班/结业 | [screen.png](stitch_/_9/screen.png) | [code.html](stitch_/_9/code.html) | 匹配 |
| 08 课程管理 | 课程列表 | `_13` | 课程列表 | [screen.png](stitch_/_13/screen.png) | [code.html](stitch_/_13/code.html) | 匹配 |
| 08 课程管理 | 课程详情 | `_57` | 课程详情 | [screen.png](stitch_/_57/screen.png) | [code.html](stitch_/_57/code.html) | 匹配 |
| 08 课程管理 | 新增 / 编辑课程 | `_24` | 新增/编辑课程 - 老师帮 | [screen.png](stitch_/_24/screen.png) | [code.html](stitch_/_24/code.html) | 匹配 |
| 08 课程管理 | 套餐轻入口 | `_6` | 套餐轻入口 | [screen.png](stitch_/_6/screen.png) | [code.html](stitch_/_6/code.html) | 匹配 |
| 09 老师管理 | 老师列表 | `_58` | Teacher List - Teacher Help | [screen.png](stitch_/_58/screen.png) | [code.html](stitch_/_58/code.html) | 匹配，标题需中文化 |
| 09 老师管理 | 老师详情 | `_51` | Teacher Details - 老师详情 | [screen.png](stitch_/_51/screen.png) | [code.html](stitch_/_51/code.html) | 匹配，标题需中文化 |
| 09 老师管理 | 新增 / 编辑老师 | `_37` | 新增老师 - Teacher Help | [screen.png](stitch_/_37/screen.png) | [code.html](stitch_/_37/code.html) | 匹配，标题可统一中文 |
| 09 老师管理 | 老师课表 | `_36` | Teacher Schedule | [screen.png](stitch_/_36/screen.png) | [code.html](stitch_/_36/code.html) | 匹配，标题需中文化 |
| 10 物品费用 | 物品费用首页 | `_56` | 物品费用 - Item & Fees Home | [screen.png](stitch_/_56/screen.png) | [code.html](stitch_/_56/code.html) | 匹配，部分底部导航英文 |
| 10 物品费用 | 物品列表 | `_38` | 物品列表 - Teacher Help | [screen.png](stitch_/_38/screen.png) | [code.html](stitch_/_38/code.html) | 匹配，标题可中文化 |
| 10 物品费用 | 新增 / 编辑物品 | `_27` | 新增物品 - Add/Edit Item | [screen.png](stitch_/_27/screen.png) | [code.html](stitch_/_27/code.html) | 匹配，部分文案需中文化 |
| 10 物品费用 | 采购入库 | `_7` | Purchase Stock-in | [screen.png](stitch_/_7/screen.png) | [code.html](stitch_/_7/code.html) | 匹配，需中文化 |
| 10 物品费用 | 费用项目 | `_40` | Teacher Help - 费用项目 | [screen.png](stitch_/_40/screen.png) | [code.html](stitch_/_40/code.html) | 匹配，标题可中文化 |
| 10 物品费用 | 库存流水 | `_21` | 库存流水 (Inventory Transaction Logs) | [screen.png](stitch_/_21/screen.png) | [code.html](stitch_/_21/code.html) | 匹配，部分示例数据需中文化 |
| 11 会员卡 | 会员卡列表 | `_2` | 会员卡列表 - 老师帮 | [screen.png](stitch_/_2/screen.png) | [code.html](stitch_/_2/code.html) | 匹配 |
| 11 会员卡 | 会员卡详情 | `_12` | 会员卡详情 - 老师帮 | [screen.png](stitch_/_12/screen.png) | [code.html](stitch_/_12/code.html) | 匹配 |
| 11 会员卡 | 发放会员卡 | `_49` | 发放会员卡 - 老师帮 | [screen.png](stitch_/_49/screen.png) | [code.html](stitch_/_49/code.html) | 匹配 |
| 11 会员卡 | 发放记录 | `_19` | 发放记录 - 老师帮 | [screen.png](stitch_/_19/screen.png) | [code.html](stitch_/_19/code.html) | 匹配 |
| 11 会员卡 | 学员持卡详情 | `_33` | 学员持卡详情 - 老师帮 | [screen.png](stitch_/_33/screen.png) | [code.html](stitch_/_33/code.html) | 匹配 |
| 12 场地管理 | 场地首页 | `_26` | Venue Manager | [screen.png](stitch_/_26/screen.png) | [code.html](stitch_/_26/code.html) | 匹配，需中文化 |
| 12 场地管理 | 订场时间表 | `_30` | Venue Schedule - Teacher Help | [screen.png](stitch_/_30/screen.png) | [code.html](stitch_/_30/code.html) | 匹配，需中文化 |
| 12 场地管理 | 代预约 | `_11` | Proxy Booking | [screen.png](stitch_/_11/screen.png) | [code.html](stitch_/_11/code.html) | 匹配，需中文化 |
| 12 场地管理 | 锁场 | `_50` | Lock Venue - Teacher Help | [screen.png](stitch_/_50/screen.png) | [code.html](stitch_/_50/code.html) | 匹配，需中文化 |
| 12 场地管理 | 预约详情 / 核销 | `_18` | Booking Details | [screen.png](stitch_/_18/screen.png) | [code.html](stitch_/_18/code.html) | 匹配，需中文化 |
| 12 场地管理 | 取消预约 | `_1` | Cancel Booking - Teacher Help App | [screen.png](stitch_/_1/screen.png) | [code.html](stitch_/_1/code.html) | 匹配，需中文化 |

## 按导出目录反查页面

| 导出目录 | 对应页面 |
| --- | --- |
| `_1` | 12 场地管理 / 取消预约 |
| `_2` | 11 会员卡 / 会员卡列表 |
| `_3` | 04 学员管理 / 学员列表 |
| `_4` | 03 点名与课后 / 点名完成页 |
| `_5` | 03 点名与课后 / 点名异常确认 |
| `_6` | 08 课程管理 / 套餐轻入口 |
| `_7` | 10 物品费用 / 采购入库 |
| `_8` | 06 我的与更多工具 / 我的页 |
| `_9` | 07 班级管理 / 升班 / 结业 |
| `_10` | 07 班级管理 / 新增 / 编辑班级 |
| `_11` | 12 场地管理 / 代预约 |
| `_12` | 11 会员卡 / 会员卡详情 |
| `_13` | 08 课程管理 / 课程列表 |
| `_14` | 03 点名与课后 / 点名页 |
| `_15` | 03 点名与课后 / 课后点评 |
| `_16` | 06 我的与更多工具 / 设置页 |
| `_17` | 02 课表与排课 / 课表首页 |
| `_18` | 12 场地管理 / 预约详情 / 核销 |
| `_19` | 11 会员卡 / 发放记录 |
| `_20` | 07 班级管理 / 班级列表 |
| `_21` | 10 物品费用 / 库存流水 |
| `_22` | 02 课表与排课 / 课程详情 / 课次详情 |
| `_23` | 06 我的与更多工具 / 更多工具页 |
| `_24` | 08 课程管理 / 新增 / 编辑课程 |
| `_25` | 01 登录与今日工作台 / 今日工作台 |
| `_26` | 12 场地管理 / 场地首页 |
| `_27` | 10 物品费用 / 新增 / 编辑物品 |
| `_28` | 06 我的与更多工具 / 班级管理轻入口 |
| `_29` | 06 我的与更多工具 / 老师管理轻入口 |
| `_30` | 12 场地管理 / 订场时间表 |
| `_31` | 05 AI 错题本 / 拍照上传 |
| `_32` | 04 学员管理 / 联系家长 |
| `_33` | 11 会员卡 / 学员持卡详情 |
| `_34` | 06 我的与更多工具 / 课程管理轻入口 |
| `_35` | 05 AI 错题本 / 错题详情 |
| `_36` | 09 老师管理 / 老师课表 |
| `_37` | 09 老师管理 / 新增 / 编辑老师 |
| `_38` | 10 物品费用 / 物品列表 |
| `_39` | 05 AI 错题本 / 编辑解析 |
| `_40` | 10 物品费用 / 费用项目 |
| `_41` | 02 课表与排课 / 调课页 |
| `_42` | 07 班级管理 / 添加学员 |
| `_43` | 04 学员管理 / 学员请假 |
| `_44` | 06 我的与更多工具 / 经营管理轻入口 |
| `_45` | 04 学员管理 / 报名 / 续费 |
| `_46` | 05 AI 错题本 / 错题本首页 |
| `_47` | 02 课表与排课 / 新增排课入口 |
| `_48` | 07 班级管理 / 班级详情 |
| `_49` | 11 会员卡 / 发放会员卡 |
| `_50` | 12 场地管理 / 锁场 |
| `_51` | 09 老师管理 / 老师详情 |
| `_52` | 02 课表与排课 / 排课冲突 |
| `_53` | 04 学员管理 / 学员详情 |
| `_54` | 01 登录与今日工作台 / 登录页 |
| `_55` | 02 课表与排课 / 日历排课 |
| `_56` | 10 物品费用 / 物品费用首页 |
| `_57` | 08 课程管理 / 课程详情 |
| `_58` | 09 老师管理 / 老师列表 |
| `_59` | 02 课表与排课 / 规则排课 |
| `ai` | 05 AI 错题本 / AI 分析中 |

## 建议优先复核的问题页面

这些页面已经能对应到业务页面，但存在英文标题、英文按钮、英文示例数据或导航文字不统一，建议让 Stitch 二次处理：

- `_1`：取消预约，英文界面。
- `_7`：采购入库，英文界面。
- `_11`：代预约，英文界面。
- `_18`：预约详情 / 核销，英文界面。
- `_21`：库存流水，部分英文示例数据。
- `_26`：场地首页，英文界面。
- `_27`：新增 / 编辑物品，部分英文文案。
- `_30`：订场时间表，英文界面。
- `_36`：老师课表，标题和底部导航部分英文。
- `_37`：新增老师，标题含英文。
- `_38`：物品列表，标题含英文。
- `_50`：锁场，英文界面。
- `_51`：老师详情，标题和部分底部导航英文。
- `_56`：物品费用首页，标题和底部导航部分英文。
- `_58`：老师列表，标题和底部导航部分英文。

可直接给 Stitch 的修正提示词：

```text
请基于当前页面保持布局、颜色、卡片、按钮大小和组件结构不变，只把页面标题、按钮、标签、说明文字、示例数据全部改成中文老师帮业务文案。不要新增页面，不要改变页面结构，不要改颜色和风格。
```
