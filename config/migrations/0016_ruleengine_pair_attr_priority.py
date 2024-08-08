# Generated by Django 3.1.4 on 2021-04-11 13:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0015_auto_20210411_0913"),
    ]

    operations = [
        migrations.AddField(
            model_name="ruleengine",
            name="pair_attr_priority",
            field=models.PositiveSmallIntegerField(
                blank=True, default=None, verbose_name="order by pair attribute"
            ),
        ),
    ]
