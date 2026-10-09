"""
老师帮 版本化 SQL 迁移脚本（最小实现，仅支持 MySQL）

迁移文件放在 sql/migrations/ 下，命名为 V<三位版本号>__<说明>.sql，例如 V002__p1_venue_time_and_card_perm.sql。
已执行的版本记录在表 sys_schema_version 中；已执行过的文件不要再修改（会校验 sha256 并提示）。

用法（在 teacher_help_service 目录下执行，读取 .env.<env> 中的数据库配置）：
    python sql/migrate.py --env=prod status      查看各版本执行状态
    python sql/migrate.py --env=prod baseline    把 V001 基线标记为已执行（新库执行完初始化 SQL 后、或存量库首次接入时执行一次）
    python sql/migrate.py --env=prod up          按版本顺序执行全部未执行的迁移
    python sql/migrate.py --env=prod up --dry-run  只打印将要执行的语句

约定：
    1. 每条语句以行尾分号结束；语句内部不要出现“行尾分号”。
    2. MySQL 的 DDL 会隐式提交，单个文件中途失败时需要人工检查后修复，再重新执行 up（成功的版本才会写入记录表）。
    3. 生产环境请保持 DB_AUTO_INIT=false（默认），表结构只通过本脚本变更。
"""

import argparse
import getpass
import glob
import hashlib
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATION_DIR = os.path.join(BASE_DIR, 'sql', 'migrations')
VERSION_TABLE = 'sys_schema_version'
BASELINE_VERSION = '001'
FILE_PATTERN = re.compile(r'^V(\d{3})__([\w\-]+)\.sql$')


def list_migrations():
    """
    按版本号顺序列出迁移文件

    :return: [(version, description, path, checksum)]
    """
    migrations = []
    for path in sorted(glob.glob(os.path.join(MIGRATION_DIR, 'V*.sql'))):
        match = FILE_PATTERN.match(os.path.basename(path))
        if not match:
            raise ValueError(f'迁移文件命名不符合 V<三位版本号>__<说明>.sql：{path}')
        with open(path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        migrations.append((match.group(1), match.group(2), path, checksum))
    versions = [item[0] for item in migrations]
    if len(versions) != len(set(versions)):
        raise ValueError('存在重复的迁移版本号')
    return migrations


def split_statements(sql_text: str):
    """
    按“行尾分号”拆分语句，忽略整行 -- 注释和空行

    :param sql_text: SQL 文件内容
    :return: 语句列表
    """
    statements = []
    buffer = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        buffer.append(line)
        if stripped.endswith(';'):
            statement = '\n'.join(buffer).strip().rstrip(';').strip()
            if statement:
                statements.append(statement)
            buffer = []
    if ''.join(buffer).strip():
        raise ValueError('迁移文件最后一条语句缺少行尾分号')
    return statements


def get_connection():
    import pymysql
    from config.env import DataBaseConfig

    if DataBaseConfig.db_type != 'mysql':
        raise SystemExit('migrate.py 目前只支持 MySQL')
    return pymysql.connect(
        host=DataBaseConfig.db_host,
        port=DataBaseConfig.db_port,
        user=DataBaseConfig.db_username,
        password=DataBaseConfig.db_password,
        database=DataBaseConfig.db_database,
        charset='utf8mb4',
        autocommit=True,
    )


def ensure_version_table(cursor):
    cursor.execute(
        f'CREATE TABLE IF NOT EXISTS {VERSION_TABLE} ('
        'version VARCHAR(10) NOT NULL PRIMARY KEY, '
        'description VARCHAR(200) NOT NULL, '
        'checksum CHAR(64) NOT NULL, '
        "applied_by VARCHAR(64) NOT NULL DEFAULT '', "
        'applied_time DATETIME NOT NULL'
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库迁移版本记录'"
    )


def get_applied(cursor):
    cursor.execute(f'SELECT version, checksum FROM {VERSION_TABLE}')
    return {row[0]: row[1] for row in cursor.fetchall()}


def record_version(cursor, version, description, checksum):
    cursor.execute(
        f'INSERT INTO {VERSION_TABLE} (version, description, checksum, applied_by, applied_time) '
        'VALUES (%s, %s, %s, %s, %s)',
        (version, description, checksum, getpass.getuser(), datetime.now()),
    )


def main():
    parser = argparse.ArgumentParser(description='老师帮版本化 SQL 迁移')
    parser.add_argument('--env', default='dev', help='运行环境，对应 .env.<env>')
    parser.add_argument('command', choices=['status', 'baseline', 'up'])
    parser.add_argument('--dry-run', action='store_true', help='只打印将要执行的语句')
    args = parser.parse_args()

    # config.env 会解析命令行参数，这里只把 --env 传给它
    os.chdir(BASE_DIR)
    sys.path.insert(0, BASE_DIR)
    sys.argv = [sys.argv[0], f'--env={args.env}']

    migrations = list_migrations()
    if args.command == 'up' and args.dry_run:
        for version, description, path, _ in migrations:
            with open(path, encoding='utf-8') as f:
                statements = split_statements(f.read())
            print(f'-- V{version} {description}：{len(statements)} 条语句')
            for statement in statements:
                print(statement + ';')
        return

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            ensure_version_table(cursor)
            applied = get_applied(cursor)
            if args.command == 'status':
                for version, description, _, checksum in migrations:
                    state = '未执行'
                    if version in applied:
                        state = '已执行' if applied[version] == checksum else '已执行(文件已被修改!)'
                    print(f'V{version} {description}: {state}')
                return
            if args.command == 'baseline':
                baseline = [item for item in migrations if item[0] == BASELINE_VERSION]
                if not baseline:
                    raise SystemExit('缺少基线文件 V001__*.sql')
                if BASELINE_VERSION in applied:
                    print('基线已存在，无需重复执行')
                    return
                version, description, _, checksum = baseline[0]
                record_version(cursor, version, description, checksum)
                print(f'已标记基线 V{version}')
                return
            if BASELINE_VERSION not in applied:
                raise SystemExit('尚未建立基线：请先按 README 初始化数据库，再执行 baseline')
            for version, description, path, checksum in migrations:
                if version in applied:
                    if applied[version] != checksum:
                        print(f'警告：V{version} 已执行但文件内容已变化，请勿修改已发布的迁移文件')
                    continue
                with open(path, encoding='utf-8') as f:
                    statements = split_statements(f.read())
                print(f'执行 V{version} {description}（{len(statements)} 条语句）')
                for statement in statements:
                    cursor.execute(statement)
                record_version(cursor, version, description, checksum)
            print('迁移完成')
    finally:
        connection.close()


if __name__ == '__main__':
    main()
