# 老师帮 (Teacher Help) - 项目概览

## 📋 项目基本信息

**项目名称**: RuoYi-FastAPI (老师帮)  
**项目类型**: 教学管理系统后端服务  
**技术栈**: Python FastAPI + SQLAlchemy + Redis + APScheduler  
**数据库**: MySQL / PostgreSQL (支持双数据库)  
**运行环境**: Python 3.x + Uvicorn  
**主要端口**: 9099

---

## 🏗️ 项目架构

### 整体结构
```
teacher_help_service/
├── app.py                    # 应用入口
├── server.py                 # FastAPI 应用配置
├── requirements.txt          # 依赖管理
├── config/                   # 配置模块
├── module_admin/             # 系统管理模块
├── module_teach/             # 教学管理模块
├── module_generator/         # 代码生成模块
├── module_task/              # 任务调度模块
├── middlewares/              # 中间件
├── exceptions/               # 异常处理
├── utils/                    # 工具函数
├── sub_applications/         # 子应用
└── sql/                      # 数据库脚本
```

### 分层架构
采用标准的 **MVC + Service** 分层模式：
- **Controller**: 路由处理和请求验证
- **Service**: 业务逻辑处理
- **DAO**: 数据访问层
- **Entity**: 数据模型 (DO/VO)
- **Annotation/Aspect**: 切面和注解

---

## 🔧 核心配置

### 配置文件 (`config/env.py`)
- **AppSettings**: 应用配置 (主机、端口、版本等)
- **JwtSettings**: JWT认证配置
- **DataBaseSettings**: 数据库配置 (支持 MySQL/PostgreSQL)
- **RedisSettings**: Redis 缓存配置
- **GenSettings**: 代码生成配置
- **UploadSettings**: 文件上传配置

### 环境变量加载
- 支持 `.env.dev`, `.env.prod` 等环境文件（不入库，复制 `.env.example` 后填写真实配置）
- 通过命令行参数 `--env` 指定运行环境

---

## 📦 主要模块

### 1. **module_admin** - 系统管理模块
负责系统基础功能管理：
- **用户管理** (user_controller): 用户增删改查、权限管理
- **角色管理** (role_controller): 角色配置、权限分配
- **菜单管理** (menu_controller): 菜单树结构管理
- **部门管理** (dept_controller): 组织结构管理
- **岗位管理** (post_controller): 岗位配置
- **字典管理** (dict_controller): 系统字典维护
- **参数管理** (config_controller): 系统参数配置
- **登录认证** (login_controller): 用户登录、JWT令牌
- **验证码** (captcha_controller): 图形验证码生成
- **日志管理** (log_controller): 操作日志、登录日志
- **在线用户** (online_controller): 在线用户监控
- **定时任务** (job_controller): 任务调度管理
- **缓存监控** (cache_controller): Redis 缓存监控
- **服务器监控** (server_controller): 系统资源监控

### 2. **module_teach** - 教学管理模块
核心业务模块，处理教学相关功能：
- **教师管理** (teacher_controller): 教师信息、科目、年级
- **学生管理** (teach_student_controller): 学生档案、学习特征
- **家长管理** (teach_parent_controller): 家长信息、联系方式
- **排课管理** (teach_schedule_event_controller): 课程安排、时间表
- **考勤管理** (teach_schedule_attendance_controller): 学生考勤记录

**核心数据模型**:
- `TeachTeacher`: 教师信息表
- `TeachStudent`: 学生信息表
- `TeachParent`: 家长信息表
- `TeachScheduleEvent`: 排课事件表
- `TeachScheduleAttendance`: 考勤记录表
- `TeachBaseUser`: 基础用户表 (关联 sys_user)

### 3. **module_generator** - 代码生成模块
自动化代码生成工具：
- 支持从数据库表生成 Python/Vue/SQL 代码
- 模板系统支持自定义代码生成规则
- 生成的代码包括 Entity、DAO、Service、Controller

### 4. **module_task** - 任务调度模块
- 基于 APScheduler 的定时任务管理
- 支持 Cron 表达式配置

---

## 🔐 安全与认证

### 认证机制
- **JWT Token**: 基于 PyJWT 的令牌认证
- **密码加密**: 使用 bcrypt 进行密码哈希
- **CORS**: 跨域资源共享配置

### 权限控制
- **接口权限验证**: `CheckUserInterfaceAuth` 装饰器
- **数据权限范围**: `GetDataScope` 装饰器
- **角色权限**: 基于角色的访问控制 (RBAC)

---

## 🛠️ 工具与工具类

| 工具类 | 功能 |
|--------|------|
| `common_util.py` | 通用工具 (驼峰转换、数据处理) |
| `excel_util.py` | Excel 导入导出 |
| `pwd_util.py` | 密码加密解密 |
| `response_util.py` | 统一响应格式 |
| `page_util.py` | 分页处理 |
| `log_util.py` | 日志记录 (loguru) |
| `time_format_util.py` | 时间格式化 |
| `upload_util.py` | 文件上传处理 |
| `cron_util.py` | Cron 表达式处理 |
| `message_util.py` | 消息处理 |

---

## 📊 数据库支持

### 支持的数据库
- **MySQL**: 默认配置
- **PostgreSQL**: 通过 `db_type` 配置切换

### 数据库连接
- 使用 SQLAlchemy 异步 ORM
- 连接池配置: 池大小 50、最大溢出 10、回收时间 3600s

---

## 🚀 启动方式

### 开发环境
```bash
python app.py
```

### 生产环境
```bash
uvicorn app:app --host 0.0.0.0 --port 9099 --reload=false
```

### 指定环境
```bash
python app.py --env prod
```

---

## 📝 API 文档

- **Swagger UI**: `http://localhost:9099/docs`
- **ReDoc**: `http://localhost:9099/redoc`

---

## 🔄 生命周期事件

应用启动时执行的初始化流程:
1. 初始化数据库表结构
2. 创建 Redis 连接池
3. 初始化系统字典和参数到 Redis
4. 初始化定时任务调度器

应用关闭时:
1. 关闭 Redis 连接
2. 关闭定时任务调度器

---

## 📚 相关文档

- `doc/产品资料/老师帮-产品需求分析报告.md`: 产品需求分析
- `doc/产品资料/老师帮-产品需求调研.md`: 需求调研报告
- `doc/产品资料/老师帮-后台功能结构图.md`: 功能结构设计
- `doc/数据库设计/老师帮-数据库设计文档.md`: 数据库设计文档

---

## 🔗 依赖关键库

| 库 | 版本 | 用途 |
|----|------|------|
| FastAPI | 0.115.8 | Web 框架 |
| SQLAlchemy | 2.0.38 | ORM 框架 |
| asyncmy | 0.2.10 | MySQL 异步驱动 |
| redis | 5.2.1 | Redis 客户端 |
| APScheduler | 3.11.0 | 定时任务 |
| loguru | 0.7.3 | 日志记录 |
| Pydantic | - | 数据验证 |
| PyJWT | 2.10.1 | JWT 认证 |
| passlib | 1.7.4 | 密码加密 |

---

## 📌 项目特点

✅ 完整的 RBAC 权限系统  
✅ 支持多数据库 (MySQL/PostgreSQL)  
✅ 异步数据库操作  
✅ Redis 缓存集成  
✅ 定时任务调度  
✅ 自动代码生成  
✅ 完善的日志系统  
✅ 统一的异常处理  
✅ 中间件支持 (CORS、Gzip、追踪)  
✅ Swagger API 文档自动生成

---

**最后更新**: 2025-10-29
