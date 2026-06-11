from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from config.database import Base


class AstItemCourse(Base):
    """
    物品课程关联表
    """

    __tablename__ = 'ast_item_course'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    item_id = Column(Integer, ForeignKey('ast_item.id'), nullable=False, comment='物品ID')
    course_id = Column(Integer, nullable=False, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
