from sqlalchemy import Column, Integer
from config.database import Base


class TeachTeacherSubject(Base):
    """
    教师-科目关联表
    """

    __tablename__ = 'teach_teacher_subject'

    teacher_id = Column(Integer, primary_key=True, nullable=False, comment='教师ID')
    subject_id = Column(Integer, primary_key=True, nullable=False, comment='科目ID')


class TeachTeacherGrade(Base):
    """
    教师-年级关联表
    """

    __tablename__ = 'teach_teacher_grade'

    teacher_id = Column(Integer, primary_key=True, nullable=False, comment='教师ID')
    grade_id = Column(Integer, primary_key=True, nullable=False, comment='年级ID')

