from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Cloudips(models.Model):
    """服务器运营商"""
    cloudipsname = models.CharField(max_length=10, verbose_name="服务器运营商")
    describe = models.CharField(max_length=10, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    class Meta:
        verbose_name = "服务器运营商"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.describe


class Envirment(models.Model):
    """服务器环境"""
    envname = models.CharField(max_length=20, verbose_name="服务器运行环境")
    describe = models.CharField(max_length=20, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    phpbin = models.CharField(max_length=100, verbose_name="PHP环境路径", null=True)
    vhost_path = models.CharField(max_length=100, verbose_name="网站虚拟目录路径", null=True)
    fastcgi_pass = models.CharField(max_length=64, verbose_name="后端PHP处理方式", null=True, blank=True)

    class Meta:
        verbose_name = "运行环境"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.describe


class Jobs(models.Model):
    """任务"""
    jid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="任务名称")
    path = models.CharField(max_length=100, verbose_name="任务路径")
    describe = models.CharField(max_length=50, verbose_name="描述")

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Device(models.Model):
    """服务器详情"""
    hostname = models.CharField(max_length=50, verbose_name="服务器名称", null=False, unique=True, db_index=True)
    ipaddress = models.GenericIPAddressField(verbose_name='服务器IP地址', db_index=True)
    sshuser = models.CharField(max_length=20, verbose_name="服务器登陆用户")
    sshpassword = models.CharField(max_length=50, verbose_name="服务器登陆密码", null=False)
    websitepath = models.CharField(max_length=200, verbose_name="网站存放位置", null=False)
    envirment = models.ForeignKey(Envirment, verbose_name="运行环境", on_delete=models.DO_NOTHING)
    cloudips = models.ForeignKey(Cloudips, verbose_name="服务器运营商", on_delete=models.DO_NOTHING)
    customer_name = models.CharField(max_length=50, verbose_name="客户用户名", null=True)
    sshport = models.PositiveSmallIntegerField(verbose_name="服务器登陆端口", default=22)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    # is_monitor = models.BooleanField(verbose_name="是否监控")
    is_maintenance = models.BooleanField(verbose_name="是否维护", default=0)
    maintenance_duration = models.CharField(max_length=25, verbose_name="维护期限", null=True, blank=True)
    deploy_times = models.IntegerField(verbose_name="部署队列和计划任务次数", default=0)
    deploy_weiqingshop_times = models.SmallIntegerField(verbose_name="部署框架与商城次数", default=0)
    deploy_frameworkshop_times = models.SmallIntegerField(verbose_name="部署微擎与商城次数", default=0)
    others = models.TextField(verbose_name="其他内容", null=True, blank=True)
    paid = models.BooleanField(verbose_name="商城收费客户", default=0)
    ftpuser = models.CharField(max_length=32, default='www', verbose_name="ftp用户名")
    ftppassword = models.CharField(max_length=32, verbose_name="ftp密码", null=True)
    mysqluser = models.CharField(max_length=32, default='root', verbose_name="mysql用户名")
    mysqlpassword = models.CharField(max_length=32, verbose_name="mysql密码", null=True)
    mysqladdress = models.CharField(max_length=64, default='127.0.0.1', verbose_name="mysql连接地址")
    # 商城版本 0为独立版，1为微擎版
    shop_version = models.BooleanField(verbose_name="商城版本", default=0)
    mongodbuser = models.CharField(max_length=32, verbose_name='mongodb用户名', default='root')
    mongodbaddress = models.CharField(max_length=64, verbose_name='mongodb连接地址', default='127.0.0.1')

    class Meta:
        verbose_name = "用户设备信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname


class Deploy_record(models.Model):
    """部署队列和计划任务记录"""
    hostname = models.ForeignKey(Device, related_name='deploy_record', verbose_name="服务器名称", on_delete=models.CASCADE)
    # hostname = models.CharField(verbose_name="服务器名称", max_length=32, null=True)
    deploy_datetime = models.DateTimeField(auto_now_add=True, verbose_name="部署时间")
    desc = models.CharField(max_length=100, verbose_name="描述", null=True)
    operator = models.CharField(max_length=20, verbose_name="操作员", null=True)
    # operator = models.ForeignKey(User, verbose_name="操作员", on_delete=models.DO_NOTHING, null=True)
    remote_ip = models.GenericIPAddressField(verbose_name="远程访问地址", null=True)
    # jobname = models.ForeignKey(Jobs, on_delete=models.DO_NOTHING, null=True, verbose_name="任务名称")
    jobname = models.CharField(max_length=32, null=True, verbose_name="任务名称")
    result = models.TextField(null=True, verbose_name="执行任务结果")

    class Meta:
        verbose_name = "部署记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "结果"


class Password_record(models.Model):
    """独立密码表"""
    ipaddress = models.ForeignKey(Device, db_column="server_ip", related_name="PASSWORD", on_delete=models.CASCADE)
    sshpassword = models.CharField(max_length=600, verbose_name="服务器登陆密码", null=False)
    ftppassword = models.CharField(max_length=600, verbose_name="ftp密码", null=True)
    mysqlpassword = models.CharField(max_length=600, verbose_name="mysql密码", null=True)
    mongodbpassword = models.CharField(max_length=600, verbose_name="mongodb密码", null=True)

    def __str__(self):
        return "密码表"

    class Meta:
        verbose_name = "密码表"
        verbose_name_plural = verbose_name

        default_permissions = ()

        permissions = (
            ("select_table", "查看密码表"),
            ("change_table", "修改密码表"),
            ("decode_password", "解密加密密码")
        )
