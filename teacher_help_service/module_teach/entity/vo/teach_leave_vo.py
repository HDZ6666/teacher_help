from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size

from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachLeavePageQueryModel(BaseModel):
    """
    请假申请分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    student_id: Optional[int] = Field(default=None, description='学员ID')
    student_keyword: Optional[str] = Field(default=None, description='学员姓名')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    leave_type: Optional[int] = Field(default=None, description='请假类型')
    leave_status: Optional[int] = Field(default=None, description='请假状态')
    begin_time: Optional[date] = Field(default=None, description='请假开始日期')
    end_time: Optional[date] = Field(default=None, description='请假结束日期')


class TeachLeaveBaseModel(BaseModel):
    """
    请假申请基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    student_id: int = Field(description='学员ID')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    event_id: Optional[int] = Field(default=None, description='关联课次(排课事件)ID')
    leave_type: Optional[int] = Field(default=1, description='请假类型(1=事假 2=病假 3=其他)')
    leave_date: Optional[date] = Field(default=None, description='请假日期')
    leave_reason: Optional[str] = Field(default=None, description='请假事由', max_length=500)
    leave_image: Optional[str] = Field(default=None, description='请假图片(凭证)', max_length=500)
    is_deduct: Optional[int] = Field(default=0, description='是否扣课时(0=否 1=是)')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='leave_reason', message='请假事由不能为空')
    @Size(field_name='leave_reason', min_length=0, max_length=500, message='请假事由长度不能超过500个字符')
    def get_leave_reason(self):
        return self.leave_reason

    def validate_fields(self):
        if not self.student_id:
            raise ModelValidatorException(message='请选择请假学员')
        self.get_leave_reason()
        if not self.event_id and not self.leave_date:
            raise ModelValidatorException(message='请选择请假课次或请假日期')


class AddTeachLeaveModel(TeachLeaveBaseModel):
    """
    提交请假申请模型
    """


class ApproveTeachLeaveModel(BaseModel):
    """
    请假审批模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int = Field(description='请假申请ID')
    leave_status: int = Field(description='审批结果(2=已通过 3=已拒绝)')
    approve_remark: Optional[str] = Field(default=None, description='审批备注', max_length=500)

    def validate_fields(self):
        if self.leave_status not in [2, 3]:
            raise ModelValidatorException(message='审批结果不正确')


class DeleteTeachLeaveModel(BaseModel):
    """
    撤销请假申请模型
    """

    leave_ids: str = Field(description='请假申请ID，多个用逗号分隔')
