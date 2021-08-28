# Generated by Django 2.1.2 on 2018-11-15 13:21

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0008_auto_20181114_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deploy_record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deploy_datetime', models.DateTimeField(default=datetime.datetime.now, verbose_name='部署时间')),
                ('desc', models.CharField(max_length=100, null=True, verbose_name='描述')),
            ],
        ),
        migrations.RemoveField(
            model_name='device',
            name='deploy_desc',
        ),
        migrations.AddField(
            model_name='deploy_record',
            name='hostname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='device.Device', verbose_name='服务器名称'),
        ),
    ]
