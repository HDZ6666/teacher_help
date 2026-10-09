from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from config.database import Base


class TeachTeacher(Base):
    """
    教师信息表
    """

    __tablename__ = 'teach_teachers'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('teach_base_users.id'), nullable=False, unique=True, comment='关联基础用户ID')
    teacher_name = Column(String(50), nullable=False, comment='教师姓名')
    nickname = Column(String(50), nullable=True, comment='昵称')
    avatar_url = Column(String(512), nullable=True, comment='头像URL')
    id_card = Column(String(18), nullable=True, comment='身份证号')
    qualification_cert = Column(String(255), nullable=True, comment='教师资格证号')
    work_experience = Column(Integer, nullable=True, default=0, comment='教学经验(年)')
    introduction = Column(Text, nullable=True, comment='个人简介')
    hourly_rate = Column(String(20), nullable=True, default='0.00', comment='默认课时费')
    bank_account = Column(String(50), nullable=True, comment='银行账号')
    bank_name = Column(String(100), nullable=True, comment='开户银行')
    settlement_cycle = Column(String(1), nullable=True, default='0', comment='结算周期（0周结 1月结）')
    status = Column(String(1), nullable=False, default='0', comment='帐号状态（0正常 1停用 2已注销）')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
