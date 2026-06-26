from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, SMALLINT, String, Text

from config.database import Base


class TeachStudentComment(Base):
    """
    课后点评表
    """

    __tablename__ = 'teach_student_comment'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    attendance_id = Column(Integer, nullable=True, comment='点名记录ID')
    attendance_detail_id = Column(Integer, nullable=True, comment='点名明细ID')
    class_id = Column(Integer, nullable=True, comment='班级ID')
    student_id = Column(Integer, nullable=False, comment='学员ID')
    student_name = Column(String(50), nullable=True, comment='学员姓名快照')
    course_id = Column(Integer, nullable=True, comment='课程ID')
    course_name = Column(String(100), nullable=True, comment='课程名称快照')
    teacher_id = Column(Integer, nullable=True, comment='老师ID')
    teacher_name = Column(String(50), nullable=True, comment='老师姓名快照')
    class_date = Column(Date, nullable=True, comment='上课日期')
    performance_score = Column(Integer, nullable=True, comment='课堂表现评分(1-5)')
    homework_score = Column(Integer, nullable=True, comment='作业评分(1-5)')
    comment_content = Column(Text, nullable=True, comment='点评内容')
    strengths = Column(String(500), nullable=True, comment='优点表现')
    weaknesses = Column(String(500), nullable=True, comment='不足之处')
    suggestions = Column(String(500), nullable=True, comment='改进建议')
    comment_type = Column(String(20), nullable=True, default='single', comment='点评类型(single=单个 unified=统一 batch=批量)')
    status = Column(SMALLINT, nullable=True, default=1, comment='状态(1=已发布 2=已撤销)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
