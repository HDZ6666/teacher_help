from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachCourseAccountPageQueryModel(BaseModel):
    """
    报读情况（学员课程账户）分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名/家长手机号')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    status: Optional[str] = Field(default=None, description='账户状态 active/stopped/completed/transferred')


class _AccountBatchModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    account_ids: List[int] = Field(min_length=1, max_length=200, description='课程账户ID列表')


class TransferCourseAccountModel(_AccountBatchModel):
    """
    批量转课：转出所选课程账户的全部剩余数量到目标课程
    """

    target_course_id: int = Field(description='转入课程ID')
    target_class_id: Optional[int] = Field(default=None, description='转入班级ID（可选，须与转入课程对应）')
    validity_mode: Literal['keep', 'unified'] = Field(
        default='keep', description='keep=按原课程有效期 unified=统一有效期'
    )
    valid_start_date: Optional[date] = Field(default=None, description='统一有效期开始')
    valid_end_date: Optional[date] = Field(default=None, description='统一有效期结束')
    enroll_date: Optional[date] = Field(default=None, description='经办日期')
    reason: Optional[str] = Field(default=None, max_length=200, description='对内备注')

    @model_validator(mode='after')
    def check_validity(self):
        if self.validity_mode == 'unified':
            if not self.valid_end_date:
                raise ModelValidatorException(message='统一有效期需要填写结束日期')
            if self.valid_start_date and self.valid_start_date > self.valid_end_date:
                raise ModelValidatorException(message='有效期开始日期不能晚于结束日期')
        return self


class ClearCourseAccountModel(_AccountBatchModel):
    """
    批量课时清零
    """

    reason: str = Field(min_length=1, max_length=200, description='清零原因（必填）')


class ChangeCourseValidityModel(_AccountBatchModel):
    """
    批量修改课程有效期
    """

    valid_start_date: Optional[date] = Field(default=None, description='有效期开始（为空则不修改）')
    valid_end_date: date = Field(description='有效期结束')
    reason: Optional[str] = Field(default=None, max_length=200, description='备注')

    @model_validator(mode='after')
    def check_dates(self):
        if self.valid_start_date and self.valid_start_date > self.valid_end_date:
            raise ModelValidatorException(message='有效期开始日期不能晚于结束日期')
        return self


class StopCourseAccountModel(_AccountBatchModel):
    """
    停课
    """

    stop_date: date = Field(description='停课日期')
    planned_resume_date: Optional[date] = Field(default=None, description='计划复课日期（仅记录）')
    reason: str = Field(min_length=1, max_length=30, description='停课备注（必填，限30字）')

    @model_validator(mode='after')
    def check_dates(self):
        if self.planned_resume_date and self.planned_resume_date < self.stop_date:
            raise ModelValidatorException(message='复课日期不能早于停课日期')
        return self


class ResumeCourseAccountModel(_AccountBatchModel):
    """
    复课
    """

    resume_date: Optional[date] = Field(default=None, description='复课日期，默认今天')
    reason: Optional[str] = Field(default=None, max_length=200, description='备注')


class CompleteCourseAccountModel(_AccountBatchModel):
    """
    结课：剩余数量清零、移出对应班级
    """

    reason: Optional[str] = Field(default=None, max_length=200, description='备注')


@as_query
class TeachStudentFollowPageQueryModel(BaseModel):
    """
    学员跟进记录分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名')
    follow_type: Optional[str] = Field(default=None, description='跟进方式')
    begin_time: Optional[date] = Field(default=None, description='跟进开始日期')
    end_time: Optional[date] = Field(default=None, description='跟进结束日期')


class TeachStudentFollowModel(BaseModel):
    """
    新增/修改学员跟进记录
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: Optional[int] = Field(default=None, description='主键ID（修改时必填）')
    student_id: int = Field(description='学员ID')
    follow_type: Literal['phone', 'wechat', 'visit', 'other'] = Field(description='跟进方式')
    follow_stage: Optional[str] = Field(default=None, max_length=50, description='跟进阶段')
    content: str = Field(min_length=1, max_length=2000, description='跟进内容')
    follow_time: Optional[datetime] = Field(default=None, description='跟进时间，默认当前时间')
    next_follow_date: Optional[date] = Field(default=None, description='下次跟进日期')
    follow_user_id: Optional[int] = Field(default=None, description='跟进人(sys_user.user_id)，默认当前登录人')


class ClassBatchIdsModel(BaseModel):
    """
    班级批量结业
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    class_ids: List[int] = Field(min_length=1, max_length=100, description='班级ID列表')
    end_date: Optional[date] = Field(default=None, description='结业日期，默认今天')


class ClassPromoteItemModel(BaseModel):
    """
    批量升班单项：一个原班级升入一个新班级
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source_class_id: int = Field(description='原班级ID')
    class_name: str = Field(min_length=1, max_length=100, description='新班级名称')
    course_id: Optional[int] = Field(default=None, description='新班级关联课程，默认沿用原班级课程')
    teacher_id: Optional[int] = Field(default=None, description='新班级老师，默认沿用原班级老师')
    max_students: Optional[int] = Field(default=None, ge=0, description='班级容量，默认沿用')
    classroom: Optional[str] = Field(default=None, max_length=100, description='上课教室，默认沿用')
    lesson_hours: Optional[float] = Field(default=None, gt=0, description='默认授课课时，默认沿用')
    start_date: Optional[date] = Field(default=None, description='开班日期')
    student_ids: Optional[List[int]] = Field(default=None, description='升班学员，默认原班级全部在读学员')


class ClassPromoteModel(BaseModel):
    """
    批量升班
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: List[ClassPromoteItemModel] = Field(min_length=1, max_length=50, description='升班明细')
    graduate_source: bool = Field(default=False, description='升班后是否将原班级标记为已结课（默认否）')
