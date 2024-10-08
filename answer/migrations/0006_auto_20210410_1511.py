# Generated by Django 3.1.4 on 2021-04-10 15:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("config", "0011_finalruleenginecsv"),
        ("question", "0008_auto_20210227_0742"),
        ("answer", "0005_auto_20191213_1028"),
    ]

    operations = [
        migrations.AlterField(
            model_name="examanswer",
            name="attribute",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="config.tableattribute",
            ),
        ),
        migrations.AlterField(
            model_name="examanswer",
            name="exam",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="question.exam",
            ),
        ),
        migrations.AlterField(
            model_name="examanswer",
            name="qun",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="question.examquestion",
            ),
        ),
        migrations.AlterField(
            model_name="examanswer",
            name="tbl_header",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="config.tableheader",
            ),
        ),
        migrations.AlterField(
            model_name="examanswer",
            name="tbl_name",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="config.tablename",
            ),
        ),
        migrations.AlterField(
            model_name="examanswer",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
