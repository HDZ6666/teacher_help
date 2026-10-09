"""
应用配置与路由（P1）：生产环境关闭接口文档、默认不自动建表；P1 新接口已注册
"""

import sys

from config.env import GetConfig


def build_config(monkeypatch, env: str):
    # GetConfig 会把 --env 写入 APP_ENV，先 setenv 让 monkeypatch 在用例结束后还原
    monkeypatch.setenv('APP_ENV', 'test')
    monkeypatch.setattr(sys, 'argv', [sys.argv[0], f'--env={env}'])
    return GetConfig()


def test_prod_defaults_disable_docs_and_auto_init(monkeypatch):
    monkeypatch.delenv('APP_DOCS_ENABLED', raising=False)
    monkeypatch.delenv('DB_AUTO_INIT', raising=False)
    config = build_config(monkeypatch, 'prod')
    assert config.get_app_config().app_docs_enabled is False
    assert config.get_database_config().db_auto_init is False


def test_dev_defaults_keep_docs_and_auto_init(monkeypatch):
    monkeypatch.delenv('APP_DOCS_ENABLED', raising=False)
    monkeypatch.delenv('DB_AUTO_INIT', raising=False)
    config = build_config(monkeypatch, 'dev')
    assert config.get_app_config().app_docs_enabled is True
    assert config.get_database_config().db_auto_init is True


def test_explicit_flags_override_env_default(monkeypatch):
    monkeypatch.setenv('APP_DOCS_ENABLED', 'true')
    monkeypatch.setenv('DB_AUTO_INIT', 'true')
    config = build_config(monkeypatch, 'prod')
    assert config.get_app_config().app_docs_enabled is True
    assert config.get_database_config().db_auto_init is True


def test_routes_registered():
    from server import app

    paths = {getattr(route, 'path', '') for route in app.routes}
    for path in [
        '/teach/card/grant/consume',
        '/teach/venue/booking/list',
        '/teach/leave/approve',
        '/teach/comment/list',
        '/teach/class/{class_id}/attendance',
    ]:
        assert path in paths, path
