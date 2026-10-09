from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from module_admin.annotation.pydantic_annotation import as_query


# ======================== 场馆 ========================
@as_query
class TeachVenuePageQueryModel(BaseModel):
    """
    场馆分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    venue_name: Optional[str] = Field(default=None, description='场馆名称')
    status: Optional[int] = Field(default=None, description='启用状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AddTeachVenueModel(BaseModel):
    """
    新增场馆模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    venue_no: Optional[str] = Field(default=None, description='场馆编号', max_length=50)
    venue_name: str = Field(description='场馆名称', max_length=100)
    address: Optional[str] = Field(default=None, description='场馆地址', max_length=255)
    description: Optional[str] = Field(default=None, description='场馆描述', max_length=500)
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @Xss(field_name='venue_name', message='场馆名称不能包含脚本字符')
    @NotBlank(field_name='venue_name', message='场馆名称不能为空')
    @Size(field_name='venue_name', min_length=0, max_length=100, message='场馆名称长度不能超过100个字符')
    def get_venue_name(self):
        return self.venue_name

    def validate_fields(self):
        self.get_venue_name()


class EditTeachVenueModel(AddTeachVenueModel):
    """
    编辑场馆模型
    """

    id: int = Field(description='场馆ID')


class ChangeTeachVenueStatusModel(BaseModel):
    """
    场馆启停模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='场馆ID')
    status: int = Field(description='启用状态')


class DeleteTeachVenueModel(BaseModel):
    """
    删除场馆模型
    """

    venue_ids: str = Field(description='场馆ID，多个用逗号分隔')


# ======================== 场地 ========================
class TeachCourtTimeModel(BaseModel):
    """
    场地可约时段模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='时段ID')
    court_id: Optional[int] = Field(default=None, description='场地ID')
    week_day: int = Field(description='星期(1-7)')
    start_time: str = Field(description='开始时间')
    end_time: str = Field(description='结束时间')


class TeachCourtQueryModel(BaseModel):
    """
    场地查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    venue_id: Optional[int] = Field(default=None, description='场馆ID')
    court_name: Optional[str] = Field(default=None, description='场地名称')
    court_type: Optional[str] = Field(default=None, description='场地类型')
    status: Optional[int] = Field(default=None, description='启用状态')


class AddTeachCourtModel(BaseModel):
    """
    新增场地模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    venue_id: int = Field(description='所属场馆ID')
    court_no: Optional[str] = Field(default=None, description='场地编号', max_length=50)
    court_name: str = Field(description='场地名称', max_length=100)
    court_type: Optional[str] = Field(default=None, description='场地类型', max_length=50)
    price_per_hour: Optional[Decimal] = Field(default=0, description='每小时价格')
    price_per_half_hour: Optional[Decimal] = Field(default=0, description='每半小时价格')
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)
    times: Optional[List[TeachCourtTimeModel]] = Field(default_factory=list, description='可约时段')

    @Xss(field_name='court_name', message='场地名称不能包含脚本字符')
    @NotBlank(field_name='court_name', message='场地名称不能为空')
    @Size(field_name='court_name', min_length=0, max_length=100, message='场地名称长度不能超过100个字符')
    def get_court_name(self):
        return self.court_name

    def validate_fields(self):
        self.get_court_name()


class EditTeachCourtModel(AddTeachCourtModel):
    """
    编辑场地模型
    """

    id: int = Field(description='场地ID')


class DeleteTeachCourtModel(BaseModel):
    """
    删除场地模型
    """

    court_ids: str = Field(description='场地ID，多个用逗号分隔')


