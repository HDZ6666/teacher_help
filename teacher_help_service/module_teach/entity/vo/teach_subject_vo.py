from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class SubjectModel(BaseModel):
    """
    科目表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    subject_id: Optional[int] = Field(default=None, description='科目ID')
    subject_code: Optional[str] = Field(default=None, description='科目编码')
    subject_name: Optional[str] = Field(default=None, description='科目名称')
    subject_category: Optional[str] = Field(default=None, description='科目类别')
    subject_sort: Optional[int] = Field(default=None, description='显示顺序')
    status: Optional[str] = Field(default=None, description='状态（0正常 1停用）')
    del_flag: Optional[str] = Field(default=None, description='删除标志（0代表存在 2代表删除）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeacherSubjectModel(BaseModel):
    """
    教师-科目关联表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    teacher_id: Optional[int] = Field(default=None, description='教师ID')
    subject_id: Optional[int] = Field(default=None, description='科目ID')

