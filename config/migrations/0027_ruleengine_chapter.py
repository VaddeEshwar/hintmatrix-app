# Generated by Django 3.1.4 on 2021-07-09 18:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0026_chapter"),
    ]

    operations = [
        migrations.AddField(
            model_name="ruleengine",
            name="chapter",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="config.chapter",
                verbose_name="chapter",
            ),
        ),
    ]
