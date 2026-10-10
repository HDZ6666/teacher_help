from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachScheduleEventPageQueryModel(BaseModel):
    """
    排课事件分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    subject_code: Optional[str] = Field(default=None, description='学科字典码')
    classroom: Optional[str] = Field(default=None, description='上课教室')
    status: Optional[Literal['0', '1', '2', '3']] = Field(default=None, description='状态')
    event_date: Optional[date] = Field(default=None, description='上课日期')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')


class AddTeachScheduleEventModel(BaseModel):
    """
    新增排课事件模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    teacher_id: int = Field(description='教师ID')
    class_id: int = Field(description='班级ID')
    course_id: int = Field(description='课程ID')
    subject_code: Optional[str] = Field(default=None, description='学科字典码', max_length=50)
    start_time: datetime = Field(description='开始时间')
    end_time: datetime = Field(description='结束时间')
    student_ids: Optional[List[int]] = Field(default=None, description='学生ID列表')
    classroom: Optional[str] = Field(default=None, description='上课教室', max_length=100)
    lesson_hours: Optional[float] = Field(default=1, description='授课课时')
    content: Optional[str] = Field(default=None, description='上课内容', max_length=500)
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='teacher_id', message='教师ID不能为空')
    def get_teacher_id(self):
        return self.teacher_id

    @NotBlank(field_name='class_id', message='班级ID不能为空')
    def get_class_id(self):
        return self.class_id

    @NotBlank(field_name='course_id', message='课程ID不能为空')
    def get_course_id(self):
        return self.course_id

    @NotBlank(field_name='start_time', message='开始时间不能为空')
    def get_start_time(self):
        return self.start_time

    @NotBlank(field_name='end_time', message='结束时间不能为空')
    def get_end_time(self):
        return self.end_time

    def validate_fields(self):
        self.get_teacher_id()
        self.get_class_id()
        self.get_course_id()
        self.get_start_time()
        self.get_end_time()


class EditTeachScheduleEventModel(BaseModel):
    """
    编辑排课事件模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int = Field(description='事件ID')
    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    subject_code: Optional[str] = Field(default=None, description='学科字典码', max_length=50)
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    status: Optional[Literal['0', '1', '2', '3']] = Field(default=None, description='状态')
    student_ids: Optional[List[int]] = Field(default=None, description='学生ID列表')
    classroom: Optional[str] = Field(default=None, description='上课教室', max_length=100)
    lesson_hours: Optional[float] = Field(default=None, description='授课课时')
    content: Optional[str] = Field(default=None, description='上课内容', max_length=500)
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='id', message='事件ID不能为空')
    def get_id(self):
        return self.id

    def validate_fields(self):
        self.get_id()


class DeleteTeachScheduleEventModel(BaseModel):
    """
    删除排课事件模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    event_ids: str = Field(description='事件ID列表，逗号分隔')

    @NotBlank(field_name='event_ids', message='事件ID不能为空')
    def get_event_ids(self):
        return self.event_ids

    def validate_fields(self):
        self.get_event_ids()


class TeachScheduleEventResponseModel(BaseModel):
    """
    排课事件响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: Optional[int] = Field(default=None, description='事件ID')
    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    teacher_name: Optional[str] = Field(default=None, description='教师姓名')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    class_name: Optional[str] = Field(default=None, description='班级名称')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    schedule_color: Optional[str] = Field(default=None, description='课表颜色')
    subject_code: Optional[str] = Field(default=None, description='学科字典码')
    subject_name: Optional[str] = Field(default=None, description='学科名称')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    event_date: Optional[date] = Field(default=None, description='上课日期')
    classroom: Optional[str] = Field(default=None, description='上课教室')
    lesson_hours: Optional[float] = Field(default=None, description='授课课时')
    content: Optional[str] = Field(default=None, description='上课内容')
    status: Optional[str] = Field(default=None, description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    roster_frozen_at: Optional[datetime] = Field(default=None, description='名单冻结时间')
    cached_planned: Optional[int] = Field(default=None, description='计划人数')
    cached_present: Optional[int] = Field(default=None, description='出勤人数')
    cached_late: Optional[int] = Field(default=None, description='迟到人数')
    cached_excused: Optional[int] = Field(default=None, description='请假人数')
    cached_absent: Optional[int] = Field(default=None, description='缺勤人数')
    cached_rate: Optional[float] = Field(default=None, description='出勤率(%)')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeachScheduleEventDetailModel(BaseModel):
    """
    排课事件详情模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: Optional[int] = Field(default=None, description='事件ID')
    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    teacher_name: Optional[str] = Field(default=None, description='教师姓名')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    class_name: Optional[str] = Field(default=None, description='班级名称')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    schedule_color: Optional[str] = Field(default=None, description='课表颜色')
    subject_code: Optional[str] = Field(default=None, description='学科字典码')
    subject_name: Optional[str] = Field(default=None, description='学科名称')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    event_date: Optional[date] = Field(default=None, description='上课日期')
    classroom: Optional[str] = Field(default=None, description='上课教室')
    lesson_hours: Optional[float] = Field(default=None, description='授课课时')
    content: Optional[str] = Field(default=None, description='上课内容')
    status: Optional[str] = Field(default=None, description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    roster_frozen_at: Optional[datetime] = Field(default=None, description='名单冻结时间')
    cached_planned: Optional[int] = Field(default=None, description='计划人数')
    cached_present: Optional[int] = Field(default=None, description='出勤人数')
    cached_late: Optional[int] = Field(default=None, description='迟到人数')
    cached_excused: Optional[int] = Field(default=None, description='请假人数')
    cached_absent: Optional[int] = Field(default=None, description='缺勤人数')
    cached_rate: Optional[float] = Field(default=None, description='出勤率(%)')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')
    event_type: Optional[str] = Field(default=None, description='课次类型 normal常规 makeup补课')
    students: Optional[List[dict]] = Field(default=None, description='学生名单')


class CalendarQueryModel(BaseModel):
    """
    日历查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    classroom: Optional[str] = Field(default=None, description='上课教室')
    start: datetime = Field(description='开始时间')
    end: datetime = Field(description='结束时间')

    @NotBlank(field_name='start', message='开始时间不能为空')
    def get_start(self):
        return self.start

    @NotBlank(field_name='end', message='结束时间不能为空')
    def get_end(self):
        return self.end

    def validate_fields(self):
        self.get_start()
        self.get_end()
