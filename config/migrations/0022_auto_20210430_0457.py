# Generated by Django 3.1.4 on 2021-04-30 04:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0021_auto_20210430_0347"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tableattribute",
            name="tr_type",
        ),
        migrations.AddField(
            model_name="tableattribute",
            name="tbl_header",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="config.tableheader",
            ),
        ),
    ]
