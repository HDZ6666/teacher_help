from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class AstItemSkuModel(BaseModel):
    """
    物品SKU模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='SKU ID')
    item_id: Optional[int] = Field(default=None, description='物品ID')
    sku_no: Optional[str] = Field(default=None, description='SKU编号')
    sku_name: Optional[str] = Field(default=None, description='SKU名称')
    spec_text: Optional[str] = Field(default=None, description='规格文本')
    spec1_value: Optional[str] = Field(default=None, description='规格1值')
    spec2_value: Optional[str] = Field(default=None, description='规格2值')
    price: Optional[Decimal] = Field(default=0, description='售卖价格')
    cost_price: Optional[Decimal] = Field(default=0, description='成本价')
    stock: Optional[int] = Field(default=0, description='库存数量')
    available_stock: Optional[int] = Field(default=0, description='可用库存')
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注')


class AstItemSkuPayloadModel(BaseModel):
    """
    物品SKU保存入参
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: Optional[int] = Field(default=None, description='SKU ID')
    sku_no: Optional[str] = Field(default=None, description='SKU编号')
    sku_name: Optional[str] = Field(default=None, description='SKU名称')
    spec_text: Optional[str] = Field(default=None, description='规格文本')
    spec1_value: Optional[str] = Field(default=None, description='规格1值')
    spec2_value: Optional[str] = Field(default=None, description='规格2值')
    price: Optional[Decimal] = Field(default=None, description='售卖价格')
    cost_price: Optional[Decimal] = Field(default=None, description='成本价')
    stock: Optional[int] = Field(default=None, description='库存数量')
    status: Optional[int] = Field(default=1, description='启用状态')
    specs: Optional[List[dict]] = Field(default=None, description='前端规格结构')


@as_query
class AstStockRecordPageQueryModel(BaseModel):
    """
    出入库流水分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    keyword: Optional[str] = Field(default=None, description='物品名称关键字')
    item_name: Optional[str] = Field(default=None, description='物品名称')
    business_type: Optional[str] = Field(default=None, description='业务类型')
    stock_type: Optional[str] = Field(default=None, description='出入库类型(in/out)')
    related_type: Optional[str] = Field(default=None, description='关联角色类型')
    related_name: Optional[str] = Field(default=None, description='关联角色名称')
    item_names: Optional[str] = Field(default=None, description='物品名称，多个用逗号分隔')
    exclude_voided: Optional[bool] = Field(default=True, description='是否过滤已作废记录')
    begin_time: Optional[str] = Field(default=None, description='开始日期')
    end_time: Optional[str] = Field(default=None, description='结束日期')


class AstStockOperationItemModel(BaseModel):
    """
    出入库操作明细
    """

    model_config = ConfigDict(alias_generator=to_camel)

    item_id: Optional[int] = Field(default=None, description='物品ID')
    item_name: Optional[str] = Field(default=None, description='物品名称')
    sku_id: int = Field(description='SKU ID')
    sku_name: Optional[str] = Field(default=None, description='SKU名称')
    spec_text: Optional[str] = Field(default=None, description='规格文本')
    quantity: Optional[int] = Field(default=None, description='数量')
    price: Optional[Decimal] = Field(default=None, description='前端单价字段')
    unit_price: Optional[Decimal] = Field(default=None, description='采购单价')
    current_stock: Optional[int] = Field(default=None, description='盘点当前库存')
    actual_stock: Optional[int] = Field(default=None, description='盘点实际库存')
    remark: Optional[str] = Field(default=None, description='备注')


class AddPurchaseOrderModel(BaseModel):
    """
    新建采购入库模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    purchase_date: Optional[Any] = Field(default=None, description='采购日期')
    supplier_name: Optional[str] = Field(default=None, description='供应商名称')
    payment_method: Optional[str] = Field(default=None, description='支付方式')
    account_name: Optional[str] = Field(default=None, description='账户名称')
    account: Optional[str] = Field(default=None, description='前端账户字段')
    year_book: Optional[str] = Field(default=None, description='年度账本')
    operator_name: Optional[str] = Field(default=None, description='经办人')
    operator: Optional[str] = Field(default=None, description='前端经办人字段')
    remark: Optional[str] = Field(default=None, description='备注')
    items: List[AstStockOperationItemModel] = Field(default_factory=list, description='采购明细')


