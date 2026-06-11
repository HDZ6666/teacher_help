from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Date, SMALLINT
from config.database import Base


class AstPurchaseOrder(Base):
    """
    采购单主表
    """

    __tablename__ = 'ast_purchase_order'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    order_no = Column(String(50), nullable=False, unique=True, comment='采购单号')
    purchase_date = Column(Date, nullable=False, comment='采购日期')
    supplier_id = Column(Integer, nullable=True, comment='供应商ID')
    supplier_name = Column(String(100), nullable=True, comment='供应商名称')
    total_quantity = Column(Integer, nullable=True, default=0, comment='总数量')
    total_amount = Column(DECIMAL(10, 2), nullable=True, default=0.00, comment='总金额')
    payment_method = Column(String(20), nullable=True, comment='支付方式')
    account_id = Column(Integer, nullable=True, comment='账户ID')
    account_name = Column(String(100), nullable=True, comment='账户名称')
    year_book = Column(String(20), nullable=True, comment='年度账本')
    status = Column(SMALLINT, nullable=True, default=1, comment='状态(0=草稿 1=已完成 2=已取消)')
    operator_id = Column(Integer, nullable=True, comment='操作人ID')
    operator_name = Column(String(50), nullable=True, comment='操作人姓名')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
    del_flag = Column(SMALLINT, nullable=True, default=0, comment='删除标志(0=存在 1=删除)')
