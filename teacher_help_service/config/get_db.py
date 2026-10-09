import importlib
import os
from config.database import async_engine, AsyncSessionLocal, Base
from module_ast.schema import patch_ast_schema
from module_teach.schema import patch_teach_schedule_schema
from utils.log_util import logger


# 需要在 create_all 前完整注册到 Base.metadata 的业务实体包
BUSINESS_DO_PACKAGES = ['module_teach.entity.do', 'module_ast.entity.do']


def import_business_do_modules():
    """
    导入全部业务数据库实体，确保 create_all 前所有表都已注册到 Base.metadata

    :return: 已导入的模块名列表
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imported_modules = []
    for package in BUSINESS_DO_PACKAGES:
        package_dir = os.path.join(base_dir, *package.split('.'))
        for file_name in sorted(os.listdir(package_dir)):
            if file_name.endswith('_do.py'):
                module_name = f'{package}.{file_name[:-3]}'
                importlib.import_module(module_name)
                imported_modules.append(module_name)
    return imported_modules


async def get_db():
    """
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接

    :return:
    """
    async with AsyncSessionLocal() as current_db:
        yield current_db


async def init_create_table():
    """
    应用启动时初始化数据库连接

    :return:
    """
    logger.info('初始化数据库连接...')
    import_business_do_modules()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await patch_ast_schema(conn)
        await patch_teach_schedule_schema(conn)
    logger.info('数据库连接成功')