class AddReceiveStockModel(BaseModel):
    """
    领用出库模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    receive_time: Optional[Any] = Field(default=None, description='领用时间')
    role_type: Optional[str] = Field(default=None, description='角色类型')
    role_name: Optional[str] = Field(default=None, description='角色名称')
    operator: Optional[str] = Field(default=None, description='操作人')
    remark: Optional[str] = Field(default=None, description='备注')
    items: List[AstStockOperationItemModel] = Field(default_factory=list, description='领用明细')


class AddReturnStockModel(BaseModel):
    """
    退领入库模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    return_time: Optional[Any] = Field(default=None, description='退领时间')
    role_type: Optional[str] = Field(default=None, description='角色类型')
    role_name: Optional[str] = Field(default=None, description='角色名称')
    operator: Optional[str] = Field(default=None, description='操作人')
    remark: Optional[str] = Field(default=None, description='备注')
    items: List[AstStockOperationItemModel] = Field(default_factory=list, description='退领明细')


class AddInventoryStockModel(BaseModel):
    """
    库存盘点模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    inventory_date: Optional[Any] = Field(default=None, description='盘点日期')
    operator: Optional[str] = Field(default=None, description='操作人')
    remark: Optional[str] = Field(default=None, description='备注')
    items: List[AstStockOperationItemModel] = Field(default_factory=list, description='盘点明细')


@as_query
class AstFeeItemPageQueryModel(BaseModel):
    """
    费用分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    fee_name: Optional[str] = Field(default=None, description='费用名称')
    status: Optional[int] = Field(default=None, description='启用状态')


class AstFeeCourseModel(BaseModel):
    """
    费用绑定课程模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='主键ID')
    fee_id: Optional[int] = Field(default=None, description='费用ID')
    course_id: int = Field(description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称')


class AddAstFeeItemModel(BaseModel):
    """
    新增费用模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    fee_name: str = Field(description='费用名称', max_length=100)
    amount: Optional[Decimal] = Field(default=None, description='费用金额')
    price: Optional[Decimal] = Field(default=None, description='前端售卖单价字段')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    sort: Optional[int] = Field(default=0, description='排序')
    course_ids: Optional[List[int]] = Field(default_factory=list, description='课程ID列表')
    course_names: Optional[List[str]] = Field(default_factory=list, description='课程名称列表')
    courses: Optional[List[AstFeeCourseModel]] = Field(default_factory=list, description='课程列表')
    remark: Optional[str] = Field(default=None, description='备注')


class EditAstFeeItemModel(AddAstFeeItemModel):
    """
    编辑费用模型
    """

    id: int = Field(description='费用ID')


class ChangeAstFeeStatusModel(BaseModel):
    """
    修改费用启停状态模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='费用ID')
    status: int = Field(description='启用状态')


class DeleteAstFeeItemModel(BaseModel):
    """
    删除费用模型
    """

    fee_ids: str = Field(description='费用ID，多个用逗号分隔')


class AstFeeItemResponseModel(BaseModel):
    """
    费用响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='费用ID')
    fee_name: str = Field(description='费用名称')
    amount: Decimal = Field(description='费用金额')
    price: Decimal = Field(description='售卖单价')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: int = Field(description='启用状态')
    sort: Optional[int] = Field(default=0, description='排序')
    course_ids: List[int] = Field(default_factory=list, description='课程ID列表')
    course_names: List[str] = Field(default_factory=list, description='课程名称列表')
    course_name: Optional[str] = Field(default=None, description='课程名称展示')
    courses: List[AstFeeCourseModel] = Field(default_factory=list, description='课程列表')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AstStockRecordResponseModel(BaseModel):
    """
    出入库流水响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='流水ID')
    record_no: str = Field(description='流水号')
    stock_date: Optional[Any] = Field(default=None, description='出入库时间')
    item_id: int = Field(description='物品ID')
    item_name: str = Field(description='物品名称')
    sku_id: int = Field(description='SKU ID')
    sku_name: str = Field(description='SKU名称')
    business_type: str = Field(description='业务类型')
    quantity: int = Field(description='数量')
    stock_before: Optional[int] = Field(default=0, description='操作前库存')
    stock_after: Optional[int] = Field(default=0, description='操作后库存')
    role_type: Optional[str] = Field(default=None, description='角色类型')
    role_name: Optional[str] = Field(default=None, description='角色名称')
    business_no: Optional[str] = Field(default=None, description='关联业务编号')
    operator: Optional[str] = Field(default=None, description='经办人')
    remark: Optional[str] = Field(default=None, description='备注')
