# Generated by Django 2.1.2 on 2018-10-26 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0003_auto_20181023_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='sshpassword',
            field=models.CharField(max_length=50, verbose_name='服务器登陆密码'),
        ),
    ]
