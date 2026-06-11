import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.dao.teach_parent_dao import TeachParentDao
from module_teach.dao.teach_base_user_dao import TeachBaseUserDao
from module_teach.entity.do.teach_parent_do import TeachParent
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.vo.teach_parent_vo import (
    TeachParentPageQueryModel,
    AddTeachParentModel,
    EditTeachParentModel,
    DeleteTeachParentModel,
    TeachParentResponseModel,
    TeachParentDetailModel
)
from utils.pwd_util import PwdUtil
from utils.excel_util import ExcelUtil
from utils.common_util import CamelCaseUtil
from module_admin.entity.vo.common_vo import CrudResponseModel
from config.constant import CommonConstant
from exceptions.exception import ServiceException


class TeachParentService:
    """
    家长业务逻辑层 - 处理家长相关的业务逻辑
    """

    @classmethod
    async def get_teach_parent_list_services(cls, query_db: AsyncSession, query_object: TeachParentPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取家长分页列表service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 家长列表信息对象
        """
        parent_list_result = await TeachParentDao.get_teach_parent_list(query_db, query_object, data_scope_sql, is_page)

        # 处理返回数据 - PageUtil已经转为字典，直接使用字典解包
        if is_page:
            # 分页结果 - rows 已经是字典列表
            rows = [{**row[0], 'phone': row[1].get('phone') if isinstance(row[1], dict) else ''} for row in parent_list_result.rows]

            from utils.page_util import PageResponseModel
            return PageResponseModel(
                **{
                    **parent_list_result.model_dump(by_alias=True),
                    'rows': rows
                }
            )
        else:
            # 非分页结果 - 已经是字典列表
            result_list = [{**row[0], 'phone': row[1].get('phone') if isinstance(row[1], dict) else ''} for row in parent_list_result]
            return result_list

    @classmethod
    async def get_teach_parent_detail_services(cls, query_db: AsyncSession, parent_id: int):
        """
        获取家长详情service

        :param query_db: orm对象
        :param parent_id: 家长ID
        :return: 家长详情信息对象
        """
        parent_result = await TeachParentDao.get_teach_parent_by_id(query_db, parent_id)

        if not parent_result:
            # 返回空模型对象，提供必填字段的默认值
            empty_data = {
                'id': 0,
                'user_id': 0,
                'parent_name': '',
                'status': 0,
                'create_time': datetime.now(),
                'update_time': datetime.now()
            }
            return TeachParentDetailModel(**CamelCaseUtil.transform_result(empty_data))
        
        # 解包对象元组
        parent_obj, base_user_obj = parent_result

        # 组装详情数据
        parent_detail = {
            'id': parent_obj.id,
            'user_id': parent_obj.user_id,
            'parent_name': parent_obj.parent_name,
            'nickname': parent_obj.nickname,
            'avatar_url': parent_obj.avatar_url,
            'wechat_id': parent_obj.wechat_id,
            'emergency_contact': parent_obj.emergency_contact,
            'address': parent_obj.address,
            'occupation': parent_obj.occupation,
            'education_level': parent_obj.education_level,
            'family_income_range': parent_obj.family_income_range,
            'payment_preference': parent_obj.payment_preference,
            'status': parent_obj.status,
            'create_time': parent_obj.create_time,
            'update_time': parent_obj.update_time,
            'remark': parent_obj.remark,
            'phone': base_user_obj.phone
        }

        # 使用 CamelCaseUtil 转换字段名，然后创建模型
        return TeachParentDetailModel(**CamelCaseUtil.transform_result(parent_detail))

    @classmethod
    async def add_teach_parent_services(cls, query_db: AsyncSession, add_parent: AddTeachParentModel, current_user_name: str):
        """
        新增家长service

        :param query_db: orm对象
        :param add_parent: 新增家长对象
        :param current_user_name: 当前用户名
        :return: 新增家长校验结果
        """
        phone_unique_result = await cls.check_parent_phone_unique_services(query_db, add_parent.phone)
        if phone_unique_result == CommonConstant.NOT_UNIQUE:
            raise ServiceException(message='手机号已存在')
        try:
            base_user = TeachBaseUser(
                phone=add_parent.phone,
                password_hash=PwdUtil.get_password_hash(add_parent.password),
                user_type=2,
                status=1,
                create_by=current_user_name,
                update_by=current_user_name
            )
            base_user = await TeachBaseUserDao.add_teach_base_user(query_db, base_user)
            parent = TeachParent(
                user_id=base_user.id,
                parent_name=add_parent.parent_name,
                nickname=add_parent.nickname,
                avatar_url=add_parent.avatar_url,
                wechat_id=add_parent.wechat_id,
                emergency_contact=add_parent.emergency_contact,
                address=add_parent.address,
                occupation=add_parent.occupation,
                education_level=add_parent.education_level,
                family_income_range=add_parent.family_income_range,
                payment_preference=add_parent.payment_preference,
                status=add_parent.status,
                create_by=current_user_name,
                update_by=current_user_name,
                remark=add_parent.remark
            )
            await TeachParentDao.add_teach_parent(query_db, parent)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_parent_services(cls, query_db: AsyncSession, edit_parent: EditTeachParentModel, current_user_name: str):
        """
        编辑家长service

        :param query_db: orm对象
        :param edit_parent: 编辑家长对象
        :param current_user_name: 当前用户名
        :return: 编辑家长校验结果
        """
        parent_result = await TeachParentDao.get_teach_parent_by_id(query_db, edit_parent.id)
        if not parent_result:
            raise ServiceException(message='家长不存在')

        try:
            parent_obj, _ = parent_result
            if edit_parent.parent_name is not None:
                parent_obj.parent_name = edit_parent.parent_name
            if edit_parent.nickname is not None:
                parent_obj.nickname = edit_parent.nickname
            if edit_parent.avatar_url is not None:
                parent_obj.avatar_url = edit_parent.avatar_url
            if edit_parent.wechat_id is not None:
                parent_obj.wechat_id = edit_parent.wechat_id
            if edit_parent.emergency_contact is not None:
                parent_obj.emergency_contact = edit_parent.emergency_contact
            if edit_parent.address is not None:
                parent_obj.address = edit_parent.address
            if edit_parent.occupation is not None:
                parent_obj.occupation = edit_parent.occupation
            if edit_parent.education_level is not None:
                parent_obj.education_level = edit_parent.education_level
            if edit_parent.family_income_range is not None:
                parent_obj.family_income_range = edit_parent.family_income_range
            if edit_parent.payment_preference is not None:
                parent_obj.payment_preference = edit_parent.payment_preference
            if edit_parent.status is not None:
                parent_obj.status = edit_parent.status
            if edit_parent.remark is not None:
                parent_obj.remark = edit_parent.remark
            parent_obj.update_by = current_user_name
            await TeachParentDao.edit_teach_parent(query_db, parent_obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_parent_services(cls, query_db: AsyncSession, delete_parent: DeleteTeachParentModel, current_user_name: str):
        """
        删除家长service

        :param query_db: orm对象
        :param delete_parent: 删除家长对象
        :param current_user_name: 当前用户名
        :return: 删除家长校验结果
        """
        parent_ids = [int(id_str) for id_str in delete_parent.ids.split(',') if id_str.strip()]
        if not parent_ids:
            raise ServiceException(message='请选择要删除的家长')
        try:
            delete_count = await TeachParentDao.delete_teach_parent(query_db, parent_ids)
            for parent_id in parent_ids:
                parent_result = await TeachParentDao.get_teach_parent_by_id(query_db, parent_id)
                if parent_result:
                    parent_obj, _ = parent_result
                    await TeachBaseUserDao.delete_teach_base_user(query_db, [parent_obj.user_id])
            await query_db.commit()
            if delete_count == 0:
                raise ServiceException(message='删除失败，家长不存在或已被删除')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def check_parent_phone_unique_services(cls, query_db: AsyncSession, phone: str, parent_id: int = None):
        """
        校验家长手机号是否唯一service

        :param query_db: orm对象
        :param phone: 手机号
        :param parent_id: 家长ID
        :return: 校验结果
        """
        is_unique = await TeachBaseUserDao.check_teach_base_user_phone_unique(query_db, phone, parent_id)
        return CommonConstant.UNIQUE if is_unique else CommonConstant.NOT_UNIQUE

    @staticmethod
    async def export_teach_parent_list_services(parent_list: List):
        """
        导出家长信息service

        :param parent_list: 家长信息列表
        :return: 家长信息对应excel的二进制数据
        """
        # 创建表头
        header_list = [
            '家长ID', '家长姓名', '手机号', '昵称', '微信号',
            '紧急联系电话', '家庭住址', '职业', '学历',
            '家庭收入范围', '付费偏好', '状态', '备注', '创建时间'
        ]

        # 创建数据行
        data_list = []
        for parent in parent_list:
            # 状态名称映射 - 统一转为字符串比较
            status_value = str(parent.get('status', ''))
            if status_value == '1':
                status_name = '正常'
            elif status_value == '2':
                status_name = '暂停'
            elif status_value == '3':
                status_name = '已注销'
            else:
                status_name = '未知'

            # 家庭收入范围名称映射
            income_value = parent.get('family_income_range')
            if income_value == 1:
                income_range_name = '5k以下'
            elif income_value == 2:
                income_range_name = '5-10k'
            elif income_value == 3:
                income_range_name = '10-20k'
            elif income_value == 4:
                income_range_name = '20k以上'
            else:
                income_range_name = '未知'

            # 付费偏好名称映射
            payment_value = parent.get('payment_preference')
            if payment_value == 1:
                payment_preference_name = '按课时'
            elif payment_value == 2:
                payment_preference_name = '包月'
            elif payment_value == 3:
                payment_preference_name = '包季'
            elif payment_value == 4:
                payment_preference_name = '包年'
            else:
                payment_preference_name = '未知'

            data_row = [
                parent.get('id', ''),
                parent.get('parent_name', ''),
                parent.get('phone', ''),
                parent.get('nickname', ''),
                parent.get('wechat_id', ''),
                parent.get('emergency_contact', ''),
                parent.get('address', ''),
                parent.get('occupation', ''),
                parent.get('education_level', ''),
                income_range_name,
                payment_preference_name,
                status_name,
                parent.get('remark', ''),
                parent.get('create_time', '')
            ]
            data_list.append(data_row)

        binary_data = ExcelUtil.export_excel_data(header_list, data_list, '家长信息')
        return binary_data
