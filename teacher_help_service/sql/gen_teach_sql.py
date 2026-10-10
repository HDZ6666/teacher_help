"""
根据 SQLAlchemy 实体生成教学域建表 SQL 与 teach/ast 菜单按钮权限种子 SQL

用法（在 teacher_help_service 目录下执行，需要能 import 项目依赖，不需要连接数据库）：
    python sql/gen_teach_sql.py

输出：
    sql/teacher_help_teach_tables.sql  全部 teach_* 表的 CREATE TABLE（MySQL 方言）
    sql/teacher_help_menu.sql          teach:* / ast:* / common:file:* 菜单与按钮权限种子
"""

import ast
import glob
import os
import re
import sys
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)
sys.argv = [sys.argv[0], '--env=dev']

from sqlalchemy.dialects import mysql  # noqa: E402
from sqlalchemy.schema import CreateTable  # noqa: E402

from config.database import Base  # noqa: E402
from config.get_db import import_business_do_modules  # noqa: E402

TABLE_SQL_FILE = os.path.join(BASE_DIR, 'sql', 'teacher_help_teach_tables.sql')
MENU_SQL_FILE = os.path.join(BASE_DIR, 'sql', 'teacher_help_menu.sql')
TABLE_OPTION_PATTERN = r"^\)COMMENT=('(?:[^']|'')*') ENGINE=InnoDB CHARSET=utf8mb4$"

# 菜单ID段：5000 根目录，5001-5099 模块目录，5100 起按钮
MENU_ROOT_ID = 5000
MENU_GROUP_START_ID = 5001
MENU_BUTTON_START_ID = 5100

# 权限前缀 -> (模块名称, 路由地址)
PERM_GROUPS = [
    ('teach:student', '学员管理', 'student'),
    ('teach:parent', '家长管理', 'parent'),
    ('teach:teacher', '老师管理', 'teacher'),
    ('teach:class', '班级管理', 'class'),
    ('teach:course', '课程管理', 'course'),
    ('teach:schedule:event', '排课管理', 'schedule-event'),
    ('teach:schedule:attendance', '考勤管理', 'schedule-attendance'),
    ('teach:classRecord', '上课记录', 'class-record'),
    ('teach:card', '会员卡管理', 'card'),
    ('teach:venue', '场地管理', 'venue'),
    ('teach:comment', '课后点评', 'comment'),
    ('teach:leave', '请假管理', 'leave'),
    ('ast:item', '物品管理', 'item'),
    ('ast:inventory', '出入库管理', 'inventory'),
    ('ast:fee', '费用管理', 'fee'),
    ('common:file', '通用文件', 'file'),
]

ACTION_LABELS = {
    'list': '列表',
    'query': '查询',
    'add': '新增',
    'edit': '修改',
    'remove': '删除',
    'export': '导出',
    'import': '导入',
    'grant': '发放',
    'checkin': '签到',
    'manual': '补签',
    'stat': '统计',
    'upload': '上传',
    'download': '下载',
    'consume': '核销',
    'revoke': '撤销点名',
    'makeup': '标记已补',
    'assign': '分配跟进人/学管师',
    'follow': '跟进记录',
    'account': '报读课程变更（转课/清零/有效期/停复结课）',
    'promote': '批量升班',
    'graduate': '批量结业',
    'reschedule': '调课',
    'temp': '临时学员',
    'batch': '按周重复排课',
    'editDetail': '修改单个学员点名',
    'makeupClass': '开补课班',
    'permission': '老师权限配置',
}

