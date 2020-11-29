## User Manuals

[link](https://github.com/Peternal/Online-Questionnaire/blob/master/User%20Manuals.pdf)


## Development Environment

- Python 3.6.8  
- Django 3.0.6 


### Using virturalenv

```
pip install virtualenv

切换到项目目录下, 执行下面的命令

virtualenv venv

venv\scripts\activate
```
### Install Requirements
```
pip install -r requirements.txt
```

### Using mysql
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


### Import Database
```
打开mysql，创建papers

create database papers default charset utf8;

导入papers.sql
```

### Migrate
```
如果导入papers.sql后无法创建中文问卷，建议直接使用migrate

同样先创建papers

create database papers default charset utf8;

切换到项目目录下, 执行migrate命令

python manage.py makemigrations

python manage.py migrate

```



### Startup

```
python manage.py runserver 0.0.0.0:8000

项目初始无用户账号，请在注册页面创建

django后台地址：

127.0.0.1:8000/admin/

账号 admin 
密码 admin
```
