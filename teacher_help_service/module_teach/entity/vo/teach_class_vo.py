from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachClassPageQueryModel(BaseModel):
    """
    班级分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    class_name: Optional[str] = Field(default=None, description='班级名称')
    class_mode: Optional[Literal['group', 'one_to_one']] = Field(default=None, description='班型')
    class_type: Optional[str] = Field(default=None, description='班级分类')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    teacher_id: Optional[int] = Field(default=None, description='老师ID')
    enroll_status: Optional[int] = Field(default=None, description='招生状态')
    student_keyword: Optional[str] = Field(default=None, description='学员姓名或手机号')
    status: Optional[int] = Field(default=None, description='启用状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TeachClassBaseModel(BaseModel):
    """
    班级基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    class_no: Optional[str] = Field(default=None, description='班级编号', max_length=50)
    class_name: str = Field(description='班级名称', max_length=100)
    class_mode: Optional[Literal['group', 'one_to_one']] = Field(default='group', description='班型')
    class_type: Optional[str] = Field(default='custom', description='班级分类')
    course_id: int = Field(description='课程ID')
    teacher_id: Optional[int] = Field(default=None, description='主讲老师ID')
    assistant_id: Optional[int] = Field(default=None, description='助教ID')
    classroom: Optional[str] = Field(default=None, description='上课教室', max_length=100)
    max_students: Optional[int] = Field(default=0, description='班级容量')
    min_students: Optional[int] = Field(default=0, description='开课人数')
    allow_over_capacity: Optional[int] = Field(default=1, description='是否允许超员')
    allow_online_enroll: Optional[int] = Field(default=0, description='是否支持在线选班')
    allow_recharge: Optional[int] = Field(default=1, description='是否允许充值购时')
    auto_assign_name: Optional[int] = Field(default=0, description='是否自动点名')
    lesson_hours: Optional[Decimal] = Field(default=Decimal('1'), description='授课课时')
    default_consumption: Optional[Decimal] = Field(default=Decimal('0'), description='默认消耗金额')
    enroll_status: Optional[int] = Field(default=1, description='招生状态')
    start_date: Optional[date] = Field(default=None, description='开课日期')
    end_date: Optional[date] = Field(default=None, description='结课日期')
    status: Optional[int] = Field(default=1, description='启用状态')
    is_historical: Optional[int] = Field(default=0, description='是否过往在读班级')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @Xss(field_name='class_name', message='班级名称不能包含脚本字符')
    @NotBlank(field_name='class_name', message='班级名称不能为空')
    @Size(field_name='class_name', min_length=0, max_length=100, message='班级名称长度不能超过100个字符')
    def get_class_name(self):
        return self.class_name

    def validate_fields(self):
        self.get_class_name()
        if not self.course_id:
            raise ModelValidatorException(message='关联课程不能为空')
        if self.max_students is not None and self.max_students < 0:
            raise ModelValidatorException(message='班级容量不能小于0')
        if self.min_students is not None and self.min_students < 0:
            raise ModelValidatorException(message='开课人数不能小于0')


class AddTeachClassModel(TeachClassBaseModel):
    """
    新增班级模型
    """


class EditTeachClassModel(TeachClassBaseModel):
    """
    编辑班级模型
    """

    id: int = Field(description='班级ID')


class DeleteTeachClassModel(BaseModel):
    """
    删除班级模型
    """

    class_ids: str = Field(description='班级ID，多个用逗号分隔')


class ChangeTeachClassRechargeModel(BaseModel):
    """
    班级充值购时开关模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='班级ID')
    allow_recharge: int = Field(description='是否允许充值购时')


class AddTeachClassStudentModel(BaseModel):
    """
    添加班级学员模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    student_ids: List[int] = Field(default_factory=list, description='学员ID列表')
    course_account_id: Optional[int] = Field(default=None, description='课程账户ID')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    def validate_fields(self):
        if not self.student_ids:
            raise ModelValidatorException(message='请选择要添加的学员')


class RemoveTeachClassStudentModel(BaseModel):
    """
    移出班级学员模型
    """

    student_ids: str = Field(description='学员ID，多个用逗号分隔')


class TeachClassModel(BaseModel):
    """
    班级响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='班级ID')
    class_no: Optional[str] = Field(default=None, description='班级编号')
    class_name: str = Field(description='班级名称')
    class_mode: str = Field(description='班型')
    class_type: str = Field(description='班级分类')
    course_id: int = Field(description='课程ID')
    course_name: str = Field(description='课程名称')
    teacher_id: Optional[int] = Field(default=None, description='主讲老师ID')
    teacher_name: Optional[str] = Field(default=None, description='主讲老师')
    max_students: Optional[int] = Field(default=0, description='班级容量')
    current_students: Optional[int] = Field(default=0, description='当前人数')
    allow_recharge: Optional[int] = Field(default=1, description='是否允许充值购时')
    enroll_status: Optional[int] = Field(default=1, description='招生状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')


class TeachClassAttendanceDetailSubmitModel(BaseModel):
    """
    班级点名明细提交模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    student_id: int = Field(description='学员ID')
    status: int = Field(default=1, description='到课状态(1=到课 2=迟到 3=请假 4=未到)')
    deduct_quantity: int = Field(default=0, description='扣除数量')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class SubmitTeachClassAttendanceModel(BaseModel):
    """
    班级点名提交模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    event_id: Optional[int] = Field(default=None, description='排课事件ID')
    class_date: date = Field(description='上课日期')
    start_time: str = Field(description='开始时间', max_length=10)
    end_time: str = Field(description='结束时间', max_length=10)
    teacher_id: Optional[int] = Field(default=None, description='上课老师ID')
    classroom: Optional[str] = Field(default=None, description='上课教室', max_length=100)
    lesson_hours: Optional[Decimal] = Field(default=Decimal('1'), description='授课课时')
    content: Optional[str] = Field(default=None, description='上课内容', max_length=500)
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)
    details: List[TeachClassAttendanceDetailSubmitModel] = Field(default_factory=list, description='点名明细')

    def validate_fields(self):
        if not self.details:
            raise ModelValidatorException(message='点名学员不能为空')
