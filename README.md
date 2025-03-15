# 项目说明

本项目支持 Django 5.1.7 版本。

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 文件中设置以下变量：

- **运行的域名**: `DJANGO_ALLOWED_HOSTS`
- **是否开启 DEBUG**: `DJANGO_DEBUG`
- **SECRET_KEY**: `DJANGO_SECRET_KEY`
- **MySQL 数据库配置**:
  - 服务器: `DB_HOST`
  - 端口: `DB_PORT`
  - 数据库名: `DB_NAME`
  - 用户: `DB_USER`
  - 密码: `DB_PASSWORD`

### 3. 执行数据库初始化

```bash
python manage.py makemigrations
python manage.py makemigrations img_admin xadmin
python manage.py migrate
```

### 4. 创建超级管理员

```bash
python manage.py createsuperuser
```

### 5. 运行后端程序

#### 方式 1

```bash
python manage.py runserver
```

#### 方式 2

安装 `waitress` 并运行：

```bash
pip install waitress
waitress-serve --threads=8 --connection-limit=2000 --backlog=2048 --port=8000 liuyanben.wsgi:application
```


