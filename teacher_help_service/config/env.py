import argparse
import os
import sys
import warnings
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import Literal, Optional


class AppSettings(BaseSettings):
    """
    应用配置
    """

    app_env: str = 'dev'
    app_name: str = 'RuoYi-FasAPI'
    app_root_path: str = '/dev-api'
    app_host: str = '0.0.0.0'
    app_port: int = 9099
    app_version: str = '1.0.0'
    app_reload: bool = True
    app_ip_location_query: bool = True
    app_same_time_login: bool = True
    # 是否开放 /docs、/redoc、/openapi.json；未设置时生产环境(APP_ENV=prod)关闭，其他环境开启
    app_docs_enabled: Optional[bool] = None


JWT_SECRET_PLACEHOLDER = 'CHANGE_ME_TO_A_RANDOM_64_HEX_SECRET'


def is_prod_env():
    """
    当前是否为生产环境（APP_ENV=prod）
    """
    return os.environ.get('APP_ENV', 'dev') == 'prod'


class JwtSettings(BaseSettings):
    """
    Jwt配置
    """

    # 不再内置真实秘钥，必须通过 .env.* 或环境变量 JWT_SECRET_KEY 设置
    jwt_secret_key: str = JWT_SECRET_PLACEHOLDER
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 1440
    jwt_redis_expire_minutes: int = 30


class DataBaseSettings(BaseSettings):
    """
    数据库配置
    """

    db_type: Literal['mysql', 'postgresql'] = 'mysql'
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    db_username: str = 'root'
    db_password: str = ''
    db_database: str = 'ruoyi-fastapi'
    db_echo: bool = False
    db_max_overflow: int = 10
    db_pool_size: int = 50
    db_pool_recycle: int = 3600
    db_pool_timeout: int = 30
    # 启动时是否自动执行 create_all 与补列 ALTER；未设置时生产环境(APP_ENV=prod)关闭，其他环境开启
    # 生产环境请使用 sql/migrations 下的版本化脚本 + sql/migrate.py 管理表结构
    db_auto_init: Optional[bool] = None

    @computed_field
    @property
    def sqlglot_parse_dialect(self) -> str:
        if self.db_type == 'postgresql':
            return 'postgres'
        return self.db_type


class BusinessRuleSettings(BaseSettings):
    """
    业务规则开关（P2）
    以下规则尚待产品确认，默认值保持当前的保守行为，仅在确认后通过环境变量调整
    """

    # 场地折扣卡折扣率口径：auto=0<r<=1 视为比例、1<r<=10 视为“几折”（默认）；ratio=只接受比例；zhe=只接受“几折”
    card_discount_rate_mode: Literal['auto', 'ratio', 'zhe'] = 'auto'
    # 预订/锁场是否必须完全落在场地的“可约时段”内；默认 false（不强制，与 P1 行为一致）
    venue_booking_require_open_time: bool = False
    # 批量锁场单次最多生成的锁场记录数（日期数 x 场地数）
    venue_lock_batch_max: int = 500


class RedisSettings(BaseSettings):
    """
    Redis配置
    """

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_username: str = ''
    redis_password: str = ''
    redis_database: int = 0


class GenSettings:
    """
    代码生成配置
    """

    author = 'insistence'
    package_name = 'module_admin.system'
    auto_remove_pre = False
    table_prefix = 'sys_'
    allow_overwrite = False

    GEN_PATH = 'vf_admin/gen_path'

    def __init__(self):
        if not os.path.exists(self.GEN_PATH):
            os.makedirs(self.GEN_PATH)


