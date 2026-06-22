from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, SMALLINT
from config.database import Base


class TeachCourse(Base):
    """
    课程基础信息表
    """

    __tablename__ = 'teach_course'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    course_no = Column(String(50), nullable=True, unique=True, comment='课程编号')
    course_name = Column(String(100), nullable=False, comment='课程名称')
    course_type = Column(String(32), nullable=False, default='one_to_many', comment='课程类型(one_to_many=一对多 one_to_one=一对一)')
    schedule_color = Column(String(20), nullable=True, default='#409EFF', comment='课表颜色')
    grade = Column(String(50), nullable=True, comment='年级')
    grade_label = Column(String(50), nullable=True, comment='年级名称')
    subject = Column(String(50), nullable=True, comment='科目')
    subject_label = Column(String(50), nullable=True, comment='科目名称')
    semester = Column(String(50), nullable=True, comment='学期')
    semester_label = Column(String(50), nullable=True, comment='学期名称')
    student_count = Column(Integer, nullable=True, default=0, comment='在读学员数')
    online_sale = Column(SMALLINT, nullable=True, default=0, comment='线上售卖状态(0=未售卖 1=售卖)')
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
