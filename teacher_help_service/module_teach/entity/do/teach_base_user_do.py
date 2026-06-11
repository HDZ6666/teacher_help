from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, func
from config.database import Base


class TeachBaseUser(Base):
    """
    基础用户表
    """

    __tablename__ = 'teach_base_users'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    phone = Column(String(20), nullable=False, unique=True, comment='手机号，唯一登录凭证')
    password_hash = Column(String(255), nullable=False, comment='加盐哈希后的密码')
    user_type = Column(String(1), nullable=False, comment='用户类型（0教师 1家长）')
    status = Column(String(1), nullable=False, default='0', comment='帐号状态（0正常 1停用）')
    last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')
    del_flag = Column(String(1), nullable=False, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=False, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=False, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
