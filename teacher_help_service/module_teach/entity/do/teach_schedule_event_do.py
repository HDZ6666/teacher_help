from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL
from config.database import Base


class TeachScheduleEvent(Base):
    """
    排课事件表
    """

    __tablename__ = 'teach_schedule_events'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    teacher_id = Column(Integer, nullable=False, comment='教师ID')
    course_id = Column(Integer, nullable=True, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称快照')
    class_id = Column(Integer, nullable=True, comment='班级ID')
    class_name = Column(String(100), nullable=True, comment='班级名称快照')
    subject_code = Column(String(50), nullable=True, comment='学科字典码')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    event_date = Column(Date, nullable=False, comment='上课日期')
    classroom = Column(String(100), nullable=True, comment='上课教室')
    lesson_hours = Column(DECIMAL(6, 2), nullable=True, default=1, comment='授课课时')
    content = Column(String(500), nullable=True, comment='上课内容')
    status = Column(String(1), nullable=False, default='0', comment='状态（0已安排 1进行中 2已完成 3取消）')
    roster_frozen_at = Column(DateTime, nullable=True, comment='名单冻结时间')
    cached_planned = Column(Integer, nullable=False, default=0, comment='计划人数')
    cached_present = Column(Integer, nullable=False, default=0, comment='出勤人数')
    cached_late = Column(Integer, nullable=False, default=0, comment='迟到人数')
    cached_excused = Column(Integer, nullable=False, default=0, comment='请假人数')
    cached_absent = Column(Integer, nullable=False, default=0, comment='缺勤人数')
    cached_rate = Column(DECIMAL(5, 2), nullable=True, comment='出勤率缓存(%)')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
