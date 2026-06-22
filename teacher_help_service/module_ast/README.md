# 物品费用管理模块 (module_ast)

物品费用管理模块负责维护机构的物品档案、SKU、采购入库、领用/退领、盘点流水和费用项目。当前模块已经具备独立管理与演示能力，后续完整业务闭环还需要继续对接课程套餐、报名订单和支付流水。

## 已实现范围

- 物品管理：列表、详情、新增、编辑、删除、启停、库存预警、线上售卖、绑定课程。
- SKU 管理：按规格生成 SKU，保存 SKU 价格、库存、状态和规格文本。
- 出入库管理：采购入库、领用出库、退领入库、盘点、流水查询、详情、作废回滚、导出。
- 采购导入：下载采购单模板，按 Excel 导入采购明细并生成入库流水。
- 费用项目：列表、详情、新增、编辑、删除、启停、线上售卖、绑定课程。
- 选择项接口：物品/SKU 选项、领用/退领角色姓名选项。

## 主要接口

| 功能 | 方法 | 路径 | 权限标识 |
| --- | --- | --- | --- |
| 物品列表 | GET | `/ast/item/list` | `ast:item:list` |
| 物品详情 | GET | `/ast/item/{item_id}` | `ast:item:query` |
| 新增物品 | POST | `/ast/item` | `ast:item:add` |
| 编辑物品 | PUT | `/ast/item` | `ast:item:edit` |
| 删除物品 | DELETE | `/ast/item/{item_ids}` | `ast:item:remove` |
| SKU 列表 | GET | `/ast/inventory/item/{item_id}/skus` | `ast:item:query` 或 `ast:inventory:list` |
| 可选物品 | GET | `/ast/inventory/items/options` | `ast:item:list` 或 `ast:inventory:list` |
| 角色姓名选项 | GET | `/ast/inventory/role-options` | `ast:inventory:add` 或 `ast:inventory:list` |
| 出入库列表 | GET | `/ast/inventory/stock/list` | `ast:inventory:list` |
| 出入库详情 | GET | `/ast/inventory/stock/{record_id}` | `ast:inventory:query` |
| 出入库作废 | PUT | `/ast/inventory/stock/{record_id}/void` | `ast:inventory:edit` 或 `ast:inventory:add` |
| 出入库导出 | POST | `/ast/inventory/stock/export` | `ast:inventory:export` 或 `ast:inventory:list` |
| 采购入库 | POST | `/ast/inventory/purchase` | `ast:inventory:add` |
| 采购模板 | POST | `/ast/inventory/purchase/import/template` | `ast:inventory:add` 或 `ast:inventory:export` |
| 采购导入 | POST | `/ast/inventory/purchase/import` | `ast:inventory:add` 或 `ast:inventory:import` |
| 领用 | POST | `/ast/inventory/receive` | `ast:inventory:add` |
| 退领 | POST | `/ast/inventory/return` | `ast:inventory:add` |
| 盘点 | POST | `/ast/inventory/inventory` | `ast:inventory:add` |
| 费用列表 | GET | `/ast/inventory/fee/list` | `ast:fee:list` |
| 费用详情 | GET | `/ast/inventory/fee/{fee_id}` | `ast:fee:query` |
| 新增费用 | POST | `/ast/inventory/fee` | `ast:fee:add` |
| 编辑费用 | PUT | `/ast/inventory/fee` | `ast:fee:edit` |
| 费用启停 | PUT | `/ast/inventory/fee/changeStatus` | `ast:fee:edit` |
| 删除费用 | DELETE | `/ast/inventory/fee/{fee_ids}` | `ast:fee:remove` |

## 前端页面

- 页面：`teacher_help_admin/src/views/assistant/inventory/index.vue`
- API：`teacher_help_admin/src/api/assistant/inventory.js`
- 风格：RuoYi Vue3 + Element Plus，使用查询表单、工具栏、表格、分页、弹窗和抽屉。

## 数据字典

- `ast_item_type`：物品类型。
- `ast_business_type`：业务类型，包含 `purchase`、`receive`、`return`、`inventory`。
- `ast_source_type`：来源类型。
- `ast_purchase_status`：采购单状态。
- `ast_role_type`：领用/退领角色类型。
- `ast_payment_method`：支付方式。

## 后续待联动

- 与课程套餐模块联动：物品和费用作为套餐明细参与售卖方案。
- 与报名订单模块联动：报名购买物品后自动生成销售出库流水。
- 与支付/财务模块联动：采购付款、报名收款和费用消费进入统一财务账。
- 与学员报读模块联动：报读记录沉淀课程、物品、费用、课时和有效期快照。
