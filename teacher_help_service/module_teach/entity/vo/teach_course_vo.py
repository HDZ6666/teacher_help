from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size, Xss
from module_admin.annotation.pydantic_annotation import as_query


@as_query
class TeachCoursePageQueryModel(BaseModel):
    """
    课程分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    course_type: Optional[str] = Field(default=None, description='课程类型')
    status: Optional[int] = Field(default=None, description='启用状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TeachCoursePriceModel(BaseModel):
    """
    课程定价标准模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='定价ID')
    course_id: Optional[int] = Field(default=None, description='课程ID')
    charge_type: Optional[str] = Field(default=None, description='收费方式')
    price_name: Optional[str] = Field(default='单价', description='定价名称')
    quantity: Optional[int] = Field(default=1, description='购买数量')
    total_price: Optional[Decimal] = Field(default=0, description='总价')
    unit_price: Optional[Decimal] = Field(default=None, description='单价')
    deduct_rule: Optional[str] = Field(default=None, description='扣课时规则')
    absence_rule: Optional[str] = Field(default=None, description='未到扣课时规则')
    sort: Optional[int] = Field(default=0, description='排序')
    status: Optional[int] = Field(default=1, description='状态')


class TeachCourseModel(BaseModel):
    """
    课程基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='课程ID')
    course_no: Optional[str] = Field(default=None, description='课程编号')
    course_name: Optional[str] = Field(default=None, description='课程名称')
    course_type: Optional[str] = Field(default='one_to_many', description='课程类型')
    schedule_color: Optional[str] = Field(default='#409EFF', description='课表颜色')
    grade: Optional[str] = Field(default=None, description='年级')
    grade_label: Optional[str] = Field(default=None, description='年级名称')
    subject: Optional[str] = Field(default=None, description='科目')
    subject_label: Optional[str] = Field(default=None, description='科目名称')
    semester: Optional[str] = Field(default=None, description='学期')
    semester_label: Optional[str] = Field(default=None, description='学期名称')
    student_count: Optional[int] = Field(default=0, description='在读学员数')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    del_flag: Optional[int] = Field(default=0, description='删除标志')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AddTeachCourseModel(BaseModel):
    """
    新增课程模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    course_no: Optional[str] = Field(default=None, description='课程编号', max_length=50)
    course_name: str = Field(description='课程名称', max_length=100)
    course_type: Optional[str] = Field(default='one_to_many', description='课程类型')
    schedule_color: Optional[str] = Field(default='#409EFF', description='课表颜色')
    grade: Optional[str] = Field(default=None, description='年级', max_length=50)
    grade_label: Optional[str] = Field(default=None, description='年级名称', max_length=50)
    subject: Optional[str] = Field(default=None, description='科目', max_length=50)
    subject_label: Optional[str] = Field(default=None, description='科目名称', max_length=50)
    semester: Optional[str] = Field(default=None, description='学期', max_length=50)
    semester_label: Optional[str] = Field(default=None, description='学期名称', max_length=50)
    student_count: Optional[int] = Field(default=0, description='在读学员数')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)
    prices: Optional[List[TeachCoursePriceModel]] = Field(default_factory=list, description='定价标准')
    class_prices: Optional[List[TeachCoursePriceModel]] = Field(default_factory=list, description='按课时定价')
    month_prices: Optional[List[TeachCoursePriceModel]] = Field(default_factory=list, description='按月定价')
    day_prices: Optional[List[TeachCoursePriceModel]] = Field(default_factory=list, description='按天定价')
    charge_by_class: Optional[bool] = Field(default=False, description='是否按课时收费')
    charge_by_month: Optional[bool] = Field(default=False, description='是否按月收费')
    charge_by_day: Optional[bool] = Field(default=False, description='是否按天收费')
    class_deduct_rule: Optional[str] = Field(default='normal', description='扣课时规则')
    class_absence_rule: Optional[str] = Field(default='deduct', description='未到扣课时规则')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')

    @Xss(field_name='course_name', message='课程名称不能包含脚本字符')
    @NotBlank(field_name='course_name', message='课程名称不能为空')
    @Size(field_name='course_name', min_length=0, max_length=100, message='课程名称长度不能超过100个字符')
    def get_course_name(self):
        return self.course_name

    def validate_fields(self):
        self.get_course_name()


class EditTeachCourseModel(AddTeachCourseModel):
    """
    编辑课程模型
    """

    id: int = Field(description='课程ID')


