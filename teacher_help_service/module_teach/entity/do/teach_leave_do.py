from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Integer, SMALLINT, String
from config.database import Base


class TeachLeaveApplication(Base):
    """
    请假申请表
    """

    __tablename__ = 'teach_leave_application'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    leave_no = Column(String(50), nullable=True, unique=True, comment='请假编号')
    student_id = Column(Integer, nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=False, comment='学员姓名快照')
    class_id = Column(Integer, nullable=True, comment='班级ID')
    class_name = Column(String(100), nullable=True, comment='班级名称快照')
    course_id = Column(Integer, nullable=True, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称快照')
    event_id = Column(Integer, nullable=True, comment='关联课次(排课事件)ID')
    leave_type = Column(SMALLINT, nullable=False, default=1, comment='请假类型(1=事假 2=病假 3=其他)')
    leave_date = Column(Date, nullable=False, comment='请假日期')
    leave_reason = Column(String(500), nullable=True, comment='请假事由')
    leave_image = Column(String(500), nullable=True, comment='请假图片(凭证)')
    is_deduct = Column(SMALLINT, nullable=False, default=0, comment='是否扣课时(0=否 1=是)')
    leave_status = Column(SMALLINT, nullable=False, default=1, comment='状态(1=待审批 2=已通过 3=已拒绝)')
    applicant_id = Column(Integer, nullable=True, comment='申请人ID')
    applicant_name = Column(String(50), nullable=True, comment='申请人姓名快照')
    approver_id = Column(Integer, nullable=True, comment='审批人ID')
    approver_name = Column(String(50), nullable=True, comment='审批人姓名快照')
    apply_time = Column(DateTime, nullable=True, default=datetime.now, comment='申请时间')
    approve_time = Column(DateTime, nullable=True, comment='审批时间')
    approve_remark = Column(String(500), nullable=True, comment='审批备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
