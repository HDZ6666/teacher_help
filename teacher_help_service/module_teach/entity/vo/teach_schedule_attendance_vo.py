from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachScheduleAttendancePageQueryModel(BaseModel):
    """
    考勤分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    event_id: Optional[int] = Field(default=None, description='事件ID')
    student_id: Optional[int] = Field(default=None, description='学生ID')
    status: Optional[Literal[0, 1, 2, 3, 4]] = Field(default=None, description='考勤状态')


class CheckInModel(BaseModel):
    """
    签到模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    event_id: int = Field(description='事件ID')
    student_id: int = Field(description='学生ID')
    check_in_method: Literal['Q', 'M'] = Field(default='Q', description='签到方式')
    notes: Optional[str] = Field(default=None, description='备注', max_length=255)

    @NotBlank(field_name='event_id', message='事件ID不能为空')
    def get_event_id(self):
        return self.event_id

    @NotBlank(field_name='student_id', message='学生ID不能为空')
    def get_student_id(self):
        return self.student_id

    def validate_fields(self):
        self.get_event_id()
        self.get_student_id()


class ManualAttendanceModel(BaseModel):
    """
    手动补录考勤模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    event_id: int = Field(description='事件ID')
    student_id: int = Field(description='学生ID')
    status: Literal[0, 1, 2, 3, 4] = Field(description='考勤状态')
    notes: Optional[str] = Field(default=None, description='备注', max_length=255)

    @NotBlank(field_name='event_id', message='事件ID不能为空')
    def get_event_id(self):
        return self.event_id

    @NotBlank(field_name='student_id', message='学生ID不能为空')
    def get_student_id(self):
        return self.student_id

    @NotBlank(field_name='status', message='考勤状态不能为空')
    def get_status(self):
        return self.status

    def validate_fields(self):
        self.get_event_id()
        self.get_student_id()
        self.get_status()


class TeachScheduleAttendanceResponseModel(BaseModel):
    """
    考勤响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='考勤ID')
    event_id: Optional[int] = Field(default=None, description='事件ID')
    student_id: Optional[int] = Field(default=None, description='学生ID')
    student_name: Optional[str] = Field(default=None, description='学生姓名')
    status: Optional[int] = Field(default=None, description='考勤状态')
    status_name: Optional[str] = Field(default=None, description='考勤状态名称')
    is_countable: Optional[int] = Field(default=None, description='是否计入出勤率')
    check_in_time: Optional[datetime] = Field(default=None, description='签到时间')
    check_in_method: Optional[str] = Field(default=None, description='签到方式')
    operator_id: Optional[int] = Field(default=None, description='操作人ID')
    notes: Optional[str] = Field(default=None, description='备注')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')


class AttendanceStatModel(BaseModel):
    """
    考勤统计模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    event_id: Optional[int] = Field(default=None, description='事件ID')
    total: Optional[int] = Field(default=0, description='总人数')
    planned: Optional[int] = Field(default=0, description='计划人数（计入分母）')
    present: Optional[int] = Field(default=0, description='出勤人数')
    late: Optional[int] = Field(default=0, description='迟到人数')
    excused: Optional[int] = Field(default=0, description='请假人数')
    absent: Optional[int] = Field(default=0, description='缺勤人数')
    not_arrived: Optional[int] = Field(default=0, description='未到人数')
    attendance_rate: Optional[float] = Field(default=0.0, description='出勤率(%)')

