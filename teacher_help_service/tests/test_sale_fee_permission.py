"""
P3 第二批：销售订单详情、费用导入（整表校验）、老师权限（只改业务菜单子树）
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from tests.helpers import raises_service
from tests.test_student_import_follow import make_xlsx
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.role_do import SysRole, SysRoleMenu
from module_ast.entity.do.ast_fee_course_do import AstFeeCourse
from module_ast.entity.do.ast_fee_item_do import AstFeeItem
from module_ast.entity.do.ast_item_stock_record_do import AstItemStockRecord
from module_ast.service.ast_sale_fee_service import AstSaleFeeService
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_enrollment_order_do import TeachEnrollmentOrder, TeachEnrollmentOrderItem
from module_teach.service.teach_teacher_permission_service import TeachTeacherPermissionService

FEE_HEADERS = ['*费用名称', '*金额', '线上售卖', '状态', '排序', '关联课程', '备注']


async def test_sale_order_detail(db, factory):
    student = await factory.student('张三')
    order = await factory.add(
        TeachEnrollmentOrder(
            order_no='EO001', student_id=student.id, student_name='张三', parent_phone='13800001234',
            total_amount=Decimal('150'), receivable_amount=Decimal('150'), paid_amount=Decimal('100'),
        )
    )
    await factory.add(
        TeachEnrollmentOrderItem(
            order_id=order.id, student_id=student.id, item_type='item', item_id=1, item_name='书包', spec_id=1,
            quantity=1, unit_price=Decimal('150'), total_price=Decimal('150'), subtotal_price=Decimal('150'),
        )
    )
    await factory.add(
        AstItemStockRecord(
            record_no='SR001', item_id=1, item_name='书包', sku_id=1, sku_name='默认', business_type='sale',
            quantity=-1, stock_before=5, stock_after=4, source_type='enrollment_order', source_id=order.id,
            record_date=date.today(),
        )
    )
    await db.commit()
    result = await AstSaleFeeService.get_sale_order_detail_services(db, order.id)
    assert result['order']['parentPhone'] == '138****1234'
    assert result['order']['arrearsAmount'] == Decimal('50')
    assert len(result['goodsItems']) == 1 and result['stockRecords'][0]['stockTypeLabel'] == '出库'
    with raises_service('不存在'):
        await AstSaleFeeService.get_sale_order_detail_services(db, 999)


async def test_fee_import_whole_file_validation(db, factory):
    await factory.add(TeachCourse(course_name='少儿英语', status=1, del_flag=0))
    await factory.add(AstFeeItem(fee_name='报名费', amount=Decimal('50'), del_flag=0))
    await db.commit()
    bad = make_xlsx(
        FEE_HEADERS,
        [
            ['教材费', '120', '否', '启用', '1', '少儿英语', None],
            ['报名费', '10', None, None, None, None, None],
            ['教材费', '20', None, None, None, None, None],
            ['资料费', 'abc', None, None, None, None, None],
            ['场地费', '30', '可以', None, None, '不存在的课', None],
        ],
    )
    result = await AstSaleFeeService.import_fee_services(db, bad, 'tester')
    assert not result['success'] and result['errorCount'] == 4
    assert [error['row'] for error in result['errors']] == [3, 4, 5, 6]
    count = (await db.execute(select(AstFeeItem))).scalars().all()
    assert len(count) == 1
    good = make_xlsx(FEE_HEADERS, [['教材费', '120.5', '是', '停用', '2', '少儿英语', '新学期'], ['杂费', '0']])
    result = await AstSaleFeeService.import_fee_services(db, good, 'tester')
    assert result['success'] and result['successCount'] == 2
    fee = (await db.execute(select(AstFeeItem).where(AstFeeItem.fee_name == '教材费'))).scalars().first()
    assert (fee.amount, fee.online_sale, fee.status, fee.sort) == (Decimal('120.50'), 1, 0, 2)
    links = (await db.execute(select(AstFeeCourse).where(AstFeeCourse.fee_id == fee.id))).scalars().all()
    assert [link.course_name for link in links] == ['少儿英语']
    assert AstSaleFeeService.get_fee_template_services()[:2] == b'PK'


async def setup_menus(db, factory):
    for menu_id, parent_id, name, menu_type in [
        (1, 0, '系统管理', 'M'),
        (5000, 0, '老师帮业务权限', 'M'),
        (5006, 5000, '排课管理', 'M'),
        (5131, 5006, '排课管理列表', 'F'),
        (5132, 5006, '排课管理查询', 'F'),
        (5008, 5000, '上课记录', 'M'),
        (5138, 5008, '上课记录列表', 'F'),
    ]:
        db.add(SysMenu(menu_id=menu_id, parent_id=parent_id, menu_name=name, menu_type=menu_type, order_num=1))
    db.add(SysRole(role_id=1, role_name='超级管理员', role_key='admin', role_sort=1, del_flag='0'))
    db.add(SysRole(role_id=2, role_name='老师', role_key='teacher', role_sort=2, del_flag='0'))
    db.add(SysRoleMenu(role_id=2, menu_id=1))
    db.add(SysRoleMenu(role_id=2, menu_id=5138))
    await db.commit()


async def test_teacher_permission_only_touches_business_subtree(db, factory):
    await setup_menus(db, factory)
    roles = await TeachTeacherPermissionService.get_roles_services(db)
    teacher = next(role for role in roles if role['roleId'] == 2)
    assert (teacher['grantedCount'], teacher['totalCount']) == (1, 3)
    tree = await TeachTeacherPermissionService.get_role_tree_services(db, 2)
    assert tree['menus'][0]['id'] == 5000 and tree['checkedKeys'] == [5138]
    await TeachTeacherPermissionService.save_role_menus_services(db, 2, [5131], 'tester')
    rows = (await db.execute(select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == 2))).scalars().all()
    # 系统菜单(1)保留；5138 被取消；5131 及其上级 5006、5000 自动补齐
    assert sorted(rows) == [1, 5000, 5006, 5131]
    with raises_service('只能分配'):
        await TeachTeacherPermissionService.save_role_menus_services(db, 2, [1], 'tester')
    with raises_service('超级管理员'):
        await TeachTeacherPermissionService.save_role_menus_services(db, 1, [5131], 'tester')
