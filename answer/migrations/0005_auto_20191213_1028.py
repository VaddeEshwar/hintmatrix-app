# Generated by Django 2.2.4 on 2019-12-13 10:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0005_tablewiseheaderwithattribute"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("question", "0004_auto_20191129_1051"),
        ("answer", "0004_auto_20191213_0933"),
    ]

    operations = [
        migrations.AddField(
            model_name="examanswer",
            name="user",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="examanswer",
            unique_together={
                ("user", "exam", "qun", "tbl_name", "tbl_header", "attribute")
            },
        ),
    ]
