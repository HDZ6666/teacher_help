from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from module_ast.dao.ast_item_dao import AstItemDao
from module_ast.entity.vo.ast_item_vo import (
    AstItemPageQueryModel,
    AstItemModel,
    AddAstItemModel,
    EditAstItemModel,
    DeleteAstItemModel,
    AstItemDetailModel
)
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.common_util import CamelCaseUtil
from exceptions.exception import ServiceException


class AstItemService:
    """
    物品管理模块服务层
    """

    @classmethod
    async def get_ast_item_list_services(
        cls, query_db: AsyncSession, query_object: AstItemPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        获取物品列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 物品列表信息对象
        """
        item_list_result = await AstItemDao.get_ast_item_list(query_db, query_object, data_scope_sql, is_page)

        return item_list_result
    
    @classmethod
    async def get_ast_item_detail_services(cls, query_db: AsyncSession, item_id: int):
        """
        获取物品详情信息service

        :param query_db: orm对象
        :param item_id: 物品ID
        :return: 物品详情信息对象
        """
        item = await AstItemDao.get_ast_item_by_id(query_db, item_id)
        if item:
            result = AstItemDetailModel(**CamelCaseUtil.transform_result(item))
        else:
            result = AstItemDetailModel(**dict())

        return result

    @classmethod
    async def add_ast_item_services(cls, query_db: AsyncSession, page_object: AddAstItemModel):
        """
        新增物品信息service

        :param query_db: orm对象
        :param page_object: 新增物品对象
        :return: 新增物品校验结果
        """
        add_item = AstItemModel(**page_object.model_dump(by_alias=True))
        if page_object.item_no and not await cls.check_item_no_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增物品{page_object.item_name}失败，物品编号已存在')
        else:
            try:
                await AstItemDao.add_ast_item_dao(query_db, add_item)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='新增成功')
            except Exception as e:
                await query_db.rollback()
                raise e

    @classmethod
    async def edit_ast_item_services(cls, query_db: AsyncSession, page_object: EditAstItemModel):
        """
        编辑物品信息service

        :param query_db: orm对象
        :param page_object: 编辑物品对象
        :return: 编辑物品校验结果
        """
        edit_item = page_object.model_dump(exclude_unset=True)
        item_info = await cls.item_detail_services(query_db, edit_item.get('id'))
        if item_info:
            if page_object.item_no and not await cls.check_item_no_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改物品{page_object.item_name}失败，物品编号已存在')
            try:
                await AstItemDao.edit_ast_item_dao(query_db, edit_item)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='物品不存在')

    @classmethod
    async def delete_ast_item_services(cls, query_db: AsyncSession, page_object: DeleteAstItemModel):
        """
        删除物品信息service

        :param query_db: orm对象
        :param page_object: 删除物品对象
        :return: 删除物品校验结果
        """
        if page_object.item_ids:
            item_id_list = page_object.item_ids.split(',')
            try:
                for item_id in item_id_list:
                    item_id_dict = dict(
                        id=item_id, updateBy=page_object.update_by, updateTime=page_object.update_time
                    )
                    await AstItemDao.delete_ast_item_dao(query_db, AstItemModel(**item_id_dict))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入物品id为空')

    @classmethod
    async def item_detail_services(cls, query_db: AsyncSession, item_id: int):
        """
        获取物品详细信息service（内部使用）

        :param query_db: orm对象
        :param item_id: 物品id
        :return: 物品信息对象
        """
        item = await AstItemDao.get_ast_item_by_id(query_db, item_id)
        return item

    @classmethod
    async def check_item_no_unique_services(cls, query_db: AsyncSession, page_object):
        """
        校验物品编号是否唯一service

        :param query_db: orm对象
        :param page_object: 物品对象
        :return: 校验结果
        """
        item_id = -1 if page_object.id is None else page_object.id
        item = await AstItemDao.get_ast_item_by_no(query_db, page_object.item_no)
        if item and item.id != item_id:
            return False

        return True

