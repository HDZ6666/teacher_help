from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from exceptions.exception import ModelValidatorException


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RescheduleLessonModel(_CamelModel):
    """
    课次调课：修改上课时间/老师/教室（仅未点名、未取消的课次）
    """

    event_id: int = Field(description='课次ID')
    start_time: datetime = Field(description='新开始时间')
    end_time: datetime = Field(description='新结束时间')
    teacher_id: Optional[int] = Field(default=None, description='新上课老师ID，不传则不变')
    classroom: Optional[str] = Field(default=None, max_length=100, description='新上课教室，不传则不变')
    reason: Optional[str] = Field(default=None, max_length=200, description='调课原因')

    @model_validator(mode='after')
    def check_time(self):
        if self.end_time <= self.start_time:
            raise ModelValidatorException(message='结束时间必须晚于开始时间')
        if self.start_time.date() != self.end_time.date():
            raise ModelValidatorException(message='开始和结束时间必须在同一天')
        return self


class AddTempStudentModel(_CamelModel):
    """
    添加临时学员（只加入单个课次）。课次已点名时须同时提交到课状态与扣课数量，直接补点名扣课
    """

    event_id: int = Field(description='课次ID')
    student_id: int = Field(description='学员ID')
    course_account_id: Optional[int] = Field(default=None, description='扣课课程账户ID，不传则取该课程最新有效账户')
    status: Optional[Literal[1, 2, 3, 4]] = Field(
        default=None, description='到课状态(已点名课次必填)'
    )
    deduct_quantity: int = Field(default=0, ge=0, le=99, description='扣课数量(已点名课次)')
    remark: Optional[str] = Field(default=None, max_length=200, description='备注')


class WeeklyScheduleModel(_CamelModel):
    """
    班级按周重复排课
    """

    class_id: int = Field(description='班级ID')
    start_date: date = Field(description='开始日期')
    end_date: date = Field(description='结束日期')
    weekdays: List[int] = Field(min_length=1, max_length=7, description='星期几(1=周一 ... 7=周日)')
    start_clock: str = Field(pattern=r'^\d{2}:\d{2}$', description='上课开始时间 HH:MM')
    end_clock: str = Field(pattern=r'^\d{2}:\d{2}$', description='上课结束时间 HH:MM')
    teacher_id: Optional[int] = Field(default=None, description='上课老师ID，不传取班级主讲老师')
    classroom: Optional[str] = Field(default=None, max_length=100, description='上课教室，不传取班级教室')
    lesson_hours: Optional[Decimal] = Field(default=None, description='授课课时，不传取班级默认')
    content: Optional[str] = Field(default=None, max_length=500, description='上课内容')

    @model_validator(mode='after')
    def check_range(self):
        if self.end_date < self.start_date:
            raise ModelValidatorException(message='结束日期不能早于开始日期')
        if (self.end_date - self.start_date).days > 366:
            raise ModelValidatorException(message='按周排课的日期范围不能超过一年')
        if any(day < 1 or day > 7 for day in self.weekdays):
            raise ModelValidatorException(message='星期取值为1~7')
        if self.end_clock <= self.start_clock:
            raise ModelValidatorException(message='结束时间必须晚于开始时间')
        return self


class EditAttendanceDetailModel(_CamelModel):
    """
    修改单个学员点名（同一课次内改到课状态/扣课数量）
    """

    detail_id: int = Field(description='点名明细ID')
    status: Literal[1, 2, 3, 4] = Field(description='到课状态 1到课 2迟到 3请假 4未到')
    deduct_quantity: int = Field(default=0, ge=0, le=99, description='扣课数量')
    remark: Optional[str] = Field(default=None, max_length=500, description='备注')
    reason: str = Field(min_length=1, max_length=200, description='修改原因')


class EditAttendanceRecordModel(_CamelModel):
    """
    编辑课次（已点名的上课记录）：只改记录信息，不改学员扣课
    """

    id: int = Field(description='点名记录ID')
    class_date: date = Field(description='上课日期')
    start_time: str = Field(pattern=r'^\d{2}:\d{2}$', description='开始时间 HH:MM')
    end_time: str = Field(pattern=r'^\d{2}:\d{2}$', description='结束时间 HH:MM')
    teacher_id: Optional[int] = Field(default=None, description='上课老师ID')
    classroom: Optional[str] = Field(default=None, max_length=100, description='上课教室')
    lesson_hours: Decimal = Field(gt=0, le=99, description='授课课时')
    content: Optional[str] = Field(default=None, max_length=500, description='上课内容')
    remark: Optional[str] = Field(default=None, max_length=500, description='备注')

    @model_validator(mode='after')
    def check_time(self):
        if self.end_time <= self.start_time:
            raise ModelValidatorException(message='结束时间必须晚于开始时间')
        return self


class MakeupClassModel(_CamelModel):
    """
    开补课班：从缺课记录（请假/未到）生成一节补课课次
    """

    detail_ids: List[int] = Field(min_length=1, max_length=100, description='缺课记录（点名明细）ID列表')
    start_time: datetime = Field(description='补课开始时间')
    end_time: datetime = Field(description='补课结束时间')
    teacher_id: int = Field(description='上课老师ID')
    classroom: Optional[str] = Field(default=None, max_length=100, description='上课教室')
    lesson_hours: Optional[Decimal] = Field(default=None, description='授课课时')
    content: Optional[str] = Field(default=None, max_length=500, description='上课内容')

    @model_validator(mode='after')
    def check_time(self):
        if self.end_time <= self.start_time:
            raise ModelValidatorException(message='结束时间必须晚于开始时间')
        if self.start_time.date() != self.end_time.date():
            raise ModelValidatorException(message='开始和结束时间必须在同一天')
        return self