class UploadSettings:
    """
    上传配置
    """

    UPLOAD_PREFIX = '/profile'
    UPLOAD_PATH = 'vf_admin/upload_path'
    UPLOAD_MACHINE = 'A'
    # 单个上传文件大小上限（字节），默认 50MB
    UPLOAD_MAX_SIZE = 50 * 1024 * 1024
    DEFAULT_ALLOWED_EXTENSION = [
        # 图片
        'bmp',
        'gif',
        'jpg',
        'jpeg',
        'png',
        # word excel powerpoint
        'doc',
        'docx',
        'xls',
        'xlsx',
        'ppt',
        'pptx',
        'txt',
        # 压缩文件
        'rar',
        'zip',
        'gz',
        'bz2',
        # 视频格式
        'mp4',
        'avi',
        'rmvb',
        # pdf
        'pdf',
    ]
    DOWNLOAD_PATH = 'vf_admin/download_path'

    def __init__(self):
        if not os.path.exists(self.UPLOAD_PATH):
            os.makedirs(self.UPLOAD_PATH)
        if not os.path.exists(self.DOWNLOAD_PATH):
            os.makedirs(self.DOWNLOAD_PATH)


class CachePathConfig:
    """
    缓存目录配置
    """

    PATH = os.path.join(os.path.abspath(os.getcwd()), 'caches')
    PATHSTR = 'caches'


class GetConfig:
    """
    获取配置
    """

    def __init__(self):
        self.parse_cli_args()

    @lru_cache()
    def get_app_config(self):
        """
        获取应用配置
        """
        # 实例化应用配置模型
        app_settings = AppSettings()
        if app_settings.app_docs_enabled is None:
            app_settings.app_docs_enabled = not is_prod_env()
        return app_settings

    @lru_cache()
    def get_jwt_config(self):
        """
        获取Jwt配置
        """
        # 实例化Jwt配置模型
        jwt_settings = JwtSettings()
        if jwt_settings.jwt_secret_key in ('', JWT_SECRET_PLACEHOLDER):
            if is_prod_env():
                raise ValueError('生产环境必须设置 JWT_SECRET_KEY，禁止使用占位值')
            warnings.warn('JWT_SECRET_KEY 未设置，当前使用占位值，仅允许在开发环境使用', stacklevel=2)
        return jwt_settings

    @lru_cache()
    def get_database_config(self):
        """
        获取数据库配置
        """
        # 实例化数据库配置模型
        database_settings = DataBaseSettings()
        if database_settings.db_auto_init is None:
            database_settings.db_auto_init = not is_prod_env()
        return database_settings

    @lru_cache()
    def get_business_rule_config(self):
        """
        获取业务规则开关
        """
        return BusinessRuleSettings()

    @lru_cache()
    def get_redis_config(self):
        """
        获取Redis配置
        """
        # 实例化Redis配置模型
        return RedisSettings()

    @lru_cache()
    def get_gen_config(self):
        """
        获取代码生成配置
        """
        # 实例化代码生成配置
        return GenSettings()

    @lru_cache()
    def get_upload_config(self):
        """
        获取数据库配置
        """
        # 实例上传配置
        return UploadSettings()

    @staticmethod
    def parse_cli_args():
        """
        解析命令行参数
        """
        if 'uvicorn' in sys.argv[0]:
            # 使用uvicorn启动时，命令行参数需要按照uvicorn的文档进行配置，无法自定义参数
            pass
        else:
            # 使用argparse定义命令行参数
            parser = argparse.ArgumentParser(description='命令行参数')
            parser.add_argument('--env', type=str, default='', help='运行环境')
            # 解析命令行参数
            args = parser.parse_args()
            # 设置环境变量，如果未设置命令行参数，默认APP_ENV为dev
            os.environ['APP_ENV'] = args.env if args.env else 'dev'
        # 读取运行环境
        run_env = os.environ.get('APP_ENV', '')
        # 运行环境未指定时默认加载.env.dev
        env_file = '.env.dev'
        # 运行环境不为空时按命令行参数加载对应.env文件
        if run_env != '':
            env_file = f'.env.{run_env}'
        # 加载配置
        load_dotenv(env_file)


# 实例化获取配置类
get_config = GetConfig()
# 应用配置
AppConfig = get_config.get_app_config()
# Jwt配置
JwtConfig = get_config.get_jwt_config()
# 数据库配置
DataBaseConfig = get_config.get_database_config()
# Redis配置
RedisConfig = get_config.get_redis_config()
# 代码生成配置
GenConfig = get_config.get_gen_config()
# 上传配置
UploadConfig = get_config.get_upload_config()
# 业务规则开关
BusinessRuleConfig = get_config.get_business_rule_config()
