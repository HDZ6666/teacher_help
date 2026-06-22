from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_ast.entity.vo.ast_inventory_vo import (
    AddAstFeeItemModel,
    AddInventoryStockModel,
    AddPurchaseOrderModel,
    AddReceiveStockModel,
    AddReturnStockModel,
    AstFeeItemPageQueryModel,
    AstStockRecordPageQueryModel,
    ChangeAstFeeStatusModel,
    DeleteAstFeeItemModel,
    EditAstFeeItemModel,
)
from module_ast.service.ast_inventory_service import AstInventoryService
from utils.log_util import logger
from utils.common_util import bytes2file_response
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


astInventoryController = APIRouter(prefix='/ast/inventory', dependencies=[Depends(LoginService.get_current_user)])


@astInventoryController.get(
    '/item/{item_id}/skus',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:item:query', 'ast:inventory:list']))],
)
async def get_item_skus(request: Request, item_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await AstInventoryService.get_item_skus_services(query_db, item_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@astInventoryController.get(
    '/items/options',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:item:list', 'ast:inventory:list']))],
)
async def get_available_items(request: Request, keyword: str | None = None, query_db: AsyncSession = Depends(get_db)):
    result = await AstInventoryService.get_available_items_services(query_db, keyword)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@astInventoryController.get(
    '/role-options',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:inventory:add', 'ast:inventory:list']))],
)
async def get_role_options(
    request: Request,
    role_type: str | None = Query(default=None, alias='roleType'),
    keyword: str | None = None,
    query_db: AsyncSession = Depends(get_db),
):
    result = await AstInventoryService.get_role_options_services(query_db, role_type, keyword)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@astInventoryController.get(
    '/stock/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:list'))],
)
async def get_stock_record_list(
    request: Request,
    stock_query: AstStockRecordPageQueryModel = Depends(AstStockRecordPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await AstInventoryService.get_stock_record_list_services(query_db, stock_query, is_page=True)
    summary = await AstInventoryService.get_stock_record_summary_services(query_db, stock_query)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result, dict_content={'summary': summary})


@astInventoryController.post(
    '/stock/export',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:inventory:export', 'ast:inventory:list']))],
)
@Log(title='物品出入库记录', business_type=BusinessType.EXPORT)
async def export_stock_record_list(
    request: Request,
    stock_query: AstStockRecordPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    stock_query_result = await AstInventoryService.get_stock_record_list_services(query_db, stock_query, is_page=False)
    stock_export_result = await AstInventoryService.export_stock_record_list_services(stock_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(stock_export_result))


@astInventoryController.get(
    '/stock/{record_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:query'))],
)
async def get_stock_record_detail(request: Request, record_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await AstInventoryService.get_stock_record_detail_services(query_db, record_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@astInventoryController.put(
    '/stock/{record_id}/void',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:inventory:edit', 'ast:inventory:add']))],
)
@Log(title='物品出入库记录作废', business_type=BusinessType.UPDATE)
async def void_stock_record(
    request: Request,
    record_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.void_stock_record_services(query_db, record_id, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.post('/purchase', dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:add'))])
@Log(title='物品采购入库', business_type=BusinessType.INSERT)
async def create_purchase(
    request: Request,
    purchase_form: AddPurchaseOrderModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.create_purchase_services(query_db, purchase_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@astInventoryController.post(
    '/purchase/import/template',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:inventory:add', 'ast:inventory:export']))],
)
async def download_purchase_import_template(request: Request):
    result = await AstInventoryService.get_purchase_import_template_services()
    logger.info('下载成功')
    return ResponseUtil.streaming(data=bytes2file_response(result))


@astInventoryController.post(
    '/purchase/import',
    dependencies=[Depends(CheckUserInterfaceAuth(['ast:inventory:add', 'ast:inventory:import']))],
)
@Log(title='物品采购导入', business_type=BusinessType.IMPORT)
async def import_purchase(
    request: Request,
    file: UploadFile = File(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.import_purchase_services(query_db, file, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@astInventoryController.post('/receive', dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:add'))])
@Log(title='物品领用', business_type=BusinessType.INSERT)
async def create_receive(
    request: Request,
    receive_form: AddReceiveStockModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.create_receive_services(query_db, receive_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.post('/return', dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:add'))])
@Log(title='物品退领', business_type=BusinessType.INSERT)
async def create_return(
    request: Request,
    return_form: AddReturnStockModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.create_return_services(query_db, return_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.post('/inventory', dependencies=[Depends(CheckUserInterfaceAuth('ast:inventory:add'))])
@Log(title='物品库存盘点', business_type=BusinessType.INSERT)
async def create_inventory(
    request: Request,
    inventory_form: AddInventoryStockModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.create_inventory_services(query_db, inventory_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.get(
    '/fee/list',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:list'))],
)
async def get_fee_list(
    request: Request,
    fee_query: AstFeeItemPageQueryModel = Depends(AstFeeItemPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await AstInventoryService.get_fee_list_services(query_db, fee_query, is_page=True)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@astInventoryController.post('/fee', dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:add'))])
@Log(title='费用项目', business_type=BusinessType.INSERT)
async def add_fee(
    request: Request,
    fee_form: AddAstFeeItemModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.add_fee_services(query_db, fee_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@astInventoryController.put('/fee', dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:edit'))])
@Log(title='费用项目', business_type=BusinessType.UPDATE)
async def edit_fee(
    request: Request,
    fee_form: EditAstFeeItemModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.edit_fee_services(query_db, fee_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.put('/fee/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:edit'))])
@Log(title='费用状态', business_type=BusinessType.UPDATE)
async def change_fee_status(
    request: Request,
    fee_form: ChangeAstFeeStatusModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await AstInventoryService.change_fee_status_services(query_db, fee_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@astInventoryController.get('/fee/{fee_id}', dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:query'))])
async def get_fee_detail(request: Request, fee_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await AstInventoryService.get_fee_detail_services(query_db, fee_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@astInventoryController.delete('/fee/{fee_ids}', dependencies=[Depends(CheckUserInterfaceAuth('ast:fee:remove'))])
@Log(title='费用项目', business_type=BusinessType.DELETE)
async def delete_fee(
    request: Request,
    fee_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_form = DeleteAstFeeItemModel(feeIds=fee_ids)
    result = await AstInventoryService.delete_fee_services(query_db, delete_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
