from datetime import datetime, date
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import Network, NotBlank, Size, Xss
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachStudentPageQueryModel(BaseModel):
    """
    学生分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    student_name: Optional[str] = Field(default=None, description='学生姓名')
    parent_name: Optional[str] = Field(default=None, description='家长姓名')
    school_name: Optional[str] = Field(default=None, description='就读学校')
    grade: Optional[str] = Field(default=None, description='年级')
    gender: Optional[Literal['0', '1', '2']] = Field(default=None, description='性别')
    status: Optional[Literal['1', '2', '3', '4']] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AddTeachStudentModel(BaseModel):
    """
    新增学生模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    parent_id: int = Field(description='关联家长ID')
    student_name: str = Field(description='学生姓名', max_length=50)
    gender: Optional[int] = Field(default=0, description='性别: 0-未知, 1-男, 2-女')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    school_name: Optional[str] = Field(default=None, description='就读学校', max_length=100)
    grade: Optional[str] = Field(default=None, description='年级', max_length=20)
    class_name: Optional[str] = Field(default=None, description='班级', max_length=50)
    student_id_in_school: Optional[str] = Field(default=None, description='学号', max_length=50)
    learning_style: Optional[int] = Field(default=None, description='学习风格: 1-视觉型, 2-听觉型, 3-动觉型')
    personality_traits: Optional[List[str]] = Field(default=None, description='性格特点标签')
    learning_difficulties: Optional[str] = Field(default=None, description='学习困难点')
    interests_hobbies: Optional[List[str]] = Field(default=None, description='兴趣爱好')
    medical_notes: Optional[str] = Field(default=None, description='医疗备注(过敏史等)')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人电话', max_length=20)
    status: Optional[Literal['1', '2', '3', '4']] = Field(default='1', description='状态: 1-在读, 2-休学, 3-转学, 4-毕业')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='student_name', message='学生姓名不能为空')
    @Size(field_name='student_name', min_length=0, max_length=50, message='学生姓名长度不能超过50个字符')
    @Xss(field_name='student_name', message='学生姓名不能包含脚本字符')
    def get_student_name(self):
        return self.student_name

    @NotBlank(field_name='parent_id', message='家长ID不能为空')
    def get_parent_id(self):
        return self.parent_id

    def validate_fields(self):
        self.get_student_name()
        self.get_parent_id()


class EditTeachStudentModel(BaseModel):
    """
    编辑学生模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='学生ID')
    student_name: Optional[str] = Field(default=None, description='学生姓名', max_length=50)
    gender: Optional[Literal['0', '1', '2']] = Field(default=None, description='性别: 0-未知, 1-男, 2-女')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    school_name: Optional[str] = Field(default=None, description='就读学校', max_length=100)
    grade: Optional[str] = Field(default=None, description='年级', max_length=20)
    class_name: Optional[str] = Field(default=None, description='班级', max_length=50)
    student_id_in_school: Optional[str] = Field(default=None, description='学号', max_length=50)
    learning_style: Optional[int] = Field(default=None, description='学习风格: 1-视觉型, 2-听觉型, 3-动觉型')
    personality_traits: Optional[List[str]] = Field(default=None, description='性格特点标签')
    learning_difficulties: Optional[str] = Field(default=None, description='学习困难点')
    interests_hobbies: Optional[List[str]] = Field(default=None, description='兴趣爱好')
    medical_notes: Optional[str] = Field(default=None, description='医疗备注(过敏史等)')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人电话', max_length=20)
    status: Optional[Literal['1', '2', '3', '4']] = Field(default=None, description='状态: 1-在读, 2-休学, 3-转学, 4-毕业')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)

    @NotBlank(field_name='student_name', message='学生姓名不能为空')
    @Size(field_name='student_name', min_length=0, max_length=50, message='学生姓名长度不能超过50个字符')
    @Xss(field_name='student_name', message='学生姓名不能包含脚本字符')
    def get_student_name(self):
        return self.student_name

    def validate_fields(self):
        self.get_student_name()


class DeleteTeachStudentModel(BaseModel):
    """
    删除学生模型
    """

    ids: str = Field(description='学生ID，多个用逗号分隔')


class TeachStudentResponseModel(BaseModel):
    """
    学生响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='学生ID')
    parent_id: int = Field(description='关联家长ID')
    parent_name: Optional[str] = Field(default=None, description='家长姓名')
    student_name: str = Field(description='学生姓名')
    gender: Optional[int] = Field(default=None, description='性别')
    gender_name: Optional[str] = Field(default=None, description='性别名称')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    age: Optional[int] = Field(default=None, description='年龄')
    school_name: Optional[str] = Field(default=None, description='就读学校')
    grade: Optional[str] = Field(default=None, description='年级')
    class_name: Optional[str] = Field(default=None, description='班级')
    learning_style: Optional[int] = Field(default=None, description='学习风格')
    learning_style_name: Optional[str] = Field(default=None, description='学习风格名称')
    personality_traits: Optional[List[str]] = Field(default=None, description='性格特点标签')
    interests_hobbies: Optional[List[str]] = Field(default=None, description='兴趣爱好')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TeachStudentDetailModel(BaseModel):
    """
    学生详情模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='学生ID')
    parent_id: int = Field(description='关联家长ID')
    parent_name: Optional[str] = Field(default=None, description='家长姓名')
    parent_phone: Optional[str] = Field(default=None, description='家长手机号')
    student_name: str = Field(description='学生姓名')
    gender: Optional[int] = Field(default=None, description='性别')
    gender_name: Optional[str] = Field(default=None, description='性别名称')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    age: Optional[int] = Field(default=None, description='年龄')
    school_name: Optional[str] = Field(default=None, description='就读学校')
    grade: Optional[str] = Field(default=None, description='年级')
    class_name: Optional[str] = Field(default=None, description='班级')
    student_id_in_school: Optional[str] = Field(default=None, description='学号')
    learning_style: Optional[int] = Field(default=None, description='学习风格')
    learning_style_name: Optional[str] = Field(default=None, description='学习风格名称')
    personality_traits: Optional[List[str]] = Field(default=None, description='性格特点标签')
    learning_difficulties: Optional[str] = Field(default=None, description='学习困难点')
    interests_hobbies: Optional[List[str]] = Field(default=None, description='兴趣爱好')
    medical_notes: Optional[str] = Field(default=None, description='医疗备注')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人电话')
    status: int = Field(description='状态')
    status_name: Optional[str] = Field(default=None, description='状态名称')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime = Field(description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')
