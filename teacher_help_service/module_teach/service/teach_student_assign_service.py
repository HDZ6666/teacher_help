from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.entity.do.teach_student_do import TeachStudent


class TeachStudentAssignService:
    """
    学员跟进人/学管师分配（P2）：候选人为系统员工账号（sys_user，正常状态、未删除）
    """

    ROLE_COLUMNS = {
        'follower': ('follower_user_id', '跟进人'),
        'advisor': ('advisor_user_id', '学管师'),
    }

    @classmethod
    def _role(cls, role: str):
        if role not in cls.ROLE_COLUMNS:
            raise ServiceException(message='分配类型只能是 follower（跟进人）或 advisor（学管师）')
        return cls.ROLE_COLUMNS[role]

    @classmethod
    async def get_staff_options_services(cls, query_db: AsyncSession, role: str, keyword: Optional[str] = None):
        """
        候选员工列表，附带已分配的在读学员数
        """
        column_name, _ = cls._role(role)
        column = getattr(TeachStudent, column_name)
        assigned = (
            select(column.label('user_id'), func.count().label('cnt'))
            .where(TeachStudent.del_flag == '0', TeachStudent.status == '0', column.is_not(None))
            .group_by(column)
            .subquery()
        )
        query = (
            select(SysUser.user_id, SysUser.nick_name, SysUser.phonenumber, assigned.c.cnt)
            .outerjoin(assigned, assigned.c.user_id == SysUser.user_id)
            .where(SysUser.del_flag == '0', SysUser.status == '0')
            .order_by(SysUser.user_id)
        )
        if keyword:
            query = query.where(SysUser.nick_name.like(f'%{keyword}%'))
        rows = (await query_db.execute(query)).all()
        return [
            {
                'id': row.user_id,
                'name': row.nick_name,
                'phone': cls.mask_phone(row.phonenumber),
                'assignedCount': row.cnt or 0,
            }
            for row in rows
        ]

    @staticmethod
    def mask_phone(phone: Optional[str]):
        if not phone:
            return '-'
        return f'{phone[:3]}****{phone[-4:]}' if len(phone) >= 7 else phone

    @classmethod
    async def assign_services(
        cls, query_db: AsyncSession, student_ids: List[int], role: str, user_id: Optional[int], operator: str
    ):
        """
        批量分配（user_id 为空表示改为待分配）
        """
        column_name, label = cls._role(role)
        unique_ids = sorted(set(student_ids))
        if user_id is not None:
            user = (
                await query_db.execute(
                    select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == '0', SysUser.status == '0')
                )
            ).scalar_one_or_none()
            if user is None:
                raise ServiceException(message=f'{label}不存在或已停用')
        student_query = select(TeachStudent).where(TeachStudent.id.in_(unique_ids), TeachStudent.del_flag == '0')
        students = (await query_db.execute(student_query)).scalars().all()
        missing = sorted(set(unique_ids) - {student.id for student in students})
        if missing:
            raise ServiceException(message=f'学员不存在：{missing}')
        now = datetime.now()
        try:
            for student in students:
                setattr(student, column_name, user_id)
                student.update_by = operator
                student.update_time = now
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        action = f'分配{label}' if user_id is not None else f'清空{label}'
        return CrudResponseModel(is_success=True, message=f'已为 {len(students)} 名学员{action}')

    @classmethod
    async def fill_staff_names(cls, query_db: AsyncSession, rows: list):
        """
        为学员列表行补充 follower/advisor 姓名（行内为 followerUserId/advisorUserId）
        """
        user_ids = {
            row.get(key)
            for row in rows
            if isinstance(row, dict)
            for key in ('followerUserId', 'advisorUserId')
            if row.get(key)
        }
        names = {}
        if user_ids:
            user_query = select(SysUser.user_id, SysUser.nick_name).where(SysUser.user_id.in_(user_ids))
            result = await query_db.execute(user_query)
            names = {row.user_id: row.nick_name for row in result.all()}
        for row in rows:
            if isinstance(row, dict):
                row['follower'] = names.get(row.get('followerUserId'), '')
                row['advisor'] = names.get(row.get('advisorUserId'), '')
        return rows
