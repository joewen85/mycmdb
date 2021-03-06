# Generated by Django 2.1.7 on 2019-03-27 04:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('device', '0017_auto_20190218_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploy_record',
            name='operator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='操作员'),
        ),
        migrations.AddField(
            model_name='deploy_record',
            name='remote_ip',
            field=models.GenericIPAddressField(null=True, verbose_name='远程访问地址'),
        ),
        migrations.AlterField(
            model_name='deploy_record',
            name='hostname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='device.Device', verbose_name='服务器名称'),
        ),
        migrations.AlterField(
            model_name='device',
            name='cloudips',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='device.Cloudips', verbose_name='服务器运营商'),
        ),
        migrations.AlterField(
            model_name='device',
            name='envirment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='device.Envirment', verbose_name='运行环境'),
        ),
    ]
