# Generated by Django 3.1.4 on 2023-09-01 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_auto_20230901_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='ip_address',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='user_agent',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
