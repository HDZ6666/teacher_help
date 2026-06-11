from collections import defaultdict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from module_ast.dao.ast_item_dao import AstItemDao
from module_ast.dao.ast_inventory_dao import AstInventoryDao
from module_ast.service.ast_inventory_service import AstInventoryService
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
from utils.excel_util import ExcelUtil


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
        if hasattr(item_list_result, 'rows'):
            item_ids = [item.get('id') for item in item_list_result.rows if item.get('id')]
            skus = await AstInventoryDao.get_item_skus_by_item_ids(query_db, item_ids)
            sku_map = defaultdict(list)
            for sku in skus:
                sku_map[sku.item_id].append(sku)
            item_list_result.rows = [
                AstInventoryService.format_item_row(item, sku_map.get(item.get('id'), []))
                for item in item_list_result.rows
            ]
            item_list_result.rows = await AstInventoryService.attach_item_courses(query_db, item_list_result.rows)
        else:
            item_ids = [item.get('id') for item in item_list_result if item.get('id')]
            skus = await AstInventoryDao.get_item_skus_by_item_ids(query_db, item_ids)
            sku_map = defaultdict(list)
            for sku in skus:
                sku_map[sku.item_id].append(sku)
            item_list_result = [
                AstInventoryService.format_item_row(item, sku_map.get(item.get('id'), []))
                for item in item_list_result
            ]
            item_list_result = await AstInventoryService.attach_item_courses(query_db, item_list_result)

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
            item_dict = CamelCaseUtil.transform_result(item)
            skus = await AstInventoryDao.get_item_skus_by_item_id(query_db, item.id)
            AstInventoryService.format_item_row(item_dict, skus)
            await AstInventoryService.attach_item_courses(query_db, [item_dict])
            result = AstItemDetailModel(**item_dict)
        else:
            raise ServiceException(message='物品不存在')

        return result

    @classmethod
    async def add_ast_item_services(cls, query_db: AsyncSession, page_object: AddAstItemModel):
        """
        新增物品信息service

        :param query_db: orm对象
        :param page_object: 新增物品对象
        :return: 新增物品校验结果
        """
        AstInventoryService.normalize_item_save_payload(page_object)
        if not page_object.item_no:
            page_object.item_no = AstInventoryService.make_no('ITEM')
        add_item = AstItemModel(
            **page_object.model_dump(
                by_alias=True,
                exclude={'skus', 'specs', 'single_price', 'item_images', 'course_ids', 'course_names', 'courses'},
            )
        )
        if page_object.item_no and not await cls.check_item_no_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增物品{page_object.item_name}失败，物品编号已存在')
        else:
            try:
                item = await AstItemDao.add_ast_item_dao(query_db, add_item)
                await AstInventoryService.sync_item_skus_services(query_db, item, page_object, page_object.create_by or '')
                await AstInventoryService.save_item_courses(query_db, item.id, page_object, page_object.create_by or '')
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
        AstInventoryService.normalize_item_save_payload(page_object)
        edit_item = page_object.model_dump(
            exclude_unset=True,
            exclude={'skus', 'specs', 'single_price', 'item_images', 'course_ids', 'course_names', 'courses'}
        )
        item_info = await cls.item_detail_services(query_db, edit_item.get('id'))
        if item_info:
            if page_object.item_no and not await cls.check_item_no_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改物品{page_object.item_name}失败，物品编号已存在')
            try:
                await AstItemDao.edit_ast_item_dao(query_db, edit_item)
                await AstInventoryService.sync_item_skus_services(
                    query_db, item_info, page_object, page_object.update_by or ''
                )
                await AstInventoryService.save_item_courses(query_db, item_info.id, page_object, page_object.update_by or '')
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
                    await AstInventoryDao.soft_delete_item_skus_by_item_id(
                        query_db, int(item_id), page_object.update_by or ''
                    )
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
        item_id = -1 if getattr(page_object, 'id', None) is None else page_object.id
        item = await AstItemDao.get_ast_item_by_no(query_db, page_object.item_no)
        if item and item.id != item_id:
            return False

        return True

    @staticmethod
    async def export_ast_item_list_services(item_list: list):
        """
        导出物品信息service
        """
        mapping_dict = {
            'itemCode': '物品编码',
            'itemName': '物品名称',
            'itemType': '物品类型',
            'skuCount': 'SKU数量',
            'totalStock': '总库存',
            'warningStock': '库存预警',
            'isWarning': '预警状态',
            'priceRange': '单价范围',
            'courseName': '绑定课程',
            'enableStock': '开启库存',
            'onlineSale': '线上售卖',
            'status': '启用状态',
            'remark': '备注',
        }
        for item in item_list:
            item['itemType'] = '实物' if str(item.get('itemType')) == '1' else '虚拟'
            item['isWarning'] = '预警' if item.get('isWarning') else '正常'
            item['enableStock'] = '开启' if item.get('enableStock') == 1 else '关闭'
            item['onlineSale'] = '开启' if item.get('onlineSale') == 1 else '关闭'
            item['status'] = '启用' if item.get('status') == 1 else '停用'
        return ExcelUtil.export_list2excel(item_list, mapping_dict)
