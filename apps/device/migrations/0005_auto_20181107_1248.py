# Generated by Django 2.1.2 on 2018-11-07 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0004_auto_20181026_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='customer_name',
            field=models.CharField(max_length=50, null=True, verbose_name='客户用户名'),
        ),
    ]
