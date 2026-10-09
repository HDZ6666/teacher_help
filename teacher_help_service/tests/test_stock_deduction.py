"""
库存扣减（P0）：行锁读取 + 条件更新，禁止负库存
"""

from datetime import date


from tests.helpers import raises_service
from module_ast.dao.ast_inventory_dao import AstInventoryDao
from module_ast.entity.do.ast_item_do import AstItem
from module_ast.entity.do.ast_item_sku_do import AstItemSku
from module_ast.service.ast_inventory_service import AstInventoryService


async def make_sku(db, stock: int):
    item = AstItem(item_name='测试物品', item_type=1)
    db.add(item)
    await db.flush()
    sku = AstItemSku(item_id=item.id, sku_name='默认', stock=stock, available_stock=stock)
    db.add(sku)
    await db.flush()
    await db.commit()
    return sku.id


async def change(db, sku_id, quantity):
    return await AstInventoryService.apply_stock_change(
        db,
        sku_id=sku_id,
        quantity=quantity,
        business_type='receive',
        source_type='test',
        source_id=None,
        related_type=None,
        related_name=None,
        operator_name='tester',
        record_date=date.today(),
        create_by='tester',
    )


async def test_stock_deduct_until_zero_then_reject(db):
    sku_id = await make_sku(db, 3)
    record = await change(db, sku_id, -2)
    assert (record.stock_before, record.stock_after) == (3, 1)
    record = await change(db, sku_id, -1)
    assert record.stock_after == 0
    await db.commit()
    with raises_service('库存不足'):
        await change(db, sku_id, -1)


async def test_conditional_update_rejects_stale_or_negative(db):
    sku_id = await make_sku(db, 5)
    # 读取到的库存已过期（被其他事务改过）时不更新
    assert await AstInventoryDao.update_item_sku_stock_dao(db, sku_id, 4, 3, {}) == 0
    # 更新后为负数时不更新
    assert await AstInventoryDao.update_item_sku_stock_dao(db, sku_id, 5, -1, {}) == 0
    assert await AstInventoryDao.update_item_sku_stock_dao(db, sku_id, 5, 2, {}) == 1
