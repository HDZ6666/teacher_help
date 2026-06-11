from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, CHAR
from config.database import Base


class TeachGrade(Base):
    """
    教学年级字典表
    """

    __tablename__ = 'teach_grades'

    grade_id = Column(Integer, primary_key=True, autoincrement=True, comment='年级ID')
    grade_code = Column(String(64), nullable=False, comment='年级编码（唯一标识）')
    grade_name = Column(String(50), nullable=False, comment='年级名称')
    education_level = Column(String(50), default=None, comment='教育阶段（小学、初中、高中）')
    grade_sort = Column(Integer, default=0, comment='显示顺序')
    status = Column(CHAR(1), default='0', comment='状态（0正常 1停用）')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), default=None, comment='备注')

