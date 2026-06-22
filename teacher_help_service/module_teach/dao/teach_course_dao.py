from datetime import datetime
from sqlalchemy import and_, desc, func, or_, select, update  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.dept_do import SysDept  # noqa: F401
from module_admin.entity.do.role_do import SysRoleDept  # noqa: F401
from module_teach.entity.do.teach_course_package_do import TeachCoursePackage
from module_teach.entity.do.teach_course_do import TeachCourse
from module_teach.entity.do.teach_package_item_do import TeachPackageItem
from module_teach.entity.do.teach_course_price_do import TeachCoursePrice
from module_teach.entity.vo.teach_course_vo import TeachCoursePackagePageQueryModel, TeachCoursePageQueryModel
from utils.page_util import PageUtil


class TeachCourseDao:
    """
    课程管理模块数据库操作层
    """

    @classmethod
    async def get_teach_course_list(
        cls, db: AsyncSession, query_object: TeachCoursePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCourse).where(TeachCourse.del_flag == 0)
        if query_object.course_name:
            query = query.where(TeachCourse.course_name.like(f'%{query_object.course_name}%'))
        if query_object.course_type:
            query = query.where(TeachCourse.course_type == query_object.course_type)
        if query_object.status is not None:
            query = query.where(TeachCourse.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachCourse.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCourse.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCourse.create_time), desc(TeachCourse.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_course_by_id(cls, db: AsyncSession, course_id: int):
        result = await db.execute(
            select(TeachCourse).where(TeachCourse.id == course_id, TeachCourse.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_teach_course_by_no(cls, db: AsyncSession, course_no: str):
        result = await db.execute(
            select(TeachCourse).where(TeachCourse.course_no == course_no, TeachCourse.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def add_teach_course(cls, db: AsyncSession, course: TeachCourse):
        db.add(course)
        await db.flush()
        await db.refresh(course)
        return course

    @classmethod
    async def edit_teach_course(cls, db: AsyncSession, course: TeachCourse):
        course.update_time = datetime.now()
        await db.flush()
        return course

    @classmethod
    async def delete_teach_course(cls, db: AsyncSession, course_ids: list[int], update_by: str):
        await db.execute(
            update(TeachCourse)
            .where(and_(TeachCourse.id.in_(course_ids), TeachCourse.del_flag == 0))
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def update_teach_course_status(cls, db: AsyncSession, course_id: int, status: int, update_by: str):
        await db.execute(
            update(TeachCourse)
            .where(and_(TeachCourse.id == course_id, TeachCourse.del_flag == 0))
            .values(status=status, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def get_prices_by_course_id(cls, db: AsyncSession, course_id: int):
        result = await db.execute(
            select(TeachCoursePrice)
            .where(TeachCoursePrice.course_id == course_id, TeachCoursePrice.del_flag == 0)
            .order_by(TeachCoursePrice.charge_type, TeachCoursePrice.sort, TeachCoursePrice.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_prices_by_course_ids(cls, db: AsyncSession, course_ids: list[int]):
        if not course_ids:
            return []
        result = await db.execute(
            select(TeachCoursePrice)
            .where(TeachCoursePrice.course_id.in_(course_ids), TeachCoursePrice.del_flag == 0)
            .order_by(TeachCoursePrice.course_id, TeachCoursePrice.charge_type, TeachCoursePrice.sort, TeachCoursePrice.id)
        )
        return result.scalars().all()

    @classmethod
    async def delete_prices_by_course_id(cls, db: AsyncSession, course_id: int, update_by: str):
        await db.execute(
            update(TeachCoursePrice)
            .where(TeachCoursePrice.course_id == course_id, TeachCoursePrice.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def add_teach_course_price(cls, db: AsyncSession, price: TeachCoursePrice):
        db.add(price)
        await db.flush()
        await db.refresh(price)
        return price

    @classmethod
    async def get_available_course_list(cls, db: AsyncSession, keyword: str | None = None):
        query = select(TeachCourse).where(TeachCourse.del_flag == 0, TeachCourse.status == 1)
        if keyword:
            query = query.where(TeachCourse.course_name.like(f'%{keyword}%'))
        result = await db.execute(query.order_by(desc(TeachCourse.create_time), desc(TeachCourse.id)))
        return result.scalars().all()

    @classmethod
    async def get_teach_package_list(
        cls, db: AsyncSession, query_object: TeachCoursePackagePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        query = select(TeachCoursePackage).where(TeachCoursePackage.del_flag == 0)
        if query_object.package_name:
            query = query.where(TeachCoursePackage.package_name.like(f'%{query_object.package_name}%'))
        if query_object.status is not None:
            query = query.where(TeachCoursePackage.status == query_object.status)
        if query_object.begin_time:
            query = query.where(TeachCoursePackage.create_time >= query_object.begin_time)
        if query_object.end_time:
            query = query.where(TeachCoursePackage.create_time <= query_object.end_time)
        if data_scope_sql:
            query = query.where(eval(data_scope_sql))
        query = query.order_by(desc(TeachCoursePackage.create_time), desc(TeachCoursePackage.id))
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_teach_package_by_id(cls, db: AsyncSession, package_id: int):
        result = await db.execute(
            select(TeachCoursePackage).where(TeachCoursePackage.id == package_id, TeachCoursePackage.del_flag == 0)
        )
        return result.scalars().first()

    @classmethod
    async def get_teach_package_by_no(cls, db: AsyncSession, package_no: str):
        result = await db.execute(
            select(TeachCoursePackage).where(
                TeachCoursePackage.package_no == package_no, TeachCoursePackage.del_flag == 0
            )
        )
        return result.scalars().first()

    @classmethod
    async def add_teach_package(cls, db: AsyncSession, package: TeachCoursePackage):
        db.add(package)
        await db.flush()
        await db.refresh(package)
        return package

    @classmethod
    async def edit_teach_package(cls, db: AsyncSession, package: TeachCoursePackage):
        package.update_time = datetime.now()
        await db.flush()
        return package

    @classmethod
    async def delete_teach_package(cls, db: AsyncSession, package_ids: list[int], update_by: str):
        await db.execute(
            update(TeachCoursePackage)
            .where(and_(TeachCoursePackage.id.in_(package_ids), TeachCoursePackage.del_flag == 0))
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def update_teach_package_status(cls, db: AsyncSession, package_id: int, status: int, update_by: str):
        await db.execute(
            update(TeachCoursePackage)
            .where(and_(TeachCoursePackage.id == package_id, TeachCoursePackage.del_flag == 0))
            .values(status=status, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def get_package_items_by_package_id(cls, db: AsyncSession, package_id: int):
        result = await db.execute(
            select(TeachPackageItem)
            .where(TeachPackageItem.package_id == package_id, TeachPackageItem.del_flag == 0)
            .order_by(TeachPackageItem.sort, TeachPackageItem.id)
        )
        return result.scalars().all()

    @classmethod
    async def get_package_items_by_package_ids(cls, db: AsyncSession, package_ids: list[int]):
        if not package_ids:
            return []
        result = await db.execute(
            select(TeachPackageItem)
            .where(TeachPackageItem.package_id.in_(package_ids), TeachPackageItem.del_flag == 0)
            .order_by(TeachPackageItem.package_id, TeachPackageItem.sort, TeachPackageItem.id)
        )
        return result.scalars().all()

    @classmethod
    async def delete_package_items_by_package_id(cls, db: AsyncSession, package_id: int, update_by: str):
        await db.execute(
            update(TeachPackageItem)
            .where(TeachPackageItem.package_id == package_id, TeachPackageItem.del_flag == 0)
            .values(del_flag=1, update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def add_package_item(cls, db: AsyncSession, package_item: TeachPackageItem):
        db.add(package_item)
        await db.flush()
        await db.refresh(package_item)
        return package_item
