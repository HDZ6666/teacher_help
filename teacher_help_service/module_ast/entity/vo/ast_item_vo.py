from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class AstItemPageQueryModel(BaseModel):
    """
    物品分页查询模型
    """
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True
    )
    
    # 分页参数
    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    
    # 查询条件
    item_name: Optional[str] = Field(default=None, description='物品名称')
    item_type: Optional[Literal[1, 2]] = Field(default=None, description='物品类型(1=实物 2=虚拟)')
    category: Optional[str] = Field(default=None, description='物品分类')
    status: Optional[Literal[0, 1]] = Field(default=None, description='启用状态(0=停用 1=启用)')
    
    # 时间范围
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AstItemModel(BaseModel):
    """
    物品表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='物品ID')
    item_no: Optional[str] = Field(default=None, description='物品编号')
    item_name: Optional[str] = Field(default=None, description='物品名称')
    item_type: Optional[Literal[0, 1, 2]] = Field(default=None, description='物品类型(1=实物 2=虚拟)')
    category: Optional[str] = Field(default=None, description='物品分类')
    unit: Optional[str] = Field(default=None, description='单位')
    default_price: Optional[Decimal] = Field(default=None, description='默认售卖单价')
    image_url: Optional[str] = Field(default=None, description='物品图片')
    spec1_name: Optional[str] = Field(default=None, description='规格1名称')
    spec1_values: Optional[str] = Field(default=None, description='规格1值列表')
    spec2_name: Optional[str] = Field(default=None, description='规格2名称')
    spec2_values: Optional[str] = Field(default=None, description='规格2值列表')
    total_stock: Optional[int] = Field(default=None, description='总库存')
    available_stock: Optional[int] = Field(default=None, description='可用库存')
    enable_stock: Optional[int] = Field(default=1, description='是否开启库存')
    warning_stock: Optional[int] = Field(default=0, description='库存预警数量')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[Literal[0, 1]] = Field(default=None, description='启用状态(0=停用 1=启用)')
    del_flag: Optional[int] = Field(default=None, description='删除标志(0=存在 1=删除)')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @Xss(field_name='item_name', message='物品名称不能包含脚本字符')
    @Size(field_name='item_name', min_length=0, max_length=100, message='物品名称长度不能超过100个字符')
    def get_item_name(self):
        return self.item_name

    def validate_fields(self):
        """触发所有字段验证"""
        if self.item_name:
            self.get_item_name()


class AddAstItemModel(BaseModel):
    """
    新增物品模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    # 必填字段
    item_name: str = Field(description='物品名称', max_length=100)
    item_type: Literal[1, 2] = Field(description='物品类型(1=实物 2=虚拟)')

    # 可选字段
    item_no: Optional[str] = Field(default=None, description='物品编号', max_length=50)
    category: Optional[str] = Field(default=None, description='物品分类', max_length=50)
    unit: Optional[str] = Field(default=None, description='单位', max_length=20)
    default_price: Optional[Decimal] = Field(default=None, description='默认售卖单价')
    image_url: Optional[str] = Field(default=None, description='物品图片', max_length=500)
    spec1_name: Optional[str] = Field(default=None, description='规格1名称', max_length=50)
    spec1_values: Optional[str] = Field(default=None, description='规格1值列表(逗号分隔)', max_length=500)
    spec2_name: Optional[str] = Field(default=None, description='规格2名称', max_length=50)
    spec2_values: Optional[str] = Field(default=None, description='规格2值列表(逗号分隔)', max_length=500)
    single_price: Optional[Decimal] = Field(default=None, description='前端单品单价')
    enable_stock: Optional[Literal[0, 1]] = Field(default=1, description='是否开启库存')
    warning_stock: Optional[int] = Field(default=0, description='库存预警数量')
    online_sale: Optional[Literal[0, 1]] = Field(default=0, description='线上售卖状态')
    item_images: Optional[List[Any]] = Field(default_factory=list, description='前端图片列表')
    specs: Optional[List[dict]] = Field(default_factory=list, description='前端规格列表')
    skus: Optional[List[dict]] = Field(default_factory=list, description='前端SKU列表')
    course_ids: Optional[List[int]] = Field(default_factory=list, description='绑定课程ID列表')
    course_names: Optional[List[str]] = Field(default_factory=list, description='绑定课程名称列表')
    courses: Optional[List[dict]] = Field(default_factory=list, description='绑定课程列表')
    status: Optional[Literal[0, 1]] = Field(default=1, description='启用状态(0=停用 1=启用)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    # 审计字段
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')

    # 字段验证装饰器
    @Xss(field_name='item_name', message='物品名称不能包含脚本字符')
    @NotBlank(field_name='item_name', message='物品名称不能为空')
    @Size(field_name='item_name', min_length=0, max_length=100, message='物品名称长度不能超过100个字符')
    def get_item_name(self):
        return self.item_name

    def validate_fields(self):
        """触发所有字段验证"""
        self.get_item_name()


class EditAstItemModel(BaseModel):
    """
    编辑物品模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    # 必填字段
    id: Optional[int] = Field(default=None, description='物品ID')
    item_name: str = Field(description='物品名称', max_length=100)
    item_type: Literal[1, 2] = Field(description='物品类型(1=实物 2=虚拟)')

    # 可选字段
    item_no: Optional[str] = Field(default=None, description='物品编号', max_length=50)
    category: Optional[str] = Field(default=None, description='物品分类', max_length=50)
    unit: Optional[str] = Field(default=None, description='单位', max_length=20)
    default_price: Optional[Decimal] = Field(default=None, description='默认售卖单价')
    image_url: Optional[str] = Field(default=None, description='物品图片', max_length=500)
    spec1_name: Optional[str] = Field(default=None, description='规格1名称', max_length=50)
    spec1_values: Optional[str] = Field(default=None, description='规格1值列表(逗号分隔)', max_length=500)
    spec2_name: Optional[str] = Field(default=None, description='规格2名称', max_length=50)
    spec2_values: Optional[str] = Field(default=None, description='规格2值列表(逗号分隔)', max_length=500)
    single_price: Optional[Decimal] = Field(default=None, description='前端单品单价')
    enable_stock: Optional[Literal[0, 1]] = Field(default=1, description='是否开启库存')
    warning_stock: Optional[int] = Field(default=0, description='库存预警数量')
    online_sale: Optional[Literal[0, 1]] = Field(default=0, description='线上售卖状态')
    item_images: Optional[List[Any]] = Field(default_factory=list, description='前端图片列表')
    specs: Optional[List[dict]] = Field(default_factory=list, description='前端规格列表')
    skus: Optional[List[dict]] = Field(default_factory=list, description='前端SKU列表')
    course_ids: Optional[List[int]] = Field(default_factory=list, description='绑定课程ID列表')
    course_names: Optional[List[str]] = Field(default_factory=list, description='绑定课程名称列表')
    courses: Optional[List[dict]] = Field(default_factory=list, description='绑定课程列表')
    status: Optional[Literal[0, 1]] = Field(default=1, description='启用状态(0=停用 1=启用)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    # 审计字段
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')

    # 字段验证装饰器
    @Xss(field_name='item_name', message='物品名称不能包含脚本字符')
    @NotBlank(field_name='item_name', message='物品名称不能为空')
    @Size(field_name='item_name', min_length=0, max_length=100, message='物品名称长度不能超过100个字符')
    def get_item_name(self):
        return self.item_name

    def validate_fields(self):
        """触发所有字段验证"""
        self.get_item_name()


class DeleteAstItemModel(BaseModel):
    """
    删除物品模型
    """

    item_ids: str = Field(description='物品ID，多个用逗号分隔')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')


class AstItemResponseModel(BaseModel):
    """
    物品响应模型（列表）
    """
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True
    )
    
    id: int = Field(description='物品ID')
    item_no: Optional[str] = Field(default=None, description='物品编号')
    item_code: Optional[str] = Field(default=None, description='前端物品编码')
    item_name: str = Field(description='物品名称')
    item_type: int = Field(description='物品类型')
    item_type_label: Optional[str] = Field(default=None, description='物品类型标签')
    category: Optional[str] = Field(default=None, description='物品分类')
    unit: Optional[str] = Field(default=None, description='单位')
    default_price: Optional[Decimal] = Field(default=None, description='默认售卖单价')
    total_stock: Optional[int] = Field(default=0, description='总库存')
    available_stock: Optional[int] = Field(default=0, description='可用库存')
    sku_count: Optional[int] = Field(default=0, description='SKU数量')
    price_range: Optional[str] = Field(default=None, description='价格范围')
    enable_stock: Optional[int] = Field(default=1, description='是否开启库存')
    warning_stock: Optional[int] = Field(default=0, description='库存预警数量')
    is_warning: Optional[bool] = Field(default=False, description='是否库存预警')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    course_ids: Optional[List[int]] = Field(default_factory=list, description='绑定课程ID列表')
    course_names: Optional[List[str]] = Field(default_factory=list, description='绑定课程名称列表')
    course_name: Optional[str] = Field(default=None, description='绑定课程展示')
    courses: Optional[List[dict]] = Field(default_factory=list, description='绑定课程列表')
    status: int = Field(description='启用状态')
    create_time: datetime = Field(description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AstItemDetailModel(BaseModel):
    """
    物品详情模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True
    )

    id: int = Field(description='物品ID')
    item_no: Optional[str] = Field(default=None, description='物品编号')
    item_code: Optional[str] = Field(default=None, description='前端物品编码')
    item_name: str = Field(description='物品名称')
    item_type: int = Field(description='物品类型')
    item_type_label: Optional[str] = Field(default=None, description='物品类型标签')
    category: Optional[str] = Field(default=None, description='物品分类')
    unit: Optional[str] = Field(default=None, description='单位')
    default_price: Optional[Decimal] = Field(default=None, description='默认售卖单价')
    image_url: Optional[str] = Field(default=None, description='物品图片')
    spec1_name: Optional[str] = Field(default=None, description='规格1名称')
    spec1_values: Optional[str] = Field(default=None, description='规格1值列表')
    spec2_name: Optional[str] = Field(default=None, description='规格2名称')
    spec2_values: Optional[str] = Field(default=None, description='规格2值列表')
    total_stock: Optional[int] = Field(default=0, description='总库存')
    available_stock: Optional[int] = Field(default=0, description='可用库存')
    sku_count: Optional[int] = Field(default=0, description='SKU数量')
    price_range: Optional[str] = Field(default=None, description='价格范围')
    enable_stock: Optional[int] = Field(default=1, description='是否开启库存')
    warning_stock: Optional[int] = Field(default=0, description='库存预警数量')
    is_warning: Optional[bool] = Field(default=False, description='是否库存预警')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    single_price: Optional[Decimal] = Field(default=None, description='前端单品单价')
    item_images: Optional[List[Any]] = Field(default_factory=list, description='前端图片列表')
    specs: Optional[List[dict]] = Field(default_factory=list, description='前端规格列表')
    skus: Optional[List[dict]] = Field(default_factory=list, description='SKU列表')
    course_ids: Optional[List[int]] = Field(default_factory=list, description='绑定课程ID列表')
    course_names: Optional[List[str]] = Field(default_factory=list, description='绑定课程名称列表')
    course_name: Optional[str] = Field(default=None, description='绑定课程展示')
    courses: Optional[List[dict]] = Field(default_factory=list, description='绑定课程列表')
    status: int = Field(description='启用状态')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: datetime = Field(description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
