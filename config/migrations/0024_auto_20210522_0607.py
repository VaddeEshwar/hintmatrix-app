# Generated by Django 3.1.4 on 2021-05-22 06:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0023_ruleengine_tbl_attribute_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ruleengine",
            name="header2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="header2",
                to="config.tableheader",
                verbose_name="Header2 / Column2 Name",
            ),
        ),
        migrations.AlterField(
            model_name="ruleengine",
            name="tbl2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tbl2",
                to="config.tablename",
                verbose_name="Table2 Name",
            ),
        ),
    ]
