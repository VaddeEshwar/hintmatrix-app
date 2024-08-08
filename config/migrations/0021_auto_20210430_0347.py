# Generated by Django 3.1.4 on 2021-04-30 03:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0020_auto_20210430_0318"),
    ]

    operations = [
        migrations.AddField(
            model_name="tableheader",
            name="status",
            field=models.PositiveIntegerField(default=0, verbose_name="row status"),
        ),
        migrations.AddField(
            model_name="tablename",
            name="status",
            field=models.PositiveIntegerField(default=0, verbose_name="row status"),
        ),
        migrations.AlterField(
            model_name="tableheader",
            name="c_on",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created on"),
        ),
        migrations.AlterField(
            model_name="tableheader",
            name="is_active",
            field=models.PositiveSmallIntegerField(
                default=0, verbose_name="active row"
            ),
        ),
        migrations.AlterField(
            model_name="tableheader",
            name="u_on",
            field=models.DateTimeField(auto_now=True, verbose_name="updated on"),
        ),
        migrations.AlterField(
            model_name="tablename",
            name="c_on",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created on"),
        ),
        migrations.AlterField(
            model_name="tablename",
            name="is_active",
            field=models.PositiveSmallIntegerField(
                default=0, verbose_name="active row"
            ),
        ),
        migrations.AlterField(
            model_name="tablename",
            name="u_on",
            field=models.DateTimeField(auto_now=True, verbose_name="updated on"),
        ),
    ]
