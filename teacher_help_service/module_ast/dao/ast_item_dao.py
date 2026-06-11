from sqlalchemy import select, desc, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from module_ast.entity.do.ast_item_do import AstItem
from module_ast.entity.vo.ast_item_vo import AstItemPageQueryModel, AstItemModel
from utils.page_util import PageUtil


class AstItemDao:
    """
    物品管理模块数据库操作层
    """

    @classmethod
    async def get_ast_item_list(
        cls, db: AsyncSession, query_object: AstItemPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        根据查询参数获取物品列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 物品列表信息对象
        """
        query = (
            select(AstItem)
            .where(
                AstItem.del_flag == 0,
                AstItem.item_name.like(f'%{query_object.item_name}%') if query_object.item_name else True,
                AstItem.item_type == query_object.item_type if query_object.item_type is not None else True,
                AstItem.category.like(f'%{query_object.category}%') if query_object.category else True,
                AstItem.status == query_object.status if query_object.status is not None else True,
                AstItem.create_time >= query_object.begin_time if query_object.begin_time else True,
                AstItem.create_time <= query_object.end_time if query_object.end_time else True,
                eval(data_scope_sql) if data_scope_sql else True,
            )
            .order_by(desc(AstItem.create_time))
            .distinct()
        )

        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
    
    @classmethod
    async def get_ast_item_by_id(cls, db: AsyncSession, item_id: int):
        """
        根据物品id获取物品详细信息

        :param db: orm对象
        :param item_id: 物品id
        :return: 物品信息对象
        """
        query_item_info = (
            (
                await db.execute(
                    select(AstItem)
                    .where(AstItem.id == item_id, AstItem.del_flag == 0)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_item_info

    @classmethod
    async def get_ast_item_by_no(cls, db: AsyncSession, item_no: str):
        """
        根据物品编号获取物品信息

        :param db: orm对象
        :param item_no: 物品编号
        :return: 物品信息对象
        """
        query_item_info = (
            (
                await db.execute(
                    select(AstItem)
                    .where(AstItem.item_no == item_no, AstItem.del_flag == 0)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_item_info

    @classmethod
    async def add_ast_item_dao(cls, db: AsyncSession, item: AstItemModel):
        """
        新增物品数据库操作

        :param db: orm对象
        :param item: 物品对象
        :return: 新增校验结果
        """
        db_item = AstItem(**item.model_dump(exclude_none=True))
        db.add(db_item)
        await db.flush()
        await db.refresh(db_item)

        return db_item

    @classmethod
    async def edit_ast_item_dao(cls, db: AsyncSession, item: dict):
        """
        编辑物品数据库操作

        :param db: orm对象
        :param item: 需要更新的物品字典
        :return: 编辑校验结果
        """
        await db.execute(
            update(AstItem),
            [item],
        )

    @classmethod
    async def delete_ast_item_dao(cls, db: AsyncSession, item: AstItemModel):
        """
        删除物品数据库操作

        :param db: orm对象
        :param item: 物品对象
        :return: 删除校验结果
        """
        await db.execute(
            update(AstItem)
            .where(AstItem.id == item.id)
            .values(del_flag=1, update_by=item.update_by, update_time=item.update_time)
        )
