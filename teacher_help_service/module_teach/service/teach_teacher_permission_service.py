from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_teacher_permission_dao import TeachTeacherPermissionDao


class TeachTeacherPermissionService:
    """
    老师权限：基于若依 sys_role / sys_menu，为角色勾选“老师帮业务权限”(menu_id=5000) 下的菜单与按钮。

    - 只读写 5000 子树内的 sys_role_menu，角色在系统管理等其他菜单上的授权保持不变；
    - 超级管理员角色(role_id=1 / role_key=admin)天然拥有全部权限，不允许在这里修改；
    - 勾选按钮时自动补齐其上级目录/菜单（与若依角色授权保存父节点的口径一致）。
    """

    ROOT_MENU_ID = 5000

    @classmethod
    def is_admin_role(cls, role):
        return role.role_id == 1 or role.role_key == 'admin'

    @classmethod
    async def get_scope(cls, query_db: AsyncSession):
        menus = await TeachTeacherPermissionDao.get_all_menus(query_db)
        children: dict[int, list] = {}
        menu_map = {}
        for menu in menus:
            menu_map[menu.menu_id] = menu
            children.setdefault(menu.parent_id, []).append(menu)
        if cls.ROOT_MENU_ID not in menu_map:
            raise ServiceException(message='未找到“老师帮业务权限”菜单(5000)，请先执行菜单初始化 SQL')
        scope = {}
        stack = [cls.ROOT_MENU_ID]
        while stack:
            menu_id = stack.pop()
            scope[menu_id] = menu_map[menu_id]
            stack.extend(child.menu_id for child in children.get(menu_id, []))
        return scope, children

    @classmethod
    def build_tree(cls, menu_id: int, scope: dict, children: dict):
        menu = scope[menu_id]
        node = {
            'id': menu.menu_id,
            'label': menu.menu_name,
            'menuType': menu.menu_type,
            'perms': menu.perms,
            'status': menu.status,
        }
        kids = [
            cls.build_tree(child.menu_id, scope, children)
            for child in children.get(menu_id, [])
            if child.menu_id in scope
        ]
        if kids:
            node['children'] = kids
        return node

    @classmethod
    async def get_roles_services(cls, query_db: AsyncSession):
        scope, _ = await cls.get_scope(query_db)
        roles = await TeachTeacherPermissionDao.get_roles(query_db)
        counts: dict[int, int] = {}
        for role_id, menu_id in await TeachTeacherPermissionDao.get_role_menu_ids(query_db, [r.role_id for r in roles]):
            if menu_id in scope and scope[menu_id].menu_type == 'F':
                counts[role_id] = counts.get(role_id, 0) + 1
        total = sum(1 for menu in scope.values() if menu.menu_type == 'F')
        return [
            {
                'roleId': role.role_id,
                'roleName': role.role_name,
                'roleKey': role.role_key,
                'status': role.status,
                'remark': role.remark,
                'isAdmin': cls.is_admin_role(role),
                'grantedCount': total if cls.is_admin_role(role) else counts.get(role.role_id, 0),
                'totalCount': total,
            }
            for role in roles
        ]

    @classmethod
    async def get_role_tree_services(cls, query_db: AsyncSession, role_id: int):
        role = await TeachTeacherPermissionDao.get_role(query_db, role_id)
        if not role:
            raise ServiceException(message='角色不存在')
        scope, children = await cls.get_scope(query_db)
        granted = {
            menu_id
            for _, menu_id in await TeachTeacherPermissionDao.get_role_menu_ids(query_db, [role_id])
            if menu_id in scope
        }
        # 只返回叶子节点作为勾选项，父节点由树组件按子节点状态半选/全选，避免误选整棵子树
        checked = [menu_id for menu_id in granted if not any(c.menu_id in scope for c in children.get(menu_id, []))]
        return {
            'roleId': role.role_id,
            'roleName': role.role_name,
            'isAdmin': cls.is_admin_role(role),
            'menus': [cls.build_tree(cls.ROOT_MENU_ID, scope, children)],
            'checkedKeys': sorted(checked),
        }

    @classmethod
    async def save_role_menus_services(cls, query_db: AsyncSession, role_id: int, menu_ids: list[int], operator: str):
        role = await TeachTeacherPermissionDao.get_role(query_db, role_id)
        if not role:
            raise ServiceException(message='角色不存在')
        if cls.is_admin_role(role):
            raise ServiceException(message='超级管理员拥有全部权限，不需要也不允许在此修改')
        scope, _ = await cls.get_scope(query_db)
        invalid = [menu_id for menu_id in menu_ids if menu_id not in scope]
        if invalid:
            raise ServiceException(message='只能分配“老师帮业务权限”下的菜单')
        selected = set()
        for menu_id in set(menu_ids):
            current = menu_id
            while current in scope and current not in selected:
                selected.add(current)
                current = scope[current].parent_id
        try:
            await TeachTeacherPermissionDao.replace_role_menus(query_db, role_id, set(scope), selected)
            await query_db.commit()
        except Exception as e:
            await query_db.rollback()
            raise e
        buttons = sum(1 for menu_id in selected if scope[menu_id].menu_type == 'F')
        return CrudResponseModel(
            is_success=True, message=f'保存成功，{role.role_name}共{buttons}项业务按钮权限', result={'roleId': role_id}
        )
