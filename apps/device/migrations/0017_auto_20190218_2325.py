# Generated by Django 2.1.7 on 2019-02-18 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0016_auto_20190119_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cloudips',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='deploy_record',
            name='deploy_datetime',
            field=models.DateTimeField(auto_now_add=True, verbose_name='部署时间'),
        ),
        migrations.AlterField(
            model_name='device',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='envirment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
    ]