# ======================== 订场/预订 ========================
@as_query
class TeachBookingGridQueryModel(BaseModel):
    """
    订场网格查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    venue_id: int = Field(description='场馆ID')
    date: str = Field(description='预订日期(YYYY-MM-DD)')


@as_query
class TeachBookingPageQueryModel(BaseModel):
    """
    预订记录分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    venue_id: Optional[int] = Field(default=None, description='场馆ID')
    court_id: Optional[int] = Field(default=None, description='场地ID')
    booking_no: Optional[str] = Field(default=None, description='预订单编号')
    customer_name: Optional[str] = Field(default=None, description='客户姓名')
    customer_phone: Optional[str] = Field(default=None, description='客户电话')
    booking_type: Optional[str] = Field(default=None, description='预订类型')
    booking_status: Optional[int] = Field(default=None, description='预订状态')
    pay_status: Optional[int] = Field(default=None, description='支付状态')
    booking_date: Optional[str] = Field(default=None, description='预订日期')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AddTeachBookingModel(BaseModel):
    """
    代预订模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    court_id: int = Field(description='场地ID')
    booking_date: str = Field(description='预订日期(YYYY-MM-DD)')
    start_time: str = Field(description='开始时间')
    end_time: str = Field(description='结束时间')
    customer_id: Optional[int] = Field(default=None, description='学员或客户ID')
    customer_name: Optional[str] = Field(default=None, description='客户姓名', max_length=50)
    customer_phone: Optional[str] = Field(default=None, description='客户电话', max_length=20)
    booking_type: Optional[str] = Field(default='normal', description='预订类型(normal/lock)')
    origin: Optional[str] = Field(default='admin', description='来源(admin/online)')
    amount: Optional[Decimal] = Field(default=0, description='应收金额(已弃用，后端按场地价格计算)')
    discount_amount: Optional[Decimal] = Field(default=0, description='人工减免金额(不含会员卡折扣)')
    card_grant_id: Optional[int] = Field(default=None, description='场地折扣卡发放ID(须属于 customer_id 对应学员)')
    pay_status: Optional[int] = Field(default=0, description='支付状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class LockCourtBookingModel(BaseModel):
    """
    锁场模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    court_id: int = Field(description='场地ID')
    booking_date: str = Field(description='预订日期(YYYY-MM-DD)')
    start_time: str = Field(description='开始时间')
    end_time: str = Field(description='结束时间')
    cancel_reason: Optional[str] = Field(default=None, description='锁场原因', max_length=255)
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class VerifyBookingModel(BaseModel):
    """
    核销模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='预订单ID')


class CancelBookingModel(BaseModel):
    """
    取消模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='预订单ID')
    cancel_reason: Optional[str] = Field(default=None, description='取消原因', max_length=255)
    refund_amount: Optional[Decimal] = Field(default=0, description='退款金额')


class TeachBookingModel(BaseModel):
    """
    预订单基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='预订单ID')
    booking_no: Optional[str] = Field(default=None, description='预订单编号')
    court_id: Optional[int] = Field(default=None, description='场地ID')
    court_name: Optional[str] = Field(default=None, description='场地名称快照')
    venue_id: Optional[int] = Field(default=None, description='场馆ID')
    booking_date: Optional[str] = Field(default=None, description='预订日期')
    start_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')
    customer_id: Optional[int] = Field(default=None, description='客户ID')
    customer_name: Optional[str] = Field(default=None, description='客户姓名')
    customer_phone: Optional[str] = Field(default=None, description='客户电话')
    booking_type: Optional[str] = Field(default=None, description='预订类型')
    origin: Optional[str] = Field(default=None, description='来源')
    amount: Optional[Decimal] = Field(default=0, description='应收金额')
    discount_amount: Optional[Decimal] = Field(default=0, description='优惠金额')
    card_grant_id: Optional[int] = Field(default=None, description='会员卡发放ID')
    pay_status: Optional[int] = Field(default=0, description='支付状态')
    booking_status: Optional[int] = Field(default=1, description='预订状态')
    verify_time: Optional[datetime] = Field(default=None, description='核销时间')
    cancel_reason: Optional[str] = Field(default=None, description='取消原因')
    refund_amount: Optional[Decimal] = Field(default=0, description='退款金额')
    operator_id: Optional[int] = Field(default=None, description='操作人ID')
    operator_name: Optional[str] = Field(default=None, description='操作人姓名')
    remark: Optional[str] = Field(default=None, description='备注')
