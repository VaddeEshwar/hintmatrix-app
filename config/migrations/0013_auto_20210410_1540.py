# Generated by Django 3.1.4 on 2021-04-10 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0012_auto_20210410_1532"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tableattribute",
            name="code",
            field=models.CharField(blank=True, default=None, max_length=16),
        ),
        migrations.AlterField(
            model_name="tableattribute",
            name="short_name",
            field=models.CharField(blank=True, default=None, max_length=15),
        ),
    ]
