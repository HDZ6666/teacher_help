-- ----------------------------
-- 老师帮 教学域（teach_*）建表语句
-- 由 sql/gen_teach_sql.py 根据 SQLAlchemy 实体生成，生成日期 2026-10-09
-- 方言：MySQL 8.x；按外键依赖顺序排列；使用 IF NOT EXISTS，可在已有库上重复执行（不会修改已存在的表）
-- 修改实体后请重新执行 python sql/gen_teach_sql.py 生成，不要手工编辑本文件
-- ----------------------------

SET NAMES utf8mb4;

-- ----------------------------
-- teach_base_users 基础用户表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_base_users (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  phone VARCHAR(20) NOT NULL COMMENT '手机号，唯一登录凭证',
  password_hash VARCHAR(255) NOT NULL COMMENT '加盐哈希后的密码',
  user_type VARCHAR(1) NOT NULL COMMENT '用户类型（0教师 1家长）',
  status VARCHAR(1) NOT NULL COMMENT '帐号状态（0正常 1停用）',
  last_login_at DATETIME COMMENT '最后登录时间',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (phone)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='基础用户表';

-- ----------------------------
-- teach_card 会员卡模板表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_card (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  card_no VARCHAR(50) COMMENT '卡编号',
  card_name VARCHAR(100) NOT NULL COMMENT '卡名称',
  card_type VARCHAR(20) NOT NULL COMMENT '卡类型(course=课程卡 venue_discount=场地折扣卡)',
  initial_count INTEGER COMMENT '初始次数(课程卡)',
  valid_days INTEGER COMMENT '有效天数',
  effect_type VARCHAR(20) COMMENT '生效方式(immediate=立即 first_use=首次使用后)',
  discount_rate DECIMAL(5, 2) COMMENT '折扣率(场地折扣卡)',
  cover_image VARCHAR(500) COMMENT '封面图',
  price DECIMAL(10, 2) COMMENT '售价',
  online_sale SMALLINT COMMENT '线上售卖状态(0=未售卖 1=售卖)',
  description VARCHAR(500) COMMENT '卡说明',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (card_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='会员卡模板表';

-- ----------------------------
-- teach_card_course 会员卡适用课程表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_card_course (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  card_id INTEGER NOT NULL COMMENT '卡ID',
  course_id INTEGER NOT NULL COMMENT '课程ID',
  course_name VARCHAR(100) COMMENT '课程名称快照',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='会员卡适用课程表';

-- ----------------------------
-- teach_card_grant 会员卡发放记录表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_card_grant (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  grant_no VARCHAR(50) COMMENT '发放编号',
  card_id INTEGER NOT NULL COMMENT '卡ID',
  card_name VARCHAR(100) COMMENT '卡名称快照',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) COMMENT '学员姓名快照',
  grant_count INTEGER COMMENT '发放次数',
  remaining_count INTEGER COMMENT '剩余次数',
  valid_start_date DATE COMMENT '生效日期',
  valid_end_date DATE COMMENT '失效日期',
  grant_status SMALLINT COMMENT '发放状态(1=有效 2=过期 3=用完 4=作废)',
  operator_id INTEGER COMMENT '操作人ID',
  operator_name VARCHAR(50) COMMENT '操作人姓名',
  grant_time DATETIME COMMENT '发放时间',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (grant_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='会员卡发放记录表';

-- ----------------------------
-- teach_card_log 会员卡操作记录表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_card_log (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  card_id INTEGER COMMENT '卡ID',
  grant_id INTEGER COMMENT '发放记录ID',
  student_id INTEGER COMMENT '学员ID',
  action VARCHAR(20) NOT NULL COMMENT '操作类型(grant=发放 consume=消耗 void=作废 expire=过期)',
  change_count INTEGER COMMENT '变动次数',
  before_count INTEGER COMMENT '变动前次数',
  after_count INTEGER COMMENT '变动后次数',
  operator_id INTEGER COMMENT '操作人ID',
  operator_name VARCHAR(50) COMMENT '操作人姓名',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='会员卡操作记录表';

-- ----------------------------
-- teach_course 课程基础信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_course (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  course_no VARCHAR(50) COMMENT '课程编号',
  course_name VARCHAR(100) NOT NULL COMMENT '课程名称',
  course_type VARCHAR(32) NOT NULL COMMENT '课程类型(one_to_many=一对多 one_to_one=一对一)',
  schedule_color VARCHAR(20) COMMENT '课表颜色',
  grade VARCHAR(50) COMMENT '年级',
  grade_label VARCHAR(50) COMMENT '年级名称',
  subject VARCHAR(50) COMMENT '科目',
  subject_label VARCHAR(50) COMMENT '科目名称',
  semester VARCHAR(50) COMMENT '学期',
  semester_label VARCHAR(50) COMMENT '学期名称',
  student_count INTEGER COMMENT '在读学员数',
  online_sale SMALLINT COMMENT '线上售卖状态(0=未售卖 1=售卖)',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (course_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='课程基础信息表';

-- ----------------------------
-- teach_course_package 课程套餐基础信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_course_package (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  package_no VARCHAR(50) COMMENT '套餐编号',
  package_name VARCHAR(100) NOT NULL COMMENT '套餐名称',
  total_price DECIMAL(10, 2) NOT NULL COMMENT '套餐总价',
  online_sale SMALLINT COMMENT '线上售卖状态(0=未售卖 1=售卖)',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (package_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='课程套餐基础信息表';

-- ----------------------------
-- teach_grades 教学年级字典表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_grades (
  grade_id INTEGER NOT NULL COMMENT '年级ID' AUTO_INCREMENT,
  grade_code VARCHAR(64) NOT NULL COMMENT '年级编码（唯一标识）',
  grade_name VARCHAR(50) NOT NULL COMMENT '年级名称',
  education_level VARCHAR(50) COMMENT '教育阶段（小学、初中、高中）',
  grade_sort INTEGER COMMENT '显示顺序',
  status CHAR(1) COMMENT '状态（0正常 1停用）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (grade_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='教学年级字典表';

-- ----------------------------
-- teach_leave_application 请假申请表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_leave_application (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  leave_no VARCHAR(50) COMMENT '请假编号',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) NOT NULL COMMENT '学员姓名快照',
  class_id INTEGER COMMENT '班级ID',
  class_name VARCHAR(100) COMMENT '班级名称快照',
  course_id INTEGER COMMENT '课程ID',
  course_name VARCHAR(100) COMMENT '课程名称快照',
  event_id INTEGER COMMENT '关联课次(排课事件)ID',
  leave_type SMALLINT NOT NULL COMMENT '请假类型(1=事假 2=病假 3=其他)',
  leave_date DATE NOT NULL COMMENT '请假日期',
  leave_reason VARCHAR(500) COMMENT '请假事由',
  leave_image VARCHAR(500) COMMENT '请假图片(凭证)',
  is_deduct SMALLINT NOT NULL COMMENT '是否扣课时(0=否 1=是)',
  leave_status SMALLINT NOT NULL COMMENT '状态(1=待审批 2=已通过 3=已拒绝)',
  applicant_id INTEGER COMMENT '申请人ID',
  applicant_name VARCHAR(50) COMMENT '申请人姓名快照',
  approver_id INTEGER COMMENT '审批人ID',
  approver_name VARCHAR(50) COMMENT '审批人姓名快照',
  apply_time DATETIME COMMENT '申请时间',
  approve_time DATETIME COMMENT '审批时间',
  approve_remark VARCHAR(500) COMMENT '审批备注',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (leave_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='请假申请表';

-- ----------------------------
-- teach_schedule_attendances 排课事件-考勤表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_schedule_attendances (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  event_id INTEGER NOT NULL COMMENT '事件ID',
  student_id INTEGER NOT NULL COMMENT '学生ID',
  status SMALLINT NOT NULL COMMENT '考勤状态（0未到 1出勤 2迟到 3请假 4缺勤）',
  is_countable SMALLINT NOT NULL COMMENT '是否计入出勤率分母（1是 0否）',
  check_in_time DATETIME COMMENT '签到时间',
  check_in_method VARCHAR(1) COMMENT '签到方式（Q二维码 M手动）',
  operator_id INTEGER COMMENT '操作人ID',
  notes VARCHAR(255) COMMENT '备注',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0存在 2删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='排课事件-考勤表';

-- ----------------------------
-- teach_schedule_events 排课事件表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_schedule_events (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  teacher_id INTEGER NOT NULL COMMENT '教师ID',
  course_id INTEGER COMMENT '课程ID',
  course_name VARCHAR(100) COMMENT '课程名称快照',
  class_id INTEGER COMMENT '班级ID',
  class_name VARCHAR(100) COMMENT '班级名称快照',
  subject_code VARCHAR(50) COMMENT '学科字典码',
  start_time DATETIME NOT NULL COMMENT '开始时间',
  end_time DATETIME NOT NULL COMMENT '结束时间',
  event_date DATE NOT NULL COMMENT '上课日期',
  classroom VARCHAR(100) COMMENT '上课教室',
  lesson_hours DECIMAL(6, 2) COMMENT '授课课时',
  content VARCHAR(500) COMMENT '上课内容',
  status VARCHAR(1) NOT NULL COMMENT '状态（0已安排 1进行中 2已完成 3取消）',
  roster_frozen_at DATETIME COMMENT '名单冻结时间',
  cached_planned INTEGER NOT NULL COMMENT '计划人数',
  cached_present INTEGER NOT NULL COMMENT '出勤人数',
  cached_late INTEGER NOT NULL COMMENT '迟到人数',
  cached_excused INTEGER NOT NULL COMMENT '请假人数',
  cached_absent INTEGER NOT NULL COMMENT '缺勤人数',
  cached_rate DECIMAL(5, 2) COMMENT '出勤率缓存(%%)',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='排课事件表';

-- ----------------------------
-- teach_student_comment 课后点评表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_student_comment (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  attendance_id INTEGER COMMENT '点名记录ID',
  attendance_detail_id INTEGER COMMENT '点名明细ID',
  class_id INTEGER COMMENT '班级ID',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) COMMENT '学员姓名快照',
  course_id INTEGER COMMENT '课程ID',
  course_name VARCHAR(100) COMMENT '课程名称快照',
  teacher_id INTEGER COMMENT '老师ID',
  teacher_name VARCHAR(50) COMMENT '老师姓名快照',
  class_date DATE COMMENT '上课日期',
  performance_score INTEGER COMMENT '课堂表现评分(1-5)',
  homework_score INTEGER COMMENT '作业评分(1-5)',
  comment_content TEXT COMMENT '点评内容',
  strengths VARCHAR(500) COMMENT '优点表现',
  weaknesses VARCHAR(500) COMMENT '不足之处',
  suggestions VARCHAR(500) COMMENT '改进建议',
  comment_type VARCHAR(20) COMMENT '点评类型(single=单个 unified=统一 batch=批量)',
  status SMALLINT COMMENT '状态(1=已发布 2=已撤销)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='课后点评表';

-- ----------------------------
-- teach_subjects 教学科目字典表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_subjects (
  subject_id INTEGER NOT NULL COMMENT '科目ID' AUTO_INCREMENT,
  subject_code VARCHAR(64) NOT NULL COMMENT '科目编码（唯一标识）',
  subject_name VARCHAR(50) NOT NULL COMMENT '科目名称',
  subject_category VARCHAR(50) COMMENT '科目类别（语文、数学、英语等）',
  subject_sort INTEGER COMMENT '显示顺序',
  status CHAR(1) COMMENT '状态（0正常 1停用）',
  del_flag CHAR(1) COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (subject_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='教学科目字典表';

-- ----------------------------
-- teach_teacher_grade 教师-年级关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_teacher_grade (
  teacher_id INTEGER NOT NULL COMMENT '教师ID',
  grade_id INTEGER NOT NULL COMMENT '年级ID',
  PRIMARY KEY (teacher_id, grade_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='教师-年级关联表';

-- ----------------------------
-- teach_teacher_subject 教师-科目关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_teacher_subject (
  teacher_id INTEGER NOT NULL COMMENT '教师ID',
  subject_id INTEGER NOT NULL COMMENT '科目ID',
  PRIMARY KEY (teacher_id, subject_id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='教师-科目关联表';

-- ----------------------------
-- teach_venue 场馆信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_venue (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  venue_no VARCHAR(50) COMMENT '场馆编号',
  venue_name VARCHAR(100) NOT NULL COMMENT '场馆名称',
  address VARCHAR(255) COMMENT '场馆地址',
  description VARCHAR(500) COMMENT '场馆描述',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (venue_no)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场馆信息表';

-- ----------------------------
-- teach_class 班级基础信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_class (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  class_no VARCHAR(50) COMMENT '班级编号',
  class_name VARCHAR(100) NOT NULL COMMENT '班级名称',
  class_mode VARCHAR(20) NOT NULL COMMENT '班型(group=班课 one_to_one=一对一)',
  class_type VARCHAR(20) NOT NULL COMMENT '班级分类(system=系统 custom=自建)',
  course_id INTEGER NOT NULL COMMENT '课程ID',
  course_name VARCHAR(100) NOT NULL COMMENT '课程名称快照',
  course_type VARCHAR(32) COMMENT '课程类型快照',
  teacher_id INTEGER COMMENT '主讲老师ID',
  teacher_name VARCHAR(50) COMMENT '主讲老师姓名快照',
  assistant_id INTEGER COMMENT '助教ID',
  assistant_name VARCHAR(50) COMMENT '助教姓名快照',
  classroom VARCHAR(100) COMMENT '上课教室',
  max_students INTEGER COMMENT '班级容量',
  current_students INTEGER COMMENT '当前在读人数',
  min_students INTEGER COMMENT '开课人数',
  allow_over_capacity SMALLINT COMMENT '是否允许超员',
  allow_online_enroll SMALLINT COMMENT '是否支持在线选班',
  allow_recharge SMALLINT COMMENT '是否允许充值购时',
  auto_assign_name SMALLINT COMMENT '是否自动点名',
  lesson_hours DECIMAL(6, 2) COMMENT '授课课时',
  completed_lessons INTEGER COMMENT '已上课次',
  total_lessons INTEGER COMMENT '预排课次',
  completed_hours DECIMAL(8, 2) COMMENT '已结课时',
  default_consumption DECIMAL(10, 2) COMMENT '默认消耗金额',
  enroll_status SMALLINT COMMENT '招生状态(1=招生中 2=已满员 3=已结课)',
  start_date DATE COMMENT '开课日期',
  end_date DATE COMMENT '结课日期',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  is_historical SMALLINT COMMENT '是否过往在读班级',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (class_no),
  FOREIGN KEY(course_id) REFERENCES teach_course (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='班级基础信息表';

-- ----------------------------
-- teach_course_price 课程定价标准表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_course_price (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  course_id INTEGER NOT NULL COMMENT '课程ID',
  charge_type VARCHAR(20) NOT NULL COMMENT '收费方式(class=按课时 month=按月 day=按天)',
  price_name VARCHAR(100) NOT NULL COMMENT '定价名称',
  quantity INTEGER NOT NULL COMMENT '购买数量',
  total_price DECIMAL(10, 2) NOT NULL COMMENT '总价',
  unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
  deduct_rule VARCHAR(32) COMMENT '扣课时规则',
  absence_rule VARCHAR(32) COMMENT '未到扣课时规则',
  sort INTEGER COMMENT '排序',
  status SMALLINT COMMENT '状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  FOREIGN KEY(course_id) REFERENCES teach_course (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='课程定价标准表';

-- ----------------------------
-- teach_court 场地信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_court (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  venue_id INTEGER NOT NULL COMMENT '所属场馆ID',
  venue_name VARCHAR(100) COMMENT '场馆名称快照',
  court_no VARCHAR(50) COMMENT '场地编号',
  court_name VARCHAR(100) NOT NULL COMMENT '场地名称',
  court_type VARCHAR(50) COMMENT '场地类型(如篮球/羽毛球)',
  price_per_hour DECIMAL(10, 2) COMMENT '每小时价格',
  price_per_half_hour DECIMAL(10, 2) COMMENT '每半小时价格',
  status SMALLINT COMMENT '启用状态(0=停用 1=启用)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  FOREIGN KEY(venue_id) REFERENCES teach_venue (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场地信息表';

-- ----------------------------
-- teach_package_item 课程套餐明细表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_package_item (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  package_id INTEGER NOT NULL COMMENT '套餐ID',
  item_type VARCHAR(20) NOT NULL COMMENT '项目类型(course=课程 item=物品 fee=费用)',
  item_id INTEGER NOT NULL COMMENT '项目ID',
  item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
  spec_id INTEGER COMMENT '规格或定价ID',
  spec_name VARCHAR(100) COMMENT '规格或定价名称',
  unit VARCHAR(20) COMMENT '单位',
  quantity INTEGER NOT NULL COMMENT '购买数量',
  gift_quantity INTEGER COMMENT '赠送数量',
  leave_free_quantity INTEGER COMMENT '请假免扣次数',
  unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
  total_price DECIMAL(10, 2) NOT NULL COMMENT '总价',
  discount_type VARCHAR(20) COMMENT '优惠类型(reduce=直减 discount=折扣)',
  discount_value DECIMAL(10, 2) COMMENT '优惠值',
  subtotal_price DECIMAL(10, 2) NOT NULL COMMENT '小计',
  sort INTEGER COMMENT '排序',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  FOREIGN KEY(package_id) REFERENCES teach_course_package (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='课程套餐明细表';

-- ----------------------------
-- teach_parents 家长信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_parents (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  user_id INTEGER NOT NULL COMMENT '关联基础用户ID',
  parent_name VARCHAR(50) NOT NULL COMMENT '家长姓名',
  nickname VARCHAR(50) COMMENT '昵称',
  avatar_url VARCHAR(512) COMMENT '头像URL',
  wechat_id VARCHAR(50) COMMENT '微信号',
  emergency_contact VARCHAR(20) COMMENT '紧急联系电话',
  address VARCHAR(255) COMMENT '家庭住址',
  occupation VARCHAR(50) COMMENT '职业',
  education_level VARCHAR(20) COMMENT '学历',
  family_income_range VARCHAR(1) COMMENT '家庭收入范围（0-5k以下 1-5-10k 2-10-20k 3-20k以上）',
  payment_preference VARCHAR(1) COMMENT '付费偏好（0按课时 1包月 2包季 3包年）',
  status VARCHAR(1) NOT NULL COMMENT '帐号状态（0正常 1停用 2已注销）',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (user_id),
  FOREIGN KEY(user_id) REFERENCES teach_base_users (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='家长信息表';

-- ----------------------------
-- teach_teachers 教师信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_teachers (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  user_id INTEGER NOT NULL COMMENT '关联基础用户ID',
  teacher_name VARCHAR(50) NOT NULL COMMENT '教师姓名',
  nickname VARCHAR(50) COMMENT '昵称',
  avatar_url VARCHAR(512) COMMENT '头像URL',
  id_card VARCHAR(18) COMMENT '身份证号',
  qualification_cert VARCHAR(255) COMMENT '教师资格证号',
  work_experience INTEGER COMMENT '教学经验(年)',
  introduction TEXT COMMENT '个人简介',
  hourly_rate VARCHAR(20) COMMENT '默认课时费',
  bank_account VARCHAR(50) COMMENT '银行账号',
  bank_name VARCHAR(100) COMMENT '开户银行',
  settlement_cycle VARCHAR(1) COMMENT '结算周期（0周结 1月结）',
  status VARCHAR(1) NOT NULL COMMENT '帐号状态（0正常 1停用 2已注销）',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (user_id),
  FOREIGN KEY(user_id) REFERENCES teach_base_users (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='教师信息表';

-- ----------------------------
-- teach_class_attendance 班级点名记录表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_class_attendance (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  event_id INTEGER COMMENT '排课事件ID',
  class_id INTEGER NOT NULL COMMENT '班级ID',
  class_name VARCHAR(100) NOT NULL COMMENT '班级名称快照',
  course_id INTEGER NOT NULL COMMENT '课程ID',
  course_name VARCHAR(100) NOT NULL COMMENT '课程名称快照',
  teacher_id INTEGER COMMENT '上课老师ID',
  teacher_name VARCHAR(50) COMMENT '上课老师快照',
  classroom VARCHAR(100) COMMENT '上课教室',
  class_date DATE NOT NULL COMMENT '上课日期',
  start_time VARCHAR(10) NOT NULL COMMENT '开始时间',
  end_time VARCHAR(10) NOT NULL COMMENT '结束时间',
  lesson_hours DECIMAL(6, 2) COMMENT '授课课时',
  content VARCHAR(500) COMMENT '上课内容',
  student_count INTEGER NOT NULL COMMENT '应到人数',
  present_count INTEGER NOT NULL COMMENT '到课人数',
  late_count INTEGER NOT NULL COMMENT '迟到人数',
  leave_count INTEGER NOT NULL COMMENT '请假人数',
  absent_count INTEGER NOT NULL COMMENT '未到人数',
  deducted_quantity INTEGER NOT NULL COMMENT '本次扣课合计',
  status SMALLINT COMMENT '状态(1=已点名)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  CONSTRAINT uk_class_attendance_event UNIQUE (event_id),
  FOREIGN KEY(class_id) REFERENCES teach_class (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='班级点名记录表';

-- ----------------------------
-- teach_class_teacher 班级教师关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_class_teacher (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  class_id INTEGER NOT NULL COMMENT '班级ID',
  teacher_id INTEGER NOT NULL COMMENT '教师ID',
  teacher_name VARCHAR(50) NOT NULL COMMENT '教师姓名快照',
  teacher_role VARCHAR(20) NOT NULL COMMENT '教师角色(main=主讲 assistant=助教)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  FOREIGN KEY(class_id) REFERENCES teach_class (id),
  FOREIGN KEY(teacher_id) REFERENCES teach_teachers (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='班级教师关联表';

-- ----------------------------
-- teach_court_booking 场地预订单表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_court_booking (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  booking_no VARCHAR(50) COMMENT '预订单编号',
  court_id INTEGER NOT NULL COMMENT '场地ID',
  court_name VARCHAR(100) COMMENT '场地名称快照',
  venue_id INTEGER COMMENT '所属场馆ID',
  booking_date DATE NOT NULL COMMENT '预订日期',
  start_time VARCHAR(10) NOT NULL COMMENT '开始时间',
  end_time VARCHAR(10) NOT NULL COMMENT '结束时间',
  customer_id INTEGER COMMENT '学员或客户ID',
  customer_name VARCHAR(50) COMMENT '客户姓名',
  customer_phone VARCHAR(20) COMMENT '客户电话',
  booking_type VARCHAR(20) COMMENT '预订类型(normal=预订 lock=锁场)',
  lock_group_no VARCHAR(50) COMMENT '批量锁场批次号',
  origin VARCHAR(20) COMMENT '来源(admin=代预订 online=线上)',
  amount DECIMAL(10, 2) COMMENT '应收金额',
  discount_amount DECIMAL(10, 2) COMMENT '优惠金额',
  card_grant_id INTEGER COMMENT '会员卡发放ID(会员卡折扣)',
  pay_status SMALLINT COMMENT '支付状态(0=未付 1=已付 2=已退)',
  booking_status SMALLINT COMMENT '预订状态(1=已预订 2=已核销 3=已取消)',
  verify_time DATETIME COMMENT '核销时间',
  cancel_reason VARCHAR(255) COMMENT '取消原因',
  refund_amount DECIMAL(10, 2) COMMENT '退款金额',
  operator_id INTEGER COMMENT '操作人ID',
  operator_name VARCHAR(50) COMMENT '操作人姓名',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  UNIQUE (booking_no),
  FOREIGN KEY(court_id) REFERENCES teach_court (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场地预订单表';

-- ----------------------------
-- teach_court_price_rule 场地分时价格规则表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_court_price_rule (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  court_id INTEGER NOT NULL COMMENT '场地ID',
  week_day SMALLINT NOT NULL COMMENT '星期(1-7)',
  start_time VARCHAR(10) NOT NULL COMMENT '开始时间(HH:MM)',
  end_time VARCHAR(10) NOT NULL COMMENT '结束时间(HH:MM)',
  price_per_hour DECIMAL(10, 2) COMMENT '该时段每小时价格',
  price_per_half_hour DECIMAL(10, 2) COMMENT '该时段每半小时价格',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  PRIMARY KEY (id),
  FOREIGN KEY(court_id) REFERENCES teach_court (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场地分时价格规则表';

-- ----------------------------
-- teach_court_time 场地可约时段表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_court_time (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  court_id INTEGER NOT NULL COMMENT '场地ID',
  week_day SMALLINT NOT NULL COMMENT '星期(1-7)',
  start_time VARCHAR(10) NOT NULL COMMENT '开始时间',
  end_time VARCHAR(10) NOT NULL COMMENT '结束时间',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  PRIMARY KEY (id),
  FOREIGN KEY(court_id) REFERENCES teach_court (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='场地可约时段表';

-- ----------------------------
-- teach_students 学生信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_students (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  parent_id INTEGER NOT NULL COMMENT '关联家长ID',
  student_name VARCHAR(50) NOT NULL COMMENT '学生姓名',
  gender VARCHAR(1) COMMENT '用户性别（0未知 1男 2女）',
  birthday DATE COMMENT '出生日期',
  school_name VARCHAR(100) COMMENT '就读学校',
  grade VARCHAR(20) COMMENT '年级',
  class_name VARCHAR(50) COMMENT '班级',
  student_id_in_school VARCHAR(50) COMMENT '学号',
  learning_style VARCHAR(1) COMMENT '学习风格（0视觉型 1听觉型 2动觉型）',
  personality_traits JSON COMMENT '性格特点标签',
  learning_difficulties TEXT COMMENT '学习困难点',
  interests_hobbies JSON COMMENT '兴趣爱好',
  medical_notes TEXT COMMENT '医疗备注(过敏史等)',
  emergency_contact VARCHAR(20) COMMENT '紧急联系人电话',
  status VARCHAR(1) NOT NULL COMMENT '帐号状态（0在读 1休学 2转学 3毕业）',
  del_flag VARCHAR(1) NOT NULL COMMENT '删除标志（0代表存在 2代表删除）',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  FOREIGN KEY(parent_id) REFERENCES teach_parents (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学生信息表';

-- ----------------------------
-- teach_class_attendance_detail 班级点名明细表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_class_attendance_detail (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  attendance_id INTEGER NOT NULL COMMENT '点名记录ID',
  class_id INTEGER NOT NULL COMMENT '班级ID',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) NOT NULL COMMENT '学员姓名快照',
  course_account_id INTEGER COMMENT '课程账户ID',
  status SMALLINT NOT NULL COMMENT '到课状态(1=到课 2=迟到 3=请假 4=未到)',
  deduct_quantity INTEGER NOT NULL COMMENT '扣除数量',
  before_remaining INTEGER COMMENT '扣课前剩余',
  after_remaining INTEGER COMMENT '扣课后剩余',
  consume_method VARCHAR(100) COMMENT '消费方式快照',
  makeup_flag SMALLINT NOT NULL COMMENT '补课标记(0=未补 1=已补)' DEFAULT '0',
  makeup_time DATETIME COMMENT '标记已补时间',
  makeup_by VARCHAR(64) COMMENT '标记已补操作人',
  makeup_remark VARCHAR(200) COMMENT '补课说明',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  FOREIGN KEY(attendance_id) REFERENCES teach_class_attendance (id),
  FOREIGN KEY(class_id) REFERENCES teach_class (id),
  FOREIGN KEY(student_id) REFERENCES teach_students (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='班级点名明细表';

-- ----------------------------
-- teach_class_student 班级学员关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_class_student (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  class_id INTEGER NOT NULL COMMENT '班级ID',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) NOT NULL COMMENT '学员姓名快照',
  course_account_id INTEGER COMMENT '课程账户ID',
  enrollment_order_id INTEGER COMMENT '报名订单ID',
  enrollment_order_item_id INTEGER COMMENT '报名订单明细ID',
  consume_method VARCHAR(100) COMMENT '消耗方式',
  join_date DATE COMMENT '加入日期',
  leave_date DATE COMMENT '离班日期',
  status SMALLINT COMMENT '状态(1=在读 2=已移出)',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  remark VARCHAR(500) COMMENT '备注',
  PRIMARY KEY (id),
  FOREIGN KEY(class_id) REFERENCES teach_class (id),
  FOREIGN KEY(student_id) REFERENCES teach_students (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='班级学员关联表';

-- ----------------------------
-- teach_enrollment_order 学员报名/续费订单表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_enrollment_order (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  order_no VARCHAR(50) NOT NULL COMMENT '订单号',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  student_name VARCHAR(50) NOT NULL COMMENT '学员姓名快照',
  parent_phone VARCHAR(20) COMMENT '家长手机号快照',
  order_type VARCHAR(20) NOT NULL COMMENT '订单类型(enroll=报名 renew=续费)',
  order_source VARCHAR(50) COMMENT '订单来源',
  enroll_date DATE COMMENT '经办日期',
  item_count INTEGER NOT NULL COMMENT '项目数量',
  total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
  discount_amount DECIMAL(10, 2) NOT NULL COMMENT '优惠金额',
  receivable_amount DECIMAL(10, 2) NOT NULL COMMENT '应收金额',
  paid_amount DECIMAL(10, 2) NOT NULL COMMENT '实收金额',
  status VARCHAR(20) NOT NULL COMMENT '订单状态(pending=待支付 paid=已支付)',
  performance_owner VARCHAR(64) COMMENT '业绩归属人',
  performance_type VARCHAR(32) COMMENT '业绩类型',
  performance_amount DECIMAL(10, 2) COMMENT '业绩金额',
  remark VARCHAR(500) COMMENT '订单备注',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE (order_no),
  FOREIGN KEY(student_id) REFERENCES teach_students (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学员报名/续费订单表';

-- ----------------------------
-- teach_enrollment_order_item 学员报名/续费订单明细表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_enrollment_order_item (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  order_id INTEGER NOT NULL COMMENT '订单ID',
  student_id INTEGER NOT NULL COMMENT '学员ID',
  item_type VARCHAR(20) NOT NULL COMMENT '项目类型(course=课程 item=物品 fee=费用)',
  item_id INTEGER NOT NULL COMMENT '项目ID',
  item_name VARCHAR(100) NOT NULL COMMENT '项目名称快照',
  spec_id INTEGER COMMENT '规格或定价ID',
  spec_name VARCHAR(100) COMMENT '规格或定价名称',
  charge_type VARCHAR(20) COMMENT '收费方式',
  unit VARCHAR(20) COMMENT '单位',
  quantity INTEGER NOT NULL COMMENT '购买数量',
  gift_quantity INTEGER COMMENT '赠送数量',
  leave_exempt_count INTEGER COMMENT '请假免扣次数',
  unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
  total_price DECIMAL(10, 2) NOT NULL COMMENT '总价',
  discount_type VARCHAR(20) COMMENT '优惠类型',
  discount_value DECIMAL(10, 2) COMMENT '优惠值',
  subtotal_price DECIMAL(10, 2) NOT NULL COMMENT '小计',
  start_date DATE COMMENT '课程开始日期',
  end_date DATE COMMENT '课程结束日期',
  validity_type VARCHAR(32) COMMENT '课程有效期类型',
  class_id INTEGER COMMENT '班级ID',
  class_name VARCHAR(100) COMMENT '班级名称',
  package_id INTEGER COMMENT '套餐ID',
  package_name VARCHAR(100) COMMENT '套餐名称',
  remark VARCHAR(500) COMMENT '明细备注',
  sort INTEGER COMMENT '排序',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  FOREIGN KEY(order_id) REFERENCES teach_enrollment_order (id),
  FOREIGN KEY(student_id) REFERENCES teach_students (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学员报名/续费订单明细表';

-- ----------------------------
-- teach_student_course_account 学员课程账户表
-- ----------------------------
CREATE TABLE IF NOT EXISTS teach_student_course_account (
  id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
  student_id INTEGER NOT NULL COMMENT '学员ID',
  course_id INTEGER NOT NULL COMMENT '课程ID',
  course_name VARCHAR(100) NOT NULL COMMENT '课程名称快照',
  order_id INTEGER NOT NULL COMMENT '订单ID',
  order_item_id INTEGER NOT NULL COMMENT '订单明细ID',
  charge_type VARCHAR(20) COMMENT '收费方式',
  unit VARCHAR(20) COMMENT '单位',
  purchased_quantity INTEGER NOT NULL COMMENT '购买数量',
  gift_quantity INTEGER NOT NULL COMMENT '赠送数量',
  consumed_quantity INTEGER NOT NULL COMMENT '已消耗数量',
  refunded_quantity INTEGER NOT NULL COMMENT '已退数量',
  transferred_quantity INTEGER NOT NULL COMMENT '已转数量',
  remaining_quantity INTEGER NOT NULL COMMENT '剩余数量',
  leave_exempt_count INTEGER COMMENT '请假免扣次数',
  leave_used_count INTEGER COMMENT '已用请假免扣次数',
  valid_start_date DATE COMMENT '有效期开始日期',
  valid_end_date DATE COMMENT '有效期结束日期',
  validity_type VARCHAR(32) COMMENT '有效期类型',
  class_id INTEGER COMMENT '班级ID',
  class_name VARCHAR(100) COMMENT '班级名称',
  status VARCHAR(20) NOT NULL COMMENT '状态(active=有效 stopped=停课 completed=结课)',
  remark VARCHAR(500) COMMENT '备注',
  del_flag SMALLINT COMMENT '删除标志(0=存在 1=删除)',
  create_by VARCHAR(64) COMMENT '创建者',
  create_time DATETIME COMMENT '创建时间',
  update_by VARCHAR(64) COMMENT '更新者',
  update_time DATETIME COMMENT '更新时间',
  PRIMARY KEY (id),
  FOREIGN KEY(student_id) REFERENCES teach_students (id),
  FOREIGN KEY(order_id) REFERENCES teach_enrollment_order (id),
  FOREIGN KEY(order_item_id) REFERENCES teach_enrollment_order_item (id)
)ENGINE=InnoDB CHARSET=utf8mb4 COMMENT='学员课程账户表';

-- ----------------------------
-- 已有数据库补充唯一约束（create_all 不会给已存在的表加约束，需要手工执行一次）
-- 先确认没有重复点名数据：
--   SELECT event_id, COUNT(*) FROM teach_class_attendance
--   WHERE event_id IS NOT NULL GROUP BY event_id HAVING COUNT(*) > 1;
-- 再执行：
--   ALTER TABLE teach_class_attendance ADD CONSTRAINT uk_class_attendance_event UNIQUE (event_id);
-- ----------------------------
