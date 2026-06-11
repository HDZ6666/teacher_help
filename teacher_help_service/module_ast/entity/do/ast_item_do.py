from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT
from config.database import Base


class AstItem(Base):
    """
    物品基本信息表
    """
    
    __tablename__ = 'ast_item'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 业务字段
    item_no = Column(String(50), nullable=True, unique=True, comment='物品编号')
    item_name = Column(String(100), nullable=False, comment='物品名称')
    item_type = Column(SMALLINT, nullable=False, comment='物品类型(1=实物 2=虚拟)')
    category = Column(String(50), nullable=True, comment='物品分类')
    unit = Column(String(20), nullable=True, comment='单位(本/个/套/份等)')
    default_price = Column(DECIMAL(10, 2), nullable=True, comment='默认售卖单价')
    image_url = Column(String(500), nullable=True, comment='物品图片')
    
    # 规格字段
    spec1_name = Column(String(50), nullable=True, comment='规格1名称')
    spec1_values = Column(String(500), nullable=True, comment='规格1值列表(逗号分隔)')
    spec2_name = Column(String(50), nullable=True, comment='规格2名称')
    spec2_values = Column(String(500), nullable=True, comment='规格2值列表(逗号分隔)')
    
    # 库存字段
    total_stock = Column(Integer, nullable=True, default=0, comment='总库存')
    available_stock = Column(Integer, nullable=True, default=0, comment='可用库存')
    
    # 状态字段
    status = Column(SMALLINT, nullable=True, default=1, comment='启用状态(0=停用 1=启用)')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
    
    # 审计字段
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')

