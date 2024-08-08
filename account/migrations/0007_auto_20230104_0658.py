# Generated by Django 3.1.4 on 2023-01-04 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_auto_20221229_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='userwisereference',
            name='ip_address',
            field=models.GenericIPAddressField(default='a00f:a000:a000:a000:0000:a000:a000:a000'),
        ),
        migrations.AddField(
            model_name='userwisereference',
            name='user_agent',
            field=models.CharField(default='n/a', max_length=512),
        ),
    ]
