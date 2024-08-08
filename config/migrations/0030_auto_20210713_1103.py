# Generated by Django 3.1.4 on 2021-07-13 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0029_auto_20210713_1055"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ruleengine",
            name="relationship",
            field=models.PositiveSmallIntegerField(
                choices=[(11, "1 TO 1"), (121, "1 TO 2"), (131, "1 TO 3")],
                default=11,
                verbose_name="relationship",
            ),
        ),
    ]
