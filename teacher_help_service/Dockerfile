# 老师帮后端镜像（示例）
# 构建：docker build -t teacher-help-service ./teacher_help_service
# 配置全部通过环境变量注入（见 .env.example），镜像内不包含任何 .env.* 文件或秘钥
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=prod

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9099

# 生产环境默认 DB_AUTO_INIT=false：首次部署请先执行初始化 SQL 和 `python sql/migrate.py --env=prod baseline/up`
CMD ["python", "app.py", "--env=prod"]
