from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, SmallInteger
from config.database import Base


class TeachScheduleAttendance(Base):
    """
    排课事件-考勤表
    """

    __tablename__ = 'teach_schedule_attendances'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    event_id = Column(Integer, nullable=False, comment='事件ID')
    student_id = Column(Integer, nullable=False, comment='学生ID')
    status = Column(SmallInteger, nullable=False, default=0, comment='考勤状态（0未到 1出勤 2迟到 3请假 4缺勤）')
    is_countable = Column(SmallInteger, nullable=False, default=1, comment='是否计入出勤率分母（1是 0否）')
    # P3：临时学员 / 补课学员（不在班级在读名单内，仅加入单个课次）
    is_temp = Column(SmallInteger, nullable=False, default=0, server_default='0', comment='是否临时学员（0否 1是）')
    course_account_id = Column(Integer, nullable=True, comment='临时学员扣课课程账户ID')
    makeup_detail_id = Column(Integer, nullable=True, comment='补课来源点名明细ID（开补课班生成）')
    check_in_time = Column(DateTime, nullable=True, comment='签到时间')
    check_in_method = Column(String(1), nullable=True, comment='签到方式（Q二维码 M手动）')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    notes = Column(String(255), nullable=True, comment='备注')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0存在 2删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

