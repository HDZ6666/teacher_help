from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Date, ForeignKey, JSON
from config.database import Base


class TeachStudent(Base):
    """
    学生信息表
    """

    __tablename__ = 'teach_students'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    parent_id = Column(Integer, ForeignKey('teach_parents.id'), nullable=False, comment='关联家长ID')
    student_name = Column(String(50), nullable=False, comment='学生姓名')
    gender = Column(String(1), nullable=True, default='0', comment='用户性别（0男 1女 2未知）')
    birthday = Column(Date, nullable=True, comment='出生日期')
    school_name = Column(String(100), nullable=True, comment='就读学校')
    grade = Column(String(20), nullable=True, comment='年级')
    class_name = Column(String(50), nullable=True, comment='班级')
    student_id_in_school = Column(String(50), nullable=True, comment='学号')
    learning_style = Column(String(1), nullable=True, comment='学习风格（0视觉型 1听觉型 2动觉型）')
    personality_traits = Column(JSON, nullable=True, comment='性格特点标签')
    learning_difficulties = Column(Text, nullable=True, comment='学习困难点')
    interests_hobbies = Column(JSON, nullable=True, comment='兴趣爱好')
    medical_notes = Column(Text, nullable=True, comment='医疗备注(过敏史等)')
    emergency_contact = Column(String(20), nullable=True, comment='紧急联系人电话')
    status = Column(String(1), nullable=False, default='0', comment='帐号状态（0在读 1休学 2转学 3毕业）')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
