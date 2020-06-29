## 开发环境

- Python 3.6.8  
- Django 3.0.6 


### 使用虚拟环境(virturalenv)

```
pip install virtualenv

切换到项目目录下, 执行下面的命令

virtualenv venv

venv\scripts\activate
```
### 安装依赖
```
pip install -r requirements.txt
```

### 使用mysql
```
到papers/settings/settings.py文件
修改
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'papers',
        'HOST': '',
        'PORT': '',
        'USER': 'root',
        'PASSWORD': 'mysql',
    }
}

此处默认mysql密码为mysql，请改成自己的密码
HOST默认为127.0.0.1
PORT默认为3306

```


### 导入数据库
```
打开mysql，创建papers

create database papers default charset utf8;

导入papers.sql
```

### migrate
```
如果导入papers.sql后无法创建中文问卷，建议直接使用migrate

同样先创建papers

create database papers default charset utf8;

切换到项目目录下, 执行migrate命令

python manage.py makemigrations

python manage.py migrate

```



### 启动项目

```
python manage.py runserver 0.0.0.0:8000

项目初始无用户账号，请在注册页面创建

django后台地址：

127.0.0.1:8000/admin/

账号 admin 
密码 admin
```