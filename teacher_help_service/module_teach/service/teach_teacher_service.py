from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from utils.excel_util import ExcelUtil
from utils.common_util import CamelCaseUtil
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_teach.dao.teach_teacher_dao import TeachTeacherDao
from module_teach.dao.teach_base_user_dao import TeachBaseUserDao
from module_teach.entity.do.teach_teacher_do import TeachTeacher
from module_teach.entity.do.teach_base_user_do import TeachBaseUser
from module_teach.entity.vo.teach_teacher_vo import (
    TeachTeacherPageQueryModel,
    AddTeachTeacherModel,
    EditTeachTeacherModel,
    DeleteTeachTeacherModel,
    TeachTeacherResponseModel,
    TeachTeacherDetailModel,
    TeacherSubjectModel,
    TeacherGradeModel
)
from utils.pwd_util import PwdUtil
from exceptions.exception import ServiceException
from config.constant import CommonConstant
from module_admin.service.dict_service import DictDataService


class TeachTeacherService:
    """
    教师管理模块服务层
    """

    @classmethod
    async def get_teach_teacher_list_services(cls, query_db: AsyncSession, query_object: TeachTeacherPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取教师列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 教师列表信息对象
        """
        teacher_list_result = await TeachTeacherDao.get_teach_teacher_list(
            query_db, query_object, data_scope_sql, is_page
        )

        if is_page:
            rows = []
            for row in teacher_list_result.rows:
                row_data = {**row[0], 'phone': row[1].get('phone') if isinstance(row[1], dict) else ''}
                teacher_id = row[0].get('id') if isinstance(row[0], dict) else 0
                if teacher_id:
                    subject_codes = await TeachTeacherDao.get_teacher_subjects_dao(query_db, teacher_id)
                    grade_codes = await TeachTeacherDao.get_teacher_grades_dao(query_db, teacher_id)
                    subjects = []
                    for code in subject_codes:
                        label = await DictDataService.query_dict_data_info_services(query_db, 'teach_subject', code)
                        subjects.append(label if label else code)
                    grades = []
                    for code in grade_codes:
                        label = await DictDataService.query_dict_data_info_services(query_db, 'teach_grade', code)
                        grades.append(label if label else code)
                    row_data['subjects'] = subjects
                    row_data['grades'] = grades
                else:
                    row_data['subjects'] = []
                    row_data['grades'] = []
                rows.append(row_data)
            from utils.page_util import PageResponseModel
            return PageResponseModel(
                **{
                    **teacher_list_result.model_dump(by_alias=True),
                    'rows': rows
                }
            )
        else:
            result_list = []
            for row in teacher_list_result:
                row_data = {**row[0], 'phone': row[1].get('phone') if isinstance(row[1], dict) else ''}
                teacher_id = row[0].get('id') if isinstance(row[0], dict) else 0
                if teacher_id:
                    subject_codes = await TeachTeacherDao.get_teacher_subjects_dao(query_db, teacher_id)
                    grade_codes = await TeachTeacherDao.get_teacher_grades_dao(query_db, teacher_id)
                    subjects = []
                    for code in subject_codes:
                        label = await DictDataService.query_dict_data_info_services(query_db, 'teach_subject', code)
                        subjects.append(label if label else code)
                    grades = []
                    for code in grade_codes:
                        label = await DictDataService.query_dict_data_info_services(query_db, 'teach_grade', code)
                        grades.append(label if label else code)
                    row_data['subjects'] = subjects
                    row_data['grades'] = grades
                else:
                    row_data['subjects'] = []
                    row_data['grades'] = []
                result_list.append(row_data)
            return result_list

    @classmethod
    async def get_teach_teacher_detail_services(cls, query_db: AsyncSession, teacher_id: int):
        """
        获取教师详情service

        :param query_db: orm对象
        :param teacher_id: 教师ID
        :return: 教师详情信息对象
        """
        teacher_result = await TeachTeacherDao.get_teach_teacher_by_id(query_db, teacher_id)
        if not teacher_result:
            empty_data = {
                'id': 0,
                'user_id': 0,
                'teacher_name': '',
                'status': 0,
                'create_time': datetime.now(),
                'update_time': datetime.now()
            }
            return TeachTeacherDetailModel(**CamelCaseUtil.transform_result(empty_data))

        teacher_obj, base_user_obj = teacher_result
        subject_codes = await TeachTeacherDao.get_teacher_subjects_dao(query_db, teacher_id)
        grade_codes = await TeachTeacherDao.get_teacher_grades_dao(query_db, teacher_id)
        subjects = []
        for code in subject_codes:
            label = await DictDataService.query_dict_data_info_services(query_db, 'teach_subject', code)
            subjects.append(label if label else code)
        grades = []
        for code in grade_codes:
            label = await DictDataService.query_dict_data_info_services(query_db, 'teach_grade', code)
            grades.append(label if label else code)

        teacher_detail = {
            'id': teacher_obj.id,
            'user_id': teacher_obj.user_id,
            'teacher_name': teacher_obj.teacher_name,
            'nickname': teacher_obj.nickname,
            'avatar_url': teacher_obj.avatar_url,
            'id_card': teacher_obj.id_card,
            'subject_codes': subject_codes,
            'grade_codes': grade_codes,
            'subjects': subjects,
            'grades': grades,
            'qualification_cert': teacher_obj.qualification_cert,
            'work_experience': teacher_obj.work_experience,
            'introduction': teacher_obj.introduction,
            'hourly_rate': teacher_obj.hourly_rate,
            'bank_account': teacher_obj.bank_account,
            'bank_name': teacher_obj.bank_name,
            'settlement_cycle': teacher_obj.settlement_cycle,
            'status': teacher_obj.status,
            'create_time': teacher_obj.create_time,
            'update_time': teacher_obj.update_time,
            'remark': teacher_obj.remark,
            'phone': base_user_obj.phone
        }
        return TeachTeacherDetailModel(**CamelCaseUtil.transform_result(teacher_detail))

    @classmethod
    async def check_teacher_phone_unique_services(cls, query_db: AsyncSession, phone: str, teacher_id: int = None):
        """
        校验教师手机号是否唯一service

        :param query_db: orm对象
        :param phone: 手机号
        :param teacher_id: 教师ID
        :return: 校验结果
        """
        user_id = -1 if teacher_id is None else teacher_id
        base_user = await TeachBaseUserDao.get_teach_base_user_by_phone(query_db, phone)
        if base_user and base_user.id != user_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_teach_teacher_services(cls, query_db: AsyncSession, add_teacher: AddTeachTeacherModel, current_user_name: str):
        """
        新增教师service

        :param query_db: orm对象
        :param add_teacher: 新增教师对象
        :param current_user_name: 当前用户名
        :return: 新增教师校验结果
        """
        phone_unique_result = await cls.check_teacher_phone_unique_services(query_db, add_teacher.phone)
        if phone_unique_result == CommonConstant.NOT_UNIQUE:
            raise ServiceException(message='手机号已存在')
        try:
            base_user = TeachBaseUser(
                phone=add_teacher.phone,
                password_hash=PwdUtil.get_password_hash(add_teacher.password),
                user_type='0',
                status='0',
                create_by=current_user_name,
                update_by=current_user_name
            )
            base_user = await TeachBaseUserDao.add_teach_base_user(query_db, base_user)
            teacher = TeachTeacher(
                user_id=base_user.id,
                teacher_name=add_teacher.teacher_name,
                nickname=add_teacher.nickname,
                avatar_url=add_teacher.avatar_url,
                id_card=add_teacher.id_card,
                qualification_cert=add_teacher.qualification_cert,
                work_experience=add_teacher.work_experience,
                introduction=add_teacher.introduction,
                hourly_rate=add_teacher.hourly_rate,
                bank_account=add_teacher.bank_account,
                bank_name=add_teacher.bank_name,
                settlement_cycle=add_teacher.settlement_cycle,
                status=add_teacher.status,
                create_by=current_user_name,
                update_by=current_user_name,
                remark=add_teacher.remark
            )
            teacher = await TeachTeacherDao.add_teach_teacher(query_db, teacher)
            teacher_id = teacher.id
            if add_teacher.subject_codes:
                for subject_code in add_teacher.subject_codes:
                    await TeachTeacherDao.add_teacher_subject_dao(
                        query_db,
                        TeacherSubjectModel(teacherId=teacher_id, subjectCode=subject_code)
                    )
            if add_teacher.grade_codes:
                for grade_code in add_teacher.grade_codes:
                    await TeachTeacherDao.add_teacher_grade_dao(
                        query_db,
                        TeacherGradeModel(teacherId=teacher_id, gradeCode=grade_code)
                    )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_teacher_services(cls, query_db: AsyncSession, edit_teacher: EditTeachTeacherModel, current_user_name: str):
        """
        编辑教师service

        :param query_db: orm对象
        :param edit_teacher: 编辑教师对象
        :param current_user_name: 当前用户名
        :return: 编辑教师校验结果
        """
        teacher_result = await TeachTeacherDao.get_teach_teacher_by_id(query_db, edit_teacher.id)
        if not teacher_result:
            raise ServiceException(message='教师不存在')
        try:
            teacher_obj, _ = teacher_result
            if edit_teacher.teacher_name is not None:
                teacher_obj.teacher_name = edit_teacher.teacher_name
            if edit_teacher.nickname is not None:
                teacher_obj.nickname = edit_teacher.nickname
            if edit_teacher.avatar_url is not None:
                teacher_obj.avatar_url = edit_teacher.avatar_url
            if edit_teacher.id_card is not None:
                teacher_obj.id_card = edit_teacher.id_card
            if edit_teacher.qualification_cert is not None:
                teacher_obj.qualification_cert = edit_teacher.qualification_cert
            if edit_teacher.work_experience is not None:
                teacher_obj.work_experience = edit_teacher.work_experience
            if edit_teacher.introduction is not None:
                teacher_obj.introduction = edit_teacher.introduction
            if edit_teacher.hourly_rate is not None:
                teacher_obj.hourly_rate = edit_teacher.hourly_rate
            if edit_teacher.bank_account is not None:
                teacher_obj.bank_account = edit_teacher.bank_account
            if edit_teacher.bank_name is not None:
                teacher_obj.bank_name = edit_teacher.bank_name
            if edit_teacher.settlement_cycle is not None:
                teacher_obj.settlement_cycle = edit_teacher.settlement_cycle
            if edit_teacher.status is not None:
                teacher_obj.status = edit_teacher.status
            if edit_teacher.remark is not None:
                teacher_obj.remark = edit_teacher.remark
            teacher_obj.update_by = current_user_name
            await TeachTeacherDao.edit_teach_teacher(query_db, teacher_obj)
            await TeachTeacherDao.delete_teacher_subject_dao(query_db, edit_teacher.id)
            await TeachTeacherDao.delete_teacher_grade_dao(query_db, edit_teacher.id)
            if edit_teacher.subject_codes:
                for subject_code in edit_teacher.subject_codes:
                    await TeachTeacherDao.add_teacher_subject_dao(
                        query_db,
                        TeacherSubjectModel(teacherId=edit_teacher.id, subjectCode=subject_code)
                    )
            if edit_teacher.grade_codes:
                for grade_code in edit_teacher.grade_codes:
                    await TeachTeacherDao.add_teacher_grade_dao(
                        query_db,
                        TeacherGradeModel(teacherId=edit_teacher.id, gradeCode=grade_code)
                    )
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_teacher_services(cls, query_db: AsyncSession, delete_teacher: DeleteTeachTeacherModel, current_user_name: str):
        """
        删除教师service

        :param query_db: orm对象
        :param delete_teacher: 删除教师对象
        :param current_user_name: 当前用户名
        :return: 删除教师校验结果
        """
        teacher_ids = [int(id_str) for id_str in delete_teacher.ids.split(',') if id_str.strip()]
        if not teacher_ids:
            raise ServiceException(message='请选择要删除的教师')
        try:
            for teacher_id in teacher_ids:
                await TeachTeacherDao.delete_teacher_subject_dao(query_db, teacher_id)
                await TeachTeacherDao.delete_teacher_grade_dao(query_db, teacher_id)
                teacher_result = await TeachTeacherDao.get_teach_teacher_by_id(query_db, teacher_id)
                if teacher_result:
                    teacher_obj, _ = teacher_result
                    await TeachBaseUserDao.delete_teach_base_user(query_db, [teacher_obj.user_id])
            delete_count = await TeachTeacherDao.delete_teach_teacher(query_db, teacher_ids)
            await query_db.commit()
            if delete_count == 0:
                raise ServiceException(message='删除失败，教师不存在或已被删除')
        except Exception as e:
            await query_db.rollback()
            raise e

    @staticmethod
    async def export_teach_teacher_list_services(teacher_list: List):
        """
        导出教师信息service

        :param teacher_list: 教师信息列表
        :return: 教师信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'id': '教师序号',
            'teacher_name': '教师姓名',
            'phone': '手机号码',
            'teaching_subjects': '教学科目',
            'teaching_grades': '教学年级',
            'work_experience': '教学经验(年)',
            'hourly_rate': '课时费',
            'bank_account': '银行账号',
            'bank_name': '开户银行',
            'settlement_cycle': '结算周期',
            'status': '状态',
            'create_time': '创建时间'
        }

        # 处理状态映射和其他字段转换
        for item in teacher_list:
            # 状态映射 - 统一转为字符串比较
            status_value = str(item.get('status', ''))
            if status_value == '1':
                item['status'] = '正常'
            elif status_value == '2':
                item['status'] = '暂停接单'
            elif status_value == '3':
                item['status'] = '已注销'
            else:
                item['status'] = '未知'

            # 结算周期映射
            settlement_value = str(item.get('settlement_cycle', ''))
            if settlement_value == '1':
                item['settlement_cycle'] = '周结'
            elif settlement_value == '2':
                item['settlement_cycle'] = '月结'
            else:
                item['settlement_cycle'] = '未设置'

            # 处理JSON字段 - 如果是列表则转为字符串
            teaching_subjects = item.get('teaching_subjects')
            if teaching_subjects and isinstance(teaching_subjects, list):
                item['teaching_subjects'] = ', '.join(teaching_subjects)
            elif not teaching_subjects:
                item['teaching_subjects'] = ''

            teaching_grades = item.get('teaching_grades')
            if teaching_grades and isinstance(teaching_grades, list):
                item['teaching_grades'] = ', '.join(teaching_grades)
            elif not teaching_grades:
                item['teaching_grades'] = ''

        binary_data = ExcelUtil.export_list2excel(teacher_list, mapping_dict)
        return binary_data
