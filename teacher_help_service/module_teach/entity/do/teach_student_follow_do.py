from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Integer, SMALLINT, String, Text
from config.database import Base


class TeachStudentFollow(Base):
    """
    学员跟进记录表（P3）
    """

    __tablename__ = 'teach_student_follow'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    student_id = Column(Integer, nullable=False, index=True, comment='学员ID')
    student_name = Column(String(50), nullable=True, comment='学员姓名快照')
    follow_type = Column(String(20), nullable=False, comment='跟进方式(phone=电话 wechat=微信 visit=面谈 other=其他)')
    follow_stage = Column(String(50), nullable=True, comment='跟进阶段')
    content = Column(Text, nullable=False, comment='跟进内容')
    follow_time = Column(DateTime, nullable=False, comment='跟进时间')
    next_follow_date = Column(Date, nullable=True, comment='下次跟进日期')
    follow_user_id = Column(Integer, nullable=True, comment='跟进人(sys_user.user_id)')
    follow_user_name = Column(String(64), nullable=True, comment='跟进人姓名快照')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
