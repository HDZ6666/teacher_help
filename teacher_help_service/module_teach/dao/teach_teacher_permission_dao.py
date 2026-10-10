from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.role_do import SysRole, SysRoleMenu


class TeachTeacherPermissionDao:
    """
    老师权限（业务中心菜单授权）数据库操作层：只读写 sys_role / sys_menu / sys_role_menu
    """

    @classmethod
    async def get_roles(cls, db: AsyncSession):
        result = await db.execute(select(SysRole).where(SysRole.del_flag == '0').order_by(SysRole.role_sort))
        return result.scalars().all()

    @classmethod
    async def get_role(cls, db: AsyncSession, role_id: int):
        result = await db.execute(select(SysRole).where(SysRole.role_id == role_id, SysRole.del_flag == '0'))
        return result.scalars().first()

    @classmethod
    async def get_all_menus(cls, db: AsyncSession):
        result = await db.execute(select(SysMenu).order_by(SysMenu.parent_id, SysMenu.order_num, SysMenu.menu_id))
        return result.scalars().all()

    @classmethod
    async def get_role_menu_ids(cls, db: AsyncSession, role_ids: list[int]):
        if not role_ids:
            return []
        result = await db.execute(
            select(SysRoleMenu.role_id, SysRoleMenu.menu_id).where(SysRoleMenu.role_id.in_(role_ids))
        )
        return result.all()

    @classmethod
    async def replace_role_menus(cls, db: AsyncSession, role_id: int, scope_ids: set[int], menu_ids: set[int]):
        """
        只替换角色在业务中心范围（scope_ids）内的菜单授权，范围外的系统菜单授权保持不变
        """
        if scope_ids:
            await db.execute(
                delete(SysRoleMenu).where(SysRoleMenu.role_id == role_id, SysRoleMenu.menu_id.in_(scope_ids))
            )
        for menu_id in sorted(menu_ids):
            db.add(SysRoleMenu(role_id=role_id, menu_id=menu_id))
        await db.flush()
