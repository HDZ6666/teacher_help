from config.database import async_engine, AsyncSessionLocal, Base
from module_ast.schema import patch_ast_schema
from module_teach.schema import patch_teach_schedule_schema
from utils.log_util import logger


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
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await patch_ast_schema(conn)
        await patch_teach_schedule_schema(conn)
    logger.info('数据库连接成功')
