from datetime import datetime
from sqlalchemy import Column, Date, DateTime, DECIMAL, ForeignKey, Integer, SMALLINT, String
from config.database import Base


class TeachEnrollmentOrder(Base):
    """
    学员报名/续费订单表
    """

    __tablename__ = 'teach_enrollment_order'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    order_no = Column(String(50), nullable=False, unique=True, comment='订单号')
    student_id = Column(Integer, ForeignKey('teach_students.id'), nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=False, comment='学员姓名快照')
    parent_phone = Column(String(20), nullable=True, comment='家长手机号快照')
    order_type = Column(String(20), nullable=False, default='enroll', comment='订单类型(enroll=报名 renew=续费)')
    order_source = Column(String(50), nullable=True, default='机构创建', comment='订单来源')
    enroll_date = Column(Date, nullable=True, comment='经办日期')
    item_count = Column(Integer, nullable=False, default=0, comment='项目数量')
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0, comment='订单总金额')
    discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0, comment='优惠金额')
    receivable_amount = Column(DECIMAL(10, 2), nullable=False, default=0, comment='应收金额')
    paid_amount = Column(DECIMAL(10, 2), nullable=False, default=0, comment='实收金额')
    status = Column(String(20), nullable=False, default='paid', comment='订单状态(pending=待支付 paid=已支付)')
    performance_owner = Column(String(64), nullable=True, comment='业绩归属人')
    performance_type = Column(String(32), nullable=True, comment='业绩类型')
    performance_amount = Column(DECIMAL(10, 2), nullable=True, default=0, comment='业绩金额')
    remark = Column(String(500), nullable=True, comment='订单备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class TeachEnrollmentOrderItem(Base):
    """
    学员报名/续费订单明细表
    """

    __tablename__ = 'teach_enrollment_order_item'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    order_id = Column(Integer, ForeignKey('teach_enrollment_order.id'), nullable=False, comment='订单ID')
    student_id = Column(Integer, ForeignKey('teach_students.id'), nullable=False, comment='学员ID')
    item_type = Column(String(20), nullable=False, comment='项目类型(course=课程 item=物品 fee=费用)')
    item_id = Column(Integer, nullable=False, comment='项目ID')
    item_name = Column(String(100), nullable=False, comment='项目名称快照')
    spec_id = Column(Integer, nullable=True, comment='规格或定价ID')
    spec_name = Column(String(100), nullable=True, comment='规格或定价名称')
    charge_type = Column(String(20), nullable=True, comment='收费方式')
    unit = Column(String(20), nullable=True, comment='单位')
    quantity = Column(Integer, nullable=False, default=1, comment='购买数量')
    gift_quantity = Column(Integer, nullable=True, default=0, comment='赠送数量')
    leave_exempt_count = Column(Integer, nullable=True, default=0, comment='请假免扣次数')
    unit_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='单价')
    total_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='总价')
    discount_type = Column(String(20), nullable=True, default='reduce', comment='优惠类型')
    discount_value = Column(DECIMAL(10, 2), nullable=True, default=0, comment='优惠值')
    subtotal_price = Column(DECIMAL(10, 2), nullable=False, default=0, comment='小计')
    start_date = Column(Date, nullable=True, comment='课程开始日期')
    end_date = Column(Date, nullable=True, comment='课程结束日期')
    validity_type = Column(String(32), nullable=True, comment='课程有效期类型')
    class_id = Column(Integer, nullable=True, comment='班级ID')
    class_name = Column(String(100), nullable=True, comment='班级名称')
    package_id = Column(Integer, nullable=True, comment='套餐ID')
    package_name = Column(String(100), nullable=True, comment='套餐名称')
    remark = Column(String(500), nullable=True, comment='明细备注')
    sort = Column(Integer, nullable=True, default=0, comment='排序')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class TeachStudentCourseAccount(Base):
    """
    学员课程账户表
    """

    __tablename__ = 'teach_student_course_account'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    student_id = Column(Integer, ForeignKey('teach_students.id'), nullable=False, comment='学员ID')
    course_id = Column(Integer, nullable=False, comment='课程ID')
    course_name = Column(String(100), nullable=False, comment='课程名称快照')
    order_id = Column(Integer, ForeignKey('teach_enrollment_order.id'), nullable=False, comment='订单ID')
    order_item_id = Column(Integer, ForeignKey('teach_enrollment_order_item.id'), nullable=False, comment='订单明细ID')
    charge_type = Column(String(20), nullable=True, comment='收费方式')
    unit = Column(String(20), nullable=True, comment='单位')
    purchased_quantity = Column(Integer, nullable=False, default=0, comment='购买数量')
    gift_quantity = Column(Integer, nullable=False, default=0, comment='赠送数量')
    consumed_quantity = Column(Integer, nullable=False, default=0, comment='已消耗数量')
    refunded_quantity = Column(Integer, nullable=False, default=0, comment='已退数量')
    transferred_quantity = Column(Integer, nullable=False, default=0, comment='已转数量')
    remaining_quantity = Column(Integer, nullable=False, default=0, comment='剩余数量')
    # 课时清零/结课清零的数量（P3），购买+赠送 = 已消耗+已退+已转+已清零+剩余
    cleared_quantity = Column(Integer, nullable=False, default=0, server_default='0', comment='已清零数量')
    leave_exempt_count = Column(Integer, nullable=True, default=0, comment='请假免扣次数')
    leave_used_count = Column(Integer, nullable=True, default=0, comment='已用请假免扣次数')
    valid_start_date = Column(Date, nullable=True, comment='有效期开始日期')
    valid_end_date = Column(Date, nullable=True, comment='有效期结束日期')
    validity_type = Column(String(32), nullable=True, comment='有效期类型')
    class_id = Column(Integer, nullable=True, comment='班级ID')
    class_name = Column(String(100), nullable=True, comment='班级名称')
    status = Column(
        String(20),
        nullable=False,
        default='active',
        comment='状态(active=有效 stopped=停课 completed=结课 transferred=已转出)',
    )
    # 停课/结课信息（P3）
    stop_date = Column(Date, nullable=True, comment='停课日期')
    planned_resume_date = Column(Date, nullable=True, comment='计划复课日期(仅记录，需手动复课)')
    stop_reason = Column(String(100), nullable=True, comment='停课原因')
    complete_date = Column(Date, nullable=True, comment='结课/转出日期')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class TeachCourseAccountLog(Base):
    """
    学员课程账户操作日志表（P3：转课/课时清零/改有效期/停课/复课/结课/导入）
    """

    __tablename__ = 'teach_course_account_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    batch_no = Column(String(50), nullable=False, comment='操作批次号')
    op_type = Column(
        String(20),
        nullable=False,
        comment='操作类型(transfer_out=转出 transfer_in=转入 clear=课时清零 validity=改有效期 stop=停课 resume=复课 '
        'complete=结课 import=导入 attendance_edit=修改点名)',
    )
    account_id = Column(Integer, nullable=False, index=True, comment='课程账户ID')
    student_id = Column(Integer, nullable=False, index=True, comment='学员ID')
    student_name = Column(String(50), nullable=True, comment='学员姓名快照')
    course_id = Column(Integer, nullable=True, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称快照')
    change_quantity = Column(Integer, nullable=False, default=0, comment='变动数量(减少为负)')
    before_remaining = Column(Integer, nullable=True, comment='变动前剩余')
    after_remaining = Column(Integer, nullable=True, comment='变动后剩余')
    before_status = Column(String(20), nullable=True, comment='变动前状态')
    after_status = Column(String(20), nullable=True, comment='变动后状态')
    before_valid_start = Column(Date, nullable=True, comment='变动前有效期开始')
    before_valid_end = Column(Date, nullable=True, comment='变动前有效期结束')
    after_valid_start = Column(Date, nullable=True, comment='变动后有效期开始')
    after_valid_end = Column(Date, nullable=True, comment='变动后有效期结束')
    related_account_id = Column(Integer, nullable=True, comment='关联课程账户ID(转课对方账户)')
    related_order_id = Column(Integer, nullable=True, comment='关联订单ID')
    reason = Column(String(200), nullable=True, comment='原因/备注')
    create_by = Column(String(64), nullable=True, default='', comment='操作人')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='操作时间')