class BatchAddTeachCourseModel(BaseModel):
    """
    批量新增课程模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    courses: List[AddTeachCourseModel] = Field(default_factory=list, description='课程列表')

    def validate_fields(self):
        if not self.courses:
            raise ValueError('请至少添加一门课程')
        for course in self.courses:
            course.validate_fields()


class ChangeTeachCourseStatusModel(BaseModel):
    """
    课程启停模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='课程ID')
    status: int = Field(description='启用状态')


class DeleteTeachCourseModel(BaseModel):
    """
    删除课程模型
    """

    course_ids: str = Field(description='课程ID，多个用逗号分隔')


class TeachCourseDetailModel(TeachCourseModel):
    """
    课程详情模型
    """

    prices: List[TeachCoursePriceModel] = Field(default_factory=list, description='定价标准')
    class_prices: List[TeachCoursePriceModel] = Field(default_factory=list, description='按课时定价')
    month_prices: List[TeachCoursePriceModel] = Field(default_factory=list, description='按月定价')
    day_prices: List[TeachCoursePriceModel] = Field(default_factory=list, description='按天定价')


@as_query
class TeachCoursePackagePageQueryModel(BaseModel):
    """
    套餐分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    page_num: int = Field(default=1, description='页码')
    page_size: int = Field(default=10, description='每页数量')
    package_name: Optional[str] = Field(default=None, description='套餐名称')
    status: Optional[int] = Field(default=None, description='启用状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TeachPackageItemModel(BaseModel):
    """
    套餐明细模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='明细ID')
    package_id: Optional[int] = Field(default=None, description='套餐ID')
    item_type: str = Field(description='项目类型')
    item_id: int = Field(description='项目ID')
    item_name: str = Field(description='项目名称')
    spec_id: Optional[int] = Field(default=None, description='规格或定价ID')
    spec_name: Optional[str] = Field(default=None, description='规格或定价名称')
    unit: Optional[str] = Field(default=None, description='单位')
    quantity: Optional[int] = Field(default=1, description='购买数量')
    gift_quantity: Optional[int] = Field(default=0, description='赠送数量')
    leave_free_quantity: Optional[int] = Field(default=0, description='请假免扣次数')
    unit_price: Optional[Decimal] = Field(default=0, description='单价')
    total_price: Optional[Decimal] = Field(default=0, description='总价')
    discount_type: Optional[str] = Field(default='reduce', description='优惠类型')
    discount_value: Optional[Decimal] = Field(default=0, description='优惠值')
    subtotal_price: Optional[Decimal] = Field(default=0, description='小计')
    sort: Optional[int] = Field(default=0, description='排序')


class TeachCoursePackageModel(BaseModel):
    """
    套餐基础模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='套餐ID')
    package_no: Optional[str] = Field(default=None, description='套餐编号')
    package_name: Optional[str] = Field(default=None, description='套餐名称')
    total_price: Optional[Decimal] = Field(default=0, description='套餐总价')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    del_flag: Optional[int] = Field(default=0, description='删除标志')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class AddTeachCoursePackageModel(BaseModel):
    """
    新增套餐模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    package_no: Optional[str] = Field(default=None, description='套餐编号', max_length=50)
    package_name: str = Field(description='套餐名称', max_length=100)
    total_price: Optional[Decimal] = Field(default=0, description='套餐总价')
    online_sale: Optional[int] = Field(default=0, description='线上售卖状态')
    status: Optional[int] = Field(default=1, description='启用状态')
    remark: Optional[str] = Field(default=None, description='备注', max_length=500)
    items: Optional[List[TeachPackageItemModel]] = Field(default_factory=list, description='套餐明细')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')

    @Xss(field_name='package_name', message='套餐名称不能包含脚本字符')
    @NotBlank(field_name='package_name', message='套餐名称不能为空')
    @Size(field_name='package_name', min_length=0, max_length=100, message='套餐名称长度不能超过100个字符')
    def get_package_name(self):
        return self.package_name

    def validate_fields(self):
        self.get_package_name()


class EditTeachCoursePackageModel(AddTeachCoursePackageModel):
    """
    编辑套餐模型
    """

    id: int = Field(description='套餐ID')


class ChangeTeachPackageStatusModel(BaseModel):
    """
    套餐启停模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='套餐ID')
    status: int = Field(description='启用状态')


class DeleteTeachCoursePackageModel(BaseModel):
    """
    删除套餐模型
    """

    package_ids: str = Field(description='套餐ID，多个用逗号分隔')


class TeachCoursePackageDetailModel(TeachCoursePackageModel):
    """
    套餐详情模型
    """

    items: List[TeachPackageItemModel] = Field(default_factory=list, description='套餐明细')