# P0 之后新增的权限使用固定菜单ID（5900 起），避免插入到顺序编号中间导致已有按钮ID整体后移、
# 已分配给角色的 sys_role_menu 关系错位。新增权限请在这里追加，ID 只增不改。
PINNED_BUTTON_IDS = {
    'teach:card:consume': 5900,
    'teach:classRecord:revoke': 5901,
    'teach:schedule:event:export': 5902,
    'teach:classRecord:export': 5903,
    'teach:classRecord:makeup': 5904,
    'teach:student:assign': 5905,
    'teach:student:import': 5906,
    'teach:student:follow': 5907,
    'teach:student:account': 5908,
    'teach:class:import': 5909,
    'teach:class:promote': 5910,
    'teach:class:graduate': 5911,
    'teach:schedule:event:reschedule': 5912,
    'teach:schedule:event:temp': 5913,
    'teach:schedule:event:batch': 5914,
    'teach:classRecord:editDetail': 5915,
    'teach:classRecord:edit': 5916,
    'teach:classRecord:makeupClass': 5917,
}


def collect_perms():
    """
    扫描 Controller 中 CheckUserInterfaceAuth 使用的权限标识
    """
    files = sorted(glob.glob('module_teach/controller/*.py') + glob.glob('module_ast/controller/*.py'))
    files.append('module_admin/controller/common_controller.py')
    perms = set()
    for file_path in files:
        with open(file_path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'CheckUserInterfaceAuth' and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant):
                    perms.add(arg.value)
                elif isinstance(arg, (ast.List, ast.Tuple)):
                    perms.update(item.value for item in arg.elts if isinstance(item, ast.Constant))
    return sorted(perms)


def sql_str(value):
    if value is None:
        return 'null'
    return "'" + str(value).replace("'", "''") + "'"


