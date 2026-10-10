from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from module_admin.annotation.pydantic_annotation import as_query


class ClassRecordQueryBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='page number')
    page_size: int = Field(default=10, description='page size')
    class_id: Optional[int] = Field(default=None, description='class id')
    course_id: Optional[int] = Field(default=None, description='course id')
    teacher_id: Optional[int] = Field(default=None, description='teacher id')
    begin_time: Optional[date] = Field(default=None, description='begin class date')
    end_time: Optional[date] = Field(default=None, description='end class date')


@as_query
class ClassRecordAttendanceQueryModel(ClassRecordQueryBaseModel):
    status: Optional[int] = Field(default=None, description='attendance record status')


@as_query
class ClassRecordStudentAttendanceQueryModel(ClassRecordQueryBaseModel):
    status: Optional[int] = Field(default=None, description='student attendance status')


@as_query
class ClassRecordOvertimeQueryModel(ClassRecordQueryBaseModel):
    pass


@as_query
class ClassRecordMakeupQueryModel(ClassRecordQueryBaseModel):
    student_keyword: Optional[str] = Field(default=None, description='student name or phone')
    makeup_flag: Optional[int] = Field(default=None, description='makeup flag 0=not made up 1=made up')


@as_query
class ClassRecordAbsenceQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='page number')
    page_size: int = Field(default=10, description='page size')
    student_keyword: Optional[str] = Field(default=None, description='student name or phone')
    class_id: Optional[int] = Field(default=None, description='class id')
    min_absences: Optional[int] = Field(default=None, description='minimum missed count')
    max_absences: Optional[int] = Field(default=None, description='maximum missed count')


class RevokeClassAttendanceModel(BaseModel):
    """
    撤销点名模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int = Field(description='点名记录ID')
    reason: Optional[str] = Field(default=None, description='撤销原因', max_length=200)


class MarkMakeupModel(BaseModel):
    """
    缺课标记已补模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    ids: List[int] = Field(min_length=1, max_length=500, description='点名明细ID列表')
    remark: Optional[str] = Field(default=None, max_length=200, description='补课说明')
