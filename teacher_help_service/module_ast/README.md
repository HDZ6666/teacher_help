# 物品费用管理模块 (module_ast)

## 📋 模块概述

物品费用管理模块负责管理教育培训机构的物品库存和费用项目。

### 功能模块

- ✅ **物品管理** - 已实现
- ⏳ **SKU管理** - 待实现
- ⏳ **采购管理** - 待实现
- ⏳ **出入库管理** - 待实现
- ⏳ **费用项目管理** - 待实现

---

## 🎯 已实现功能

### 1. 物品管理 (ast_item)

#### API 接口列表

| 接口 | 方法 | 路径 | 权限标识 | 说明 |
|------|------|------|---------|------|
| 获取物品列表 | GET | `/ast/item/list` | `ast:item:list` | 分页查询物品列表 |
| 获取物品详情 | GET | `/ast/item/{item_id}` | `ast:item:query` | 根据ID查询物品详情 |
| 新增物品 | POST | `/ast/item` | `ast:item:add` | 新增物品信息 |
| 编辑物品 | PUT | `/ast/item` | `ast:item:edit` | 编辑物品信息 |
| 删除物品 | DELETE | `/ast/item/{item_ids}` | `ast:item:remove` | 删除物品（逻辑删除） |

#### 查询参数

```json
{
  "pageNum": 1,
  "pageSize": 10,
  "itemName": "物品名称（模糊查询）",
  "itemType": 1,  // 1=实物 2=虚拟
  "category": "物品分类（模糊查询）",
  "status": 1,  // 0=停用 1=启用
  "beginTime": "2025-01-01",
  "endTime": "2025-12-31"
}
```

#### 响应数据格式

**列表响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "success": true,
  "data": {
    "total": 3,
    "rows": [
      {
        "id": 1,
        "itemNo": "ITEM001",
        "itemName": "T恤",
        "itemType": 1,
        "itemTypeLabel": "实物",
        "category": "服装",
        "unit": "件",
        "defaultPrice": 99.00,
        "totalStock": 0,
        "availableStock": 0,
        "status": 1,
        "createTime": "2025-11-18T10:31:19",
        "remark": "校服T恤"
      }
    ],
    "pageNum": 1,
    "pageSize": 10
  }
}
```

**详情响应**：
```json
{
  "code": 200,
  "msg": "操作成功",
  "success": true,
  "data": {
    "id": 1,
    "itemNo": "ITEM001",
    "itemName": "T恤",
    "itemType": 1,
    "itemTypeLabel": "实物",
    "category": "服装",
    "unit": "件",
    "defaultPrice": 99.00,
    "imageUrl": null,
    "spec1Name": "颜色",
    "spec1Values": "黑色,白色",
    "spec2Name": "码数",
    "spec2Values": "X,L,XL",
    "totalStock": 0,
    "availableStock": 0,
    "status": 1,
    "createBy": "admin",
    "createTime": "2025-11-18T10:31:19",
    "updateBy": "",
    "updateTime": "2025-11-18T10:31:19",
    "remark": "校服T恤"
  }
}
```

---

## 📁 模块结构

```
module_ast/
├── __init__.py
├── README.md
├── controller/
│   └── ast_item_controller.py      # 物品管理控制器
├── service/
│   └── ast_item_service.py         # 物品管理服务层
├── dao/
│   └── ast_item_dao.py              # 物品管理数据访问层
└── entity/
    ├── do/
    │   ├── ast_item_do.py           # 物品数据库实体
    │   └── ast_item_sku_do.py       # SKU数据库实体
    └── vo/
        └── ast_item_vo.py           # 物品视图对象
```

---

## 🔧 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy (异步)
- **验证**: Pydantic
- **数据库**: MySQL
- **架构**: 四层架构（Controller → Service → DAO → Entity）

---

## 📝 开发规范

遵循项目统一的编码规范，详见 `docs/code_architecture_style_analysis.md`

### 命名规范

- **模块前缀**: `ast_` (asset 的缩写)
- **路由前缀**: `/ast/`
- **权限标识**: `ast:{功能}:{操作}`
- **表名**: `ast_{entity}` (复数形式)

### 数据字典

需要在系统字典中配置以下字典类型：

- `ast_item_type` - 物品类型（1=实物 2=虚拟）
- `ast_business_type` - 业务类型（purchase/receive/return/inventory）
- `ast_source_type` - 来源类型
- `ast_purchase_status` - 采购单状态
- `ast_role_type` - 角色类型
- `ast_payment_method` - 支付方式

---

## 🚀 快速开始

### 1. 启动服务

```bash
python app.py
```

### 2. 访问 API 文档

```
http://localhost:9099/docs
```

### 3. 测试接口

使用 Swagger UI 或 Postman 测试接口，需要先登录获取 token。

---

## ✅ 已完成

- [x] 物品管理 CRUD 接口
- [x] 分页查询
- [x] 字典数据转换
- [x] 数据权限控制
- [x] 操作日志记录
- [x] 参数验证

## 📅 待开发

- [ ] SKU 管理接口
- [ ] 采购管理接口
- [ ] 出入库管理接口
- [ ] 费用项目管理接口
- [ ] 导出功能
- [ ] 批量导入功能