def generate_table_sql():
    import_business_do_modules()
    table_doc = {}
    for mapper in Base.registry.mappers:
        doc = (mapper.class_.__doc__ or '').strip().splitlines()
        if doc:
            table_doc[mapper.local_table.name] = doc[0].strip()
    tables = [table for table in Base.metadata.sorted_tables if table.name.startswith('teach_')]
    lines = [
        '-- ----------------------------',
        '-- 老师帮 教学域（teach_*）建表语句',
        f'-- 由 sql/gen_teach_sql.py 根据 SQLAlchemy 实体生成，生成日期 {date.today().isoformat()}',
        '-- 方言：MySQL 8.x；按外键依赖顺序排列；使用 IF NOT EXISTS，可在已有库上重复执行（不会修改已存在的表）',
        '-- 修改实体后请重新执行 python sql/gen_teach_sql.py 生成，不要手工编辑本文件',
        '-- ----------------------------',
        '',
        'SET NAMES utf8mb4;',
        '',
    ]
    for table in tables:
        original_comment = table.comment
        if not table.comment and table.name in table_doc:
            table.comment = table_doc[table.name]
        table.dialect_kwargs['mysql_engine'] = 'InnoDB'
        table.dialect_kwargs['mysql_charset'] = 'utf8mb4'
        ddl = str(CreateTable(table, if_not_exists=True).compile(dialect=mysql.dialect())).strip()
        table.comment = original_comment
        lines.append('-- ----------------------------')
        lines.append(f'-- {table.name} {table_doc.get(table.name, "")}'.rstrip())
        lines.append('-- ----------------------------')
        ddl_lines = [line.replace('\t', '  ').rstrip() for line in ddl.splitlines()]
        # 不同 SQLAlchemy 版本表选项顺序不同，统一为 ENGINE/CHARSET 在前、COMMENT 在后，避免无意义的 diff
        ddl_lines = [
            re.sub(TABLE_OPTION_PATTERN, r')ENGINE=InnoDB CHARSET=utf8mb4 COMMENT=\1', line) for line in ddl_lines
        ]
        lines.append('\n'.join(ddl_lines) + ';')
        lines.append('')
    lines.extend(
        [
            '-- ----------------------------',
            '-- 已有数据库补充唯一约束（create_all 不会给已存在的表加约束，需要手工执行一次）',
            '-- 先确认没有重复点名数据：',
            '--   SELECT event_id, COUNT(*) FROM teach_class_attendance',
            '--   WHERE event_id IS NOT NULL GROUP BY event_id HAVING COUNT(*) > 1;',
            '-- 再执行：',
            '--   ALTER TABLE teach_class_attendance ADD CONSTRAINT uk_class_attendance_event UNIQUE (event_id);',
            '-- ----------------------------',
            '',
        ]
    )
    with open(TABLE_SQL_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    return [table.name for table in tables]


def menu_row(menu_id, name, parent_id, order_num, path, menu_type, perms, icon='#', remark=''):
    # 目录默认隐藏（业务页面为静态路由），按钮保持若依默认显示状态
    visible = '1' if menu_type == 'M' else '0'
    return (
        f"({menu_id}, {sql_str(name)}, {parent_id}, {order_num}, {sql_str(path)}, null, null, '', 1, 0, "
        f"'{menu_type}', '{visible}', '0', {sql_str(perms)}, {sql_str(icon)}, 'admin', sysdate(), '', null, "
        f'{sql_str(remark)})'
    )


def generate_menu_sql(perms):
    rows = [
        menu_row(
            MENU_ROOT_ID,
            '老师帮业务权限',
            0,
            90,
            'teacher-help-perm',
            'M',
            None,
            'education',
            '业务接口权限容器（PC 端业务页面为静态路由，本目录默认隐藏，仅用于角色分配按钮权限）',
        )
    ]
    group_ids = {}
    used_perms = set()
    button_id = MENU_BUTTON_START_ID
    for index, (prefix, name, path) in enumerate(PERM_GROUPS):
        group_perms = [perm for perm in perms if perm.rsplit(':', 1)[0] == prefix]
        if not group_perms:
            continue
        group_id = MENU_GROUP_START_ID + index
        group_ids[prefix] = group_id
        rows.append(menu_row(group_id, name, MENU_ROOT_ID, index + 1, path, 'M', None, '#', f'{prefix}:*'))
        sequential_perms = [perm for perm in group_perms if perm not in PINNED_BUTTON_IDS]
        pinned_perms = [perm for perm in group_perms if perm in PINNED_BUTTON_IDS]
        for order_num, perm in enumerate(sequential_perms + pinned_perms, start=1):
            action = perm.rsplit(':', 1)[1]
            if perm in PINNED_BUTTON_IDS:
                menu_id = PINNED_BUTTON_IDS[perm]
            else:
                menu_id = button_id
                button_id += 1
            rows.append(
                menu_row(menu_id, f'{name}{ACTION_LABELS.get(action, action)}', group_id, order_num, '#', 'F', perm)
            )
            used_perms.add(perm)
    unmatched = sorted(set(perms) - used_perms)
    if unmatched:
        raise ValueError(f'以下权限没有归属模块，请在 PERM_GROUPS 中补充：{unmatched}')
    lines = [
        '-- ----------------------------',
        '-- 老师帮 teach:* / ast:* / common:file:* 菜单与按钮权限种子',
        '-- 由 sql/gen_teach_sql.py 扫描 Controller 中 CheckUserInterfaceAuth 生成',
        f'-- 生成日期 {date.today().isoformat()}',
        '-- 菜单ID段 5000-5999；重复执行时按主键更新名称/权限，不影响已分配给角色的关系（sys_role_menu）',
        '-- 超级管理员拥有 *:*:*，无需分配；其他角色请在“角色管理”中勾选对应按钮',
        '-- ----------------------------',
        '',
        'insert into sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, '
        'is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, '
        'update_time, remark) values',
        ',\n'.join(rows),
        'on duplicate key update menu_name = values(menu_name), parent_id = values(parent_id), '
        'order_num = values(order_num), perms = values(perms), remark = values(remark);',
        '',
    ]
    with open(MENU_SQL_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    return len(rows)


if __name__ == '__main__':
    table_names = generate_table_sql()
    all_perms = collect_perms()
    menu_count = generate_menu_sql(all_perms)
    print(f'已生成 {TABLE_SQL_FILE}：{len(table_names)} 张表')
    print(f'已生成 {MENU_SQL_FILE}：{menu_count} 条菜单（{len(all_perms)} 个权限标识）')
