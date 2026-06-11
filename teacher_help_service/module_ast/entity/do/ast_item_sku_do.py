from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, SMALLINT, ForeignKey
from config.database import Base


class AstItemSku(Base):
    """
    物品SKU表
    """
    
    __tablename__ = 'ast_item_sku'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 外键
    item_id = Column(Integer, ForeignKey('ast_item.id'), nullable=False, comment='物品ID')
    
    # 业务字段
    sku_no = Column(String(50), nullable=True, unique=True, comment='SKU编号')
    sku_name = Column(String(100), nullable=False, comment='SKU名称')
    spec1_value = Column(String(50), nullable=True, comment='规格1值')
    spec2_value = Column(String(50), nullable=True, comment='规格2值')
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment='售卖价格')
    stock = Column(Integer, nullable=True, default=0, comment='库存数量')
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

