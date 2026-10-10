from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import CurrentUserModel, LoginService
from module_teach.entity.vo.teach_venue_vo import (
    AddTeachBookingModel,
    AddTeachCourtModel,
    AddTeachVenueModel,
    CancelBookingModel,
    CancelLockGroupModel,
    ChangeTeachVenueStatusModel,
    DeleteTeachCourtModel,
    DeleteTeachVenueModel,
    EditTeachCourtModel,
    EditTeachVenueModel,
    LockCourtBookingModel,
    TeachBookingGridQueryModel,
    TeachBookingPageQueryModel,
    TeachBookingQuoteQueryModel,
    TeachVenuePageQueryModel,
    VerifyBookingModel,
)
from module_teach.service.teach_venue_service import TeachVenueService
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


teachVenueController = APIRouter(prefix='/teach/venue', dependencies=[Depends(LoginService.get_current_user)])


# ======================== 场馆 ========================
@teachVenueController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:list'))]
)
async def get_venue_list(
    request: Request,
    venue_page_query: TeachVenuePageQueryModel = Depends(TeachVenuePageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachVenue')),
):
    result = await TeachVenueService.get_venue_list_services(query_db, venue_page_query, data_scope_sql, is_page=True)
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachVenueController.post('', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:add'))])
@Log(title='场馆管理', business_type=BusinessType.INSERT)
async def add_venue(
    request: Request,
    add_venue: AddTeachVenueModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.add_venue_services(query_db, add_venue, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachVenueController.put('', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='场馆管理', business_type=BusinessType.UPDATE)
async def edit_venue(
    request: Request,
    edit_venue: EditTeachVenueModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.edit_venue_services(query_db, edit_venue, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.put('/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='场馆状态', business_type=BusinessType.UPDATE)
async def change_venue_status(
    request: Request,
    status_form: ChangeTeachVenueStatusModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.change_venue_status_services(query_db, status_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.delete('/{venue_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:remove'))])
@Log(title='场馆管理', business_type=BusinessType.DELETE)
async def delete_venue(
    request: Request,
    venue_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_model = DeleteTeachVenueModel(venue_ids=venue_ids)
    result = await TeachVenueService.delete_venue_services(query_db, delete_model, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


# ======================== 场地 ========================
@teachVenueController.get('/court/list', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:list'))])
async def get_court_list(
    request: Request,
    venue_id: int | None = None,
    court_name: str | None = None,
    court_type: str | None = None,
    status: int | None = None,
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachVenueService.get_court_list_services(
        query_db, venue_id, court_name=court_name, court_type=court_type, status=status
    )
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachVenueController.post('/court', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:add'))])
@Log(title='场地管理', business_type=BusinessType.INSERT)
async def add_court(
    request: Request,
    add_court: AddTeachCourtModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.add_court_services(query_db, add_court, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachVenueController.put('/court', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='场地管理', business_type=BusinessType.UPDATE)
async def edit_court(
    request: Request,
    edit_court: EditTeachCourtModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.edit_court_services(query_db, edit_court, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.delete('/court/{court_ids}', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:remove'))])
@Log(title='场地管理', business_type=BusinessType.DELETE)
async def delete_court(
    request: Request,
    court_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    delete_model = DeleteTeachCourtModel(court_ids=court_ids)
    result = await TeachVenueService.delete_court_services(query_db, delete_model, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.get('/court/{court_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:query'))])
async def get_court_detail(request: Request, court_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachVenueService.get_court_detail_services(query_db, court_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


# ======================== 订场 / 预订 ========================
@teachVenueController.get('/booking/grid', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:list'))])
async def get_booking_grid(
    request: Request,
    grid_query: TeachBookingGridQueryModel = Depends(TeachBookingGridQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachVenueService.get_booking_grid_services(query_db, grid_query)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachVenueController.get(
    '/booking/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:list'))]
)
async def get_booking_list(
    request: Request,
    booking_page_query: TeachBookingPageQueryModel = Depends(TeachBookingPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('TeachCourtBooking')),
):
    result = await TeachVenueService.get_booking_list_services(
        query_db, booking_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')
    return ResponseUtil.success(model_content=result)


@teachVenueController.post('/booking', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:add'))])
@Log(title='代预订', business_type=BusinessType.INSERT)
async def add_booking(
    request: Request,
    add_booking: AddTeachBookingModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.add_booking_services(
        query_db, add_booking, current_user.user.user_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachVenueController.post('/booking/lock', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:add'))])
@Log(title='锁场', business_type=BusinessType.INSERT)
async def lock_court(
    request: Request,
    lock_form: LockCourtBookingModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.lock_court_services(
        query_db, lock_form, current_user.user.user_id, current_user.user.user_name
    )
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachVenueController.put('/booking/lock/cancel', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='解除锁场', business_type=BusinessType.UPDATE)
async def cancel_lock_group(
    request: Request,
    cancel_form: CancelLockGroupModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.cancel_lock_group_services(query_db, cancel_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@teachVenueController.get('/booking/quote', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:list'))])
async def get_booking_quote(
    request: Request,
    quote_query: TeachBookingQuoteQueryModel = Depends(TeachBookingQuoteQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    result = await TeachVenueService.get_booking_quote_services(query_db, quote_query)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


@teachVenueController.put('/booking/verify', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='预订核销', business_type=BusinessType.UPDATE)
async def verify_booking(
    request: Request,
    verify_form: VerifyBookingModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.verify_booking_services(query_db, verify_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.put('/booking/cancel', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:edit'))])
@Log(title='预订取消', business_type=BusinessType.UPDATE)
async def cancel_booking(
    request: Request,
    cancel_form: CancelBookingModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    result = await TeachVenueService.cancel_booking_services(query_db, cancel_form, current_user.user.user_name)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@teachVenueController.get('/booking/{booking_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:query'))])
async def get_booking_detail(request: Request, booking_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachVenueService.get_booking_detail_services(query_db, booking_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)


# ======================== 场馆详情(置于最后避免与静态路由冲突) ========================
@teachVenueController.get('/{venue_id}', dependencies=[Depends(CheckUserInterfaceAuth('teach:venue:query'))])
async def get_venue_detail(request: Request, venue_id: int, query_db: AsyncSession = Depends(get_db)):
    result = await TeachVenueService.get_venue_detail_services(query_db, venue_id)
    logger.info('获取成功')
    return ResponseUtil.success(data=result)
