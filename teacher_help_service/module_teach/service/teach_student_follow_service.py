from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import ServiceException
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.dao.teach_student_follow_dao import TeachStudentFollowDao
from module_teach.entity.do.teach_student_follow_do import TeachStudentFollow
from module_teach.entity.vo.teach_student_account_vo import TeachStudentFollowModel, TeachStudentFollowPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel


class TeachStudentFollowService:
    """
    学员跟进记录服务层（P3）
    """

    FOLLOW_TYPE_LABELS = {'phone': '电话', 'wechat': '微信', 'visit': '面谈', 'other': '其他'}

    @classmethod
    def format_row(cls, follow: TeachStudentFollow):
        row = CamelCaseUtil.transform_result(follow)
        row['followTypeName'] = cls.FOLLOW_TYPE_LABELS.get(follow.follow_type, follow.follow_type)
        return row

    @classmethod
    async def get_follow_list_services(cls, query_db: AsyncSession, query_object: TeachStudentFollowPageQueryModel):
        rows, total = await TeachStudentFollowDao.get_follow_list(query_db, query_object)
        return PageResponseModel(
            rows=[cls.format_row(row) for row in rows],
            pageNum=query_object.page_num,
            pageSize=query_object.page_size,
            total=total,
            hasNext=total > query_object.page_num * query_object.page_size,
        )

    @classmethod
    async def resolve_follow_user(cls, query_db: AsyncSession, user_id: int | None, current_user):
        if not user_id or user_id == current_user.user_id:
            return current_user.user_id, current_user.nick_name or current_user.user_name
        user = (
            (await query_db.execute(select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == '0')))
            .scalars()
            .first()
        )
        if not user:
            raise ServiceException(message='跟进人不存在')
        if user.status != '0':
            raise ServiceException(message='跟进人账号已停用')
        return user.user_id, user.nick_name or user.user_name

    @classmethod
    async def save_follow_services(cls, query_db: AsyncSession, page_object: TeachStudentFollowModel, current_user):
        """
        新增/修改跟进记录；current_user 为登录用户 user 对象（user_id/user_name/nick_name）
        """
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, page_object.student_id)
        if not student_result:
            raise ServiceException(message='学员不存在')
        student = student_result[0]
        follow_time = page_object.follow_time or datetime.now()
        if page_object.next_follow_date and page_object.next_follow_date < follow_time.date():
            raise ServiceException(message='下次跟进日期不能早于本次跟进日期')
        user_id, user_name = await cls.resolve_follow_user(query_db, page_object.follow_user_id, current_user)
        try:
            if page_object.id:
                follow = await TeachStudentFollowDao.get_follow_by_id(query_db, page_object.id)
                if not follow:
                    raise ServiceException(message='跟进记录不存在')
                if follow.student_id != student.id:
                    raise ServiceException(message='跟进记录不属于该学员')
            else:
                follow = TeachStudentFollow(student_id=student.id, create_by=current_user.user_name)
            follow.student_name = student.student_name
            follow.follow_type = page_object.follow_type
            follow.follow_stage = page_object.follow_stage
            follow.content = page_object.content
            follow.follow_time = follow_time
            follow.next_follow_date = page_object.next_follow_date
            follow.follow_user_id = user_id
            follow.follow_user_name = user_name
            follow.update_by = current_user.user_name
            follow.update_time = datetime.now()
            if not page_object.id:
                await TeachStudentFollowDao.add_follow(query_db, follow)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='保存成功', result={'id': follow.id})
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_follow_services(cls, query_db: AsyncSession, follow_ids: str, current_user_name: str):
        ids = [int(item) for item in follow_ids.split(',') if item.strip().isdigit()]
        if not ids:
            raise ServiceException(message='请选择要删除的跟进记录')
        try:
            count = await TeachStudentFollowDao.delete_follows(query_db, ids, current_user_name)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message=f'删除成功{count}条')
        except Exception as e:
            await query_db.rollback()
            raise e
