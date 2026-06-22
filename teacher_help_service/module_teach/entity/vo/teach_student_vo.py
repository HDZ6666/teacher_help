from datetime import datetime, date
from decimal import Decimal
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


class TeachStudentEnrollItemModel(BaseModel):
    """
    学员报名/续费项目模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    item_type: Literal['course', 'item', 'fee'] = Field(description='项目类型')
    item_id: int = Field(description='项目ID')
    item_name: str = Field(description='项目名称')
    spec_id: Optional[int] = Field(default=None, description='规格或定价ID')
    spec_name: Optional[str] = Field(default=None, description='规格或定价名称')
    charge_type: Optional[str] = Field(default=None, description='收费方式')
    unit: Optional[str] = Field(default=None, description='单位')
    quantity: int = Field(default=1, description='购买数量')
    gift_quantity: int = Field(default=0, description='赠送数量')
    leave_exempt_count: int = Field(default=0, description='请假免扣次数')
    unit_price: Decimal = Field(default=Decimal('0'), description='单价')
    total_price: Optional[Decimal] = Field(default=None, description='总价')
    discount_type: Optional[Literal['reduce', 'discount']] = Field(default='reduce', description='优惠类型')
    discount_value: Decimal = Field(default=Decimal('0'), description='优惠值')
    subtotal_price: Optional[Decimal] = Field(default=None, description='小计')
    start_date: Optional[date] = Field(default=None, description='课程开始日期')
    end_date: Optional[date] = Field(default=None, description='课程结束日期')
    validity_type: Optional[str] = Field(default=None, description='课程有效期类型')
    class_id: Optional[int] = Field(default=None, description='班级ID')
    class_name: Optional[str] = Field(default=None, description='班级名称')
    package_id: Optional[int] = Field(default=None, description='套餐ID')
    package_name: Optional[str] = Field(default=None, description='套餐名称')
    remark: Optional[str] = Field(default=None, description='明细备注')
    sort: Optional[int] = Field(default=0, description='排序')

    def validate_fields(self):
        if not self.item_name:
            raise ModelValidatorException(message='报名项目名称不能为空')
        if self.quantity <= 0:
            raise ModelValidatorException(message='购买数量必须大于0')
        if self.gift_quantity < 0:
            raise ModelValidatorException(message='赠送数量不能小于0')
        if self.unit_price < 0:
            raise ModelValidatorException(message='项目单价不能小于0')


class TeachStudentEnrollModel(BaseModel):
    """
    学员报名/续费提交模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    student_id: int = Field(description='学员ID')
    order_type: Optional[Literal['enroll', 'renew']] = Field(default='enroll', description='订单类型')
    enroll_date: Optional[date] = Field(default=None, description='经办日期')
    performance_owner: Optional[str] = Field(default=None, description='业绩归属人')
    performance_type: Optional[str] = Field(default=None, description='业绩类型')
    performance_amount: Optional[Decimal] = Field(default=Decimal('0'), description='业绩金额')
    remark: Optional[str] = Field(default=None, description='备注')
    items: List[TeachStudentEnrollItemModel] = Field(default_factory=list, description='报名项目')

    def validate_fields(self):
        if not self.student_id:
            raise ModelValidatorException(message='学员不能为空')
        if not self.items:
            raise ModelValidatorException(message='请至少选择一个报名项目')
        for item in self.items:
            item.validate_fields()


class TeachStudentCourseAccountModel(BaseModel):
    """
    学员报读课程响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='课程账户ID')
    student_id: int = Field(description='学员ID')
    course_id: int = Field(description='课程ID')
    course_name: str = Field(description='课程名称')
    order_id: int = Field(description='订单ID')
    order_no: Optional[str] = Field(default=None, description='订单号')
    charge_type: Optional[str] = Field(default=None, description='收费方式')
    unit: Optional[str] = Field(default=None, description='单位')
    purchased_quantity: int = Field(description='购买数量')
    gift_quantity: int = Field(description='赠送数量')
    consumed_quantity: int = Field(description='已消耗数量')
    remaining_quantity: int = Field(description='剩余数量')
    leave_exempt_count: Optional[int] = Field(default=0, description='请假免扣次数')
    valid_start_date: Optional[date] = Field(default=None, description='有效期开始日期')
    valid_end_date: Optional[date] = Field(default=None, description='有效期结束日期')
    class_name: Optional[str] = Field(default=None, description='班级名称')
    status: str = Field(description='状态')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')


class TeachStudentOrderItemModel(BaseModel):
    """
    学员订单明细响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='明细ID')
    order_id: int = Field(description='订单ID')
    item_type: str = Field(description='项目类型')
    item_type_name: Optional[str] = Field(default=None, description='项目类型名称')
    item_id: int = Field(description='项目ID')
    item_name: str = Field(description='项目名称')
    spec_name: Optional[str] = Field(default=None, description='规格名称')
    unit: Optional[str] = Field(default=None, description='单位')
    quantity: int = Field(description='购买数量')
    gift_quantity: Optional[int] = Field(default=0, description='赠送数量')
    unit_price: Decimal = Field(description='单价')
    subtotal_price: Decimal = Field(description='小计')
    package_name: Optional[str] = Field(default=None, description='套餐名称')


class TeachStudentOrderModel(BaseModel):
    """
    学员订单响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: int = Field(description='订单ID')
    order_no: str = Field(description='订单号')
    student_id: int = Field(description='学员ID')
    order_type: str = Field(description='订单类型')
    order_type_name: Optional[str] = Field(default=None, description='订单类型名称')
    order_source: Optional[str] = Field(default=None, description='订单来源')
    enroll_date: Optional[date] = Field(default=None, description='经办日期')
    item_count: int = Field(description='项目数量')
    total_amount: Decimal = Field(description='总金额')
    discount_amount: Decimal = Field(description='优惠金额')
    receivable_amount: Decimal = Field(description='应收金额')
    paid_amount: Decimal = Field(description='实收金额')
    status: str = Field(description='订单状态')
    status_name: Optional[str] = Field(default=None, description='订单状态名称')
    performance_owner: Optional[str] = Field(default=None, description='业绩归属人')
    remark: Optional[str] = Field(default=None, description='备注')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    items: List[TeachStudentOrderItemModel] = Field(default_factory=list, description='订单明细')
