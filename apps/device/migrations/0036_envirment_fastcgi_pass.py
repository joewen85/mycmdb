# Generated by Django 2.2.17 on 2021-03-29 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0035_auto_20210318_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='envirment',
            name='fastcgi_pass',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='后端PHP处理方式'),
        ),
    ]
