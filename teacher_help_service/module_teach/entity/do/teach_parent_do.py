from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from config.database import Base


class TeachParent(Base):
    """
    家长信息表
    """

    __tablename__ = 'teach_parents'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('teach_base_users.id'), nullable=False, unique=True, comment='关联基础用户ID')
    parent_name = Column(String(50), nullable=False, comment='家长姓名')
    nickname = Column(String(50), nullable=True, comment='昵称')
    avatar_url = Column(String(512), nullable=True, comment='头像URL')
    wechat_id = Column(String(50), nullable=True, comment='微信号')
    emergency_contact = Column(String(20), nullable=True, comment='紧急联系电话')
    address = Column(String(255), nullable=True, comment='家庭住址')
    occupation = Column(String(50), nullable=True, comment='职业')
    education_level = Column(String(20), nullable=True, comment='学历')
    family_income_range = Column(String(1), nullable=True, comment='家庭收入范围（0-5k以下 1-5-10k 2-10-20k 3-20k以上）')
    payment_preference = Column(String(1), nullable=True, default='0', comment='付费偏好（0按课时 1包月 2包季 3包年）')
    status = Column(String(1), nullable=False, default='0', comment='帐号状态（0正常 1停用 2已注销）')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
