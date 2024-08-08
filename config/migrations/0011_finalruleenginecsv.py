# Generated by Django 3.1.4 on 2021-04-10 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0010_tableattribute_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinalRuleEngineCsv",
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
                    "attribute_code",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "atribute_name",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "relationship",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "pair_with_attribute",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                ("pairing_priority", models.IntegerField(blank=True, null=True)),
                (
                    "operation1",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "table1_name",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "header1_name",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "table1_header1_help",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "operation2",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "table2_name",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "header2_name",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                (
                    "table2_header2_help",
                    models.CharField(blank=True, max_length=1024, null=True),
                ),
                ("c_on", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "final_Rule_engine_csv",
                "managed": False,
            },
        ),
    ]
