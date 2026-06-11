import re
from datetime import datetime
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import Network, NotBlank, Size, Xss
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


class TeacherSubjectModel(BaseModel):
    """
    教师科目关联模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    subject_code: str = Field(description='科目代码')


class TeacherGradeModel(BaseModel):
    """
    教师年级关联模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    grade_code: str = Field(description='年级代码')


@as_query
class TeachTeacherPageQueryModel(BaseModel):
    """
    教师分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    teacher_name: Optional[str] = Field(default=None, description='教师姓名')
    phone: Optional[str] = Field(default=None, description='手机号')
    teaching_subjects: Optional[str] = Field(default=None, description='教学科目')
    status: Optional[Literal['1', '2', '3']] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AddTeachTeacherModel(BaseModel):
    """
    新增教师模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    phone: str = Field(description='手机号', min_length=11, max_length=11)
    password: str = Field(description='密码', min_length=6, max_length=20)
    teacher_name: str = Field(description='教师姓名', max_length=50)
    nickname: Optional[str] = Field(default=None, description='昵称', max_length=50)
    avatar_url: Optional[str] = Field(default=None, description='头像URL', max_length=512)
    id_card: Optional[str] = Field(default=None, description='身份证号', max_length=18)
    subject_codes: Optional[List[str]] = Field(default=[], description='科目代码列表')
    grade_codes: Optional[List[str]] = Field(default=[], description='年级代码列表')
    qualification_cert: Optional[str] = Field(default=None, description='教师资格证号', max_length=255)
    work_experience: Optional[int] = Field(default=0, description='教学经验(年)')
    introduction: Optional[str] = Field(default=None, description='个人简介')
    hourly_rate: Optional[float] = Field(default=0.00, description='默认课时费')
    bank_account: Optional[str] = Field(default=None, description='银行账号', max_length=50)
    bank_name: Optional[str] = Field(default=None, description='开户银行', max_length=100)
    settlement_cycle: Optional[Literal['0', '1']] = Field(default='0', description='结算周期（0周结 1月结）')
    status: Optional[Literal['0', '1', '2']] = Field(default='0', description='状态（0正常 1停用 2已注销）')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @model_validator(mode='after')
    def check_password(self) -> 'AddTeachTeacherModel':
        pattern = r"""^[^<>"'|\\]+$"""
        if self.password is None or re.match(pattern, self.password):
            return self
        else:
            raise ModelValidatorException(message='密码不能包含非法字符：< > " \' \\ |')

    @Xss(field_name='teacher_name', message='教师姓名不能包含脚本字符')
    @NotBlank(field_name='teacher_name', message='教师姓名不能为空')
    @Size(field_name='teacher_name', min_length=0, max_length=50, message='教师姓名长度不能超过50个字符')
    def get_teacher_name(self):
        return self.teacher_name

    @Size(field_name='phone', min_length=11, max_length=11, message='手机号码长度必须为11位')
    def get_phone(self):
        return self.phone

    @Xss(field_name='nickname', message='昵称不能包含脚本字符')
    @Size(field_name='nickname', min_length=0, max_length=50, message='昵称长度不能超过50个字符')
    def get_nickname(self):
        return self.nickname

    @Size(field_name='id_card', min_length=0, max_length=18, message='身份证号长度不能超过18个字符')
    def get_id_card(self):
        return self.id_card

    def validate_fields(self):
        self.get_teacher_name()
        self.get_phone()
        if self.nickname:
            self.get_nickname()
        if self.id_card:
            self.get_id_card()


