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
```
```bash
pip install -r requirement.txt
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
脚本运行方式：推荐使用supervisor来管理进程

1.运行项目
```bash
uwsgi --ini uwsgi.ini
```

2.设置开机启动
* 将start_cmdb.sh复制到/etc/init.d/cmdb,并修改里面的path为项目的路径，赋予执行权限
```bash
chmod +x /etc/init.d/cmdb
chkconfig --add cmdb
chkconfig cmdb on

```

3.使用supervisor管理
```bash
cmdb.ini: python核心进去启动配置
channels.ini：使用asgi/channels实现websocket长连接进程
```

完成开启自启动