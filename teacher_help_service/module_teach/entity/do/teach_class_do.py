from datetime import datetime
from sqlalchemy import Column, Date, DateTime, DECIMAL, ForeignKey, Integer, SMALLINT, String, UniqueConstraint
from config.database import Base


class TeachClass(Base):
    """
    班级基础信息表
    """

    __tablename__ = 'teach_class'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    class_no = Column(String(50), nullable=True, unique=True, comment='班级编号')
    class_name = Column(String(100), nullable=False, comment='班级名称')
    class_mode = Column(String(20), nullable=False, default='group', comment='班型(group=班课 one_to_one=一对一)')
    class_type = Column(String(20), nullable=False, default='custom', comment='班级分类(system=系统 custom=自建)')
    course_id = Column(Integer, ForeignKey('teach_course.id'), nullable=False, comment='课程ID')
    course_name = Column(String(100), nullable=False, comment='课程名称快照')
    course_type = Column(String(32), nullable=True, comment='课程类型快照')
    teacher_id = Column(Integer, nullable=True, comment='主讲老师ID')
    teacher_name = Column(String(50), nullable=True, comment='主讲老师姓名快照')
    assistant_id = Column(Integer, nullable=True, comment='助教ID')
    assistant_name = Column(String(50), nullable=True, comment='助教姓名快照')
    classroom = Column(String(100), nullable=True, comment='上课教室')
    max_students = Column(Integer, nullable=True, default=0, comment='班级容量')
    current_students = Column(Integer, nullable=True, default=0, comment='当前在读人数')
    min_students = Column(Integer, nullable=True, default=0, comment='开课人数')
    allow_over_capacity = Column(SMALLINT, nullable=True, default=1, comment='是否允许超员')
    allow_online_enroll = Column(SMALLINT, nullable=True, default=0, comment='是否支持在线选班')
    allow_recharge = Column(SMALLINT, nullable=True, default=1, comment='是否允许充值购时')
    auto_assign_name = Column(SMALLINT, nullable=True, default=0, comment='是否自动点名')
    lesson_hours = Column(DECIMAL(6, 2), nullable=True, default=1, comment='授课课时')
    completed_lessons = Column(Integer, nullable=True, default=0, comment='已上课次')
    total_lessons = Column(Integer, nullable=True, default=0, comment='预排课次')
    completed_hours = Column(DECIMAL(8, 2), nullable=True, default=0, comment='已结课时')
    default_consumption = Column(DECIMAL(10, 2), nullable=True, default=0, comment='默认消耗金额')
    enroll_status = Column(SMALLINT, nullable=True, default=1, comment='招生状态(1=招生中 2=已满员 3=已结课)')
    start_date = Column(Date, nullable=True, comment='开课日期')
    end_date = Column(Date, nullable=True, comment='结课日期')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    is_historical = Column(SMALLINT, nullable=True, default=0, comment='是否过往在读班级')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachClassStudent(Base):
    """
    班级学员关联表
    """

    __tablename__ = 'teach_class_student'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    class_id = Column(Integer, ForeignKey('teach_class.id'), nullable=False, comment='班级ID')
    student_id = Column(Integer, ForeignKey('teach_students.id'), nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=False, comment='学员姓名快照')
    course_account_id = Column(Integer, nullable=True, comment='课程账户ID')
    enrollment_order_id = Column(Integer, nullable=True, comment='报名订单ID')
    enrollment_order_item_id = Column(Integer, nullable=True, comment='报名订单明细ID')
    consume_method = Column(String(100), nullable=True, comment='消耗方式')
    join_date = Column(Date, nullable=True, comment='加入日期')
    leave_date = Column(Date, nullable=True, comment='离班日期')
    status = Column(SMALLINT, nullable=True, default=1, comment='状态(1=在读 2=已移出)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachClassTeacher(Base):
    """
    班级教师关联表
    """

    __tablename__ = 'teach_class_teacher'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    class_id = Column(Integer, ForeignKey('teach_class.id'), nullable=False, comment='班级ID')
    teacher_id = Column(Integer, ForeignKey('teach_teachers.id'), nullable=False, comment='教师ID')
    teacher_name = Column(String(50), nullable=False, comment='教师姓名快照')
    teacher_role = Column(String(20), nullable=False, default='main', comment='教师角色(main=主讲 assistant=助教)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class TeachClassAttendance(Base):
    """
    班级点名记录表
    """

    __tablename__ = 'teach_class_attendance'
    # 同一排课课次只允许一条点名记录（event_id 为空的临时点名不受限制）
    # 后续实现撤销点名时需物理删除或清空 event_id，否则无法重新点名
    __table_args__ = (UniqueConstraint('event_id', name='uk_class_attendance_event'),)

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    event_id = Column(Integer, nullable=True, comment='排课事件ID')
    class_id = Column(Integer, ForeignKey('teach_class.id'), nullable=False, comment='班级ID')
    class_name = Column(String(100), nullable=False, comment='班级名称快照')
    course_id = Column(Integer, nullable=False, comment='课程ID')
    course_name = Column(String(100), nullable=False, comment='课程名称快照')
    teacher_id = Column(Integer, nullable=True, comment='上课老师ID')
    teacher_name = Column(String(50), nullable=True, comment='上课老师快照')
    classroom = Column(String(100), nullable=True, comment='上课教室')
    class_date = Column(Date, nullable=False, comment='上课日期')
    start_time = Column(String(10), nullable=False, comment='开始时间')
    end_time = Column(String(10), nullable=False, comment='结束时间')
    lesson_hours = Column(DECIMAL(6, 2), nullable=True, default=1, comment='授课课时')
    content = Column(String(500), nullable=True, comment='上课内容')
    student_count = Column(Integer, nullable=False, default=0, comment='应到人数')
    present_count = Column(Integer, nullable=False, default=0, comment='到课人数')
    late_count = Column(Integer, nullable=False, default=0, comment='迟到人数')
    leave_count = Column(Integer, nullable=False, default=0, comment='请假人数')
    absent_count = Column(Integer, nullable=False, default=0, comment='未到人数')
    deducted_quantity = Column(Integer, nullable=False, default=0, comment='本次扣课合计')
    status = Column(SMALLINT, nullable=True, default=1, comment='状态(1=已点名)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')


class TeachClassAttendanceDetail(Base):
    """
    班级点名明细表
    """

    __tablename__ = 'teach_class_attendance_detail'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    attendance_id = Column(Integer, ForeignKey('teach_class_attendance.id'), nullable=False, comment='点名记录ID')
    class_id = Column(Integer, ForeignKey('teach_class.id'), nullable=False, comment='班级ID')
    student_id = Column(Integer, ForeignKey('teach_students.id'), nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=False, comment='学员姓名快照')
    course_account_id = Column(Integer, nullable=True, comment='课程账户ID')
    status = Column(SMALLINT, nullable=False, default=1, comment='到课状态(1=到课 2=迟到 3=请假 4=未到)')
    deduct_quantity = Column(Integer, nullable=False, default=0, comment='扣除数量')
    before_remaining = Column(Integer, nullable=True, comment='扣课前剩余')
    after_remaining = Column(Integer, nullable=True, comment='扣课后剩余')
    consume_method = Column(String(100), nullable=True, comment='消费方式快照')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
