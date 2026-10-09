"""
测试公共配置：使用 aiosqlite 临时库，不依赖 MySQL / Redis

说明：SQLite 会忽略 SELECT ... FOR UPDATE，因此这里验证的是业务判重、条件更新与状态流转逻辑；
真正的行锁行为需要在 MySQL 上验证（见 doc/P1修复记录-2026-10-09.md）。
"""

import os
import sys
from datetime import date, datetime, timedelta

import pytest
import pytest_asyncio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)
# config.env 会用 argparse 解析命令行，测试时只保留 --env 参数，避免与 pytest 参数冲突
sys.argv = [sys.argv[0], '--env=test']

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from config.database import Base  # noqa: E402
from config.get_db import import_business_do_modules  # noqa: E402

import_business_do_modules()


@pytest_asyncio.fixture
async def engine(tmp_path):
    test_engine = create_async_engine(f'sqlite+aiosqlite:///{tmp_path / "test.db"}')
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as session:
        yield session


class Factory:
    """
    最小测试数据工厂
    """

    def __init__(self, db):
        self.db = db
        self.seq = 0

    def next(self):
        self.seq += 1
        return self.seq

    async def add(self, obj):
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def student(self, name: str):
        from module_teach.entity.do.teach_base_user_do import TeachBaseUser
        from module_teach.entity.do.teach_parent_do import TeachParent
        from module_teach.entity.do.teach_student_do import TeachStudent

        n = self.next()
        user = await self.add(TeachBaseUser(phone=f'1380000{n:04d}', password_hash='x', user_type='1'))
        parent = await self.add(TeachParent(user_id=user.id, parent_name=f'{name}家长'))
        return await self.add(TeachStudent(parent_id=parent.id, student_name=name))

    async def teacher(self, name: str):
        from module_teach.entity.do.teach_base_user_do import TeachBaseUser
        from module_teach.entity.do.teach_teacher_do import TeachTeacher

        n = self.next()
        user = await self.add(TeachBaseUser(phone=f'1390000{n:04d}', password_hash='x', user_type='0'))
        return await self.add(TeachTeacher(user_id=user.id, teacher_name=name))

    async def course_account(self, student, remaining: int, course_id: int = 1):
        from module_teach.entity.do.teach_enrollment_order_do import TeachStudentCourseAccount

        return await self.add(
            TeachStudentCourseAccount(
                student_id=student.id,
                course_id=course_id,
                course_name='测试课程',
                order_id=1,
                order_item_id=1,
                purchased_quantity=remaining,
                remaining_quantity=remaining,
            )
        )

    async def class_with_students(self, students_with_accounts):
        from module_teach.entity.do.teach_class_do import TeachClass, TeachClassStudent

        class_obj = await self.add(TeachClass(class_name='测试班', course_id=1, course_name='测试课程'))
        for student, account in students_with_accounts:
            await self.add(
                TeachClassStudent(
                    class_id=class_obj.id,
                    student_id=student.id,
                    student_name=student.student_name,
                    course_account_id=account.id if account else None,
                    status=1,
                    del_flag=0,
                )
            )
        return class_obj

    async def event(self, class_obj, student_ids, event_date: date | None = None):
        from module_teach.entity.do.teach_schedule_attendance_do import TeachScheduleAttendance
        from module_teach.entity.do.teach_schedule_event_do import TeachScheduleEvent

        event_date = event_date or date.today()
        start = datetime.combine(event_date, datetime.min.time()) + timedelta(hours=9)
        teacher = await self.teacher('王老师')
        event = await self.add(
            TeachScheduleEvent(
                teacher_id=teacher.id,
                class_id=class_obj.id,
                class_name=class_obj.class_name,
                course_id=class_obj.course_id,
                course_name=class_obj.course_name,
                start_time=start,
                end_time=start + timedelta(hours=1),
                event_date=event_date,
            )
        )
        for student_id in student_ids:
            await self.add(TeachScheduleAttendance(event_id=event.id, student_id=student_id, status=0))
        return event


@pytest.fixture
def factory(db):
    return Factory(db)
