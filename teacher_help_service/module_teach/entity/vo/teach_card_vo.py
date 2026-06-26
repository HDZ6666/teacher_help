from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachCardPageQueryModel(BaseModel):
    """
    会员卡模板分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    card_name: Optional[str] = Field(default=None, description='卡名称')
    card_type: Optional[str] = Field(default=None, description='卡类型')
    status: Optional[int] = Field(default=None, description='启用状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TeachCardCourseModel(BaseModel):
    """
    会员卡适用课程模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='主键ID')
    card_id: Optional[int] = Field(default=None, description='卡ID')
    course_id: int = Field(description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称快照')


class TeachCardModel(BaseModel):
    """
    会员卡模板基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='卡ID')
    card_no: Optional[str] = Field(default=None, description='卡编号')
    card_name: Optional[str] = Field(default=None, description='卡名称')
    card_type: Optional[str] = Field(default='course', description='卡类型')
    initial_count: Optional[int] = Field(default=0, description='初始次数')
    valid_days: Optional[int] = Field(default=0, description='有效天数')
    effect_type: Optional[str] = Field(default='immediate', description='生效方式')
    discount_rate: Optional[Decimal] = Field(default=0, description='折扣率')
    cover_image: Optional[str] = Field(default=None, description='封面图')
    price: Optional[Decimal] = Field(default=0, description='售价')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    description: Optional[str] = Field(default=None, description='卡说明')
    status: Optional[int] = Field(default=1, description='启用状态')
    del_flag: Optional[int] = Field(default=0, description='删除标志')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AddTeachCardModel(BaseModel):
    """
    新增会员卡模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    card_no: Optional[str] = Field(default=None, description='卡编号', max_length=50)
    card_name: str = Field(description='卡名称', max_length=100)
    card_type: Optional[str] = Field(default='course', description='卡类型')
    initial_count: Optional[int] = Field(default=0, description='初始次数')
    valid_days: Optional[int] = Field(default=0, description='有效天数')
    effect_type: Optional[str] = Field(default='immediate', description='生效方式')
    discount_rate: Optional[Decimal] = Field(default=0, description='折扣率')
    cover_image: Optional[str] = Field(default=None, description='封面图', max_length=500)
    price: Optional[Decimal] = Field(default=0, description='售价')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    description: Optional[str] = Field(default=None, description='卡说明', max_length=500)
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)
    courses: Optional[List[TeachCardCourseModel]] = Field(default_factory=list, description='适用课程')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')

    @Xss(field_name='card_name', message='卡名称不能包含脚本字符')
    @NotBlank(field_name='card_name', message='卡名称不能为空')
    @Size(field_name='card_name', min_length=0, max_length=100, message='卡名称长度不能超过100个字符')
    def get_card_name(self):
        return self.card_name

    def validate_fields(self):
        self.get_card_name()


class EditTeachCardModel(AddTeachCardModel):
    """
    编辑会员卡模型
    """

    id: int = Field(description='卡ID')


class ChangeTeachCardStatusModel(BaseModel):
    """
    会员卡启停模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='卡ID')
    status: int = Field(description='启用状态')


class DeleteTeachCardModel(BaseModel):
    """
    删除会员卡模型
    """

    card_ids: str = Field(description='卡ID，多个用逗号分隔')


class TeachCardDetailModel(TeachCardModel):
    """
    会员卡详情模型
    """

    courses: List[TeachCardCourseModel] = Field(default_factory=list, description='适用课程')


@as_query
class TeachCardGrantPageQueryModel(BaseModel):
    """
    会员卡发放记录分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    card_id: Optional[int] = Field(default=None, description='卡ID')
    card_name: Optional[str] = Field(default=None, description='卡名称')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名')
    grant_status: Optional[int] = Field(default=None, description='发放状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class GrantTeachCardModel(BaseModel):
    """
    发卡给学员模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    card_id: int = Field(description='卡ID')
    student_id: int = Field(description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名')
    grant_count: Optional[int] = Field(default=None, description='发放次数(默认取卡初始次数)')
    valid_start_date: Optional[str] = Field(default=None, description='生效日期(不传按生效方式计算)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    def validate_fields(self):
        if not self.card_id:
            raise ValueError('请选择会员卡')
        if not self.student_id:
            raise ValueError('请选择学员')


class VoidTeachCardGrantModel(BaseModel):
    """
    作废发放记录模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='发放记录ID')
    remark: Optional[str] = Field(default=None, description='作废原因', max_length=500)


@as_query
class TeachCardLogPageQueryModel(BaseModel):
    """
    会员卡操作记录分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    card_id: Optional[int] = Field(default=None, description='卡ID')
    grant_id: Optional[int] = Field(default=None, description='发放记录ID')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    action: Optional[str] = Field(default=None, description='操作类型')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')
