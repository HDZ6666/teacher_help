from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachCommentPageQueryModel(BaseModel):
    """
    课后点评分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    attendance_id: Optional[int] = Field(default=None, description='点名记录ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    teacher_id: Optional[int] = Field(default=None, description='老师ID')
    comment_type: Optional[str] = Field(default=None, description='点评类型(single/unified/batch)')
    status: Optional[int] = Field(default=None, description='状态(1=已发布 2=已撤销)')
    begin_time: Optional[date] = Field(default=None, description='上课日期开始')
    end_time: Optional[date] = Field(default=None, description='上课日期结束')


class AddTeachCommentModel(BaseModel):
    """
    新增课后点评模型(单个)
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    attendance_id: Optional[int] = Field(default=None, description='点名记录ID')
    attendance_detail_id: Optional[int] = Field(default=None, description='点名明细ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    student_id: int = Field(description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名快照')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称快照')
    teacher_id: Optional[int] = Field(default=None, description='老师ID')
    teacher_name: Optional[str] = Field(default=None, description='老师姓名快照')
    class_date: Optional[date] = Field(default=None, description='上课日期')
    performance_score: Optional[int] = Field(default=None, description='课堂表现评分(1-5)')
    homework_score: Optional[int] = Field(default=None, description='作业评分(1-5)')
    comment_content: Optional[str] = Field(default=None, description='点评内容')
    strengths: Optional[str] = Field(default=None, description='优点表现', max_length=500)
    weaknesses: Optional[str] = Field(default=None, description='不足之处', max_length=500)
    suggestions: Optional[str] = Field(default=None, description='改进建议', max_length=500)
    comment_type: Optional[str] = Field(default='single', description='点评类型(single/unified/batch)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class BatchTeachCommentModel(BaseModel):
    """
    批量/统一点评模型(一组学员用同一内容)
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    attendance_id: Optional[int] = Field(default=None, description='点名记录ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    student_ids: List[int] = Field(default_factory=list, description='学员ID列表')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称快照')
    teacher_id: Optional[int] = Field(default=None, description='老师ID')
    teacher_name: Optional[str] = Field(default=None, description='老师姓名快照')
    class_date: Optional[date] = Field(default=None, description='上课日期')
    performance_score: Optional[int] = Field(default=None, description='课堂表现评分(1-5)')
    homework_score: Optional[int] = Field(default=None, description='作业评分(1-5)')
    comment_content: Optional[str] = Field(default=None, description='点评内容')
    strengths: Optional[str] = Field(default=None, description='优点表现', max_length=500)
    weaknesses: Optional[str] = Field(default=None, description='不足之处', max_length=500)
    suggestions: Optional[str] = Field(default=None, description='改进建议', max_length=500)
    comment_type: Optional[str] = Field(default='unified', description='点评类型(unified/batch)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class EditTeachCommentModel(BaseModel):
    """
    编辑课后点评模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int = Field(description='点评ID')
    performance_score: Optional[int] = Field(default=None, description='课堂表现评分(1-5)')
    homework_score: Optional[int] = Field(default=None, description='作业评分(1-5)')
    comment_content: Optional[str] = Field(default=None, description='点评内容')
    strengths: Optional[str] = Field(default=None, description='优点表现', max_length=500)
    weaknesses: Optional[str] = Field(default=None, description='不足之处', max_length=500)
    suggestions: Optional[str] = Field(default=None, description='改进建议', max_length=500)
    status: Optional[int] = Field(default=None, description='状态(1=已发布 2=已撤销)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)


class DeleteTeachCommentModel(BaseModel):
    """
    撤销/删除课后点评模型
    """

    ids: str = Field(description='点评ID，多个用逗号分隔')


class TeachCommentResponseModel(BaseModel):
    """
    课后点评响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int = Field(description='点评ID')
    attendance_id: Optional[int] = Field(default=None, description='点名记录ID')
    attendance_detail_id: Optional[int] = Field(default=None, description='点名明细ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    student_id: int = Field(description='学员ID')
    student_name: Optional[str] = Field(default=None, description='学员姓名')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    teacher_id: Optional[int] = Field(default=None, description='老师ID')
    teacher_name: Optional[str] = Field(default=None, description='老师姓名')
    class_date: Optional[date] = Field(default=None, description='上课日期')
    performance_score: Optional[int] = Field(default=None, description='课堂表现评分')
    homework_score: Optional[int] = Field(default=None, description='作业评分')
    comment_content: Optional[str] = Field(default=None, description='点评内容')
    strengths: Optional[str] = Field(default=None, description='优点表现')
    weaknesses: Optional[str] = Field(default=None, description='不足之处')
    suggestions: Optional[str] = Field(default=None, description='改进建议')
    comment_type: Optional[str] = Field(default=None, description='点评类型')
    status: Optional[int] = Field(default=None, description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
