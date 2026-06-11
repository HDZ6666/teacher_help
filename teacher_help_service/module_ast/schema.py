from sqlalchemy import text
from config.env import DataBaseConfig
from utils.log_util import logger


async def patch_ast_schema(conn):
    """
    Backfill small module-owned schema changes for existing deployments.
    """
    if DataBaseConfig.db_type != 'mysql':
        return

    async def has_column(table_name: str, column_name: str):
        result = await conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table_name
                  AND COLUMN_NAME = :column_name
                """
            ),
            {'table_name': table_name, 'column_name': column_name},
        )
        return (result.scalar() or 0) > 0

    async def add_column_if_missing(table_name: str, column_name: str, column_sql: str):
        if await has_column(table_name, column_name):
            return
        await conn.execute(text(f'ALTER TABLE `{table_name}` ADD COLUMN {column_sql}'))
        logger.info(f'已补齐字段 {table_name}.{column_name}')

    await add_column_if_missing(
        'ast_item',
        'enable_stock',
        "`enable_stock` SMALLINT DEFAULT 1 COMMENT '是否开启库存(0=关闭 1=开启)'",
    )
    await add_column_if_missing(
        'ast_item',
        'warning_stock',
        "`warning_stock` INT DEFAULT 0 COMMENT '库存预警数量'",
    )
    await add_column_if_missing(
        'ast_item',
        'online_sale',
        "`online_sale` SMALLINT DEFAULT 0 COMMENT '线上售卖状态(0=关闭 1=开启)'",
    )
    await add_column_if_missing(
        'ast_fee_item',
        'online_sale',
        "`online_sale` SMALLINT DEFAULT 0 COMMENT '线上售卖状态(0=关闭 1=开启)'",
    )
