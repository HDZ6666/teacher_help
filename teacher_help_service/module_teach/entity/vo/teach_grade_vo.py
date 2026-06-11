from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class GradeModel(BaseModel):
    """
    年级表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    grade_id: Optional[int] = Field(default=None, description='年级ID')
    grade_code: Optional[str] = Field(default=None, description='年级编码')
    grade_name: Optional[str] = Field(default=None, description='年级名称')
    education_level: Optional[str] = Field(default=None, description='教育阶段')
    grade_sort: Optional[int] = Field(default=None, description='显示顺序')
    status: Optional[str] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeacherGradeModel(BaseModel):
    """
    教师-年级关联表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    grade_id: Optional[int] = Field(default=None, description='年级ID')

