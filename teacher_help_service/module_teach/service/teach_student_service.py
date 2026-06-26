import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_teach.dao.teach_student_dao import TeachStudentDao
from module_teach.dao.teach_parent_dao import TeachParentDao
from module_teach.entity.do.teach_student_do import TeachStudent
from module_teach.entity.vo.teach_student_vo import (
    TeachStudentPageQueryModel,
    AddTeachStudentModel,
    EditTeachStudentModel,
    DeleteTeachStudentModel,
    TeachStudentResponseModel,
    TeachStudentDetailModel
)
from utils.excel_util import ExcelUtil
from utils.common_util import CamelCaseUtil
from module_admin.entity.vo.common_vo import CrudResponseModel
from config.constant import CommonConstant
from exceptions.exception import ServiceException


class TeachStudentService:
    """
    学生管理模块服务层
    """

    @classmethod
    def calculate_age(cls, birthday: date):
        """
        根据生日计算年龄

        :param birthday: 生日
        :return: 年龄
        """
        if not birthday:
            return 0
        today = date.today()
        age = today.year - birthday.year
        if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day):
            age -= 1
        return max(0, age)

    @classmethod
    async def get_teach_student_list_services(cls, query_db: AsyncSession, query_object: TeachStudentPageQueryModel, data_scope_sql: str, is_page: bool = False):
        """
        获取学生列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 学生列表信息对象
        """
        student_list_result = await TeachStudentDao.get_teach_student_list(query_db, query_object, data_scope_sql, is_page)

        # 处理返回数据 - PageUtil已经转为字典，直接使用字典解包
        if is_page:
            # 分页结果 - rows 已经是字典列表
            rows = []
            for row in student_list_result.rows:
                # 合并字典：student, parent, base_user
                row_data = {
                    **row[0],  # student
                    'parentName': row[1].get('parentName') if isinstance(row[1], dict) else '',
                    'parentPhone': row[2].get('phone') if isinstance(row[2], dict) else ''
                }
                
                # 计算年龄
                if row_data.get('birthday'):
                    row_data['age'] = cls.calculate_age(row_data['birthday'])
                else:
                    row_data['age'] = 0

                # 处理JSON字段
                personality_traits = row_data.get('personalityTraits')
                if isinstance(personality_traits, str):
                    try:
                        row_data['personalityTraits'] = json.loads(personality_traits)
                    except:
                        row_data['personalityTraits'] = []

                interests_hobbies = row_data.get('interestsHobbies')
                if isinstance(interests_hobbies, str):
                    try:
                        row_data['interestsHobbies'] = json.loads(interests_hobbies)
                    except:
                        row_data['interestsHobbies'] = []

                rows.append(row_data)

            from utils.page_util import PageResponseModel
            return PageResponseModel(
                **{
                    **student_list_result.model_dump(by_alias=True),
                    'rows': rows
                }
            )
        else:
            # 非分页结果 - 已经是字典列表
            result_list = []
            for row in student_list_result:
                # 合并字典：student, parent, base_user
                row_data = {
                    **row[0],  # student
                    'parentName': row[1].get('parentName') if isinstance(row[1], dict) else '',
                    'parentPhone': row[2].get('phone') if isinstance(row[2], dict) else ''
                }
                
                # 计算年龄
                if row_data.get('birthday'):
                    row_data['age'] = cls.calculate_age(row_data['birthday'])
                else:
                    row_data['age'] = 0

                # 处理JSON字段
                personality_traits = row_data.get('personalityTraits')
                if isinstance(personality_traits, str):
                    try:
                        row_data['personalityTraits'] = json.loads(personality_traits)
                    except:
                        row_data['personalityTraits'] = []

                interests_hobbies = row_data.get('interestsHobbies')
                if isinstance(interests_hobbies, str):
                    try:
                        row_data['interestsHobbies'] = json.loads(interests_hobbies)
                    except:
                        row_data['interestsHobbies'] = []

                result_list.append(row_data)

            return result_list

    @classmethod
    async def get_teach_student_detail_services(cls, query_db: AsyncSession, student_id: int):
        """
        获取学生详情service

        :param query_db: orm对象
        :param student_id: 学生ID
        :return: 学生详情信息对象
        """
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, student_id)

        if not student_result:
            # 返回空模型对象，提供必填字段的默认值
            empty_data = {
                'id': 0,
                'parent_id': 0,
                'student_name': '',
                'gender': 0,
                'status': 0,
                'create_time': datetime.now(),
                'update_time': datetime.now()
            }
            return TeachStudentDetailModel(**CamelCaseUtil.transform_result(empty_data))

        # 解包对象元组
        student_obj, parent_obj, base_user_obj = student_result

        # 计算年龄
        age = cls.calculate_age(student_obj.birthday) if student_obj.birthday else 0

        # 处理JSON字段
        personality_traits = student_obj.personality_traits
        if isinstance(personality_traits, str):
            try:
                personality_traits = json.loads(personality_traits)
            except:
                personality_traits = []

        interests_hobbies = student_obj.interests_hobbies
        if isinstance(interests_hobbies, str):
            try:
                interests_hobbies = json.loads(interests_hobbies)
            except:
                interests_hobbies = []

        # 组装详情数据
        student_detail = {
            'id': student_obj.id,
            'parent_id': student_obj.parent_id,
            'student_name': student_obj.student_name,
            'gender': student_obj.gender,
            'birthday': student_obj.birthday,
            'age': age,
            'school_name': student_obj.school_name,
            'grade': student_obj.grade,
            'class_name': student_obj.class_name,
            'student_id_in_school': student_obj.student_id_in_school,
            'learning_style': student_obj.learning_style,
            'personality_traits': personality_traits,
            'learning_difficulties': student_obj.learning_difficulties,
            'interests_hobbies': interests_hobbies,
            'medical_notes': student_obj.medical_notes,
            'emergency_contact': student_obj.emergency_contact,
            'status': student_obj.status,
            'create_time': student_obj.create_time,
            'update_time': student_obj.update_time,
            'remark': student_obj.remark,
            'parent_name': parent_obj.parent_name,
            'parent_phone': base_user_obj.phone
        }

        # 使用 CamelCaseUtil 转换字段名，然后创建模型
        return TeachStudentDetailModel(**CamelCaseUtil.transform_result(student_detail))

    @classmethod
    async def add_teach_student_services(cls, query_db: AsyncSession, add_student: AddTeachStudentModel, current_user_name: str):
        """
        新增学生service

        :param query_db: orm对象
        :param add_student: 新增学生对象
        :param current_user_name: 当前用户名
        :return: 新增学生校验结果
        """
        parent = await TeachParentDao.get_teach_parent_by_id(query_db, add_student.parent_id)
        if not parent:
            raise ServiceException(message='关联的家长不存在')
        try:
            student = TeachStudent(
                parent_id=add_student.parent_id,
                student_name=add_student.student_name,
                gender=add_student.gender,
                birthday=add_student.birthday,
                school_name=add_student.school_name,
                grade=add_student.grade,
                class_name=add_student.class_name,
                student_id_in_school=add_student.student_id_in_school,
                learning_style=add_student.learning_style,
                personality_traits=json.dumps(add_student.personality_traits, ensure_ascii=False) if add_student.personality_traits else None,
                learning_difficulties=add_student.learning_difficulties,
                interests_hobbies=json.dumps(add_student.interests_hobbies, ensure_ascii=False) if add_student.interests_hobbies else None,
                medical_notes=add_student.medical_notes,
                emergency_contact=add_student.emergency_contact,
                status=add_student.status,
                create_by=current_user_name,
                update_by=current_user_name,
                remark=add_student.remark
            )
            await TeachStudentDao.add_teach_student(query_db, student)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_teach_student_services(cls, query_db: AsyncSession, edit_student: EditTeachStudentModel, current_user_name: str):
        """
        编辑学生service

        :param query_db: orm对象
        :param edit_student: 编辑学生对象
        :param current_user_name: 当前用户名
        :return: 编辑学生校验结果
        """
        student_result = await TeachStudentDao.get_teach_student_by_id(query_db, edit_student.id)
        if not student_result:
            raise ServiceException(message='学生不存在')
        try:
            student_obj, _, _ = student_result
            if edit_student.student_name is not None:
                student_obj.student_name = edit_student.student_name
            if edit_student.gender is not None:
                student_obj.gender = edit_student.gender
            if edit_student.birthday is not None:
                student_obj.birthday = edit_student.birthday
            if edit_student.school_name is not None:
                student_obj.school_name = edit_student.school_name
            if edit_student.grade is not None:
                student_obj.grade = edit_student.grade
            if edit_student.class_name is not None:
                student_obj.class_name = edit_student.class_name
            if edit_student.student_id_in_school is not None:
                student_obj.student_id_in_school = edit_student.student_id_in_school
            if edit_student.learning_style is not None:
                student_obj.learning_style = edit_student.learning_style
            if edit_student.personality_traits is not None:
                student_obj.personality_traits = json.dumps(edit_student.personality_traits, ensure_ascii=False)
            if edit_student.learning_difficulties is not None:
                student_obj.learning_difficulties = edit_student.learning_difficulties
            if edit_student.interests_hobbies is not None:
                student_obj.interests_hobbies = json.dumps(edit_student.interests_hobbies, ensure_ascii=False)
            if edit_student.medical_notes is not None:
                student_obj.medical_notes = edit_student.medical_notes
            if edit_student.emergency_contact is not None:
                student_obj.emergency_contact = edit_student.emergency_contact
            if edit_student.status is not None:
                student_obj.status = edit_student.status
            if edit_student.remark is not None:
                student_obj.remark = edit_student.remark
            student_obj.update_by = current_user_name
            await TeachStudentDao.edit_teach_student(query_db, student_obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_teach_student_services(cls, query_db: AsyncSession, delete_student: DeleteTeachStudentModel, current_user_name: str):
        """
        删除学生service

        :param query_db: orm对象
        :param delete_student: 删除学生对象
        :param current_user_name: 当前用户名
        :return: 删除学生校验结果
        """
        student_ids = [int(id_str) for id_str in delete_student.ids.split(',') if id_str.strip()]
        if not student_ids:
            raise ServiceException(message='请选择要删除的学生')
        try:
            delete_count = await TeachStudentDao.delete_teach_student(query_db, student_ids)
            await query_db.commit()
            if delete_count == 0:
                raise ServiceException(message='删除失败，学生不存在或已被删除')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def check_student_name_unique_services(cls, query_db: AsyncSession, student_name: str, parent_id: int, student_id: int = None):
        """
        校验学生姓名在同一家长下是否唯一service

        :param query_db: orm对象
        :param student_name: 学生姓名
        :param parent_id: 家长ID
        :param student_id: 学生ID
        :return: 校验结果
        """
        is_unique = await TeachStudentDao.check_student_name_unique(query_db, student_name, parent_id, student_id)
        return CommonConstant.UNIQUE if is_unique else CommonConstant.NOT_UNIQUE

    @staticmethod
    async def export_teach_student_list_services(student_list: List):
        """
        导出学生信息service

        :param student_list: 学生信息列表
        :return: 学生信息对应excel的二进制数据
        """
        # 创建表头
        header_list = [
            '学生ID', '学生姓名', '性别', '生日', '年龄', '家长姓名',
            '就读学校', '年级', '班级', '学号', '学习风格',
            '性格特点', '学习困难点', '兴趣爱好', '医疗备注',
            '紧急联系人', '状态', '备注', '创建时间'
        ]

        # 创建数据行
        data_list = []
        for student in student_list:
            # 性别名称映射 - 统一转为字符串比较
            gender_value = str(student.get('gender', ''))
            if gender_value == '0':
                gender_name = '未知'
            elif gender_value == '1':
                gender_name = '男'
            elif gender_value == '2':
                gender_name = '女'
            else:
                gender_name = '未知'

            # 状态名称映射（0在读 1休学 2转学 3毕业，与库/DO编码对齐）
            status_value = str(student.get('status', ''))
            if status_value == '0':
                status_name = '在读'
            elif status_value == '1':
                status_name = '休学'
            elif status_value == '2':
                status_name = '转学'
            elif status_value == '3':
                status_name = '毕业'
            else:
                status_name = '未知'

            # 学习风格名称映射
            learning_style_value = student.get('learning_style')
            if learning_style_value == 1:
                learning_style_name = '视觉型'
            elif learning_style_value == 2:
                learning_style_name = '听觉型'
            elif learning_style_value == 3:
                learning_style_name = '动觉型'
            else:
                learning_style_name = '未知'

            # 处理JSON字段
            personality_traits = student.get('personality_traits', [])
            personality_traits_str = ', '.join(personality_traits) if isinstance(personality_traits, list) else str(personality_traits or '')

            interests_hobbies = student.get('interests_hobbies', [])
            interests_hobbies_str = ', '.join(interests_hobbies) if isinstance(interests_hobbies, list) else str(interests_hobbies or '')

            # 计算年龄
            age = ''
            if student.get('birthday'):
                try:
                    birthday = student['birthday']
                    if isinstance(birthday, str):
                        from datetime import datetime
                        birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - birthday.year
                    if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day):
                        age -= 1
                except:
                    age = ''

            data_row = [
                student.get('id', ''),
                student.get('student_name', ''),
                gender_name,
                student.get('birthday', ''),
                age,
                student.get('parent_name', ''),
                student.get('school_name', ''),
                student.get('grade', ''),
                student.get('class_name', ''),
                student.get('student_id_in_school', ''),
                learning_style_name,
                personality_traits_str,
                student.get('learning_difficulties', ''),
                interests_hobbies_str,
                student.get('medical_notes', ''),
                student.get('emergency_contact', ''),
                status_name,
                student.get('remark', ''),
                student.get('create_time', '')
            ]
            data_list.append(data_row)

        binary_data = ExcelUtil.export_excel_data(header_list, data_list, '学生信息')
        return binary_data
