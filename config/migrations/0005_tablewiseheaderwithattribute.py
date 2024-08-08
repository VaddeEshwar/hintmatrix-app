# Generated by Django 2.2.4 on 2019-12-02 15:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0004_tablename"),
    ]

    operations = [
        migrations.CreateModel(
            name="TableWiseHeaderWithAttribute",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "slug",
                    models.CharField(
                        blank=True, default=None, max_length=64, null=True, unique=True
                    ),
                ),
                ("is_active", models.NullBooleanField(default=False)),
                ("c_on", models.DateTimeField(auto_now_add=True)),
                ("u_on", models.DateTimeField(auto_now=True)),
                (
                    "tbl",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="config.TableName",
                        verbose_name="Table Name",
                    ),
                ),
                (
                    "tbl_attribute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="config.TableAttribute",
                        verbose_name="Field Name",
                    ),
                ),
                (
                    "tbl_header",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="config.TableHeader",
                        verbose_name="Header / Column Name",
                    ),
                ),
            ],
            options={
                "ordering": ("-u_on",),
            },
        ),
    ]
