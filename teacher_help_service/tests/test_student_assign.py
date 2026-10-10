"""
学员跟进人/学管师分配（P2）：候选为正常状态员工，批量分配/清空，列表回填姓名
"""

from tests.helpers import raises_service
from module_admin.entity.do.user_do import SysUser
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.service.teach_student_assign_service import TeachStudentAssignService


async def add_user(factory, name, status='0'):
    n = factory.next()
    return await factory.add(
        SysUser(user_name=f'u{n}', nick_name=name, phonenumber=f'1390000{n:04d}', status=status, del_flag='0')
    )


async def test_assign_and_clear(db, factory):
    s1 = await factory.student('学员甲')
    s2 = await factory.student('学员乙')
    staff = await add_user(factory, '王老师')
    disabled = await add_user(factory, '停用员工', status='1')
    await db.commit()

    result = await TeachStudentAssignService.assign_services(db, [s1.id, s2.id], 'advisor', staff.user_id, 'tester')
    assert result.is_success
    student = await db.get(TeachStudent, s1.id, populate_existing=True)
    assert student.advisor_user_id == staff.user_id and student.follower_user_id is None

    options = await TeachStudentAssignService.get_staff_options_services(db, 'advisor')
    by_id = {item['id']: item for item in options}
    assert by_id[staff.user_id]['assignedCount'] == 2 and disabled.user_id not in by_id
    assert '****' in by_id[staff.user_id]['phone']

    rows = [{'followerUserId': None, 'advisorUserId': staff.user_id}]
    await TeachStudentAssignService.fill_staff_names(db, rows)
    assert rows[0]['advisor'] == '王老师' and rows[0]['follower'] == ''

    await TeachStudentAssignService.assign_services(db, [s1.id], 'advisor', None, 'tester')
    student = await db.get(TeachStudent, s1.id, populate_existing=True)
    assert student.advisor_user_id is None

    with raises_service('停用'):
        await TeachStudentAssignService.assign_services(db, [s1.id], 'follower', disabled.user_id, 'tester')
    with raises_service('不存在'):
        await TeachStudentAssignService.assign_services(db, [999999], 'follower', staff.user_id, 'tester')
    with raises_service('分配类型'):
        await TeachStudentAssignService.get_staff_options_services(db, 'boss')
