# Generated by Django 3.1.4 on 2021-07-12 14:42

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("question", "0010_auto_20210709_1856"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExamEvent",
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
                    models.SlugField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="row id",
                        unique=True,
                    ),
                ),
                (
                    "is_active",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="active row"
                    ),
                ),
                (
                    "status",
                    models.PositiveIntegerField(default=0, verbose_name="row status"),
                ),
                (
                    "c_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="created on"),
                ),
                (
                    "u_on",
                    models.DateTimeField(auto_now=True, verbose_name="updated on"),
                ),
                ("description", models.CharField(max_length=512)),
                ("valid", models.BooleanField(default=False, null=True)),
                ("action", models.CharField(max_length=512)),
                (
                    "exam",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="question.exam",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-u_on",),
                "abstract": False,
            },
        ),
    ]