class EditTeachTeacherModel(BaseModel):
    """
    编辑教师模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='教师ID')
    teacher_name: Optional[str] = Field(default=None, description='教师姓名', max_length=50)
    nickname: Optional[str] = Field(default=None, description='昵称', max_length=50)
    avatar_url: Optional[str] = Field(default=None, description='头像URL', max_length=512)
    id_card: Optional[str] = Field(default=None, description='身份证号', max_length=18)
    subject_codes: Optional[List[str]] = Field(default=[], description='科目代码列表')
    grade_codes: Optional[List[str]] = Field(default=[], description='年级代码列表')
    qualification_cert: Optional[str] = Field(default=None, description='教师资格证号', max_length=255)
    work_experience: Optional[int] = Field(default=None, description='教学经验(年)')
    introduction: Optional[str] = Field(default=None, description='个人简介')
    hourly_rate: Optional[float] = Field(default=None, description='默认课时费')
    bank_account: Optional[str] = Field(default=None, description='银行账号', max_length=50)
    bank_name: Optional[str] = Field(default=None, description='开户银行', max_length=100)
    settlement_cycle: Optional[Literal['0', '1']] = Field(default=None, description='结算周期（0周结 1月结）')
    status: Optional[Literal['0', '1', '2']] = Field(default=None, description='状态（0正常 1停用 2已注销）')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @Xss(field_name='teacher_name', message='教师姓名不能包含脚本字符')
    @Size(field_name='teacher_name', min_length=0, max_length=50, message='教师姓名长度不能超过50个字符')
    def get_teacher_name(self):
        return self.teacher_name

    @Xss(field_name='nickname', message='昵称不能包含脚本字符')
    @Size(field_name='nickname', min_length=0, max_length=50, message='昵称长度不能超过50个字符')
    def get_nickname(self):
        return self.nickname

    @Size(field_name='id_card', min_length=0, max_length=18, message='身份证号长度不能超过18个字符')
    def get_id_card(self):
        return self.id_card

    def validate_fields(self):
        if self.teacher_name:
            self.get_teacher_name()
        if self.nickname:
            self.get_nickname()
        if self.id_card:
            self.get_id_card()


class DeleteTeachTeacherModel(BaseModel):
    """
    删除教师模型
    """

    ids: str = Field(description='教师ID，多个用逗号分隔')


class TeachTeacherResponseModel(BaseModel):
    """
    教师响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='教师ID')
    user_id: int = Field(description='关联基础用户ID')
    phone: Optional[str] = Field(default=None, description='手机号')
    teacher_name: str = Field(description='教师姓名')
    nickname: Optional[str] = Field(default=None, description='昵称')
    avatar_url: Optional[str] = Field(default=None, description='头像URL')
    subjects: Optional[List[str]] = Field(default=None, description='教学科目名称列表')
    grades: Optional[List[str]] = Field(default=None, description='教学年级名称列表')
    qualification_cert: Optional[str] = Field(default=None, description='教师资格证号')
    work_experience: Optional[int] = Field(default=None, description='教学经验(年)')
    hourly_rate: Optional[float] = Field(default=None, description='默认课时费')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeachTeacherDetailModel(BaseModel):
    """
    教师详情模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='教师ID')
    user_id: int = Field(description='关联基础用户ID')
    phone: Optional[str] = Field(default=None, description='手机号')
    teacher_name: str = Field(description='教师姓名')
    nickname: Optional[str] = Field(default=None, description='昵称')
    avatar_url: Optional[str] = Field(default=None, description='头像URL')
    id_card: Optional[str] = Field(default=None, description='身份证号')
    subject_codes: Optional[List[str]] = Field(default=[], description='科目代码列表')
    grade_codes: Optional[List[str]] = Field(default=[], description='年级代码列表')
    subjects: Optional[List[str]] = Field(default=None, description='教学科目名称列表')
    grades: Optional[List[str]] = Field(default=None, description='教学年级名称列表')
    qualification_cert: Optional[str] = Field(default=None, description='教师资格证号')
    work_experience: Optional[int] = Field(default=None, description='教学经验(年)')
    introduction: Optional[str] = Field(default=None, description='个人简介')
    hourly_rate: Optional[float] = Field(default=None, description='默认课时费')
    bank_account: Optional[str] = Field(default=None, description='银行账号')
    bank_name: Optional[str] = Field(default=None, description='开户银行')
    settlement_cycle: Optional[int] = Field(default=None, description='结算周期')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime = Field(description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
