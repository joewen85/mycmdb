# Generated by Django 2.1.2 on 2018-11-16 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0011_auto_20181116_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='maintenance_duration',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='维护期限'),
        ),
    ]
