# mycmdb

## 项目必须安装redis
session的存储引擎改redis
如不使用，到settings.py中将下面两行注释了
```python
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = 'session'  # 指明使用那个库保存session数据

```
***

## 数据库连接说明：

### 1.centos系统配置：
* 如直接yum安装mysql-devel或mariadb-devel、mysql-server的可以忽略下面操作

* 查找系统的libmysqlclient.so.18（一般yum安装了mysql-devel或mariadb-devel都会有这个库），将libmysqlclient.so.18映射到相关mysql编译安装的目录的lib里面
```bash
如：
mysql安装路径：/usr/lib/mysql
将libmysqlclient.so.18映射到/usr/lib/mysql/lib里面，编辑/etc/ld.so.conf,加入mysql的lib文件夹，执行ldconfig应用
ln -s /usr/lib64/mysql/libmysqlclient.so.18.0.0 /usr/local/mysql/lib/libmysqlclient.so.18

```
***

### macos
使用mysqlclient 1.4.6无需操作一下步骤
~~brew install mysql-connector-c
编辑sudo vim /usr/local/bin/mysql_config
on macOS, on or about line 112:

libs="-L$pkglibdir"
libs="$libs -l "

to

libs="-L$pkglibdir"
libs="$libs -lmysqlclient -lssl -lcrypto"~~

***

## 部署
1.克隆代码
```bash
git clone https://github.com/joewen85/mycmdb.git
```

2.安装python包
```bash
pip install git+git://github.com/sshwsfc/xadmin.git@django2
pip install pipenv
```
```bash
pipenv install
```

3.创建数据库


4.创建数据表
```bash
python manage.py migrate
```
5.生成配置配置文件
```python
cp config_exapple.py config.py
并在里面配置相关信息

关于secret_key生成：
from django.core.management import utils
utils.get_random_secret_key()
```

## 运行
### 使用supervisor来管理进程

1.运行项目,先安装supervisor进程管理
```bash
# centos8
dnf install supervisor

# centos7
yum install supervisor
```

2.设置开机启动
* 将cmdb.ini，channels.ini复制到/etc/supervisord.d/
修改内容
```ini
# cmdb.ini
directory = 项目存放目录
command = uwsgi文件绝对路径 --ini 项目根目录下/uwsgi.ini

stdout_logfile = cmdb输出日志文件路径
stderr_logfile = cmdb输出错误日志文件路径
```
```ini
# channels.ini
command = 实际python执行文件的绝对路径 manage.py runserver xxxx:xxx
stdout_logfile = channel输出日志文件路径
stderr_logfile = channel输出错误日志文件路径
```
```
# ansible.cfg
需要修改：
fact_caching_connection = 127.0.0.1:6379:6:mismis
为你的redis信息 redis地址:端口:库:密码
```

3.使用supervisor管理说明
```
cmdb.ini: cmdb核心和任务执行通过uwsgi运行
channels.ini：使用asgi/channels实现websocket长连接进程，主要webssh使用
```

4.开启celery进程
```bash
# 复制项目内的celery.service到/lib/systemd/system/
cp celery.service /lib/systemd/system/ && systemctl daemon-reload && systemctl enable celery

# 修改项目中celery_worker.sh的执行权限
chmod +x celery_worker.sh
```
* celery进程启停。修改了task必须重启celery
```bash
# 启动
systemctl start celery

# 重启
systemctl restart celery

# 停止
systemctl stop celery
```

完成开启自启动
