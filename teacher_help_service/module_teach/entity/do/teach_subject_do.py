from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, CHAR
from config.database import Base


class TeachSubject(Base):
    """
    教学科目字典表
    """

    __tablename__ = 'teach_subjects'

    subject_id = Column(Integer, primary_key=True, autoincrement=True, comment='科目ID')
    subject_code = Column(String(64), nullable=False, comment='科目编码（唯一标识）')
    subject_name = Column(String(50), nullable=False, comment='科目名称')
    subject_category = Column(String(50), default=None, comment='科目类别（语文、数学、英语等）')
    subject_sort = Column(Integer, default=0, comment='显示顺序')
    status = Column(CHAR(1), default='0', comment='状态（0正常 1停用）')
    del_flag = Column(CHAR(1), default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), default=None, comment='备注')

