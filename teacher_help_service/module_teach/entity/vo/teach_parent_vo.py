from datetime import datetime
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import Network, NotBlank, Size, Xss
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachParentPageQueryModel(BaseModel):
    """
    家长分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    parent_name: Optional[str] = Field(default=None, description='家长姓名')
    phone: Optional[str] = Field(default=None, description='手机号')
    wechat_id: Optional[str] = Field(default=None, description='微信号')
    status: Optional[Literal['1', '2', '3']] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AddTeachParentModel(BaseModel):
    """
    新增家长模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    phone: str = Field(description='手机号', min_length=11, max_length=11)
    password: str = Field(description='密码', min_length=6, max_length=20)
    parent_name: str = Field(description='家长姓名', max_length=50)
    nickname: Optional[str] = Field(default=None, description='昵称', max_length=50)
    avatar_url: Optional[str] = Field(default=None, description='头像URL', max_length=512)
    wechat_id: Optional[str] = Field(default=None, description='微信号', max_length=50)
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系电话', max_length=20)
    address: Optional[str] = Field(default=None, description='家庭住址', max_length=255)
    occupation: Optional[str] = Field(default=None, description='职业', max_length=50)
    education_level: Optional[str] = Field(default=None, description='学历', max_length=20)
    family_income_range: Optional[int] = Field(default=None, description='家庭收入范围: 1-5k以下, 2-5-10k, 3-10-20k, 4-20k以上')
    payment_preference: Optional[int] = Field(default=1, description='付费偏好: 1-按课时, 2-包月, 3-包季, 4-包年')
    status: Optional[Literal['1', '2', '3']] = Field(default='1', description='状态: 1-正常, 2-暂停, 3-已注销')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='parent_name', message='家长姓名不能为空')
    @Size(field_name='parent_name', min_length=0, max_length=50, message='家长姓名长度不能超过50个字符')
    @Xss(field_name='parent_name', message='家长姓名不能包含脚本字符')
    def get_parent_name(self):
        return self.parent_name

    @NotBlank(field_name='phone', message='手机号不能为空')
    @Size(field_name='phone', min_length=11, max_length=11, message='手机号长度必须为11位')
    def get_phone(self):
        return self.phone

    def validate_fields(self):
        self.get_parent_name()
        self.get_phone()


class EditTeachParentModel(BaseModel):
    """
    编辑家长模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='家长ID')
    parent_name: Optional[str] = Field(default=None, description='家长姓名', max_length=50)
    nickname: Optional[str] = Field(default=None, description='昵称', max_length=50)
    avatar_url: Optional[str] = Field(default=None, description='头像URL', max_length=512)
    wechat_id: Optional[str] = Field(default=None, description='微信号', max_length=50)
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系电话', max_length=20)
    address: Optional[str] = Field(default=None, description='家庭住址', max_length=255)
    occupation: Optional[str] = Field(default=None, description='职业', max_length=50)
    education_level: Optional[str] = Field(default=None, description='学历', max_length=20)
    family_income_range: Optional[int] = Field(default=None, description='家庭收入范围: 1-5k以下, 2-5-10k, 3-10-20k, 4-20k以上')
    payment_preference: Optional[int] = Field(default=None, description='付费偏好: 1-按课时, 2-包月, 3-包季, 4-包年')
    status: Optional[Literal['1', '2', '3']] = Field(default=None, description='状态: 1-正常, 2-暂停, 3-已注销')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='parent_name', message='家长姓名不能为空')
    @Size(field_name='parent_name', min_length=0, max_length=50, message='家长姓名长度不能超过50个字符')
    @Xss(field_name='parent_name', message='家长姓名不能包含脚本字符')
    def get_parent_name(self):
        return self.parent_name

    def validate_fields(self):
        self.get_parent_name()


class DeleteTeachParentModel(BaseModel):
    """
    删除家长模型
    """

    ids: str = Field(description='家长ID，多个用逗号分隔')


class TeachParentResponseModel(BaseModel):
    """
    家长响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='家长ID')
    user_id: int = Field(description='关联基础用户ID')
    phone: Optional[str] = Field(default=None, description='手机号')
    parent_name: str = Field(description='家长姓名')
    nickname: Optional[str] = Field(default=None, description='昵称')
    avatar_url: Optional[str] = Field(default=None, description='头像URL')
    wechat_id: Optional[str] = Field(default=None, description='微信号')
    address: Optional[str] = Field(default=None, description='家庭住址')
    occupation: Optional[str] = Field(default=None, description='职业')
    education_level: Optional[str] = Field(default=None, description='学历')
    family_income_range: Optional[int] = Field(default=None, description='家庭收入范围')
    family_income_range_name: Optional[str] = Field(default=None, description='家庭收入范围名称')
    payment_preference: Optional[int] = Field(default=None, description='付费偏好')
    payment_preference_name: Optional[str] = Field(default=None, description='付费偏好名称')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeachParentDetailModel(BaseModel):
    """
    家长详情模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='家长ID')
    user_id: int = Field(description='关联基础用户ID')
    phone: Optional[str] = Field(default=None, description='手机号')
    parent_name: str = Field(description='家长姓名')
    nickname: Optional[str] = Field(default=None, description='昵称')
    avatar_url: Optional[str] = Field(default=None, description='头像URL')
    wechat_id: Optional[str] = Field(default=None, description='微信号')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系电话')
    address: Optional[str] = Field(default=None, description='家庭住址')
    occupation: Optional[str] = Field(default=None, description='职业')
    education_level: Optional[str] = Field(default=None, description='学历')
    family_income_range: Optional[int] = Field(default=None, description='家庭收入范围')
    family_income_range_name: Optional[str] = Field(default=None, description='家庭收入范围名称')
    payment_preference: Optional[int] = Field(default=None, description='付费偏好')
    payment_preference_name: Optional[str] = Field(default=None, description='付费偏好名称')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime = Field(description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
