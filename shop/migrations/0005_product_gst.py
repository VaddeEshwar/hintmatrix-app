# Generated by Django 3.1.4 on 2022-06-16 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20220614_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gst',
            field=models.FloatField(default=0),
        ),
    ]
