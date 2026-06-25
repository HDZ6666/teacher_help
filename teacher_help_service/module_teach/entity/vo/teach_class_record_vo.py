from datetime import date
from typing import Optional

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


@as_query
class ClassRecordAbsenceQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='page number')
    page_size: int = Field(default=10, description='page size')
    student_keyword: Optional[str] = Field(default=None, description='student name or phone')
    class_id: Optional[int] = Field(default=None, description='class id')
    min_absences: Optional[int] = Field(default=None, description='minimum missed count')
    max_absences: Optional[int] = Field(default=None, description='maximum missed count')
