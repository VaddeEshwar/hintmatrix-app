# Generated by Django 3.1.4 on 2022-12-29 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_collagedetails_collegewiseuser_userreferencecode_userwisereference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreferencecode',
            name='referral_code',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]
