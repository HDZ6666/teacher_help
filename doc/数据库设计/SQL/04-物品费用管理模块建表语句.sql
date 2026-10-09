-- =============================================
-- 物品费用管理模块 - 数据库建表语句
-- 模块代码: inventory
-- 创建日期: 2025-01-17
-- 版本: V2.1 (采购与库存分离 + 费用课程关联)
-- =============================================

-- ----------------------------
-- 1. 物品基本信息表 (ast_item)
-- ----------------------------
DROP TABLE IF EXISTS `ast_item`;
CREATE TABLE `ast_item` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `item_no` VARCHAR(50) DEFAULT NULL COMMENT '物品编号',
  `item_name` VARCHAR(100) NOT NULL COMMENT '物品名称',
  `item_type` TINYINT(1) NOT NULL COMMENT '物品类型(1=实物,2=虚拟)',
  `category` VARCHAR(50) DEFAULT NULL COMMENT '物品分类',
  `unit` VARCHAR(20) DEFAULT NULL COMMENT '单位(本/个/套/份等)',
  `default_price` DECIMAL(10,2) DEFAULT NULL COMMENT '默认售卖单价',
  `image_url` VARCHAR(500) DEFAULT NULL COMMENT '物品图片',
  `spec1_name` VARCHAR(50) DEFAULT NULL COMMENT '规格1名称(如:颜色)',
  `spec1_values` VARCHAR(500) DEFAULT NULL COMMENT '规格1值列表(逗号分隔,如:黑色,白色)',
  `spec2_name` VARCHAR(50) DEFAULT NULL COMMENT '规格2名称(如:码数)',
  `spec2_values` VARCHAR(500) DEFAULT NULL COMMENT '规格2值列表(逗号分隔,如:X,L,XL)',
  `total_stock` INT DEFAULT 0 COMMENT '总库存',
  `available_stock` INT DEFAULT 0 COMMENT '可用库存',
  `enable_stock` SMALLINT DEFAULT 1 COMMENT '是否开启库存(0=关闭 1=开启)',
  `warning_stock` INT DEFAULT 0 COMMENT '库存预警数量',
  `online_sale` SMALLINT DEFAULT 0 COMMENT '线上售卖状态(0=关闭 1=开启)',
  `status` TINYINT(1) DEFAULT 1 COMMENT '启用状态(0=停用,1=启用)',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` VARCHAR(64) DEFAULT '' COMMENT '更新者',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_item_no` (`item_no`),
  KEY `idx_item_name` (`item_name`),
  KEY `idx_item_type` (`item_type`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品基本信息表';

-- ----------------------------
-- 2. 物品SKU表 (ast_item_sku)
-- ----------------------------
DROP TABLE IF EXISTS `ast_item_sku`;
CREATE TABLE `ast_item_sku` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `item_id` BIGINT NOT NULL COMMENT '物品ID',
  `sku_no` VARCHAR(50) DEFAULT NULL COMMENT 'SKU编号',
  `sku_name` VARCHAR(100) NOT NULL COMMENT 'SKU名称(如:黑色, X)',
  `spec1_value` VARCHAR(50) DEFAULT NULL COMMENT '规格1值(如:黑色)',
  `spec2_value` VARCHAR(50) DEFAULT NULL COMMENT '规格2值(如:X)',
  `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '售卖价格',
  `cost_price` DECIMAL(10,2) DEFAULT 0.00 COMMENT '成本价',
  `stock` INT DEFAULT 0 COMMENT '库存数量',
  `available_stock` INT DEFAULT 0 COMMENT '可用库存',
  `status` TINYINT(1) DEFAULT 1 COMMENT '启用状态(0=停用,1=启用)',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` VARCHAR(64) DEFAULT '' COMMENT '更新者',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sku_no` (`sku_no`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_spec1_value` (`spec1_value`),
  KEY `idx_spec2_value` (`spec2_value`),
  KEY `idx_status` (`status`),
  KEY `idx_item_spec` (`item_id`, `spec1_value`, `spec2_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品SKU表';

-- ----------------------------
-- 3. 采购单主表 (ast_purchase_order)
-- ----------------------------
DROP TABLE IF EXISTS `ast_purchase_order`;
CREATE TABLE `ast_purchase_order` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_no` VARCHAR(50) NOT NULL COMMENT '采购单号',
  `purchase_date` DATE NOT NULL COMMENT '采购日期',
  `supplier_id` BIGINT DEFAULT NULL COMMENT '供应商ID',
  `supplier_name` VARCHAR(100) DEFAULT NULL COMMENT '供应商名称',
  `total_quantity` INT DEFAULT 0 COMMENT '总数量',
  `total_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '总金额',
  `payment_method` VARCHAR(20) DEFAULT NULL COMMENT '支付方式(cash=现金,wechat=微信,alipay=支付宝,bank=银行卡)',
  `account_id` BIGINT DEFAULT NULL COMMENT '账户ID',
  `account_name` VARCHAR(100) DEFAULT NULL COMMENT '账户名称',
  `year_book` VARCHAR(20) DEFAULT NULL COMMENT '年度账本',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态(0=草稿,1=已完成,2=已取消)',
  `operator_id` BIGINT DEFAULT NULL COMMENT '操作人ID',
  `operator_name` VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` VARCHAR(64) DEFAULT '' COMMENT '更新者',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_purchase_date` (`purchase_date`),
  KEY `idx_supplier_id` (`supplier_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购单主表';

-- ----------------------------
-- 4. 采购单明细表 (ast_purchase_order_item)
-- ----------------------------
DROP TABLE IF EXISTS `ast_purchase_order_item`;
CREATE TABLE `ast_purchase_order_item` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_id` BIGINT NOT NULL COMMENT '采购单ID',
  `item_id` BIGINT NOT NULL COMMENT '物品ID',
  `item_name` VARCHAR(100) NOT NULL COMMENT '物品名称(冗余)',
  `sku_id` BIGINT NOT NULL COMMENT 'SKU ID',
  `sku_name` VARCHAR(100) NOT NULL COMMENT 'SKU名称(冗余)',
  `unit_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '采购单价',
  `quantity` INT NOT NULL DEFAULT 0 COMMENT '采购数量',
  `total_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '小计金额',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_sku_id` (`sku_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购单明细表';

-- ----------------------------
-- 5. 物品出入库记录表 (ast_item_stock_record)
-- ----------------------------
DROP TABLE IF EXISTS `ast_item_stock_record`;
CREATE TABLE `ast_item_stock_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `record_no` VARCHAR(50) NOT NULL COMMENT '流水号',
  `item_id` BIGINT NOT NULL COMMENT '物品ID',
  `item_name` VARCHAR(100) NOT NULL COMMENT '物品名称(冗余)',
  `sku_id` BIGINT NOT NULL COMMENT 'SKU ID',
  `sku_name` VARCHAR(100) NOT NULL COMMENT 'SKU名称(冗余)',
  `business_type` VARCHAR(20) NOT NULL COMMENT '业务类型(purchase=采购,receive=领用,return=退领,inventory=盘点)',
  `quantity` INT NOT NULL COMMENT '数量(正数=入库,负数=出库)',
  `stock_before` INT DEFAULT 0 COMMENT '操作前库存',
  `stock_after` INT DEFAULT 0 COMMENT '操作后库存',
  `source_type` VARCHAR(20) DEFAULT NULL COMMENT '来源类型(purchase=采购单,receive=领用,return=退领,inventory=盘点)',
  `source_id` BIGINT DEFAULT NULL COMMENT '来源单据ID(如采购单ID)',
  `related_id` BIGINT DEFAULT NULL COMMENT '关联ID(学员ID/教师ID等)',
  `related_name` VARCHAR(50) DEFAULT NULL COMMENT '关联名称',
  `related_type` VARCHAR(20) DEFAULT NULL COMMENT '关联类型(teacher=教师,student=学生,admin=管理员)',
  `operator_id` BIGINT DEFAULT NULL COMMENT '操作人ID',
  `operator_name` VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
  `record_date` DATE NOT NULL COMMENT '记录日期',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_record_no` (`record_no`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_sku_id` (`sku_id`),
  KEY `idx_business_type` (`business_type`),
  KEY `idx_source` (`source_type`, `source_id`),
  KEY `idx_related_id` (`related_id`),
  KEY `idx_record_date` (`record_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物品出入库记录表';

-- ----------------------------
-- 6. 费用项目表 (ast_fee_item)
-- ----------------------------
DROP TABLE IF EXISTS `ast_fee_item`;
CREATE TABLE `ast_fee_item` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `fee_name` VARCHAR(100) NOT NULL COMMENT '费用名称',
  `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '费用金额',
  `online_sale` SMALLINT DEFAULT 0 COMMENT '线上售卖状态(0=关闭 1=开启)',
  `status` TINYINT(1) DEFAULT 1 COMMENT '启用状态(0=停用,1=启用)',
  `sort` INT DEFAULT 0 COMMENT '排序',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` VARCHAR(64) DEFAULT '' COMMENT '更新者',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `del_flag` TINYINT(1) DEFAULT 0 COMMENT '删除标志(0=未删除,1=已删除)',
  PRIMARY KEY (`id`),
  KEY `idx_fee_name` (`fee_name`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='费用项目表';

-- ----------------------------
-- 7. 费用课程关联表 (ast_fee_course)
-- ----------------------------
DROP TABLE IF EXISTS `ast_fee_course`;
CREATE TABLE `ast_fee_course` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `fee_id` BIGINT NOT NULL COMMENT '费用ID',
  `course_id` BIGINT NOT NULL COMMENT '课程ID',
  `course_name` VARCHAR(100) DEFAULT NULL COMMENT '课程名称(冗余)',
  `create_by` VARCHAR(64) DEFAULT '' COMMENT '创建者',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_fee_course` (`fee_id`, `course_id`),
  KEY `idx_fee_id` (`fee_id`),
  KEY `idx_course_id` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='费用课程关联表';

-- =============================================
-- 示例数据
-- =============================================

-- ----------------------------
-- 1. 物品基本信息示例数据
-- ----------------------------
-- 示例1: 双规格物品（T恤）
INSERT INTO `ast_item` (`item_no`, `item_name`, `item_type`, `category`, `unit`, `default_price`, `spec1_name`, `spec1_values`, `spec2_name`, `spec2_values`, `status`, `create_by`, `create_time`, `remark`)
VALUES ('ITEM001', 'T恤', 1, '服装', '件', 99.00, '颜色', '黑色,白色', '码数', 'X,L,XL', 1, 'admin', NOW(), '校服T恤');

-- 示例2: 单规格物品（毛包）
INSERT INTO `ast_item` (`item_no`, `item_name`, `item_type`, `category`, `unit`, `default_price`, `spec1_name`, `spec1_values`, `status`, `create_by`, `create_time`, `remark`)
VALUES ('ITEM002', '毛包', 1, '配饰', '个', 50.00, '尺寸', '小号,中号,大号', 1, 'admin', NOW(), '学生毛包');

-- 示例3: 无规格物品（教材）
INSERT INTO `ast_item` (`item_no`, `item_name`, `item_type`, `category`, `unit`, `default_price`, `status`, `create_by`, `create_time`, `remark`)
VALUES ('ITEM003', '数学教材', 1, '教材', '本', 30.00, 1, 'admin', NOW(), '小学数学教材');

-- ----------------------------
-- 2. SKU示例数据
-- ----------------------------
-- T恤的6个SKU（笛卡尔积：2种颜色 × 3种码数 = 6个SKU）
INSERT INTO `ast_item_sku` (`item_id`, `sku_no`, `sku_name`, `spec1_value`, `spec2_value`, `price`, `stock`, `available_stock`, `status`, `create_by`, `create_time`) VALUES
(1, 'SKU001', '黑色, X', '黑色', 'X', 99.00, 0, 0, 1, 'admin', NOW()),
(1, 'SKU002', '黑色, L', '黑色', 'L', 99.00, 0, 0, 1, 'admin', NOW()),
(1, 'SKU003', '黑色, XL', '黑色', 'XL', 99.00, 0, 0, 1, 'admin', NOW()),
(1, 'SKU004', '白色, X', '白色', 'X', 99.00, 0, 0, 1, 'admin', NOW()),
(1, 'SKU005', '白色, L', '白色', 'L', 99.00, 0, 0, 1, 'admin', NOW()),
(1, 'SKU006', '白色, XL', '白色', 'XL', 99.00, 0, 0, 1, 'admin', NOW());

-- 毛包的3个SKU（单规格：3个SKU）
INSERT INTO `ast_item_sku` (`item_id`, `sku_no`, `sku_name`, `spec1_value`, `price`, `stock`, `available_stock`, `status`, `create_by`, `create_time`) VALUES
(2, 'SKU007', '小号', '小号', 50.00, 0, 0, 1, 'admin', NOW()),
(2, 'SKU008', '中号', '中号', 50.00, 0, 0, 1, 'admin', NOW()),
(2, 'SKU009', '大号', '大号', 50.00, 0, 0, 1, 'admin', NOW());

-- 数学教材的1个默认SKU（无规格：1个默认SKU）
INSERT INTO `ast_item_sku` (`item_id`, `sku_no`, `sku_name`, `price`, `stock`, `available_stock`, `status`, `create_by`, `create_time`) VALUES
(3, 'SKU010', '默认', 30.00, 0, 0, 1, 'admin', NOW());

-- ----------------------------
-- 3. 采购单示例数据
-- ----------------------------
-- 采购单主表
INSERT INTO `ast_purchase_order` (`order_no`, `purchase_date`, `supplier_name`, `total_quantity`, `total_amount`, `payment_method`, `account_name`, `year_book`, `status`, `operator_name`, `create_by`, `create_time`, `remark`) VALUES
('PO20250117001', '2025-01-17', '校服供应商', 15, 1200.00, 'wechat', '微信支付账户', '2025', 1, '张老师', 'admin', NOW(), '采购校服T恤');

-- 采购单明细表
INSERT INTO `ast_purchase_order_item` (`order_id`, `item_id`, `item_name`, `sku_id`, `sku_name`, `unit_price`, `quantity`, `total_amount`, `create_by`, `create_time`, `remark`) VALUES
(1, 1, 'T恤', 1, '黑色, X', 80.00, 10, 800.00, 'admin', NOW(), '采购黑色X码T恤'),
(1, 1, 'T恤', 2, '黑色, L', 80.00, 5, 400.00, 'admin', NOW(), '采购黑色L码T恤');

-- ----------------------------
-- 4. 库存流水示例数据
-- ----------------------------
-- 采购入库流水（关联采购单）
INSERT INTO `ast_item_stock_record` (`record_no`, `item_id`, `item_name`, `sku_id`, `sku_name`, `business_type`, `quantity`, `stock_before`, `stock_after`, `source_type`, `source_id`, `operator_name`, `record_date`, `create_by`, `create_time`, `remark`) VALUES
('SR20250117001', 1, 'T恤', 1, '黑色, X', 'purchase', 10, 0, 10, 'purchase', 1, '张老师', '2025-01-17', 'admin', NOW(), '采购入库'),
('SR20250117002', 1, 'T恤', 2, '黑色, L', 'purchase', 5, 0, 5, 'purchase', 1, '张老师', '2025-01-17', 'admin', NOW(), '采购入库');

-- 领用出库流水（学生领用）
INSERT INTO `ast_item_stock_record` (`record_no`, `item_id`, `item_name`, `sku_id`, `sku_name`, `business_type`, `quantity`, `stock_before`, `stock_after`, `source_type`, `related_id`, `related_name`, `related_type`, `operator_name`, `record_date`, `create_by`, `create_time`, `remark`) VALUES
('SR20250117003', 1, 'T恤', 1, '黑色, X', 'receive', -2, 10, 8, 'receive', 1001, '张三', 'student', '李老师', '2025-01-17', 'admin', NOW(), '学生领用校服');

-- 退领入库流水（学生退领）
INSERT INTO `ast_item_stock_record` (`record_no`, `item_id`, `item_name`, `sku_id`, `sku_name`, `business_type`, `quantity`, `stock_before`, `stock_after`, `source_type`, `related_id`, `related_name`, `related_type`, `operator_name`, `record_date`, `create_by`, `create_time`, `remark`) VALUES
('SR20250117004', 1, 'T恤', 1, '黑色, X', 'return', 1, 8, 9, 'return', 1001, '张三', 'student', '李老师', '2025-01-18', 'admin', NOW(), '学生退领校服');

-- ----------------------------
-- 5. 费用项目示例数据
-- ----------------------------
INSERT INTO `ast_fee_item` (`fee_name`, `amount`, `status`, `sort`, `create_by`, `create_time`, `remark`) VALUES
('教材费', 22.00, 1, 1, 'admin', NOW(), '教材费用'),
('教材费', 60.00, 1, 2, 'admin', NOW(), '教材费用'),
('图书费', 100.00, 1, 3, 'admin', NOW(), '图书费用'),
('比赛费', 80.00, 1, 4, 'admin', NOW(), '比赛报名费'),
('活动费', 160.00, 1, 5, 'admin', NOW(), '活动费用'),
('围棋费', 200.00, 0, 6, 'admin', NOW(), '围棋课程费用（已停用）'),
('跳绳费', 120.00, 1, 7, 'admin', NOW(), '跳绳课程费用'),
('理科费', 300.00, 1, 8, 'admin', NOW(), '理科课程费用'),
('绘画费', 500.00, 1, 9, 'admin', NOW(), '绘画课程费用'),
('比赛费用', 25.00, 1, 10, 'admin', NOW(), '比赛报名费'),
('住宿费', 180.00, 1, 11, 'admin', NOW(), '住宿费用');

-- ----------------------------
-- 6. 费用课程关联示例数据
-- ----------------------------
-- 比赛费（¥80）关联3个羽毛球课程
INSERT INTO `ast_fee_course` (`fee_id`, `course_id`, `course_name`, `create_by`, `create_time`) VALUES
(4, 101, '羽毛球一对一课程', 'admin', NOW()),
(4, 102, '羽毛球一对多课程', 'admin', NOW()),
(4, 103, '羽毛球一对一课程（高级班）', 'admin', NOW());

-- 活动费（¥160）关联2个绘画课程
INSERT INTO `ast_fee_course` (`fee_id`, `course_id`, `course_name`, `create_by`, `create_time`) VALUES
(5, 201, '绘画基础班', 'admin', NOW()),
(5, 202, '绘画进阶班', 'admin', NOW());

-- 跳绳费（¥120）关联2个跳绳课程
INSERT INTO `ast_fee_course` (`fee_id`, `course_id`, `course_name`, `create_by`, `create_time`) VALUES
(7, 301, '跳绳入门', 'admin', NOW()),
(7, 302, '跳绳提高', 'admin', NOW());

-- 理科费（¥300）关联3个理科课程
INSERT INTO `ast_fee_course` (`fee_id`, `course_id`, `course_name`, `create_by`, `create_time`) VALUES
(8, 401, '数学一对一', 'admin', NOW()),
(8, 402, '物理一对一', 'admin', NOW()),
(8, 403, '化学一对一', 'admin', NOW());

-- 住宿费（¥180）关联2个住宿课程
INSERT INTO `ast_fee_course` (`fee_id`, `course_id`, `course_name`, `create_by`, `create_time`) VALUES
(11, 501, '初月住宿', 'admin', NOW()),
(11, 502, '龙门住宿', 'admin', NOW());
